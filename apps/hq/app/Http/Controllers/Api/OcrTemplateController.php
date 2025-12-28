<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\DocumentTemplate;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class OcrTemplateController extends Controller
{
    /**
     * Provide templates to OCR app.
     * 
     * GET /api/ocr/templates
     * Query parameters:
     * - calling_app_id: Required
     * - document_type: Optional filter
     * - vendor: Optional filter
     */
    public function index(Request $request): JsonResponse
    {
        $callingAppId = $request->query('calling_app_id');
        $documentType = $request->query('document_type');
        $vendor = $request->query('vendor');
        
        if (!$callingAppId) {
            return response()->json(['error' => 'calling_app_id is required'], 400);
        }
        
        // For now, only support construction_suite
        if ($callingAppId !== 'construction_suite') {
            return response()->json(['error' => 'Unknown calling app'], 400);
        }
        
        // Build query
        $query = DocumentTemplate::active();
        
        if ($documentType) {
            $query->ofType($documentType);
        }
        
        if ($vendor) {
            $query->forVendor($vendor);
        }
        
        $templates = $query->get();
        
        // Format for OCR app
        $formatted = $templates->map(function ($template) {
            return [
                'template_id' => $template->id,
                'document_type' => $template->document_type,
                'vendor' => $template->vendor_name,
                'format_name' => $template->format_name,
                'template_data' => $template->template_data,
                'field_mappings' => $template->field_mappings,
                'updated_at' => $template->updated_at->toIso8601String(),
            ];
        });
        
        return response()->json([
            'templates' => $formatted->toArray(),
        ]);
    }
    
    /**
     * Receive template updates from OCR app.
     * 
     * POST /api/ocr/templates
     */
    public function store(Request $request): JsonResponse
    {
        // This endpoint receives template updates from OCR app
        // (e.g., when user edits template in Canvas UI)
        
        $data = $request->validate([
            'calling_app_id' => 'required|string',
            'template_id' => 'required|uuid',
            'template_data' => 'required|array',
            'field_mappings' => 'nullable|array',
        ]);
        
        $template = DocumentTemplate::find($data['template_id']);
        
        if (!$template) {
            return response()->json(['error' => 'Template not found'], 404);
        }
        
        // Update template
        $template->update([
            'template_data' => $data['template_data'],
            'field_mappings' => $data['field_mappings'] ?? $template->field_mappings,
        ]);
        
        return response()->json([
            'status' => 'updated',
            'template_id' => $template->id,
        ]);
    }
}
