<x-filament-panels::page>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        @foreach([
            ['name' => 'Construction Suite',  'icon' => 'heroicon-o-wrench-screwdriver', 'url' => '#', 'status' => 'coming soon'],
            ['name' => 'Finance Tracker',     'icon' => 'heroicon-o-banknotes',          'url' => '#', 'status' => 'coming soon'],
            ['name' => 'Calendar & Tasks',    'icon' => 'heroicon-o-calendar',            'url' => '#', 'status' => 'coming soon'],
            ['name' => 'Home Systems',        'icon' => 'heroicon-o-home',                'url' => '#', 'status' => 'coming soon'],
            ['name' => 'Wine Cellar',         'icon' => 'heroicon-o-archive-box',         'url' => '#', 'status' => 'coming soon'],
            ['name' => 'Documents Vault',     'icon' => 'heroicon-o-folder-open',         'url' => '#', 'status' => 'coming soon'],
            ['name' => 'Python Sandbox',      'icon' => 'heroicon-o-code-bracket-square', 'url' => '/notebook', 'status' => 'planned'],
        ] as $app)
            <a href="{{ $app['url'] }}" class="block p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-2xl transition transform hover:-translate-y-1 border border-gray-200 dark:border-gray-700">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <x-heroicon-o {{ $app['icon'] }} class="w-12 h-12 text-primary-600"/>
                        <div>
                            <h3 class="text-xl font-bold">{{ $app['name'] }}</h3>
                            <span class="text-sm text-gray-500">{{ ucfirst($app['status']) }}</span>
                        </div>
                    </div>
                    <span class="text-3xl">→</span>
                </div>
            </a>
        @endforeach
    </div>
</x-filament-panels::page>
