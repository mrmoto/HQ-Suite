<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PurchaseReceiptLine extends Model
{
    use HasUuids;

    protected $fillable = [
        'receipt_id',
        'line_number',
        'product_id',
        'vendor_sku',
        'description',
        'quantity',
        'uom',
        'unit_price',
        'line_total',
        'taxable_amount',
        'tax_rate_applied',
        'csi_code_id',
        'project_phase',
        'notes',
    ];

    protected $casts = [
        'quantity' => 'decimal:4',
        'unit_price' => 'decimal:4',
        'line_total' => 'decimal:2',
        'taxable_amount' => 'decimal:4',
        'tax_rate_applied' => 'decimal:2',
    ];

    /**
     * Get the receipt this line belongs to.
     */
    public function receipt(): BelongsTo
    {
        return $this->belongsTo(PurchaseReceipt::class, 'receipt_id');
    }

    /**
     * Get the product for this line.
     */
    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    /**
     * Get the CSI code for this line.
     */
    public function csiCode(): BelongsTo
    {
        return $this->belongsTo(CsiCode::class);
    }
}
