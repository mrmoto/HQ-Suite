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
        // Note: app_registrations table is in DigiDoc database, not Laravel database
        // This migration is for reference/documentation only
        // Actual migration should be run in DigiDoc database using Python/SQLAlchemy
        
        // If app_registrations exists in Laravel database (for future multi-tenant support):
        if (Schema::hasTable('app_registrations')) {
            Schema::table('app_registrations', function (Blueprint $table) {
                $table->string('storage_base_path')->nullable()->after('api_key');
                $table->string('queue_directory_path')->nullable()->after('storage_base_path');
                
                $table->index('storage_base_path');
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        if (Schema::hasTable('app_registrations')) {
            Schema::table('app_registrations', function (Blueprint $table) {
                $table->dropIndex(['storage_base_path']);
                $table->dropColumn(['storage_base_path', 'queue_directory_path']);
            });
        }
    }
};
