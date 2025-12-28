<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Estimate extends Model
{
    use HasUuids;

    protected $fillable = [
        'project_id',
        'version_number',
        'parent_id',
        'title',
        'status',
    ];

    protected $casts = [
        'version_number' => 'integer',
    ];

    /**
     * Get the project for this estimate.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Get the parent estimate (for versioning).
     */
    public function parent(): BelongsTo
    {
        return $this->belongsTo(Estimate::class, 'parent_id');
    }

    /**
     * Get all child estimates (versions).
     */
    public function versions(): HasMany
    {
        return $this->hasMany(Estimate::class, 'parent_id');
    }

    /**
     * Get all lines for this estimate.
     */
    public function lines(): HasMany
    {
        return $this->hasMany(EstimateLine::class);
    }

    /**
     * Get all change orders for this estimate.
     */
    public function changeOrders(): HasMany
    {
        return $this->hasMany(ChangeOrder::class);
    }
}



