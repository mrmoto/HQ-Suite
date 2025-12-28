<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class EstimateLine extends Model
{
    use HasUuids;

    protected $fillable = [
        'estimate_id',
        'line_type',
        'line_id',
        'quantity',
        'unit_price',
        'markup',
    ];

    protected $casts = [
        'quantity' => 'decimal:4',
        'unit_price' => 'decimal:4',
        'markup' => 'decimal:2',
    ];

    /**
     * Get the estimate for this line.
     */
    public function estimate(): BelongsTo
    {
        return $this->belongsTo(Estimate::class);
    }
}



