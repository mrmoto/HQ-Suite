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
        Schema::table('purchase_receipt_lines', function (Blueprint $table) {
            // Unit of measure
            $table->string('uom')->nullable()->after('quantity');
            
            // Taxable amount (with 4 decimal precision)
            $table->decimal('taxable_amount', 15, 4)->default(0)->after('line_total');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('purchase_receipt_lines', function (Blueprint $table) {
            $table->dropColumn([
                'uom',
                'taxable_amount',
            ]);
        });
    }
};
