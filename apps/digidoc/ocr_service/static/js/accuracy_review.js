/**
 * Accuracy Review UI
 * Canvas-based UI for reviewing extracted field accuracy.
 * Supports low, mid, and high confidence pages.
 */

class AccuracyReview {
    constructor(canvasId, imageUrl, extractedFields, confidenceLevel) {
        this.canvasReview = new CanvasReview(canvasId, imageUrl);
        this.extractedFields = extractedFields || {};
        this.confidenceLevel = confidenceLevel || 'mid';
        this.fieldConfidences = extractedFields._confidences || {};
        
        this.initUI();
    }
    
    initUI() {
        this.createFieldReviewPanel();
        this.createActionButtons();
    }
    
    createFieldReviewPanel() {
        const container = document.createElement('div');
        container.className = 'field-review-panel';
        container.innerHTML = `
            <h3>Extracted Fields</h3>
            <div id="fields-list" class="fields-list"></div>
        `;
        document.body.appendChild(container);
        
        this.updateFieldsList();
    }
    
    updateFieldsList() {
        const list = document.getElementById('fields-list');
        list.innerHTML = '';
        
        Object.entries(this.extractedFields).forEach(([fieldName, value]) => {
            if (fieldName === '_confidences') return;
            
            const confidence = this.fieldConfidences[fieldName] || 1.0;
            const confidenceClass = this.getConfidenceClass(confidence);
            
            const item = document.createElement('div');
            item.className = `field-item ${confidenceClass}`;
            item.innerHTML = `
                <div class="field-header">
                    <label>${fieldName}</label>
                    <span class="confidence-badge ${confidenceClass}">
                        ${(confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <input type="text" 
                       class="field-value" 
                       data-field="${fieldName}"
                       value="${this.escapeHtml(String(value))}"
                       ${this.shouldDisableField(confidence) ? '' : ''}>
            `;
            
            // Add change listener
            item.querySelector('.field-value').addEventListener('change', (e) => {
                this.extractedFields[e.target.dataset.field] = e.target.value;
            });
            
            list.appendChild(item);
        });
    }
    
    getConfidenceClass(confidence) {
        if (confidence >= 0.95) return 'high';
        if (confidence >= 0.80) return 'mid';
        return 'low';
    }
    
    shouldDisableField(confidence) {
        // For high confidence, fields are read-only (can be overridden)
        // For mid/low, fields are editable
        return this.confidenceLevel === 'high' && confidence >= 0.95;
    }
    
    createActionButtons() {
        const container = document.createElement('div');
        container.className = 'action-buttons';
        
        if (this.confidenceLevel === 'low') {
            container.innerHTML = `
                <button id="save-all" class="btn-success">Save All Fields</button>
                <button id="flag-issues" class="btn-primary">Flag Issues</button>
            `;
        } else if (this.confidenceLevel === 'mid') {
            container.innerHTML = `
                <button id="approve-high-confidence" class="btn-primary">Approve High Confidence</button>
                <button id="save-changes" class="btn-success">Save Changes</button>
            `;
        } else {
            container.innerHTML = `
                <button id="approve-all" class="btn-success">Approve All</button>
                <button id="flag-field" class="btn-primary">Flag Field</button>
            `;
        }
        
        document.body.appendChild(container);
        
        // Add event listeners based on confidence level
        this.setupActionButtons();
    }
    
    setupActionButtons() {
        if (this.confidenceLevel === 'low') {
            document.getElementById('save-all').addEventListener('click', () => {
                this.saveAllFields();
            });
        } else if (this.confidenceLevel === 'mid') {
            document.getElementById('approve-high-confidence').addEventListener('click', () => {
                this.approveHighConfidenceFields();
            });
            document.getElementById('save-changes').addEventListener('click', () => {
                this.saveChanges();
            });
        } else {
            document.getElementById('approve-all').addEventListener('click', () => {
                this.approveAll();
            });
        }
    }
    
    saveAllFields() {
        this.completeReview();
    }
    
    approveHighConfidenceFields() {
        // Auto-approve fields with >95% confidence
        Object.entries(this.fieldConfidences).forEach(([field, conf]) => {
            if (conf >= 0.95) {
                // Mark as approved
                console.log(`Auto-approved: ${field}`);
            }
        });
        this.saveChanges();
    }
    
    saveChanges() {
        this.completeReview();
    }
    
    approveAll() {
        this.completeReview();
    }
    
    completeReview() {
        // Remove confidence metadata
        const cleanFields = {...this.extractedFields};
        delete cleanFields._confidences;
        
        const data = {
            extracted_fields: cleanFields,
            approved: true
        };
        
        fetch('/api/review/complete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'completed') {
                alert('Review completed successfully');
                window.location.href = '/review/complete';
            }
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
