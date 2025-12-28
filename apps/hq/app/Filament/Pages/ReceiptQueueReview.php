<?php

namespace App\Filament\Pages;

use App\Models\ReceiptQueue;
use App\Services\Ocr\OcrProcessingService;
use Filament\Actions\Action;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class ReceiptQueueReview extends Page implements HasForms
{
    use InteractsWithForms;

    protected static ?string $navigationIcon = 'heroicon-o-inbox';

    protected static string $view = 'filament.pages.receipt-queue-review';

    protected static ?string $navigationLabel = 'Receipt Queue';

    protected static ?string $navigationGroup = 'Construction Suite';

    public ?ReceiptQueue $selectedQueueItem = null;

    public function mount(): void
    {
        // Check if user has permission to access this feature
        // This will be enhanced with Filament Shield roles later
        
        // Handle queue parameter from URL (e.g., ?queue=uuid)
        $queueId = request()->query('queue');
        if ($queueId) {
            $this->selectedQueueItem = ReceiptQueue::find($queueId);
            
            if (!$this->selectedQueueItem) {
                Notification::make()
                    ->title('Queue item not found')
                    ->danger()
                    ->send();
            }
        }
    }

    protected function getHeaderActions(): array
    {
        return [
            Action::make('refresh')
                ->label('Refresh Queue')
                ->icon('heroicon-o-arrow-path')
                ->action('refreshQueue'),
        ];
    }

    public function refreshQueue(): void
    {
        Notification::make()
            ->title('Queue refreshed')
            ->success()
            ->send();
    }

    public function selectQueueItem(string $queueId): void
    {
        $this->selectedQueueItem = ReceiptQueue::find($queueId);
        $this->dispatch('queue-item-selected', queueId: $queueId);
    }

    public function getQueueItems()
    {
        return ReceiptQueue::where('status', 'pending')
            ->orWhere('status', 'processing')
            ->orderBy('received_at', 'desc')
            ->get();
    }

    public function getReceiptImageUrl(?ReceiptQueue $queueItem): ?string
    {
        if (!$queueItem || !$queueItem->file_path) {
            return null;
        }

        // Use documents disk (generic, document-type aware)
        return Storage::disk('documents')->url($queueItem->file_path);
    }

    public function markAsReviewed(): void
    {
        if (!$this->selectedQueueItem) {
            return;
        }

        $this->selectedQueueItem->update([
            'status' => 'reviewed',
            'reviewed_by_user_id' => auth()->id(),
            'reviewed_at' => now(),
        ]);

        Notification::make()
            ->title('Receipt marked as reviewed')
            ->success()
            ->send();

        $this->selectedQueueItem = null;
    }

    public function processReceipt(): void
    {
        if (!$this->selectedQueueItem) {
            return;
        }

        $ocrService = app(OcrProcessingService::class);
        $success = $ocrService->processReceipt($this->selectedQueueItem);

        if ($success) {
            Notification::make()
                ->title('Receipt processing started')
                ->body('OCR processing has been initiated.')
                ->success()
                ->send();
            
            // Refresh the queue item
            $this->selectedQueueItem->refresh();
        } else {
            Notification::make()
                ->title('Processing failed')
                ->body('Failed to start OCR processing. Check logs for details.')
                ->danger()
                ->send();
        }
    }

    public function getExtractedFields(): ?array
    {
        if (!$this->selectedQueueItem || !$this->selectedQueueItem->classification_result) {
            return null;
        }

        return $this->selectedQueueItem->classification_result['fields'] ?? null;
    }

    public function getOcrMetadata(): ?array
    {
        if (!$this->selectedQueueItem || !$this->selectedQueueItem->classification_result) {
            return null;
        }

        return [
            'vendor' => $this->selectedQueueItem->classification_result['vendor'] ?? null,
            'format_detected' => $this->selectedQueueItem->classification_result['format_detected'] ?? null,
            'confidence' => $this->selectedQueueItem->classification_result['confidence'] ?? null,
            'confidence_level' => $this->selectedQueueItem->classification_result['confidence_level'] ?? null,
        ];
    }

    public function flagMissingField(string $fieldName, string $fieldType = 'receipt'): void
    {
        // This would ideally save to a database table or file for tracking
        // For now, we'll just show a notification
        Notification::make()
            ->title('Field Flagged')
            ->body("Field '{$fieldName}' flagged as missing from {$fieldType} schema. Check field_discovery.md for tracking.")
            ->warning()
            ->send();
    }

    public static function shouldRegisterNavigation(): bool
    {
        // Add permission check here when using Filament Shield
        // For now, all authenticated users can access
        return true;
    }
}
