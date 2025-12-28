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
        Schema::table('purchase_receipts', function (Blueprint $table) {
            // Vendor address fields
            $table->string('vendor_address1')->nullable()->after('vendor_id');
            $table->string('vendor_address2')->nullable()->after('vendor_address1');
            $table->string('vendor_city')->nullable()->after('vendor_address2');
            $table->string('vendor_state', 2)->nullable()->after('vendor_city');
            $table->string('vendor_zip', 10)->nullable()->after('vendor_state');
            
            // Sales rep
            $table->string('sales_rep')->nullable()->after('vendor_zip');
            
            // Customer information
            $table->string('customer_number')->nullable()->after('sales_rep');
            $table->string('customer_name')->nullable()->after('customer_number');
            $table->string('customer_address1')->nullable()->after('customer_name');
            $table->string('customer_city')->nullable()->after('customer_address1');
            $table->string('customer_state', 2)->nullable()->after('customer_city');
            $table->string('customer_zip', 10)->nullable()->after('customer_state');
            
            // Additional amount fields (with 4 decimal precision)
            $table->decimal('amount_subtotal', 15, 4)->nullable()->after('subtotal');
            $table->decimal('amount_taxable', 15, 4)->nullable()->after('amount_subtotal');
            $table->decimal('tax_rate', 5, 4)->nullable()->after('amount_taxable');
            $table->decimal('amount_discount_percent', 5, 4)->default(0)->after('tax_rate');
            $table->decimal('balance_prior', 15, 4)->default(0)->after('amount_discount_percent');
            $table->decimal('amount_due_amt', 15, 4)->nullable()->after('balance_prior');
            $table->decimal('amount_balance_due', 15, 4)->default(0)->after('amount_due_amt');
            
            // Payment terms
            $table->string('payment_terms')->nullable()->after('payment_reference');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('purchase_receipts', function (Blueprint $table) {
            $table->dropColumn([
                'vendor_address1',
                'vendor_address2',
                'vendor_city',
                'vendor_state',
                'vendor_zip',
                'sales_rep',
                'customer_number',
                'customer_name',
                'customer_address1',
                'customer_city',
                'customer_state',
                'customer_zip',
                'amount_subtotal',
                'amount_taxable',
                'tax_rate',
                'amount_discount_percent',
                'balance_prior',
                'amount_due_amt',
                'amount_balance_due',
                'payment_terms',
            ]);
        });
    }
};
