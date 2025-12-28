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
        Schema::create('assembly_items', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->uuid('assembly_id');
            $table->string('item_type', 50); // 'product' or 'assembly'
            $table->uuid('item_id');
            $table->decimal('quantity', 10, 4)->default(1);
            $table->json('conditional_rules')->nullable(); // e.g., {"if": "vanity_floating", "then_use": "assembly_123"}
            $table->timestamps();

            $table->foreign('assembly_id')->references('id')->on('assemblies')->onDelete('cascade');
            $table->index('assembly_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('assembly_items');
    }
};



