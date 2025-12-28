<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

// Development preview route (only in local environment)
if (app()->environment('local')) {
    Route::get('/preview', function () {
        return view('preview');
    });
}

// API Routes for Receipt Upload (scanner/webhook endpoints)
// These routes don't require CSRF protection
Route::prefix('api/receipts')->group(function () {
    Route::post('/upload', [App\Http\Controllers\Api\ReceiptUploadController::class, 'upload'])
        ->name('api.receipts.upload')
        ->withoutMiddleware([\App\Http\Middleware\VerifyCsrfToken::class]);
    Route::get('/health', [App\Http\Controllers\Api\ReceiptUploadController::class, 'health'])
        ->name('api.receipts.health');
    Route::post('/debug', [App\Http\Controllers\Api\ReceiptUploadController::class, 'debug'])
        ->name('api.receipts.debug')
        ->withoutMiddleware([\App\Http\Middleware\VerifyCsrfToken::class]);
    Route::get('/debug', [App\Http\Controllers\Api\ReceiptUploadController::class, 'debug'])
        ->name('api.receipts.debug.get');
});

// API Routes for OCR Service (template sync and review)
Route::prefix('api/ocr')->group(function () {
    Route::get('/templates', [App\Http\Controllers\Api\OcrTemplateController::class, 'index'])
        ->name('api.ocr.templates');
    Route::post('/templates', [App\Http\Controllers\Api\OcrTemplateController::class, 'store'])
        ->name('api.ocr.templates.store')
        ->withoutMiddleware([\App\Http\Middleware\VerifyCsrfToken::class]);
    Route::get('/review/queue', [App\Http\Controllers\Api\OcrReviewController::class, 'index'])
        ->name('api.ocr.review.queue');
    Route::post('/review/complete', [App\Http\Controllers\Api\OcrReviewController::class, 'complete'])
        ->name('api.ocr.review.complete')
        ->withoutMiddleware([\App\Http\Middleware\VerifyCsrfToken::class]);
});
