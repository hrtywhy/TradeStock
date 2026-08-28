#!/bin/bash
# =============================================================
# deploy.sh — Re-deploy after pushing new code to GitHub.
# Run on your Tencent Cloud VM: sudo bash scripts/deploy.sh
# =============================================================

set -e

APP_DIR="/opt/tradestock-bot"
SERVICE_NAME="tradestock-bot"

echo ""
echo "=========================================="
echo "  IDX Bot — Deploying Update"
echo "=========================================="
echo ""

# 1. Pull latest code
echo "[1/4] Pulling latest code..."
git -C "$APP_DIR" pull
echo "      Done."

# 2. Update dependencies if requirements.txt changed
echo "[2/4] Updating Python dependencies..."
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q
echo "      Done."

# 3. Update systemd service file if it changed
echo "[3/4] Refreshing systemd service..."
cp "$APP_DIR/tradestock-bot.service" /etc/systemd/system/tradestock-bot.service
systemctl daemon-reload
echo "      Done."

# 4. Restart the service
echo "[4/4] Restarting $SERVICE_NAME..."
systemctl restart "$SERVICE_NAME"
sleep 2
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "  ? Deploy complete! Watch logs with:"
echo "     sudo journalctl -u $SERVICE_NAME -f"
echo ""
