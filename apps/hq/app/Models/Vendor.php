<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;

class Vendor extends Model
{
    use HasUuids;

    protected $fillable = [
        'name',
        'terms',
        'notes',
    ];

    /**
     * Get all addresses for the vendor.
     */
    public function addresses(): MorphMany
    {
        return $this->morphMany(Address::class, 'addressable');
    }

    /**
     * Get all contact methods for the vendor.
     */
    public function contactMethods(): MorphMany
    {
        return $this->morphMany(ContactMethod::class, 'contactable');
    }

    /**
     * Get all vendor products.
     */
    public function vendorProducts(): HasMany
    {
        return $this->hasMany(VendorProduct::class);
    }
}



