<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ReceiptQueue;
use App\Services\SlackNotificationService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class ReceiptUploadController extends Controller
{
    protected SlackNotificationService $slackService;

    public function __construct(SlackNotificationService $slackService)
    {
        $this->slackService = $slackService;
    }

    /**
     * Receive scanned receipt image from scanner or external source.
     * 
     * This endpoint accepts file uploads and stores them in the receipt queue.
     * Supports multiple scanner formats:
     * - multipart/form-data with 'file' parameter
     * - multipart/form-data with 'image' parameter
     * - multipart/form-data with 'document' parameter
     * - Raw POST data (for scanners that send binary)
     */
    public function upload(Request $request)
    {
        try {
            // Try to get file from various common parameter names
            $file = $request->file('file') 
                ?? $request->file('image') 
                ?? $request->file('document')
                ?? $request->file('scan');

            // If no file found in multipart, check for raw POST data
            if (!$file && $request->hasContent()) {
                $content = $request->getContent();
                if (!empty($content)) {
                    // Create temporary file from raw content
                    $tempFile = tempnam(sys_get_temp_dir(), 'receipt_');
                    file_put_contents($tempFile, $content);
                    
                    // Determine MIME type
                    $mimeType = mime_content_type($tempFile);
                    $extension = $this->getExtensionFromMimeType($mimeType);
                    
                    if (!$extension) {
                        // Try to detect from content
                        $extension = $this->detectFileExtension($content);
                    }
                    
                    $file = new \Illuminate\Http\UploadedFile(
                        $tempFile,
                        'scanned_receipt.' . $extension,
                        $mimeType,
                        null,
                        true
                    );
                }
            }

            if (!$file) {
                Log::warning('Receipt upload failed: No file received', [
                    'request_keys' => array_keys($request->all()),
                    'has_files' => $request->hasFile('file'),
                    'content_type' => $request->header('Content-Type'),
                    'content_length' => $request->header('Content-Length'),
                ]);

                return response()->json([
                    'success' => false,
                    'message' => 'No file received. Please send file as multipart/form-data with parameter name: file, image, document, or scan',
                    'received_parameters' => array_keys($request->all()),
                    'content_type' => $request->header('Content-Type'),
                ], 400);
            }

            // Validate file
            $validated = $request->validate([
                'file' => ['sometimes', 'image', 'mimes:jpeg,jpg,png,pdf', 'max:10240'],
                'image' => ['sometimes', 'image', 'mimes:jpeg,jpg,png,pdf', 'max:10240'],
                'document' => ['sometimes', 'file', 'mimes:jpeg,jpg,png,pdf', 'max:10240'],
            ]);

            // Get original filename for reference
            $originalFilename = $file->getClientOriginalName() ?: 'scanned_receipt';
            $extension = $file->getClientOriginalExtension() ?: 'jpg';
            
            // Generate filename: OCR_image-[timestamp-with-microseconds]-[host-name].[extension]
            $hostname = gethostname() ?: 'unknown-host';
            $timestamp = now()->format('Y-m-d_His') . '_' . str_pad((int)(microtime(true) * 1000000) % 1000000, 6, '0', STR_PAD_LEFT);
            $filename = "OCR_image-{$timestamp}-{$hostname}.{$extension}";
            
            // Store file in documents queue directory (generic, document-type aware)
            $filePath = $file->storeAs('queue', $filename, 'documents');

            // Create queue entry
            $queueItem = ReceiptQueue::create([
                'original_filename' => $originalFilename, // Keep original for reference
                'file_path' => $filePath, // This now uses OCR_image- format
                'source' => $request->input('source', 'scanner'),
                'status' => 'pending',
                'received_at' => now(),
            ]);

            // Generate review URL with embedded queue ID and permission check
            $reviewUrl = url('/admin/receipt-queue-review?queue=' . $queueItem->id);

            // Send Slack notification
            $this->slackService->notifyNewReceipt(
                $queueItem->id,
                $originalFilename,
                $reviewUrl
            );

            Log::info('Receipt uploaded successfully', [
                'queue_id' => $queueItem->id,
                'filename' => $originalFilename,
                'file_size' => $file->getSize(),
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Receipt uploaded successfully',
                'queue_id' => $queueItem->id,
                'status' => 'pending',
                'filename' => $originalFilename,
            ], 201);

        } catch (\Illuminate\Validation\ValidationException $e) {
            Log::error('Receipt upload validation failed', [
                'errors' => $e->errors(),
                'request_data' => $request->except(['file', 'image', 'document']),
            ]);

            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors' => $e->errors(),
            ], 422);

        } catch (\Exception $e) {
            Log::error('Receipt upload failed', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString(),
                'request_method' => $request->method(),
                'content_type' => $request->header('Content-Type'),
            ]);

            return response()->json([
                'success' => false,
                'message' => 'Failed to upload receipt: ' . $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Get file extension from MIME type.
     */
    protected function getExtensionFromMimeType(string $mimeType): ?string
    {
        $mimeMap = [
            'image/jpeg' => 'jpg',
            'image/jpg' => 'jpg',
            'image/png' => 'png',
            'application/pdf' => 'pdf',
            'image/gif' => 'gif',
        ];

        return $mimeMap[$mimeType] ?? null;
    }

    /**
     * Detect file extension from file content (magic bytes).
     */
    protected function detectFileExtension(string $content): string
    {
        // Check magic bytes
        $header = substr($content, 0, 4);
        
        if (substr($content, 0, 2) === "\xFF\xD8") {
            return 'jpg';
        }
        if (substr($content, 0, 8) === "\x89PNG\r\n\x1a\n") {
            return 'png';
        }
        if (substr($content, 0, 4) === "%PDF") {
            return 'pdf';
        }
        
        return 'jpg'; // Default
    }

    /**
     * Health check endpoint for the scanner to verify connectivity.
     */
    public function health()
    {
        return response()->json([
            'status' => 'ok',
            'service' => 'receipt-upload',
            'timestamp' => now()->toIso8601String(),
            'endpoint' => url('/api/receipts/upload'),
            'supported_formats' => ['jpeg', 'jpg', 'png', 'pdf'],
            'max_size_mb' => 10,
        ]);
    }

    /**
     * Debug endpoint to test scanner connectivity and see what's being received.
     */
    public function debug(Request $request)
    {
        return response()->json([
            'method' => $request->method(),
            'content_type' => $request->header('Content-Type'),
            'content_length' => $request->header('Content-Length'),
            'has_file' => $request->hasFile('file'),
            'has_image' => $request->hasFile('image'),
            'has_document' => $request->hasFile('document'),
            'request_keys' => array_keys($request->all()),
            'file_keys' => array_keys($request->allFiles()),
            'post_data' => $request->except(['file', 'image', 'document']),
            'has_content' => $request->hasContent(),
            'content_size' => strlen($request->getContent()),
        ], 200);
    }
}
