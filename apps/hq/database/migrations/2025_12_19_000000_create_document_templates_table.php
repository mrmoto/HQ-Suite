<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('document_templates', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('document_type'); // receipt, contract, bid, timecard, etc.
            $table->uuid('vendor_id')->nullable(); // Foreign key to vendors
            $table->string('vendor_name')->nullable(); // Denormalized for quick lookup
            $table->string('format_name')->nullable(); // Format identifier (e.g., "thermal_3x12", "full_size_8.5x11")
            $table->string('template_name'); // Human-readable name
            $table->json('template_data'); // Full template definition
            $table->json('field_mappings'); // Field coordinates and schema mappings
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->softDeletes();

            // Foreign keys
            $table->foreign('vendor_id')->references('id')->on('vendors')->onDelete('set null');

            // Indexes
            $table->index(['document_type', 'vendor_id', 'format_name']);
            $table->index(['vendor_name', 'format_name']);
            $table->index('document_type');
            $table->index('is_active');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('document_templates');
    }
};
