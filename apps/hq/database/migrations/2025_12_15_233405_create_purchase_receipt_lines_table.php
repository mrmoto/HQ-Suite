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
        Schema::create('purchase_receipt_lines', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->uuid('receipt_id');
            $table->integer('line_number'); // Order on receipt
            $table->uuid('product_id')->nullable(); // Foreign key to products table
            $table->string('vendor_sku')->nullable(); // Vendor-specific SKU
            $table->text('description')->nullable(); // Item description from receipt
            $table->decimal('quantity', 10, 4)->default(1);
            $table->decimal('unit_price', 12, 4)->default(0); // Price per unit before tax
            $table->decimal('line_total', 12, 2)->default(0); // quantity * unit_price
            $table->decimal('tax_rate_applied', 5, 2)->nullable(); // Percentage or amount for this line
            $table->uuid('csi_code_id')->nullable(); // Foreign key to csi_codes
            $table->string('project_phase')->nullable(); // Custom tag for internal tracking
            $table->text('notes')->nullable(); // Line-specific notes
            $table->timestamps();

            // Foreign keys
            $table->foreign('receipt_id')->references('id')->on('purchase_receipts')->onDelete('cascade');
            $table->foreign('product_id')->references('id')->on('products')->onDelete('set null');
            $table->foreign('csi_code_id')->references('id')->on('csi_codes')->onDelete('set null');

            // Indexes
            $table->index('receipt_id');
            $table->index('product_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('purchase_receipt_lines');
    }
};
