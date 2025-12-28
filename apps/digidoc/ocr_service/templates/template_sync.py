"""
Template Sync
Synchronizes templates between OCR app cache and calling applications.
Supports both push (from calling app) and pull (from OCR app) sync.
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from .template_cache import TemplateCache
from ..database.models import AppRegistration, TemplateSyncMetadata, get_session
from sqlalchemy import and_


class TemplateSync:
    """Manages template synchronization with calling applications."""
    
    def __init__(self, cache: TemplateCache):
        """
        Initialize template sync.
        
        Args:
            cache: TemplateCache instance
        """
        self.cache = cache
    
    def pull_templates(
        self,
        calling_app_id: str,
        document_type: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Pull templates from calling application.
        
        Args:
            calling_app_id: Calling application identifier
            document_type: Document type filter (optional)
            vendor: Vendor name filter (optional)
            
        Returns:
            List of templates pulled and cached
        """
        session = get_session()
        try:
            # Get app registration
            app = session.query(AppRegistration).filter(
                AppRegistration.app_id == calling_app_id,
                AppRegistration.is_active == True
            ).first()
            
            if not app:
                raise ValueError(f"App not registered: {calling_app_id}")
            
            # Build API URL
            url = f"{app.api_endpoint}/api/ocr/templates"
            params = {
                'calling_app_id': calling_app_id,
            }
            if document_type:
                params['document_type'] = document_type
            if vendor:
                params['vendor'] = vendor
            
            # Make API call
            headers = {}
            if app.api_key:
                headers['Authorization'] = f'Bearer {app.api_key}'
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            templates = data.get('templates', [])
            
            # Cache each template
            cached_templates = []
            for template_data in templates:
                cached = self.cache.cache_template(
                    calling_app_id=calling_app_id,
                    template_id=template_data['template_id'],
                    document_type=template_data.get('document_type'),
                    vendor=template_data.get('vendor'),
                    format_name=template_data.get('format_name'),
                    template_data=template_data.get('template_data', {}),
                    field_mappings=template_data.get('field_mappings', {})
                )
                
                # Update sync metadata
                self._update_sync_metadata(
                    calling_app_id,
                    template_data['template_id'],
                    'synced',
                    None
                )
                
                cached_templates.append(self.cache._template_to_dict(cached))
            
            return cached_templates
            
        except requests.exceptions.RequestException as e:
            # Update sync metadata with error
            if 'template_data' in locals():
                self._update_sync_metadata(
                    calling_app_id,
                    template_data.get('template_id', 'unknown'),
                    'error',
                    str(e)
                )
            raise
        finally:
            session.close()
    
    def push_template_update(
        self,
        calling_app_id: str,
        template_id: str,
        template_data: Dict[str, Any]
    ) -> bool:
        """
        Receive pushed template update from calling application.
        
        Args:
            calling_app_id: Calling application identifier
            template_id: Template ID from calling app
            template_data: Updated template data
            
        Returns:
            True if update successful
        """
        try:
            # Update cache
            self.cache.cache_template(
                calling_app_id=calling_app_id,
                template_id=template_id,
                document_type=template_data.get('document_type'),
                vendor=template_data.get('vendor'),
                format_name=template_data.get('format_name'),
                template_data=template_data.get('template_data', {}),
                field_mappings=template_data.get('field_mappings', {})
            )
            
            # Update sync metadata
            self._update_sync_metadata(
                calling_app_id,
                template_id,
                'synced',
                None
            )
            
            return True
        except Exception as e:
            self._update_sync_metadata(
                calling_app_id,
                template_id,
                'error',
                str(e)
            )
            return False
    
    def sync_if_needed(
        self,
        calling_app_id: str,
        document_type: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Sync templates if cache is stale or missing.
        
        Args:
            calling_app_id: Calling application identifier
            document_type: Document type filter (optional)
            vendor: Vendor name filter (optional)
            
        Returns:
            List of cached templates
        """
        # Check if we need to sync
        cached = self.cache.get_templates_for_context(
            calling_app_id,
            document_type,
            vendor
        )
        
        # For MVP: Always pull to ensure fresh templates
        # Future: Check sync metadata to determine if sync needed
        return self.pull_templates(calling_app_id, document_type, vendor)
    
    def _update_sync_metadata(
        self,
        calling_app_id: str,
        template_id: str,
        status: str,
        error: Optional[str]
    ):
        """Update template sync metadata."""
        session = get_session()
        try:
            metadata = session.query(TemplateSyncMetadata).filter(
                and_(
                    TemplateSyncMetadata.calling_app_id == calling_app_id,
                    TemplateSyncMetadata.template_id == template_id
                )
            ).first()
            
            if metadata:
                metadata.sync_status = status
                metadata.last_sync_attempt = datetime.utcnow()
                metadata.sync_error = error
                metadata.updated_at = datetime.utcnow()
            else:
                metadata = TemplateSyncMetadata(
                    calling_app_id=calling_app_id,
                    template_id=template_id,
                    sync_status=status,
                    last_sync_attempt=datetime.utcnow(),
                    sync_error=error
                )
                session.add(metadata)
            
            session.commit()
        finally:
            session.close()
