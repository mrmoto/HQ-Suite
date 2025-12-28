<?php

namespace App\Filament\Pages\Auth;

use Filament\Pages\Auth\Login as BaseLogin;

class CustomLogin extends BaseLogin
{
    /**
     * Use custom view that includes auto-fill script for development
     */
    protected static string $view = 'filament.pages.auth.custom-login';
}
