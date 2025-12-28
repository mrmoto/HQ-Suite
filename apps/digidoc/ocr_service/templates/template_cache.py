"""
Template Cache
Manages caching of document templates from calling applications.
Supports multiple formats per vendor/document type.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..database.models import CachedTemplate, TemplateSyncMetadata, get_session
from sqlalchemy import and_


class TemplateCache:
    """Manages cached document templates."""
    
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize template cache.
        
        Args:
            cache_ttl_hours: Hours before cache is considered stale
        """
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
    
    def get_cached_template(
        self,
        calling_app_id: str,
        template_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific cached template by ID.
        
        Args:
            calling_app_id: Calling application identifier
            template_id: Template ID from calling app
            
        Returns:
            Template dictionary or None if not cached
        """
        session = get_session()
        try:
            template = session.query(CachedTemplate).filter(
                and_(
                    CachedTemplate.calling_app_id == calling_app_id,
                    CachedTemplate.template_id == template_id
                )
            ).first()
            
            if template:
                return self._template_to_dict(template)
            return None
        finally:
            session.close()
    
    def get_templates_for_context(
        self,
        calling_app_id: str,
        document_type: Optional[str] = None,
        vendor: Optional[str] = None,
        format_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cached templates matching context.
        
        Args:
            calling_app_id: Calling application identifier
            document_type: Document type filter (optional)
            vendor: Vendor name filter (optional)
            format_name: Format name filter (optional)
            
        Returns:
            List of matching templates
        """
        session = get_session()
        try:
            query = session.query(CachedTemplate).filter(
                CachedTemplate.calling_app_id == calling_app_id
            )
            
            if document_type:
                query = query.filter(CachedTemplate.document_type == document_type)
            if vendor:
                query = query.filter(CachedTemplate.vendor == vendor)
            if format_name:
                query = query.filter(CachedTemplate.format_name == format_name)
            
            templates = query.all()
            return [self._template_to_dict(t) for t in templates]
        finally:
            session.close()
    
    def cache_template(
        self,
        calling_app_id: str,
        template_id: str,
        document_type: Optional[str],
        vendor: Optional[str],
        format_name: Optional[str],
        template_data: Dict[str, Any],
        field_mappings: Optional[Dict[str, Any]] = None
    ) -> CachedTemplate:
        """
        Cache a template from calling application.
        
        Args:
            calling_app_id: Calling application identifier
            template_id: Template ID from calling app
            document_type: Document type
            vendor: Vendor name
            format_name: Format identifier
            template_data: Full template definition
            field_mappings: Field mappings (optional)
            
        Returns:
            Cached template object
        """
        session = get_session()
        try:
            # Check if template already exists
            existing = session.query(CachedTemplate).filter(
                and_(
                    CachedTemplate.calling_app_id == calling_app_id,
                    CachedTemplate.template_id == template_id
                )
            ).first()
            
            if existing:
                # Update existing
                existing.document_type = document_type
                existing.vendor = vendor
                existing.format_name = format_name
                existing.template_data = template_data
                existing.field_mappings = field_mappings
                existing.last_synced_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                session.commit()
                return existing
            else:
                # Create new
                template = CachedTemplate(
                    calling_app_id=calling_app_id,
                    template_id=template_id,
                    document_type=document_type,
                    vendor=vendor,
                    format_name=format_name,
                    template_data=template_data,
                    field_mappings=field_mappings or {},
                    last_synced_at=datetime.utcnow()
                )
                session.add(template)
                session.commit()
                return template
        finally:
            session.close()
    
    def is_cache_stale(
        self,
        calling_app_id: str,
        template_id: str,
        last_updated: datetime
    ) -> bool:
        """
        Check if cached template is stale.
        
        Args:
            calling_app_id: Calling application identifier
            template_id: Template ID from calling app
            last_updated: Last update time from calling app
            
        Returns:
            True if cache is stale or missing
        """
        session = get_session()
        try:
            template = session.query(CachedTemplate).filter(
                and_(
                    CachedTemplate.calling_app_id == calling_app_id,
                    CachedTemplate.template_id == template_id
                )
            ).first()
            
            if not template:
                return True  # Not cached, consider stale
            
            # Check if cache is older than TTL
            if datetime.utcnow() - template.last_synced_at > self.cache_ttl:
                return True
            
            # Check if calling app has newer version
            if last_updated > template.last_synced_at:
                return True
            
            return False
        finally:
            session.close()
    
    def clear_cache_for_app(self, calling_app_id: str):
        """Clear all cached templates for a calling application."""
        session = get_session()
        try:
            session.query(CachedTemplate).filter(
                CachedTemplate.calling_app_id == calling_app_id
            ).delete()
            session.commit()
        finally:
            session.close()
    
    def _template_to_dict(self, template: CachedTemplate) -> Dict[str, Any]:
        """Convert template model to dictionary."""
        return {
            'id': template.id,
            'calling_app_id': template.calling_app_id,
            'template_id': template.template_id,
            'document_type': template.document_type,
            'vendor': template.vendor,
            'format_name': template.format_name,
            'template_data': template.template_data,
            'field_mappings': template.field_mappings,
            'last_synced_at': template.last_synced_at.isoformat() if template.last_synced_at else None,
        }
