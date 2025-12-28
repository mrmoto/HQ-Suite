<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\DocumentQueue;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class OcrReviewController extends Controller
{
    /**
     * Get review queue items for OCR app.
     * 
     * GET /api/ocr/review/queue
     */
    public function index(Request $request): JsonResponse
    {
        $status = $request->query('status', 'pending');
        $reviewType = $request->query('review_type');
        
        $query = DocumentQueue::withStatus($status);
        
        if ($reviewType) {
            $query->where('review_type', $reviewType);
        }
        
        $items = $query->orderBy('received_at', 'desc')->get();
        
        return response()->json([
            'items' => $items->map(function ($item) {
                return [
                    'id' => $item->id,
                    'original_filename' => $item->original_filename,
                    'file_path' => $item->file_path,
                    'document_type' => $item->document_type,
                    'review_type' => $item->review_type,
                    'template_matches' => $item->template_matches,
                    'confidence_level' => $item->confidence_level,
                    'requires_review' => $item->requires_review,
                    'classification_result' => $item->classification_result,
                    'received_at' => $item->received_at->toIso8601String(),
                ];
            })->toArray(),
        ]);
    }
    
    /**
     * Complete review and return results.
     * 
     * POST /api/ocr/review/complete
     */
    public function complete(Request $request): JsonResponse
    {
        $data = $request->validate([
            'queue_id' => 'required|uuid',
            'document_type' => 'required|string',
            'extracted_fields' => 'required|array',
            'template_id' => 'nullable|uuid',
            'review_metadata' => 'nullable|array',
        ]);
        
        $queueItem = DocumentQueue::find($data['queue_id']);
        
        if (!$queueItem) {
            return response()->json(['error' => 'Queue item not found'], 404);
        }
        
        // Update queue item
        $queueItem->update([
            'document_type' => $data['document_type'],
            'classification_result' => array_merge(
                $queueItem->classification_result ?? [],
                ['fields' => $data['extracted_fields']]
            ),
            'review_metadata' => $data['review_metadata'] ?? [],
            'status' => 'completed',
            'processed_at' => now(),
        ]);
        
        // Return success - calling app will handle database storage
        return response()->json([
            'status' => 'completed',
            'queue_id' => $queueItem->id,
            'message' => 'Review completed. Data ready for storage.',
        ]);
    }
}
