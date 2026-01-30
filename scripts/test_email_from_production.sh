#!/bin/bash
# Test email delivery from production
# Usage: ./scripts/test_email_from_production.sh [email]
EMAIL="${1:-dev@innovasaleslab.com}"
URL="https://sally-love-voice-agent.fly.dev"

echo "=== 1. Check health (SMTP status) ==="
curl -s "$URL/health" | python3 -m json.tool | grep -A1 smtp

echo ""
echo "=== 2. Send test notification (SMS + email) to $EMAIL ==="
curl -s -X POST "$URL/functions/send_notification" \
  -H "Content-Type: application/json" \
  -d "{
    \"recipient_phone\": \"+923035699010\",
    \"recipient_email\": \"$EMAIL\",
    \"message\": \"Test from Sally Love Voice Agent - if you receive this, email is working.\",
    \"notification_type\": \"both\"
  }" | python3 -m json.tool
