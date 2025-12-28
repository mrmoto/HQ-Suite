<?php

namespace App\Filament\Resources\CsiCodeResource\Pages;

use App\Filament\Resources\CsiCodeResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListCsiCodes extends ListRecords
{
    protected static string $resource = CsiCodeResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
