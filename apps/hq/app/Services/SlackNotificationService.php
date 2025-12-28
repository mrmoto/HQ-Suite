<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class SlackNotificationService
{
    protected ?string $webhookUrl;

    public function __construct()
    {
        $this->webhookUrl = config('services.slack.webhook_url');
    }

    /**
     * Send a notification to Slack about a new receipt in the queue.
     */
    public function notifyNewReceipt(string $queueId, string $filename, string $reviewUrl): bool
    {
        if (!$this->webhookUrl) {
            Log::warning('Slack webhook URL not configured');
            return false;
        }

        $message = [
            'text' => '📄 New Receipt Received',
            'blocks' => [
                [
                    'type' => 'header',
                    'text' => [
                        'type' => 'plain_text',
                        'text' => '📄 New Receipt Received',
                    ],
                ],
                [
                    'type' => 'section',
                    'fields' => [
                        [
                            'type' => 'mrkdwn',
                            'text' => "*Filename:*\n{$filename}",
                        ],
                        [
                            'type' => 'mrkdwn',
                            'text' => "*Queue ID:*\n`{$queueId}`",
                        ],
                    ],
                ],
                [
                    'type' => 'actions',
                    'elements' => [
                        [
                            'type' => 'button',
                            'text' => [
                                'type' => 'plain_text',
                                'text' => 'Review Receipt',
                            ],
                            'url' => $reviewUrl,
                            'style' => 'primary',
                        ],
                    ],
                ],
            ],
        ];

        try {
            $response = Http::post($this->webhookUrl, $message);

            if ($response->successful()) {
                return true;
            }

            Log::error('Slack notification failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);

            return false;
        } catch (\Exception $e) {
            Log::error('Slack notification exception', [
                'message' => $e->getMessage(),
            ]);

            return false;
        }
    }

    /**
     * Send a generic notification to Slack.
     */
    public function notify(string $message, string $channel = null): bool
    {
        if (!$this->webhookUrl) {
            return false;
        }

        $payload = ['text' => $message];

        if ($channel) {
            $payload['channel'] = $channel;
        }

        try {
            $response = Http::post($this->webhookUrl, $payload);
            return $response->successful();
        } catch (\Exception $e) {
            Log::error('Slack notification exception', [
                'message' => $e->getMessage(),
            ]);
            return false;
        }
    }
}



