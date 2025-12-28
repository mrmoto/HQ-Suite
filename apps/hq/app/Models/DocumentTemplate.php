<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\SoftDeletes;

class DocumentTemplate extends Model
{
    use HasUuids, SoftDeletes;

    protected $fillable = [
        'document_type',
        'vendor_id',
        'vendor_name',
        'format_name',
        'template_name',
        'template_data',
        'field_mappings',
        'is_active',
    ];

    protected $casts = [
        'template_data' => 'array',
        'field_mappings' => 'array',
        'is_active' => 'boolean',
    ];

    /**
     * Get the vendor that owns this template.
     */
    public function vendor(): BelongsTo
    {
        return $this->belongsTo(Vendor::class);
    }

    /**
     * Scope to filter by document type.
     */
    public function scopeOfType($query, string $documentType)
    {
        return $query->where('document_type', $documentType);
    }

    /**
     * Scope to filter by vendor.
     */
    public function scopeForVendor($query, string $vendorName)
    {
        return $query->where('vendor_name', $vendorName);
    }

    /**
     * Scope to filter by format.
     */
    public function scopeOfFormat($query, string $formatName)
    {
        return $query->where('format_name', $formatName);
    }

    /**
     * Scope to get active templates only.
     */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }

    /**
     * Get unique identifier for template matching.
     */
    public function getUniqueIdentifier(): string
    {
        return sprintf(
            '%s:%s:%s:%s',
            $this->document_type,
            $this->vendor_name ?? 'unknown',
            $this->format_name ?? 'default',
            $this->id
        );
    }
}
