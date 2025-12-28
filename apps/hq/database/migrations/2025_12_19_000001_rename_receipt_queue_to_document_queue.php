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
        // Rename table
        Schema::rename('receipt_queue', 'document_queue');
        
        // Add new generic document fields
        Schema::table('document_queue', function (Blueprint $table) {
            $table->string('document_type')->nullable()->after('source'); // receipt, contract, bid, etc.
            $table->string('review_type')->nullable()->after('status'); // document_type_selection, template_selection, template_editing, accuracy_review
            $table->json('template_matches')->nullable()->after('classification_result'); // Top 5 template matches with confidence
            $table->string('confidence_level')->nullable()->after('template_matches'); // low, mid, high
            $table->json('field_confidences')->nullable()->after('confidence_level'); // Per-field confidence scores
            $table->boolean('requires_review')->default(false)->after('field_confidences');
            $table->json('review_metadata')->nullable()->after('requires_review'); // Review-specific data
            
            // Add indexes
            $table->index('document_type');
            $table->index('review_type');
            $table->index('requires_review');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('document_queue', function (Blueprint $table) {
            $table->dropIndex(['document_type']);
            $table->dropIndex(['review_type']);
            $table->dropIndex(['requires_review']);
            
            $table->dropColumn([
                'document_type',
                'review_type',
                'template_matches',
                'confidence_level',
                'field_confidences',
                'requires_review',
                'review_metadata',
            ]);
        });
        
        Schema::rename('document_queue', 'receipt_queue');
    }
};
