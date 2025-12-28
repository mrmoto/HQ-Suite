<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Invoice extends Model
{
    use HasUuids;

    protected $fillable = [
        'project_id',
        'invoice_number',
        'amount',
        'due_date',
        'paid',
    ];

    protected $casts = [
        'amount' => 'decimal:2',
        'due_date' => 'date',
        'paid' => 'boolean',
    ];

    /**
     * Get the project for this invoice.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }
}



