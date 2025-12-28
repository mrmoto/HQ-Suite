<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ChangeOrder extends Model
{
    use HasUuids;

    protected $fillable = [
        'estimate_id',
        'title',
        'description',
        'amount_change',
        'approved',
    ];

    protected $casts = [
        'amount_change' => 'decimal:2',
        'approved' => 'boolean',
    ];

    /**
     * Get the estimate for this change order.
     */
    public function estimate(): BelongsTo
    {
        return $this->belongsTo(Estimate::class);
    }
}



