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
        Schema::create('contact_methods', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('contactable_type', 50);
            $table->uuid('contactable_id');
            $table->string('type', 50)->nullable(); // phone, email, url, etc.
            $table->string('value');
            $table->boolean('primary')->default(false);
            $table->timestamps();

            $table->index(['contactable_type', 'contactable_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('contact_methods');
    }
};



