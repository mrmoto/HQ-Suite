<?php

namespace App\Filament\Resources\PurchaseReceiptResource\RelationManagers;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class PurchaseReceiptLinesRelationManager extends RelationManager
{
    protected static string $relationship = 'lines';

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('line_number')
                    ->required()
                    ->numeric()
                    ->default(1)
                    ->label('Line Number'),
                Forms\Components\Select::make('product_id')
                    ->relationship('product', 'name')
                    ->searchable()
                    ->preload()
                    ->label('Product'),
                Forms\Components\TextInput::make('vendor_sku')
                    ->label('Vendor SKU'),
                Forms\Components\Textarea::make('description')
                    ->rows(2)
                    ->required()
                    ->label('Description'),
                Forms\Components\TextInput::make('quantity')
                    ->numeric()
                    ->default(1)
                    ->required()
                    ->label('Quantity'),
                Forms\Components\TextInput::make('unit_price')
                    ->numeric()
                    ->prefix('$')
                    ->required()
                    ->label('Unit Price'),
                Forms\Components\TextInput::make('line_total')
                    ->numeric()
                    ->prefix('$')
                    ->label('Line Total (auto-calculated)')
                    ->disabled(),
                Forms\Components\TextInput::make('tax_rate_applied')
                    ->numeric()
                    ->suffix('%')
                    ->label('Tax Rate'),
                Forms\Components\Select::make('csi_code_id')
                    ->relationship('csiCode', 'code')
                    ->searchable()
                    ->preload()
                    ->label('CSI Code'),
                Forms\Components\TextInput::make('project_phase')
                    ->label('Project Phase'),
                Forms\Components\Textarea::make('notes')
                    ->rows(2)
                    ->label('Notes'),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('description')
            ->columns([
                Tables\Columns\TextColumn::make('line_number')
                    ->sortable()
                    ->label('#'),
                Tables\Columns\TextColumn::make('product.name')
                    ->searchable()
                    ->label('Product'),
                Tables\Columns\TextColumn::make('description')
                    ->searchable()
                    ->limit(30)
                    ->label('Description'),
                Tables\Columns\TextColumn::make('quantity')
                    ->numeric()
                    ->sortable(),
                Tables\Columns\TextColumn::make('unit_price')
                    ->money('USD')
                    ->sortable()
                    ->label('Unit Price'),
                Tables\Columns\TextColumn::make('line_total')
                    ->money('USD')
                    ->sortable()
                    ->label('Total'),
                Tables\Columns\TextColumn::make('csi_code.code')
                    ->label('CSI Code'),
            ])
            ->filters([
                //
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ])
            ->defaultSort('line_number');
    }
}
