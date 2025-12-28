<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Brand extends Model
{
    use HasUuids;

    protected $fillable = [
        'name',
    ];

    /**
     * Get all vendor products for this brand.
     */
    public function vendorProducts(): HasMany
    {
        return $this->hasMany(VendorProduct::class);
    }
}



