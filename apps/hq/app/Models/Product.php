<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Product extends Model
{
    use HasUuids;

    protected $fillable = [
        'name',
        'description',
        'uom',
        'category',
    ];

    /**
     * Get all vendor products for this product.
     */
    public function vendorProducts(): HasMany
    {
        return $this->hasMany(VendorProduct::class);
    }
}



