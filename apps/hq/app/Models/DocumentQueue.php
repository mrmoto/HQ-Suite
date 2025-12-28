<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Storage;

class DocumentQueue extends Model
{
    use HasUuids;

    protected $table = 'document_queue';

    protected $fillable = [
        'original_filename',
        'file_path',
        'source',
        'status',
        'document_type', // receipt, contract, bid, timecard, etc.
        'review_type', // document_type_selection, template_selection, template_editing, accuracy_review
        'processed_receipt_id', // Keep for backward compatibility, but will be generic
        'ocr_raw_data',
        'classification_result',
        'template_matches', // Top 5 template matches with confidence
        'confidence_level', // low, mid, high
        'field_confidences', // Per-field confidence scores
        'requires_review',
        'review_metadata', // Review-specific data
        'error_message',
        'reviewed_by_user_id',
        'received_at',
        'processed_at',
        'reviewed_at',
    ];

    protected $casts = [
        'classification_result' => 'array',
        'template_matches' => 'array',
        'field_confidences' => 'array',
        'review_metadata' => 'array',
        'requires_review' => 'boolean',
        'received_at' => 'datetime',
        'processed_at' => 'datetime',
        'reviewed_at' => 'datetime',
    ];

    /**
     * Get the processed document record (generic - could be receipt, contract, etc.).
     * For MVP, this links to PurchaseReceipt, but architecture supports any document type.
     */
    public function processedDocument(): BelongsTo
    {
        // For now, link to PurchaseReceipt (MVP)
        // Future: Route to appropriate model based on document_type
        return $this->belongsTo(PurchaseReceipt::class, 'processed_receipt_id');
    }

    /**
     * Get the user who reviewed this queue item.
     */
    public function reviewedBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reviewed_by_user_id');
    }

    /**
     * Scope to filter by document type.
     */
    public function scopeOfType($query, string $documentType)
    {
        return $query->where('document_type', $documentType);
    }

    /**
     * Scope to filter by review type.
     */
    public function scopeRequiringReview($query)
    {
        return $query->where('requires_review', true);
    }

    /**
     * Scope to filter by status.
     */
    public function scopeWithStatus($query, string $status)
    {
        return $query->where('status', $status);
    }
    
    /**
     * Resolve full file path using tenant storage configuration.
     * 
     * @return string Full file path
     */
    public function getFullFilePath(): string
    {
        // For now, use documents disk
        // Future: Resolve using tenant's storage_base_path from app_registrations
        return Storage::disk('documents')->path($this->file_path);
    }
    
    /**
     * Get file URL for display.
     * 
     * @return string File URL
     */
    public function getFileUrl(): string
    {
        // For now, use documents disk
        // Future: Resolve using tenant's storage configuration
        return Storage::disk('documents')->url($this->file_path);
    }
}
