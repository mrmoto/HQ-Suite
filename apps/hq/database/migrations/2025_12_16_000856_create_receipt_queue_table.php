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
        Schema::create('receipt_queue', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('original_filename');
            $table->string('file_path'); // Path to uploaded image
            $table->string('source')->default('scanner'); // scanner, manual, api
            $table->string('status')->default('pending'); // pending, processing, completed, failed, reviewed
            $table->uuid('processed_receipt_id')->nullable(); // Link to purchase_receipts if processed
            $table->text('ocr_raw_data')->nullable(); // Raw OCR output
            $table->json('classification_result')->nullable(); // ML classification result
            $table->text('error_message')->nullable();
            $table->foreignId('reviewed_by_user_id')->nullable();
            $table->timestamp('received_at')->useCurrent();
            $table->timestamp('processed_at')->nullable();
            $table->timestamp('reviewed_at')->nullable();
            $table->timestamps();

            $table->foreign('processed_receipt_id')->references('id')->on('purchase_receipts')->onDelete('set null');
            $table->foreign('reviewed_by_user_id')->references('id')->on('users')->onDelete('set null');
            
            $table->index('status');
            $table->index('received_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('receipt_queue');
    }
};
