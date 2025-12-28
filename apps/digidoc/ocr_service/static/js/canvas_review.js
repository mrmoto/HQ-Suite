/**
 * Canvas Review Base Library
 * Common functionality for all Canvas-based review UIs.
 */

class CanvasReview {
    constructor(canvasId, imageUrl) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            throw new Error(`Canvas element not found: ${canvasId}`);
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.imageUrl = imageUrl;
        this.image = null;
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.fieldBoxes = [];
        this.selectedBox = null;
        
        this.init();
    }
    
    async init() {
        await this.loadImage();
        this.setupEventListeners();
        this.draw();
    }
    
    async loadImage() {
        return new Promise((resolve, reject) => {
            this.image = new Image();
            this.image.onload = () => {
                this.fitToCanvas();
                resolve();
            };
            this.image.onerror = reject;
            this.image.src = this.imageUrl;
        });
    }
    
    fitToCanvas() {
        const canvasAspect = this.canvas.width / this.canvas.height;
        const imageAspect = this.image.width / this.image.height;
        
        if (imageAspect > canvasAspect) {
            this.scale = this.canvas.width / this.image.width;
        } else {
            this.scale = this.canvas.height / this.image.height;
        }
        
        this.offsetX = (this.canvas.width - this.image.width * this.scale) / 2;
        this.offsetY = (this.canvas.height - this.image.height * this.scale) / 2;
    }
    
    setupEventListeners() {
        // Mouse events for drawing/editing boxes
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.onTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.onTouchMove(e));
        this.canvas.addEventListener('touchend', (e) => this.onTouchEnd(e));
    }
    
    getCanvasCoordinates(event) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }
    
    getImageCoordinates(canvasX, canvasY) {
        return {
            x: (canvasX - this.offsetX) / this.scale,
            y: (canvasY - this.offsetY) / this.scale
        };
    }
    
    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw image
        if (this.image) {
            this.ctx.drawImage(
                this.image,
                this.offsetX,
                this.offsetY,
                this.image.width * this.scale,
                this.image.height * this.scale
            );
        }
        
        // Draw field boxes
        this.drawFieldBoxes();
    }
    
    drawFieldBoxes() {
        this.fieldBoxes.forEach((box, index) => {
            const isSelected = box === this.selectedBox;
            
            // Convert image coordinates to canvas coordinates
            const x = this.offsetX + box.x * this.scale;
            const y = this.offsetY + box.y * this.scale;
            const w = box.width * this.scale;
            const h = box.height * this.scale;
            
            // Draw box
            this.ctx.strokeStyle = isSelected ? '#3b82f6' : '#10b981';
            this.ctx.lineWidth = isSelected ? 3 : 2;
            this.ctx.setLineDash(isSelected ? [] : [5, 5]);
            this.ctx.strokeRect(x, y, w, h);
            
            // Draw label
            if (box.label) {
                this.ctx.fillStyle = isSelected ? '#3b82f6' : '#10b981';
                this.ctx.fillRect(x, y - 20, Math.min(w, 150), 20);
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = '12px sans-serif';
                this.ctx.fillText(box.label, x + 5, y - 5);
            }
        });
    }
    
    addFieldBox(x, y, width, height, label) {
        const box = {
            x: x,
            y: y,
            width: width,
            height: height,
            label: label || `Field ${this.fieldBoxes.length + 1}`
        };
        this.fieldBoxes.push(box);
        this.draw();
        return box;
    }
    
    removeFieldBox(box) {
        const index = this.fieldBoxes.indexOf(box);
        if (index > -1) {
            this.fieldBoxes.splice(index, 1);
            if (this.selectedBox === box) {
                this.selectedBox = null;
            }
            this.draw();
        }
    }
    
    onMouseDown(event) {
        const coords = this.getCanvasCoordinates(event);
        const imgCoords = this.getImageCoordinates(coords.x, coords.y);
        
        // Check if clicking on existing box
        this.selectedBox = this.findBoxAt(imgCoords.x, imgCoords.y);
        
        if (!this.selectedBox) {
            // Start drawing new box
            this.isDragging = true;
            this.dragStartX = imgCoords.x;
            this.dragStartY = imgCoords.y;
        }
        
        this.draw();
    }
    
    onMouseMove(event) {
        if (this.isDragging && this.dragStartX !== null) {
            const coords = this.getCanvasCoordinates(event);
            const imgCoords = this.getImageCoordinates(coords.x, coords.y);
            
            // Draw preview box
            this.draw();
            this.ctx.strokeStyle = '#ef4444';
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([5, 5]);
            
            const x = this.offsetX + this.dragStartX * this.scale;
            const y = this.offsetY + this.dragStartY * this.scale;
            const w = (imgCoords.x - this.dragStartX) * this.scale;
            const h = (imgCoords.y - this.dragStartY) * this.scale;
            
            this.ctx.strokeRect(x, y, w, h);
        }
    }
    
    onMouseUp(event) {
        if (this.isDragging) {
            const coords = this.getCanvasCoordinates(event);
            const imgCoords = this.getImageCoordinates(coords.x, coords.y);
            
            const width = Math.abs(imgCoords.x - this.dragStartX);
            const height = Math.abs(imgCoords.y - this.dragStartY);
            
            if (width > 10 && height > 10) {
                const x = Math.min(this.dragStartX, imgCoords.x);
                const y = Math.min(this.dragStartY, imgCoords.y);
                this.addFieldBox(x, y, width, height);
            }
            
            this.isDragging = false;
            this.dragStartX = null;
            this.dragStartY = null;
        }
    }
    
    onTouchStart(event) {
        event.preventDefault();
        const touch = event.touches[0];
        const mouseEvent = new MouseEvent('mousedown', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.onMouseDown(mouseEvent);
    }
    
    onTouchMove(event) {
        event.preventDefault();
        const touch = event.touches[0];
        const mouseEvent = new MouseEvent('mousemove', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.onMouseMove(mouseEvent);
    }
    
    onTouchEnd(event) {
        event.preventDefault();
        const mouseEvent = new MouseEvent('mouseup', {});
        this.onMouseUp(mouseEvent);
    }
    
    findBoxAt(x, y) {
        return this.fieldBoxes.find(box => {
            return x >= box.x && x <= box.x + box.width &&
                   y >= box.y && y <= box.y + box.height;
        });
    }
    
    getFieldBoxes() {
        return this.fieldBoxes;
    }
    
    setFieldBoxes(boxes) {
        this.fieldBoxes = boxes;
        this.draw();
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CanvasReview;
}
