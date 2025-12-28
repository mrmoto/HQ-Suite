/**
 * Template Editing Review UI
 * Canvas-based UI for editing template field mappings.
 */

class TemplateEditingReview {
    constructor(canvasId, imageUrl, templateData) {
        this.canvasReview = new CanvasReview(canvasId, imageUrl);
        this.templateData = templateData || {};
        this.fieldMappings = this.templateData.field_mappings || [];
        
        // Load existing field boxes from template
        if (this.fieldMappings && this.fieldMappings.length > 0) {
            this.loadFieldBoxes();
        }
        
        this.initUI();
    }
    
    loadFieldBoxes() {
        const boxes = this.fieldMappings.map(mapping => ({
            x: mapping.x || 0,
            y: mapping.y || 0,
            width: mapping.width || 100,
            height: mapping.height || 30,
            label: mapping.field_name || 'Unnamed Field',
            field_name: mapping.field_name,
            field_type: mapping.field_type
        }));
        
        this.canvasReview.setFieldBoxes(boxes);
    }
    
    initUI() {
        this.createFieldEditor();
        this.createActionButtons();
    }
    
    createFieldEditor() {
        const container = document.createElement('div');
        container.className = 'field-editor';
        container.innerHTML = `
            <h3>Field Mappings</h3>
            <div class="field-box-list" id="field-box-list"></div>
            <button id="add-field" class="btn-primary">Add Field</button>
        `;
        document.body.appendChild(container);
        
        document.getElementById('add-field').addEventListener('click', () => {
            this.showAddFieldDialog();
        });
        
        this.updateFieldList();
    }
    
    updateFieldList() {
        const list = document.getElementById('field-box-list');
        list.innerHTML = '';
        
        this.canvasReview.getFieldBoxes().forEach((box, index) => {
            const item = document.createElement('div');
            item.className = 'field-box-item';
            if (box === this.canvasReview.selectedBox) {
                item.classList.add('selected');
            }
            
            item.innerHTML = `
                <div class="field-box-label">${box.label}</div>
                <div class="field-box-actions">
                    <button class="btn-small btn-edit" data-index="${index}">Edit</button>
                    <button class="btn-small btn-delete" data-index="${index}">Delete</button>
                </div>
            `;
            
            item.querySelector('.btn-edit').addEventListener('click', () => {
                this.editField(box, index);
            });
            
            item.querySelector('.btn-delete').addEventListener('click', () => {
                this.canvasReview.removeFieldBox(box);
                this.updateFieldList();
            });
            
            list.appendChild(item);
        });
    }
    
    showAddFieldDialog() {
        const fieldName = prompt('Enter field name:');
        if (fieldName) {
            // User will draw box on canvas, then we'll add it
            alert('Draw a box on the canvas to define the field area');
        }
    }
    
    editField(box, index) {
        const fieldName = prompt('Field name:', box.label);
        if (fieldName) {
            box.label = fieldName;
            this.canvasReview.draw();
            this.updateFieldList();
        }
    }
    
    createActionButtons() {
        const container = document.createElement('div');
        container.className = 'action-buttons';
        container.innerHTML = `
            <button id="save-template" class="btn-success">Save Template</button>
            <button id="cancel-edit" class="btn-primary">Cancel</button>
        `;
        document.body.appendChild(container);
        
        document.getElementById('save-template').addEventListener('click', () => {
            this.saveTemplate();
        });
        
        document.getElementById('cancel-edit').addEventListener('click', () => {
            if (confirm('Discard changes?')) {
                window.history.back();
            }
        });
    }
    
    saveTemplate() {
        const fieldMappings = this.canvasReview.getFieldBoxes().map(box => ({
            x: box.x,
            y: box.y,
            width: box.width,
            height: box.height,
            field_name: box.label,
            field_type: box.field_type || 'text'
        }));
        
        const data = {
            template_id: this.templateData.template_id,
            calling_app_id: this.templateData.calling_app_id,
            field_mappings: fieldMappings,
            template_data: {
                ...this.templateData.template_data,
                field_mappings: fieldMappings
            }
        };
        
        // Save to calling app via API
        fetch('/templates/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'updated') {
                alert('Template saved successfully');
                window.location.reload();
            } else {
                alert('Error saving template');
            }
        });
    }
}
