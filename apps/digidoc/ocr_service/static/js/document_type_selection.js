/**
 * Document Type Selection Review UI
 * Canvas-based UI for selecting document type and template.
 */

class DocumentTypeSelectionReview {
    constructor(canvasId, imageUrl, templateMatches) {
        this.canvasReview = new CanvasReview(canvasId, imageUrl);
        this.templateMatches = templateMatches || [];
        this.selectedDocumentType = null;
        this.selectedTemplate = null;
        
        this.initUI();
    }
    
    initUI() {
        // Create UI elements
        this.createDocumentTypeSelector();
        this.createTemplateMatchesList();
        this.createActionButtons();
    }
    
    createDocumentTypeSelector() {
        const container = document.createElement('div');
        container.className = 'document-type-selector';
        container.innerHTML = `
            <h3>Select Document Type</h3>
            <select id="document-type-select">
                <option value="">-- Select Document Type --</option>
                <option value="receipt">Receipt</option>
                <option value="contract">Contract</option>
                <option value="bid">Bid/Quote</option>
                <option value="timecard">Timecard</option>
                <option value="change_order">Change Order</option>
            </select>
        `;
        
        document.body.appendChild(container);
        
        document.getElementById('document-type-select').addEventListener('change', (e) => {
            this.selectedDocumentType = e.target.value;
            this.onDocumentTypeChanged();
        });
    }
    
    createTemplateMatchesList() {
        const container = document.createElement('div');
        container.className = 'template-matches';
        container.innerHTML = '<h3>Template Matches</h3><ul id="template-matches-list"></ul>';
        document.body.appendChild(container);
        
        this.updateTemplateMatchesList();
    }
    
    updateTemplateMatchesList() {
        const list = document.getElementById('template-matches-list');
        list.innerHTML = '';
        
        if (this.templateMatches.length === 0) {
            list.innerHTML = '<li>No template matches found. Create new template.</li>';
            return;
        }
        
        this.templateMatches.forEach((match, index) => {
            const li = document.createElement('li');
            li.className = 'template-match';
            li.innerHTML = `
                <div class="match-info">
                    <strong>${match.document_type || 'Unknown'}</strong> - 
                    ${match.vendor || 'Unknown Vendor'} - 
                    ${match.format_name || 'Default Format'}
                </div>
                <div class="match-confidence">
                    Confidence: ${(match.confidence * 100).toFixed(1)}%
                </div>
                <button class="select-template" data-index="${index}">Select</button>
            `;
            
            li.querySelector('.select-template').addEventListener('click', () => {
                this.selectTemplate(match);
            });
            
            list.appendChild(li);
        });
    }
    
    createActionButtons() {
        const container = document.createElement('div');
        container.className = 'action-buttons';
        container.innerHTML = `
            <button id="create-new-template" class="btn-primary">Create New Template</button>
            <button id="continue-review" class="btn-success" disabled>Continue</button>
        `;
        document.body.appendChild(container);
        
        document.getElementById('create-new-template').addEventListener('click', () => {
            this.createNewTemplate();
        });
        
        document.getElementById('continue-review').addEventListener('click', () => {
            this.continueReview();
        });
    }
    
    onDocumentTypeChanged() {
        // Filter templates by document type
        if (this.selectedDocumentType) {
            const filtered = this.templateMatches.filter(
                m => m.document_type === this.selectedDocumentType
            );
            this.updateTemplateMatchesList(filtered);
        }
        
        this.updateContinueButton();
    }
    
    selectTemplate(template) {
        this.selectedTemplate = template;
        this.updateContinueButton();
    }
    
    updateContinueButton() {
        const btn = document.getElementById('continue-review');
        btn.disabled = !(this.selectedDocumentType && this.selectedTemplate);
    }
    
    createNewTemplate() {
        // Open template creation UI
        // This will allow user to draw field boxes and create template
        alert('Template creation UI will be implemented');
    }
    
    continueReview() {
        // Send selection to backend
        const data = {
            document_type: this.selectedDocumentType,
            template_id: this.selectedTemplate.template_id,
            field_boxes: this.canvasReview.getFieldBoxes()
        };
        
        // Call API to proceed with selected template
        fetch('/api/review/proceed', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                window.location.href = `/review/accuracy/${result.review_id}`;
            }
        });
    }
}
