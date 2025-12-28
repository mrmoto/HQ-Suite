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
        Schema::create('estimate_lines', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->uuid('estimate_id');
            $table->string('line_type', 50)->nullable(); // 'assembly' or 'product'
            $table->uuid('line_id')->nullable(); // references assembly or product
            $table->decimal('quantity', 10, 4)->nullable();
            $table->decimal('unit_price', 12, 4)->nullable();
            $table->decimal('markup', 5, 2)->nullable(); // percentage
            $table->timestamps();

            $table->foreign('estimate_id')->references('id')->on('estimates')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('estimate_lines');
    }
};



