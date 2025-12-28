<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class ContactMethod extends Model
{
    use HasUuids;

    protected $fillable = [
        'contactable_type',
        'contactable_id',
        'type',
        'value',
        'primary',
    ];

    protected $casts = [
        'primary' => 'boolean',
    ];

    /**
     * Get the parent contactable model.
     */
    public function contactable(): MorphTo
    {
        return $this->morphTo();
    }
}



