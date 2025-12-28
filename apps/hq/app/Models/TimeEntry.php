<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class TimeEntry extends Model
{
    use HasUuids;

    protected $fillable = [
        'project_id',
        'csi_code_id',
        'employee_name',
        'hours',
        'date',
        'notes',
    ];

    protected $casts = [
        'hours' => 'decimal:2',
        'date' => 'date',
    ];

    /**
     * Get the project for this time entry.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Get the CSI code for this time entry.
     */
    public function csiCode(): BelongsTo
    {
        return $this->belongsTo(CsiCode::class);
    }
}



