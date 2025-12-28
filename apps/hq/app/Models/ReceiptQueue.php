<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ReceiptQueue extends Model
{
    use HasUuids;

    protected $table = 'receipt_queue';

    protected $fillable = [
        'original_filename',
        'file_path',
        'source',
        'status',
        'processed_receipt_id',
        'ocr_raw_data',
        'classification_result',
        'error_message',
        'reviewed_by_user_id',
        'received_at',
        'processed_at',
        'reviewed_at',
    ];

    protected $casts = [
        'classification_result' => 'array',
        'received_at' => 'datetime',
        'processed_at' => 'datetime',
        'reviewed_at' => 'datetime',
    ];

    /**
     * Get the processed receipt if one exists.
     */
    public function processedReceipt(): BelongsTo
    {
        return $this->belongsTo(PurchaseReceipt::class, 'processed_receipt_id');
    }

    /**
     * Get the user who reviewed this queue item.
     */
    public function reviewedBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reviewed_by_user_id');
    }
}



