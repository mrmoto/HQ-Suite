"""
OCR Service API Server
Flask API for processing document images (document-agnostic).
"""

import os
import sys

# Prevent PyArrow from initializing curl during fork (macOS security restriction)
# This must be set before any PyArrow/pandas imports
os.environ.setdefault('ARROW_DISABLE_CURL', '1')

import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from typing import Dict, Any, Optional
from .extractors.document_extractor import DocumentExtractor
from .ocr_processor import OCRProcessor
from .templates.template_cache import TemplateCache
from .templates.template_sync import TemplateSync
from .templates.template_matcher import TemplateMatcher
from .database.models import init_database
from .queue import enqueue_ocr_task
from .queue.queue_adapter import get_queue_adapter  # Direct import needed for status endpoint

# Initialize Flask app
# Set template and static folders for review UI
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Initialize components
extractor = None
template_cache = None
template_sync = None
template_matcher = None
ocr_processor = None


def init_components():
    """Initialize all OCR service components."""
    global extractor, template_cache, template_sync, template_matcher, ocr_processor
    
    # Initialize database
    init_database()
    
    # Initialize OCR processor
    if ocr_processor is None:
        tesseract_cmd = None
        common_paths = [
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',
            '/usr/bin/tesseract',
        ]
        for path in common_paths:
            if os.path.exists(path):
                tesseract_cmd = path
                break
        ocr_processor = OCRProcessor(tesseract_cmd=tesseract_cmd)
    
    # Initialize template cache
    if template_cache is None:
        template_cache = TemplateCache()
    
    # Initialize template sync
    if template_sync is None:
        template_sync = TemplateSync(template_cache)
    
    # Initialize template matcher
    if template_matcher is None:
        template_matcher = TemplateMatcher(template_cache, ocr_processor)
    
    # Initialize extractor (for backward compatibility)
    if extractor is None:
        extractor = DocumentExtractor(tesseract_cmd=tesseract_cmd)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ocr-service',
        'version': '0.1.0',
    }), 200


@app.route('/process', methods=['POST'])
def process_document():
    """
    Process document image (document-agnostic).
    
    Accepts:
    - file: Image file (multipart/form-data)
    - OR file_path: Path to image file (JSON)
    - calling_app_id: Calling application identifier (required)
    - context: Optional context (document_type, vendor, format_name)
    
    Returns:
    - JSON with extraction results, template matches, and review requirements
    """
    try:
        init_components()
        
        # Get calling app ID (required)
        calling_app_id = None
        if request.is_json and 'calling_app_id' in request.json:
            calling_app_id = request.json['calling_app_id']
        elif 'calling_app_id' in request.form:
            calling_app_id = request.form['calling_app_id']
        
        if not calling_app_id:
            return jsonify({'error': 'calling_app_id is required'}), 400
        
        # Get context (optional)
        context = {}
        if request.is_json and 'context' in request.json:
            context = request.json['context']
        elif 'context' in request.form:
            import json
            context = json.loads(request.form['context']) if request.form['context'] else {}
        
        document_type = context.get('document_type')
        vendor = context.get('vendor')
        format_name = context.get('format_name')
        
        # Determine file path
        file_path = None
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file provided'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', f'ocr_{filename}')
            file.save(file_path)
        
        # Handle file path (from file watcher)
        elif request.is_json and 'file_path' in request.json:
            file_path = request.json['file_path']
        elif 'file_path' in request.form:
            file_path = request.form['file_path']
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'error': 'Either "file" (multipart) or "file_path" (JSON/form) required, and file must exist'
            }), 400
        
        try:
            # Run OCR
            ocr_result = ocr_processor.process_image(file_path)
            ocr_text = ocr_result.get('text', '')
            
            # Sync templates if needed
            template_sync.sync_if_needed(calling_app_id, document_type, vendor)
            
            # Find matching templates
            template_matches = template_matcher.find_matching_templates(
                ocr_text,
                calling_app_id,
                document_type,
                vendor
            )
            
            # Determine best match
            best_match = None
            if template_matches and template_matches[0]['confidence'] >= 0.95:
                best_match = template_matches[0]
            
            # Determine if review is needed
            requires_review = False
            review_type = None
            confidence_level = None
            
            if not best_match or best_match['confidence'] < 0.90:
                # Need document type/template selection review
                requires_review = True
                if template_matches and template_matches[0]['confidence'] >= 0.80:
                    review_type = 'template_selection'
                else:
                    review_type = 'document_type_selection'
                confidence_level = 'low'
            else:
                # Try extraction with matched template
                # For MVP: Use existing extractor (will be enhanced later)
                extraction_result = extractor.extract(file_path)
                field_confidences = extraction_result.get('fields', {})
                
                # Check if any field has low confidence
                low_confidence_fields = [
                    field for field, conf in field_confidences.items()
                    if isinstance(conf, (int, float)) and conf < 0.95
                ]
                
                if low_confidence_fields:
                    requires_review = True
                    review_type = 'accuracy_review'
                    # Determine confidence level
                    avg_confidence = extraction_result.get('confidence', 0.0)
                    if avg_confidence < 0.70:
                        confidence_level = 'low'
                    elif avg_confidence < 0.85:
                        confidence_level = 'mid'
                    else:
                        confidence_level = 'high'
            
            # Build response
            response = {
                'document_id': str(uuid.uuid4()),
                'document_type': best_match['document_type'] if best_match else document_type,
                'template_matches': template_matches[:5],  # Top 5
                'requires_review': requires_review,
                'review_type': review_type,
                'confidence_level': confidence_level,
                'confidence': best_match['confidence'] if best_match else (template_matches[0]['confidence'] if template_matches else 0.0),
            }
            
            # Add extracted fields if we have a good match
            if best_match and not requires_review:
                extraction_result = extractor.extract(file_path)
                response['extracted_fields'] = extraction_result.get('fields', {})
                response['ocr_text'] = ocr_text
            else:
                response['extracted_fields'] = {}
                response['ocr_text'] = ocr_text
            
            return jsonify(response), 200
            
        finally:
            # Clean up temp file if we created it
            if 'file' in request.files and file_path and file_path.startswith('/tmp'):
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
        }), 500


@app.route('/templates/sync', methods=['POST'])
def sync_templates():
    """
    Pull templates from calling application.
    
    Accepts (JSON):
    - calling_app_id: Calling application identifier (required)
    - document_type: Document type filter (optional)
    - vendor: Vendor name filter (optional)
    
    Returns:
    - JSON with synced templates
    """
    try:
        init_components()
        
        data = request.get_json() or {}
        calling_app_id = data.get('calling_app_id')
        document_type = data.get('document_type')
        vendor = data.get('vendor')
        
        if not calling_app_id:
            return jsonify({'error': 'calling_app_id is required'}), 400
        
        templates = template_sync.pull_templates(calling_app_id, document_type, vendor)
        
        return jsonify({
            'templates': templates,
            'count': len(templates)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
        }), 500


@app.route('/templates/update', methods=['POST'])
def update_template():
    """
    Receive pushed template update from calling application.
    
    Accepts (JSON):
    - calling_app_id: Calling application identifier (required)
    - template_id: Template ID (required)
    - template_data: Updated template data (required)
    
    Returns:
    - JSON with update status
    """
    try:
        init_components()
        
        data = request.get_json() or {}
        calling_app_id = data.get('calling_app_id')
        template_id = data.get('template_id')
        template_data = data.get('template_data')
        
        if not all([calling_app_id, template_id, template_data]):
            return jsonify({
                'error': 'calling_app_id, template_id, and template_data are required'
            }), 400
        
        success = template_sync.push_template_update(
            calling_app_id,
            template_id,
            template_data
        )
        
        if success:
            return jsonify({'status': 'updated'}), 200
        else:
            return jsonify({'error': 'Update failed'}), 500
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
        }), 500


@app.route('/templates/cached', methods=['GET'])
def list_cached_templates():
    """
    List cached templates.
    
    Query parameters:
    - calling_app_id: Filter by calling app (optional)
    - document_type: Filter by document type (optional)
    - vendor: Filter by vendor (optional)
    
    Returns:
    - JSON with cached templates
    """
    try:
        init_components()
        
        calling_app_id = request.args.get('calling_app_id')
        document_type = request.args.get('document_type')
        vendor = request.args.get('vendor')
        
        if not calling_app_id:
            return jsonify({'error': 'calling_app_id is required'}), 400
        
        templates = template_cache.get_templates_for_context(
            calling_app_id,
            document_type,
            vendor
        )
        
        return jsonify({
            'templates': templates,
            'count': len(templates)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
        }), 500


@app.route('/format/detect', methods=['POST'])
def detect_format():
    """
    Detect document format only (no full extraction).
    Document-agnostic version.
    
    Accepts:
    - file: Image file (multipart/form-data)
    - OR image_path: Path to image file (JSON)
    - OR text: OCR text (JSON)
    
    Returns:
    - JSON with format detection results
    """
    try:
        init_components()
        
        # Handle OCR text directly
        if 'text' in request.json:
            text = request.json['text']
            format_template, confidence = extractor.ocr_processor.detect_format(text)
            
            return jsonify({
                'format_detected': format_template.format_id if format_template else None,
                'vendor': format_template.vendor_name if format_template else None,
                'confidence': float(confidence),
            }), 200
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file provided'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            filename = secure_filename(file.filename)
            temp_path = os.path.join('/tmp', f'ocr_{filename}')
            file.save(temp_path)
            
            try:
                # Run OCR
                ocr_result = extractor.ocr_processor.process_image(temp_path)
                text = ocr_result.get('text', '')
                
                # For MVP: Use existing format detection
                # Future: Use template matcher with cached templates
                format_template, confidence = ocr_processor.detect_format(text)
                
                return jsonify({
                    'format_detected': format_template.format_id if format_template else None,
                    'vendor': format_template.vendor_name if format_template else None,
                    'confidence': float(confidence),
                }), 200
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Handle file path
        elif 'image_path' in request.json:
            image_path = request.json['image_path']
            
            if not os.path.exists(image_path):
                return jsonify({'error': f'Image not found: {image_path}'}), 404
            
            # Run OCR
            ocr_result = extractor.ocr_processor.process_image(image_path)
            text = ocr_result.get('text', '')
            
            # Detect format
            format_template, confidence = extractor.ocr_processor.detect_format(text)
            
            return jsonify({
                'format_detected': format_template.format_id if format_template else None,
                'vendor': format_template.vendor_name if format_template else None,
                'confidence': float(confidence),
            }), 200
        
        else:
            return jsonify({
                'error': 'Either "file", "image_path", or "text" required'
            }), 400
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
        }), 500


@app.route('/review/document-type-selection/<review_id>', methods=['GET'])
def document_type_selection_review(review_id):
    """Serve document type selection review UI."""
    # Get review data from calling app API
    # For MVP: Return template with placeholder data
    return render_template('review/document_type_selection.html',
                         image_url='/static/placeholder.jpg',
                         template_matches=[])


@app.route('/review/template-editing/<template_id>', methods=['GET'])
def template_editing_review(template_id):
    """Serve template editing review UI."""
    # Get template data
    # For MVP: Return template with placeholder data
    return render_template('review/template_editing.html',
                         image_url='/static/placeholder.jpg',
                         template_data={'template_id': template_id})


@app.route('/review/accuracy/<review_id>', methods=['GET'])
def accuracy_review(review_id):
    """Serve accuracy review UI (low/mid/high)."""
    # Get review data from calling app API
    confidence_level = request.args.get('level', 'mid')
    # For MVP: Return template with placeholder data
    return render_template(f'review/accuracy_{confidence_level}.html',
                         image_url='/static/placeholder.jpg',
                         extracted_fields={},
                         confidence_level=confidence_level)


@app.route('/api/digidoc/queue', methods=['POST'])
def queue_document():
    """
    Queue a document for processing (async).
    
    Accepts (JSON):
    - file_path: Path to document file (required)
    - calling_app_id: Calling application identifier (required)
    - context: Optional context (document_type, vendor, format_name)
    
    Returns:
    - JSON with task_id for status checking
    """
    try:
        init_components()
        
        data = request.get_json() or {}
        
        # Get required fields
        file_path = data.get('file_path')
        calling_app_id = data.get('calling_app_id')
        
        if not file_path:
            return jsonify({'error': 'file_path is required'}), 400
        
        if not calling_app_id:
            return jsonify({'error': 'calling_app_id is required'}), 400
        
        # Verify file exists
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 404
        
        # Generate queue item ID
        queue_item_id = str(uuid.uuid4())
        
        # Enqueue processing task
        try:
            result = enqueue_ocr_task(
                'process_document_task',
                file_path,
                queue_item_id,
                calling_app_id
            )
            
            return jsonify({
                'task_id': result.task_id,
                'queue_item_id': queue_item_id,
                'status': result.status,
                'message': result.message
            }), 202  # 202 Accepted for async processing
            
        except Exception as e:
            return jsonify({
                'error': f'Failed to enqueue task: {str(e)}',
                'type': type(e).__name__
            }), 500
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
        }), 500


@app.route('/api/digidoc/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Get the status of a queued task.
    
    Returns:
    - JSON with task status, result (if completed), or error (if failed)
    """
    try:
        adapter = get_queue_adapter()
        status = adapter.get_task_status(task_id)
        
        if status.get('status') == 'error':
            return jsonify(status), 404
        
        return jsonify(status), 200
    
    except Exception as e:
        return jsonify({
            'task_id': task_id,
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500


if __name__ == '__main__':
    # Run development server
    port = int(os.environ.get('OCR_SERVICE_PORT', 5000))
    debug = os.environ.get('OCR_SERVICE_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting OCR Service on port {port}")
    print(f"Debug mode: {debug}")
    
    # Disable reloader to prevent fork crashes with PyArrow/curl on macOS
    # The reloader uses fork() which causes crashes when PyArrow initializes curl
    app.run(host='127.0.0.1', port=port, debug=debug, use_reloader=False)
