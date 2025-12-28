"""
Database Models for OCR App
SQLAlchemy models for template caching and app registration.
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional

Base = declarative_base()


class CachedTemplate(Base):
    """Cached document template from calling application."""
    
    __tablename__ = 'cached_templates'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    calling_app_id = Column(String(100), nullable=False, index=True)
    template_id = Column(String(100), nullable=False)  # ID from calling app
    document_type = Column(String(50), nullable=True, index=True)  # receipt, contract, bid, etc.
    vendor = Column(String(200), nullable=True, index=True)  # Vendor name
    format_name = Column(String(100), nullable=True)  # Format identifier (e.g., "thermal_3x12")
    template_data = Column(JSON, nullable=False)  # Full template definition
    field_mappings = Column(JSON, nullable=True)  # Field box coordinates and mappings
    structural_fingerprint = Column(JSON, nullable=True)  # Structural fingerprint with zone ratios (DPI/scale invariant)
    last_synced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_app_doc_vendor_format', 'calling_app_id', 'document_type', 'vendor', 'format_name'),
    )


class TemplateSyncMetadata(Base):
    """Metadata for template synchronization with calling applications."""
    
    __tablename__ = 'template_sync_metadata'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    calling_app_id = Column(String(100), nullable=False, index=True)
    template_id = Column(String(100), nullable=False, index=True)
    sync_status = Column(String(20), nullable=False, default='pending')  # synced, pending, error
    last_sync_attempt = Column(DateTime, nullable=True)
    sync_error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AppRegistration(Base):
    """Registered calling applications."""
    
    __tablename__ = 'app_registrations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    app_id = Column(String(100), nullable=False, unique=True, index=True)
    app_name = Column(String(200), nullable=False)
    api_endpoint = Column(String(500), nullable=False)  # Base URL for template sync
    api_key = Column(String(200), nullable=True)  # Authentication key (encrypted in production)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_database_url() -> str:
    """Get database URL from environment or use SQLite default."""
    import os
    db_url = os.environ.get('OCR_DATABASE_URL')
    if db_url:
        return db_url
    # Default to SQLite in project directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(project_root, 'ocr_service', 'database', 'ocr_cache.db')
    return f'sqlite:///{db_path}'


def create_engine_instance():
    """Create SQLAlchemy engine."""
    db_url = get_database_url()
    if db_url.startswith('sqlite'):
        return create_engine(db_url, connect_args={'check_same_thread': False})
    return create_engine(db_url)


def init_database():
    """Initialize database tables."""
    engine = create_engine_instance()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session."""
    engine = create_engine_instance()
    Session = sessionmaker(bind=engine)
    return Session()
