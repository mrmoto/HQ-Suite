<x-filament-pages::page>
    <div class="space-y-6">
        <!-- Queue List -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Queue Items List -->
            <div class="lg:col-span-1">
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                    <h3 class="text-lg font-semibold mb-4">Pending Receipts</h3>
                    <div class="space-y-2 max-h-[600px] overflow-y-auto">
                        @forelse($this->getQueueItems() as $item)
                            <div 
                                wire:click="selectQueueItem('{{ $item->id }}')"
                                class="p-3 rounded border cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition
                                    {{ $this->selectedQueueItem?->id === $item->id ? 'border-primary-500 bg-primary-50 dark:bg-primary-900' : '' }}"
                            >
                                <div class="font-medium text-sm">{{ $item->original_filename }}</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    Received: {{ $item->received_at->diffForHumans() }}
                                </div>
                                <div class="mt-1">
                                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
                                        @if($item->status === 'pending') bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200
                                        @elseif($item->status === 'processing') bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200
                                        @endif">
                                        {{ ucfirst($item->status) }}
                                    </span>
                                </div>
                            </div>
                        @empty
                            <div class="text-center text-gray-500 dark:text-gray-400 py-8">
                                <p>No receipts in queue</p>
                            </div>
                        @endforelse
                    </div>
                </div>
            </div>

            <!-- Receipt Preview and Actions -->
            <div class="lg:col-span-2">
                @if($this->selectedQueueItem)
                    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">{{ $this->selectedQueueItem->original_filename }}</h3>
                            <div class="flex gap-2">
                                <x-filament::button 
                                    wire:click="processReceipt"
                                    color="primary"
                                    size="sm"
                                >
                                    Start OCR Processing
                                </x-filament::button>
                                <x-filament::button 
                                    wire:click="markAsReviewed"
                                    color="success"
                                    size="sm"
                                >
                                    Mark as Reviewed
                                </x-filament::button>
                            </div>
                        </div>

                        <div class="mb-4 space-y-2 text-sm">
                            <div><strong>Queue ID:</strong> {{ $this->selectedQueueItem->id }}</div>
                            <div><strong>Received:</strong> {{ $this->selectedQueueItem->received_at->format('M d, Y g:i A') }}</div>
                            <div><strong>Source:</strong> {{ ucfirst($this->selectedQueueItem->source) }}</div>
                            <div><strong>Status:</strong> 
                                <span class="px-2 py-1 rounded text-xs font-medium
                                    @if($this->selectedQueueItem->status === 'pending') bg-yellow-100 text-yellow-800
                                    @elseif($this->selectedQueueItem->status === 'processing') bg-blue-100 text-blue-800
                                    @endif">
                                    {{ ucfirst($this->selectedQueueItem->status) }}
                                </span>
                            </div>
                        </div>

                        @if($this->getReceiptImageUrl($this->selectedQueueItem))
                            <div class="border rounded-lg p-4 bg-gray-50 dark:bg-gray-900 mb-4">
                                <img 
                                    src="{{ $this->getReceiptImageUrl($this->selectedQueueItem) }}" 
                                    alt="Receipt Image"
                                    class="max-w-full h-auto rounded"
                                />
                            </div>
                        @else
                            <div class="border rounded-lg p-8 text-center text-gray-500 mb-4">
                                Image not available
                            </div>
                        @endif

                        @php
                            $ocrMetadata = $this->getOcrMetadata();
                            $extractedFields = $this->getExtractedFields();
                        @endphp

                        @if($ocrMetadata || $extractedFields)
                            <div class="border rounded-lg p-4 bg-gray-50 dark:bg-gray-900 mb-4">
                                <h4 class="font-semibold mb-3">OCR Extraction Results</h4>
                                
                                @if($ocrMetadata)
                                    <div class="mb-4 space-y-1 text-sm">
                                        @if($ocrMetadata['vendor'])
                                            <div><strong>Vendor:</strong> {{ $ocrMetadata['vendor'] }}</div>
                                        @endif
                                        @if($ocrMetadata['format_detected'])
                                            <div><strong>Format:</strong> {{ $ocrMetadata['format_detected'] }}</div>
                                        @endif
                                        @if($ocrMetadata['confidence'] !== null)
                                            <div><strong>Confidence:</strong> 
                                                <span class="px-2 py-0.5 rounded text-xs font-medium
                                                    @if($ocrMetadata['confidence'] >= 0.85) bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200
                                                    @elseif($ocrMetadata['confidence'] >= 0.70) bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200
                                                    @else bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200
                                                    @endif">
                                                    {{ number_format($ocrMetadata['confidence'] * 100, 1) }}% ({{ $ocrMetadata['confidence_level'] ?? 'unknown' }})
                                                </span>
                                            </div>
                                        @endif
                                    </div>
                                @endif

                                @if($extractedFields)
                                    <div class="space-y-3">
                                        <h5 class="font-medium text-sm">Extracted Fields</h5>
                                        
                                        <!-- Receipt-Level Fields -->
                                        <div>
                                            <h6 class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Receipt Fields</h6>
                                            <div class="grid grid-cols-2 gap-2 text-sm">
                                                @foreach($extractedFields as $fieldName => $fieldValue)
                                                    @if(!is_array($fieldValue) && $fieldName !== 'line_items')
                                                        <div class="flex items-start justify-between p-2 bg-white dark:bg-gray-800 rounded border">
                                                            <div class="flex-1">
                                                                <div class="font-medium text-xs text-gray-600 dark:text-gray-400">{{ $fieldName }}</div>
                                                                <div class="text-sm mt-0.5">{{ is_string($fieldValue) ? Str::limit($fieldValue, 50) : $fieldValue }}</div>
                                                            </div>
                                                            <button 
                                                                wire:click="flagMissingField('{{ $fieldName }}', 'receipt')"
                                                                class="ml-2 text-xs text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300"
                                                                title="Flag as missing from schema"
                                                            >
                                                                ⚠️
                                                            </button>
                                                        </div>
                                                    @endif
                                                @endforeach
                                            </div>
                                        </div>

                                        <!-- Line Items -->
                                        @if(isset($extractedFields['line_items']) && is_array($extractedFields['line_items']) && count($extractedFields['line_items']) > 0)
                                            <div>
                                                <h6 class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Line Items ({{ count($extractedFields['line_items']) }})</h6>
                                                <div class="space-y-2 max-h-48 overflow-y-auto">
                                                    @foreach($extractedFields['line_items'] as $index => $item)
                                                        <div class="p-2 bg-white dark:bg-gray-800 rounded border text-sm">
                                                            <div class="font-medium mb-1">Item {{ $index + 1 }}</div>
                                                            <div class="grid grid-cols-2 gap-2 text-xs">
                                                                @foreach($item as $itemField => $itemValue)
                                                                    <div>
                                                                        <span class="text-gray-600 dark:text-gray-400">{{ $itemField }}:</span>
                                                                        <span class="ml-1">{{ is_string($itemValue) ? Str::limit($itemValue, 30) : $itemValue }}</span>
                                                                    </div>
                                                                @endforeach
                                                            </div>
                                                        </div>
                                                    @endforeach
                                                </div>
                                            </div>
                                        @endif
                                    </div>
                                @endif
                            </div>
                        @endif
                    </div>
                @else
                    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
                        <p class="text-gray-500 dark:text-gray-400">Select a receipt from the queue to review</p>
                    </div>
                @endif
            </div>
        </div>
    </div>
</x-filament-pages::page>
