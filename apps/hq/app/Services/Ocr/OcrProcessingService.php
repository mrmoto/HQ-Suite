<?php

namespace App\Services\Ocr;

use App\Models\ReceiptQueue;
use App\Models\PurchaseReceipt;
use App\Models\PurchaseReceiptLine;
use App\Models\Vendor;
use App\Services\Ocr\OcrFieldValidator;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class OcrProcessingService
{
    /**
     * Process a receipt from the queue using OCR.
     * 
     * Implements confidence-based workflow:
     * - High confidence (≥85%): Auto-create PurchaseReceipt
     * - Medium/Low confidence: Store in queue for review
     */
    public function processReceipt(ReceiptQueue $queueItem): bool
    {
        try {
            // Update status to processing
            $queueItem->update([
                'status' => 'processing',
                'processed_at' => now(),
            ]);

            // Get the file path (use documents disk - generic, document-type aware)
            $filePath = Storage::disk('documents')->path($queueItem->file_path);

            if (!file_exists($filePath)) {
                throw new \Exception("Receipt file not found: {$filePath}");
            }

            // Call Python OCR service
            $ocrResult = $this->callPythonOcrService($filePath);

            if (empty($ocrResult)) {
                throw new \Exception("OCR service returned empty result");
            }

            // Extract confidence and fields
            $confidence = $ocrResult['confidence'] ?? 0.0;
            $confidenceLevel = $ocrResult['confidence_level'] ?? 'low';
            $fields = $ocrResult['fields'] ?? [];
            $vendorName = $ocrResult['vendor'] ?? null;

            // Store OCR raw data
            $queueItem->update([
                'ocr_raw_data' => json_encode([
                    'text' => $ocrResult['ocr_text'] ?? '',
                    'data' => $ocrResult['ocr_data'] ?? [],
                ]),
                'classification_result' => [
                    'vendor' => $vendorName,
                    'format_detected' => $ocrResult['format_detected'] ?? null,
                    'confidence' => $confidence,
                    'confidence_level' => $confidenceLevel,
                    'fields' => $fields,
                ],
            ]);

            Log::info('OCR processing completed', [
                'queue_id' => $queueItem->id,
                'confidence' => $confidence,
                'confidence_level' => $confidenceLevel,
            ]);

            // Validate fields using format-specific validation
            $formatId = $ocrResult['format_detected'] ?? null;
            $shouldRouteToReview = false;
            
            if ($formatId) {
                $validator = new OcrFieldValidator();
                $validationResult = $validator->validate($fields, $formatId);
                $shouldRouteToReview = $validator->shouldRouteToReview($validationResult);
                
                // Store validation results
                $queueItem->update([
                    'validation_result' => $validationResult,
                ]);
                
                Log::info('Field validation completed', [
                    'queue_id' => $queueItem->id,
                    'format' => $formatId,
                    'is_valid' => $validationResult['is_valid'],
                    'missing_fields' => $validationResult['missing_fields'],
                    'confidence_issues' => $validationResult['confidence_issues'],
                ]);
            }

            // Confidence-based workflow with validation
            if ($confidence >= 0.85 && !$shouldRouteToReview) {
                // High confidence and validation passed: Auto-create PurchaseReceipt
                return $this->autoCreateReceipt($queueItem, $fields, $vendorName);
            } else {
                // Medium/Low confidence or validation failed: Flag for review
                // Set status to 'pending' so it appears in review queue
                $queueItem->update([
                    'status' => 'pending',
                ]);

                $reason = $confidence < 0.85 
                    ? 'low confidence' 
                    : 'validation failed';
                
                Log::info('Receipt flagged for review', [
                    'queue_id' => $queueItem->id,
                    'confidence' => $confidence,
                    'reason' => $reason,
                ]);

                return true;
            }

        } catch (\Exception $e) {
            Log::error('OCR processing failed', [
                'queue_id' => $queueItem->id,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString(),
            ]);

            $queueItem->update([
                'status' => 'failed',
                'error_message' => $e->getMessage(),
            ]);

            return false;
        }
    }

    /**
     * Call Python OCR service via HTTP API.
     */
    protected function callPythonOcrService(string $filePath): array
    {
        $serviceUrl = config('services.ocr.service_url', 'http://127.0.0.1:5000');
        $apiPrefix = config('services.ocr.api_prefix', '/digidoc');
        $timeout = config('services.ocr.timeout', 60);

        try {
            // Use /digidoc/ API prefix for all DigiDoc service calls
            $response = Http::timeout($timeout)
                ->attach('file', file_get_contents($filePath), basename($filePath))
                ->post("{$serviceUrl}{$apiPrefix}/process");

            if ($response->failed()) {
                throw new \Exception("OCR service error: " . $response->body());
            }

            $result = $response->json();

            if (isset($result['error'])) {
                throw new \Exception("OCR service error: " . $result['error']);
            }

            return $result;

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            throw new \Exception("Could not connect to OCR service at {$serviceUrl}. Is the service running?");
        } catch (\Exception $e) {
            throw new \Exception("OCR service call failed: " . $e->getMessage());
        }
    }

    /**
     * Auto-create PurchaseReceipt from high-confidence extraction.
     */
    protected function autoCreateReceipt(
        ReceiptQueue $queueItem,
        array $fields,
        ?string $vendorName
    ): bool {
        try {
            DB::beginTransaction();

            // Find or create vendor
            $vendor = null;
            if ($vendorName) {
                $vendor = Vendor::where('name', $vendorName)->first();
                if (!$vendor) {
                    // Create vendor if it doesn't exist
                    $vendor = Vendor::create([
                        'name' => $vendorName,
                    ]);
                    Log::info('Created new vendor from OCR', [
                        'vendor_id' => $vendor->id,
                        'vendor_name' => $vendorName,
                    ]);
                }
            }

            // Parse receipt date
            $receiptDate = null;
            if (isset($fields['receipt_date'])) {
                try {
                    $receiptDate = Carbon::parse($fields['receipt_date'])->format('Y-m-d');
                } catch (\Exception $e) {
                    Log::warning('Could not parse receipt date', [
                        'date_string' => $fields['receipt_date'],
                        'error' => $e->getMessage(),
                    ]);
                }
            }

            // Create PurchaseReceipt with all fields
            $receipt = PurchaseReceipt::create([
                'vendor_id' => $vendor?->id,
                'vendor_address1' => $fields['vendor_address1'] ?? null,
                'vendor_address2' => $fields['vendor_address2'] ?? null,
                'vendor_city' => $fields['vendor_city'] ?? null,
                'vendor_state' => $fields['vendor_state'] ?? null,
                'vendor_zip' => $fields['vendor_zip'] ?? null,
                'sales_rep' => $fields['sales_rep'] ?? null,
                'customer_number' => $fields['customer_number'] ?? null,
                'customer_name' => $fields['customer_name'] ?? null,
                'customer_address1' => $fields['customer_address1'] ?? null,
                'customer_city' => $fields['customer_city'] ?? null,
                'customer_state' => $fields['customer_state'] ?? null,
                'customer_zip' => $fields['customer_zip'] ?? null,
                'purchase_date' => $receiptDate ? Carbon::parse($receiptDate) : now(),
                'receipt_date' => $receiptDate,
                'receipt_number' => $fields['receipt_number'] ?? null,
                'subtotal' => $this->parseDecimal($fields['subtotal'] ?? 0),
                'amount_subtotal' => $this->parseDecimal($fields['amount_subtotal'] ?? $fields['subtotal'] ?? 0, 4),
                'amount_taxable' => $this->parseDecimal($fields['amount_taxable'] ?? 0, 4),
                'tax_rate' => $this->parseDecimal($fields['tax_rate'] ?? null, 4),
                'amount_discount_percent' => $this->parseDecimal($fields['amount_discount_percent'] ?? 0, 4),
                'balance_prior' => $this->parseDecimal($fields['balance_prior'] ?? 0, 4),
                'tax_amount' => $this->parseDecimal($fields['tax_amount'] ?? 0),
                'total_amount' => $this->parseDecimal($fields['total_amount'] ?? 0),
                'amount_due_amt' => $this->parseDecimal($fields['amount_due_amt'] ?? $fields['total_amount'] ?? 0, 4),
                'amount_balance_due' => $this->parseDecimal($fields['amount_balance_due'] ?? 0, 4),
                'payment_method' => $fields['payment_method'] ?? null,
                'payment_terms' => $fields['payment_terms'] ?? null,
                'receipt_image_path' => $queueItem->file_path,
                'status' => 'draft',
                'entered_by_user_id' => auth()->id(), // Current user if authenticated
            ]);

            // Create receipt lines with all fields
            if (isset($fields['line_items']) && is_array($fields['line_items'])) {
                $lineNumber = 1;
                foreach ($fields['line_items'] as $item) {
                    PurchaseReceiptLine::create([
                        'receipt_id' => $receipt->id,
                        'line_number' => $item['line_number'] ?? $lineNumber++,
                        'vendor_sku' => $item['vendor_sku'] ?? null,
                        'description' => $item['description'] ?? null,
                        'quantity' => $this->parseDecimal($item['quantity'] ?? 1, 4),
                        'uom' => $item['uom'] ?? null,
                        'unit_price' => $this->parseDecimal($item['unit_price'] ?? 0, 4),
                        'line_total' => $this->parseDecimal($item['line_total'] ?? 0),
                        'taxable_amount' => $this->parseDecimal($item['taxable_amount'] ?? $item['line_total'] ?? 0, 4),
                        'tax_rate_applied' => $this->parseDecimal($item['tax_rate_applied'] ?? null),
                        'csi_code_id' => $item['csi_code_id'] ?? null,
                        'notes' => $item['notes'] ?? null,
                    ]);
                }
            }

            // Update queue item
            $queueItem->update([
                'status' => 'completed',
                'processed_receipt_id' => $receipt->id,
            ]);

            DB::commit();

            Log::info('Auto-created PurchaseReceipt from high-confidence OCR', [
                'queue_id' => $queueItem->id,
                'receipt_id' => $receipt->id,
            ]);

            return true;

        } catch (\Exception $e) {
            DB::rollBack();
            
            Log::error('Failed to auto-create PurchaseReceipt', [
                'queue_id' => $queueItem->id,
                'error' => $e->getMessage(),
            ]);

            // Update queue to pending status so user can manually review and create
            $queueItem->update([
                'status' => 'pending',
            ]);

            throw $e;
        }
    }

    /**
     * Parse decimal value from various formats.
     * 
     * @param mixed $value Value to parse
     * @param int $decimals Number of decimal places (default: 2)
     * @return float Parsed decimal value
     */
    protected function parseDecimal($value, int $decimals = 2): float
    {
        if ($value === null) {
            return 0.0;
        }
        
        if (is_numeric($value)) {
            return round((float) $value, $decimals);
        }

        if (is_string($value)) {
            // Remove currency symbols and commas
            $cleaned = preg_replace('/[^0-9.]/', '', $value);
            return round((float) $cleaned, $decimals);
        }

        return 0.0;
    }

    /**
     * Classify document type using ML (to be implemented).
     */
    public function classifyDocument(ReceiptQueue $queueItem): string
    {
        // For Phase A.1, we assume all documents are receipts
        // Future: Call ML classification service
        return 'receipt';
    }

    /**
     * Extract receipt data from OCR result (legacy method for compatibility).
     */
    public function extractReceiptData(array $ocrResult): array
    {
        // This method is kept for compatibility but extraction is now done in Python
        return $ocrResult['fields'] ?? [];
    }
}



