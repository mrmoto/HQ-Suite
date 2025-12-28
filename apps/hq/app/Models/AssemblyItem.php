<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class AssemblyItem extends Model
{
    use HasUuids;

    protected $fillable = [
        'assembly_id',
        'item_type',
        'item_id',
        'quantity',
        'conditional_rules',
    ];

    protected $casts = [
        'quantity' => 'decimal:4',
        'conditional_rules' => 'array',
    ];

    /**
     * Get the assembly this item belongs to.
     */
    public function assembly(): BelongsTo
    {
        return $this->belongsTo(Assembly::class);
    }

    /**
     * Get the parent item model (product or assembly).
     */
    public function item(): MorphTo
    {
        return $this->morphTo();
    }
}



