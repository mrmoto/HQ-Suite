<?php

namespace App\Filament\Resources;

use App\Filament\Resources\PurchaseReceiptResource\Pages;
use App\Filament\Resources\PurchaseReceiptResource\RelationManagers;
use App\Models\PurchaseReceipt;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class PurchaseReceiptResource extends Resource
{
    protected static ?string $model = PurchaseReceipt::class;

    protected static ?string $navigationIcon = 'heroicon-o-receipt-percent';

    protected static ?string $navigationLabel = 'Purchase Receipts';

    protected static ?string $navigationGroup = 'Construction Suite';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Receipt Information')
                    ->schema([
                        Forms\Components\Select::make('project_id')
                            ->relationship('project', 'name')
                            ->searchable()
                            ->preload()
                            ->label('Project'),
                        Forms\Components\Select::make('vendor_id')
                            ->relationship('vendor', 'name')
                            ->searchable()
                            ->preload()
                            ->required()
                            ->label('Vendor'),
                        Forms\Components\DateTimePicker::make('purchase_date')
                            ->required()
                            ->default(now())
                            ->label('Purchase Date & Time'),
                        Forms\Components\DatePicker::make('receipt_date')
                            ->label('Receipt Date (if different)'),
                        Forms\Components\Select::make('purchased_by_user_id')
                            ->relationship('purchasedBy', 'name')
                            ->searchable()
                            ->preload()
                            ->label('Purchased By'),
                        Forms\Components\TextInput::make('receipt_number')
                            ->label('Receipt/Invoice Number'),
                        Forms\Components\TextInput::make('po_number')
                            ->label('PO Number'),
                    ])
                    ->columns(2),

                Forms\Components\Section::make('Financial Details')
                    ->schema([
                        Forms\Components\TextInput::make('subtotal')
                            ->numeric()
                            ->default(0)
                            ->prefix('$')
                            ->label('Subtotal'),
                        Forms\Components\TextInput::make('tax_amount')
                            ->numeric()
                            ->default(0)
                            ->prefix('$')
                            ->label('Tax Amount'),
                        Forms\Components\TextInput::make('total_amount')
                            ->numeric()
                            ->default(0)
                            ->prefix('$')
                            ->required()
                            ->label('Total Amount'),
                        Forms\Components\Select::make('payment_method')
                            ->options([
                                'cash' => 'Cash',
                                'credit_card' => 'Credit Card',
                                'debit_card' => 'Debit Card',
                                'check' => 'Check',
                                'ach' => 'ACH',
                                'wire' => 'Wire Transfer',
                                'other' => 'Other',
                            ])
                            ->label('Payment Method'),
                        Forms\Components\TextInput::make('payment_reference')
                            ->label('Payment Reference (Check #, Card Last 4, etc.)'),
                    ])
                    ->columns(2),

                Forms\Components\Section::make('Receipt Images')
                    ->schema([
                        Forms\Components\FileUpload::make('receipt_image_path')
                            ->disk('documents')  // Use documents disk (generic, document-type aware)
                            ->directory('receipts')
                            ->image()
                            ->imageEditor()
                            ->maxSize(10240) // 10MB
                            ->label('Receipt Image'),
                        Forms\Components\FileUpload::make('receipt_image_thumbnail')
                            ->disk('documents')  // Use documents disk (generic, document-type aware)
                            ->directory('thumbnails')
                            ->image()
                            ->maxSize(2048) // 2MB
                            ->label('Thumbnail (auto-generated if empty)'),
                    ])
                    ->columns(2),

                Forms\Components\Section::make('Status & Approval')
                    ->schema([
                        Forms\Components\Select::make('status')
                            ->options([
                                'draft' => 'Draft',
                                'submitted' => 'Submitted',
                                'approved' => 'Approved',
                                'reimbursed' => 'Reimbursed',
                                'archived' => 'Archived',
                            ])
                            ->default('draft')
                            ->required()
                            ->label('Status'),
                        Forms\Components\Select::make('entered_by_user_id')
                            ->relationship('enteredBy', 'name')
                            ->searchable()
                            ->preload()
                            ->default(auth()->id())
                            ->label('Entered By'),
                        Forms\Components\Select::make('approved_by_user_id')
                            ->relationship('approvedBy', 'name')
                            ->searchable()
                            ->preload()
                            ->label('Approved By'),
                        Forms\Components\DateTimePicker::make('approved_at')
                            ->label('Approved At'),
                        Forms\Components\DateTimePicker::make('reimbursed_at')
                            ->label('Reimbursed At'),
                    ])
                    ->columns(2),

                Forms\Components\Textarea::make('notes')
                    ->rows(3)
                    ->columnSpanFull()
                    ->label('Notes'),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('receipt_number')
                    ->searchable()
                    ->sortable()
                    ->label('Receipt #'),
                Tables\Columns\TextColumn::make('vendor.name')
                    ->searchable()
                    ->sortable()
                    ->label('Vendor'),
                Tables\Columns\TextColumn::make('project.name')
                    ->searchable()
                    ->sortable()
                    ->label('Project'),
                Tables\Columns\TextColumn::make('purchase_date')
                    ->dateTime()
                    ->sortable()
                    ->label('Purchase Date'),
                Tables\Columns\TextColumn::make('total_amount')
                    ->money('USD')
                    ->sortable()
                    ->label('Total'),
                Tables\Columns\TextColumn::make('status')
                    ->badge()
                    ->color(fn (string $state): string => match ($state) {
                        'draft' => 'gray',
                        'submitted' => 'warning',
                        'approved' => 'success',
                        'reimbursed' => 'info',
                        'archived' => 'danger',
                        default => 'gray',
                    })
                    ->sortable(),
                Tables\Columns\TextColumn::make('payment_method')
                    ->badge()
                    ->label('Payment'),
                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'draft' => 'Draft',
                        'submitted' => 'Submitted',
                        'approved' => 'Approved',
                        'reimbursed' => 'Reimbursed',
                        'archived' => 'Archived',
                    ]),
                Tables\Filters\SelectFilter::make('project_id')
                    ->relationship('project', 'name')
                    ->searchable()
                    ->preload(),
                Tables\Filters\SelectFilter::make('vendor_id')
                    ->relationship('vendor', 'name')
                    ->searchable()
                    ->preload(),
                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
                Tables\Actions\RestoreAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\RestoreBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            RelationManagers\PurchaseReceiptLinesRelationManager::class,
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListPurchaseReceipts::route('/'),
            'create' => Pages\CreatePurchaseReceipt::route('/create'),
            'edit' => Pages\EditPurchaseReceipt::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->withoutGlobalScopes([
                SoftDeletingScope::class,
            ]);
    }
}
