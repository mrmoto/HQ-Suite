<x-filament-panels::page.simple>
    @if (filament()->hasRegistration())
        <x-slot name="subheading">
            {{ __('filament-panels::pages/auth/login.actions.register.before') }}

            {{ $this->registerAction }}
        </x-slot>
    @endif

    {{ \Filament\Support\Facades\FilamentView::renderHook(\Filament\View\PanelsRenderHook::AUTH_LOGIN_FORM_BEFORE, scopes: $this->getRenderHookScopes()) }}

    <x-filament-panels::form id="form" wire:submit="authenticate">
        {{ $this->form }}

        <x-filament-panels::form.actions
            :actions="$this->getCachedFormActions()"
            :full-width="$this->hasFullWidthFormActions()"
        />
    </x-filament-panels::form>

    {{ \Filament\Support\Facades\FilamentView::renderHook(\Filament\View\PanelsRenderHook::AUTH_LOGIN_FORM_AFTER, scopes: $this->getRenderHookScopes()) }}

    @if (app()->environment('local'))
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Only auto-fill on localhost
                if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
                    // Refresh CSRF token to prevent 419 errors
                    fetch('/admin/login', {
                        method: 'GET',
                        credentials: 'same-origin'
                    }).then(function() {
                        // Auto-fill credentials after ensuring fresh session
                        setTimeout(function() {
                            const emailField = document.querySelector('input[type="email"]');
                            const passwordField = document.querySelector('input[type="password"]');
                            
                            if (emailField) {
                                emailField.value = '{{ config('app.dev_email', 'scott@scottr.net') }}';
                                // Trigger Livewire update
                                emailField.dispatchEvent(new Event('input', { bubbles: true }));
                                emailField.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            
                            if (passwordField) {
                                passwordField.value = '{{ config('app.dev_password', 'password') }}';
                                // Trigger Livewire update
                                passwordField.dispatchEvent(new Event('input', { bubbles: true }));
                                passwordField.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }, 300);
                    });
                }
            });
        </script>
    @endif
</x-filament-panels::page.simple>

