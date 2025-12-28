<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class VendorProduct extends Model
{
    use HasUuids;

    protected $fillable = [
        'vendor_id',
        'product_id',
        'brand_id',
        'sku',
        'current_price',
        'last_purchased_date',
    ];

    protected $casts = [
        'current_price' => 'decimal:4',
        'last_purchased_date' => 'date',
    ];

    /**
     * Get the vendor for this vendor product.
     */
    public function vendor(): BelongsTo
    {
        return $this->belongsTo(Vendor::class);
    }

    /**
     * Get the product for this vendor product.
     */
    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    /**
     * Get the brand for this vendor product.
     */
    public function brand(): BelongsTo
    {
        return $this->belongsTo(Brand::class);
    }
}



