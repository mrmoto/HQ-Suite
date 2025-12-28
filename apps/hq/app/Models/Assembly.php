<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Assembly extends Model
{
    use HasUuids;

    protected $fillable = [
        'name',
        'description',
    ];

    /**
     * Get all items in this assembly.
     */
    public function items(): HasMany
    {
        return $this->hasMany(AssemblyItem::class);
    }
}



