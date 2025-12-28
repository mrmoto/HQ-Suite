<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class PurchaseReceipt extends Model
{
    use HasUuids, SoftDeletes;

    protected $fillable = [
        'project_id',
        'vendor_id',
        'vendor_address1',
        'vendor_address2',
        'vendor_city',
        'vendor_state',
        'vendor_zip',
        'sales_rep',
        'customer_number',
        'customer_name',
        'customer_address1',
        'customer_city',
        'customer_state',
        'customer_zip',
        'purchase_date',
        'purchased_by_user_id',
        'receipt_date',
        'receipt_number',
        'po_number',
        'subtotal',
        'amount_subtotal',
        'amount_taxable',
        'tax_rate',
        'amount_discount_percent',
        'balance_prior',
        'tax_amount',
        'total_amount',
        'amount_due_amt',
        'amount_balance_due',
        'payment_method',
        'payment_reference',
        'payment_terms',
        'receipt_image_path',
        'receipt_image_thumbnail',
        'notes',
        'status',
        'entered_by_user_id',
        'approved_by_user_id',
        'approved_at',
        'reimbursed_at',
    ];

    protected $casts = [
        'purchase_date' => 'datetime',
        'receipt_date' => 'date',
        'subtotal' => 'decimal:2',
        'amount_subtotal' => 'decimal:4',
        'amount_taxable' => 'decimal:4',
        'tax_rate' => 'decimal:4',
        'amount_discount_percent' => 'decimal:4',
        'balance_prior' => 'decimal:4',
        'tax_amount' => 'decimal:2',
        'total_amount' => 'decimal:2',
        'amount_due_amt' => 'decimal:4',
        'amount_balance_due' => 'decimal:4',
        'approved_at' => 'datetime',
        'reimbursed_at' => 'datetime',
    ];

    /**
     * Get the project this receipt belongs to.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Get the vendor for this receipt.
     */
    public function vendor(): BelongsTo
    {
        return $this->belongsTo(Vendor::class);
    }

    /**
     * Get the user who made the purchase.
     */
    public function purchasedBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'purchased_by_user_id');
    }

    /**
     * Get the user who entered this receipt.
     */
    public function enteredBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'entered_by_user_id');
    }

    /**
     * Get the user who approved this receipt.
     */
    public function approvedBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'approved_by_user_id');
    }

    /**
     * Get all receipt lines for this receipt.
     */
    public function lines(): HasMany
    {
        return $this->hasMany(PurchaseReceiptLine::class, 'receipt_id');
    }
}
