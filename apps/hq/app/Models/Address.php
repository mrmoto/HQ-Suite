<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class Address extends Model
{
    use HasUuids;

    protected $fillable = [
        'addressable_type',
        'addressable_id',
        'type',
        'street',
        'city',
        'state',
        'zip',
        'country',
    ];

    /**
     * Get the parent addressable model (client, vendor, or project).
     */
    public function addressable(): MorphTo
    {
        return $this->morphTo();
    }
}



