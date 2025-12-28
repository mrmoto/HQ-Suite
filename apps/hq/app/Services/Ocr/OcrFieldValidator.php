<?php

namespace App\Services\Ocr;

use Illuminate\Support\Facades\Log;

class OcrFieldValidator
{
    /**
     * Validate extracted fields against format-specific requirements.
     * 
     * @param array $extractedFields Extracted fields from OCR
     * @param string $formatId Format identifier (e.g., 'mead_clark_format1')
     * @return array Validation result with 'is_valid', 'missing_fields', 'confidence_issues'
     */
    public function validate(array $extractedFields, string $formatId): array
    {
        $result = [
            'is_valid' => true,
            'missing_fields' => [],
            'confidence_issues' => [],
            'warnings' => [],
        ];
        
        // Get format-specific requirements
        $requiredFields = $this->getRequiredFields($formatId);
        $fieldMappings = $this->getFieldMappings($formatId);
        
        // Check required fields
        foreach ($requiredFields as $field) {
            $value = $extractedFields[$field] ?? null;
            
            if ($value === null || $value === '' || $value === 'NULL') {
                $result['missing_fields'][] = $field;
                $result['is_valid'] = false;
            }
        }
        
        // Check confidence thresholds
        $confidenceIssues = $this->checkConfidenceThresholds($extractedFields, $formatId);
        if (!empty($confidenceIssues)) {
            $result['confidence_issues'] = $confidenceIssues;
            // High confidence issues (like amountTotal) make validation fail
            if (in_array('amountTotal', $confidenceIssues)) {
                $result['is_valid'] = false;
            }
        }
        
        // Check for data quality warnings
        $warnings = $this->checkDataQuality($extractedFields, $formatId);
        $result['warnings'] = $warnings;
        
        return $result;
    }
    
    /**
     * Get required fields for a format.
     * 
     * @param string $formatId Format identifier
     * @return array List of required field names
     */
    protected function getRequiredFields(string $formatId): array
    {
        // Format-specific required fields
        $formatRequirements = [
            'mead_clark_format1' => [
                'receipt_date',
                'receipt_number',
                'total_amount',
            ],
            // Add other formats as needed
        ];
        
        return $formatRequirements[$formatId] ?? [];
    }
    
    /**
     * Get field mappings for a format.
     * 
     * @param string $formatId Format identifier
     * @return array Field mappings
     */
    protected function getFieldMappings(string $formatId): array
    {
        // Format-specific field mappings
        $formatMappings = [
            'mead_clark_format1' => [
                'receipt_date' => 'receipt_date',
                'receipt_number' => 'receipt_number',
                'total_amount' => 'total_amount',
                'subtotal' => 'subtotal',
                'amount_subtotal' => 'amount_subtotal',
                'tax_amount' => 'tax_amount',
                'vendor' => 'vendor',
                'line_items' => 'line_items',
            ],
            // Add other formats as needed
        ];
        
        return $formatMappings[$formatId] ?? [];
    }
    
    /**
     * Check confidence thresholds for critical fields.
     * 
     * @param array $extractedFields Extracted fields
     * @param string $formatId Format identifier
     * @return array List of fields with confidence issues
     */
    protected function checkConfidenceThresholds(array $extractedFields, string $formatId): array
    {
        $issues = [];
        
        // Check amountTotal confidence (must be >99%)
        if (isset($extractedFields['total_amount'])) {
            $totalAmount = $extractedFields['total_amount'];
            $confidence = $extractedFields['total_amount_confidence'] ?? 1.0;
            
            // If confidence is provided and is below threshold
            if ($confidence < 0.99) {
                $issues[] = 'amountTotal';
                Log::warning('Total amount confidence below threshold', [
                    'format' => $formatId,
                    'total_amount' => $totalAmount,
                    'confidence' => $confidence,
                ]);
            }
            
            // Validate amountTotal is reasonable (positive, not zero for non-zero receipts)
            if ($totalAmount <= 0 && !empty($extractedFields['line_items'])) {
                $issues[] = 'amountTotal';
                Log::warning('Total amount is zero or negative but line items exist', [
                    'format' => $formatId,
                    'total_amount' => $totalAmount,
                ]);
            }
        }
        
        // Check receipt_number confidence if provided
        if (isset($extractedFields['receipt_number'])) {
            $confidence = $extractedFields['receipt_number_confidence'] ?? 1.0;
            if ($confidence < 0.85) {
                $issues[] = 'receipt_number';
                Log::warning('Receipt number confidence below threshold', [
                    'format' => $formatId,
                    'receipt_number' => $extractedFields['receipt_number'],
                    'confidence' => $confidence,
                ]);
            }
        }
        
        return $issues;
    }
    
    /**
     * Check data quality and generate warnings.
     * 
     * @param array $extractedFields Extracted fields
     * @param string $formatId Format identifier
     * @return array List of warnings
     */
    protected function checkDataQuality(array $extractedFields, string $formatId): array
    {
        $warnings = [];
        
        // Check if line items exist but subtotal doesn't match
        if (isset($extractedFields['line_items']) && is_array($extractedFields['line_items'])) {
            $calculatedSubtotal = 0;
            foreach ($extractedFields['line_items'] as $item) {
                $lineTotal = $item['line_total'] ?? $item['subtotal'] ?? 0;
                $calculatedSubtotal += (float) $lineTotal;
            }
            
            $extractedSubtotal = $extractedFields['subtotal'] ?? $extractedFields['amount_subtotal'] ?? 0;
            
            // Allow 1% tolerance for rounding differences
            $difference = abs($calculatedSubtotal - (float) $extractedSubtotal);
            $tolerance = max(0.01, $calculatedSubtotal * 0.01);
            
            if ($difference > $tolerance && $calculatedSubtotal > 0) {
                $warnings[] = sprintf(
                    'Subtotal mismatch: extracted=%.2f, calculated=%.2f, difference=%.2f',
                    $extractedSubtotal,
                    $calculatedSubtotal,
                    $difference
                );
            }
        }
        
        // Check if tax calculation is reasonable
        if (isset($extractedFields['tax_amount']) && isset($extractedFields['amount_taxable'])) {
            $taxAmount = (float) $extractedFields['tax_amount'];
            $taxableAmount = (float) $extractedFields['amount_taxable'];
            
            if ($taxableAmount > 0) {
                $calculatedTaxRate = $taxAmount / $taxableAmount;
                
                // Check if tax rate is reasonable (typically 0-0.15 for 0-15%)
                if ($calculatedTaxRate > 0.15) {
                    $warnings[] = sprintf(
                        'Tax rate seems high: %.2f%% (tax=%.2f, taxable=%.2f)',
                        $calculatedTaxRate * 100,
                        $taxAmount,
                        $taxableAmount
                    );
                }
            }
        }
        
        // Check if receipt_date is in the future
        if (isset($extractedFields['receipt_date'])) {
            try {
                $receiptDate = new \DateTime($extractedFields['receipt_date']);
                $now = new \DateTime();
                
                if ($receiptDate > $now) {
                    $warnings[] = 'Receipt date is in the future';
                }
            } catch (\Exception $e) {
                // Invalid date format - already caught as missing field
            }
        }
        
        return $warnings;
    }
    
    /**
     * Determine if receipt should be routed to review queue.
     * 
     * @param array $validationResult Validation result from validate()
     * @return bool True if should be routed to review
     */
    public function shouldRouteToReview(array $validationResult): bool
    {
        // Route to review if:
        // 1. Validation failed (missing required fields or critical confidence issues)
        // 2. There are confidence issues with critical fields
        // 3. There are multiple warnings
        
        if (!$validationResult['is_valid']) {
            return true;
        }
        
        if (!empty($validationResult['confidence_issues'])) {
            return true;
        }
        
        if (count($validationResult['warnings']) >= 3) {
            return true;
        }
        
        return false;
    }
}
