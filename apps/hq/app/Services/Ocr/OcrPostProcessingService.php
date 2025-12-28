<?php

namespace App\Services\Ocr;

use App\Models\DocumentQueue;
use App\Models\PurchaseReceipt;
use App\Models\PurchaseReceiptLine;
use App\Models\Vendor;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Carbon\Carbon;
use Intervention\Image\Facades\Image;

class OcrPostProcessingService
{
    /**
     * Process completed review and store document data.
     * Document-type aware routing to appropriate storage.
     */
    public function processCompletedReview(
        DocumentQueue $queueItem,
        array $extractedFields,
        string $documentType
    ): bool {
        try {
            DB::beginTransaction();
            
            // Route to appropriate handler based on document type
            switch ($documentType) {
                case 'receipt':
                    $result = $this->storeReceipt($queueItem, $extractedFields);
                    break;
                case 'contract':
                    // Future: $this->storeContract($queueItem, $extractedFields);
                    Log::info('Contract storage not yet implemented', ['queue_id' => $queueItem->id]);
                    $result = false;
                    break;
                case 'bid':
                    // Future: $this->storeBid($queueItem, $extractedFields);
                    Log::info('Bid storage not yet implemented', ['queue_id' => $queueItem->id]);
                    $result = false;
                    break;
                case 'timecard':
                    // Future: $this->storeTimecard($queueItem, $extractedFields);
                    Log::info('Timecard storage not yet implemented', ['queue_id' => $queueItem->id]);
                    $result = false;
                    break;
                default:
                    Log::warning('Unknown document type', [
                        'queue_id' => $queueItem->id,
                        'document_type' => $documentType
                    ]);
                    $result = false;
            }
            
            if ($result) {
                // Process file operations
                $this->processFileOperations($queueItem, $documentType, $result['record_id']);
                
                // Update queue status
                $queueItem->update([
                    'status' => 'completed',
                    'processed_at' => now(),
                ]);
                
                DB::commit();
                return true;
            }
            
            DB::rollBack();
            return false;
            
        } catch (\Exception $e) {
            DB::rollBack();
            Log::error('Post-processing failed', [
                'queue_id' => $queueItem->id,
                'error' => $e->getMessage(),
            ]);
            return false;
        }
    }
    
    /**
     * Store receipt data (MVP implementation).
     */
    protected function storeReceipt(DocumentQueue $queueItem, array $fields): array
    {
        $vendorName = $fields['vendor'] ?? null;
        
        // Find or create vendor
        $vendor = null;
        if ($vendorName) {
            $vendor = Vendor::where('name', $vendorName)->first();
            if (!$vendor) {
                $vendor = Vendor::create(['name' => $vendorName]);
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
            'entered_by_user_id' => auth()->id(),
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
        
        return [
            'record_id' => $receipt->id,
            'record_type' => 'PurchaseReceipt'
        ];
    }
    
    /**
     * Process file operations: rename, downsample, generate thumbnail.
     */
    protected function processFileOperations(
        DocumentQueue $queueItem,
        string $documentType,
        string $recordId
    ): void {
        $originalPath = $queueItem->file_path;
        
        // Use documents disk (generic, document-type aware)
        // Future: Resolve using tenant's storage_base_path from app_registrations
        $storageDisk = Storage::disk('documents');
        
        if (!$storageDisk->exists($originalPath)) {
            Log::warning('Original file not found for processing', [
                'file_path' => $originalPath
            ]);
            return;
        }
        
        // Generate new filename: processed.<document_type>.<date>.<uuid>.png
        $date = now()->format('Ymd_His');
        $extension = pathinfo($originalPath, PATHINFO_EXTENSION);
        $newFilename = "processed.{$documentType}.{$date}.{$recordId}.{$extension}";
        
        // Get directory of original file
        $directory = dirname($originalPath);
        $newPath = $directory . '/' . $newFilename;
        
        try {
            // Copy file to new location
            $storageDisk->copy($originalPath, $newPath);
            
            // Downsample original for storage
            $this->downsampleImage($originalPath);
            
            // Generate thumbnail
            $thumbnailPath = $this->generateThumbnail($newPath);
            
            // Update receipt with thumbnail path (if receipt)
            if ($documentType === 'receipt') {
                PurchaseReceipt::where('id', $recordId)->update([
                    'receipt_image_thumbnail' => $thumbnailPath
                ]);
            }
            
            // Delete original ready_ file (after successful processing)
            $storageDisk->delete($originalPath);
            
            Log::info('File processing completed', [
                'original' => $originalPath,
                'processed' => $newPath,
                'thumbnail' => $thumbnailPath,
            ]);
            
        } catch (\Exception $e) {
            Log::error('File processing failed', [
                'original' => $originalPath,
                'error' => $e->getMessage(),
            ]);
        }
    }
    
    /**
     * Downsample image for storage efficiency.
     */
    protected function downsampleImage(string $filePath): void
    {
        try {
            $storageDisk = Storage::disk('documents');
            $fullPath = $storageDisk->path($filePath);
            
            // Use Intervention Image if available, otherwise skip
            if (class_exists('Intervention\Image\Facades\Image')) {
                $img = Image::make($fullPath);
                
                // Resize if larger than 2000px on longest side
                if ($img->width() > 2000 || $img->height() > 2000) {
                    $img->resize(2000, 2000, function ($constraint) {
                        $constraint->aspectRatio();
                        $constraint->upsize();
                    });
                    $img->save($fullPath, 85); // 85% quality
                }
            }
        } catch (\Exception $e) {
            Log::warning('Image downsampling failed', [
                'file' => $filePath,
                'error' => $e->getMessage(),
            ]);
        }
    }
    
    /**
     * Generate thumbnail image.
     */
    protected function generateThumbnail(string $filePath): string
    {
        try {
            $storageDisk = Storage::disk('documents');
            $fullPath = $storageDisk->path($filePath);
            $thumbnailPath = str_replace(
                pathinfo($filePath, PATHINFO_EXTENSION),
                'thumb.' . pathinfo($filePath, PATHINFO_EXTENSION),
                $filePath
            );
            $thumbnailFullPath = $storageDisk->path($thumbnailPath);
            
            // Use Intervention Image if available
            if (class_exists('Intervention\Image\Facades\Image')) {
                $img = Image::make($fullPath);
                $img->fit(300, 300); // 300x300 thumbnail
                $img->save($thumbnailFullPath, 75);
            } else {
                // Fallback: copy original (thumbnail generation requires Intervention Image)
                $storageDisk->copy($filePath, $thumbnailPath);
            }
            
            return $thumbnailPath;
        } catch (\Exception $e) {
            Log::warning('Thumbnail generation failed', [
                'file' => $filePath,
                'error' => $e->getMessage(),
            ]);
            return $filePath; // Return original if thumbnail fails
        }
    }
    
    /**
     * Parse decimal value.
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
            $cleaned = preg_replace('/[^0-9.]/', '', $value);
            return round((float) $cleaned, $decimals);
        }
        
        return 0.0;
    }
}
