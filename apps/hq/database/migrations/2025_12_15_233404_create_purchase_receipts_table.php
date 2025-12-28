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
        Schema::create('purchase_receipts', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->uuid('project_id')->nullable();
            $table->uuid('vendor_id')->nullable();
            $table->dateTime('purchase_date');
            $table->foreignId('purchased_by_user_id')->nullable()->constrained('users')->onDelete('set null'); // Lookup based on name in OCR
            $table->date('receipt_date')->nullable(); // Date on receipt, may differ from purchase_date
            $table->string('receipt_number')->nullable(); // Vendor's receipt/invoice number
            $table->string('po_number')->nullable(); // Purchase order number
            $table->decimal('subtotal', 12, 2)->default(0);
            $table->decimal('tax_amount', 12, 2)->default(0);
            $table->decimal('total_amount', 12, 2)->default(0);
            $table->string('payment_method')->nullable(); // cash, credit card, check, ACH, etc.
            $table->string('payment_reference')->nullable(); // check number, card last 4, transaction ID
            $table->string('receipt_image_path')->nullable(); // File upload path for scanned receipt
            $table->string('receipt_image_thumbnail')->nullable(); // For quick preview
            $table->text('notes')->nullable();
            $table->string('status')->default('draft'); // draft, submitted, approved, reimbursed, archived
            $table->foreignId('entered_by_user_id')->nullable()->constrained('users')->onDelete('set null');
            $table->foreignId('approved_by_user_id')->nullable()->constrained('users')->onDelete('set null');
            $table->timestamp('approved_at')->nullable();
            $table->timestamp('reimbursed_at')->nullable();
            $table->timestamps();
            $table->softDeletes();

            // Foreign keys (user foreign keys are defined inline above)
            $table->foreign('project_id')->references('id')->on('projects')->onDelete('set null');
            $table->foreign('vendor_id')->references('id')->on('vendors')->onDelete('set null');

            // Indexes
            $table->index('project_id');
            $table->index('vendor_id');
            $table->index('status');
            $table->index('purchase_date');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('purchase_receipts');
    }
};
