<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class CsiCode extends Model
{
    use HasUuids;

    protected $fillable = [
        'code',
        'description',
        'category',
    ];

    /**
     * Get all time entries for this CSI code.
     */
    public function timeEntries(): HasMany
    {
        return $this->hasMany(TimeEntry::class);
    }
}



