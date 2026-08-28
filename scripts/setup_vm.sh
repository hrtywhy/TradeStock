#!/bin/bash
# =============================================================
# setup_vm.sh — One-time setup for IDX Swing Trading Bot
# Run on your Tencent Cloud Ubuntu VM as root or with sudo.
# Usage: sudo bash scripts/setup_vm.sh
# =============================================================

set -e  # Exit on any error

# -- CONFIG ----------------------------------------------------
REPO_URL="https://github.com/hrtywhy/TradeStock.git"
APP_DIR="/opt/tradestock-bot"
SERVICE_USER="tradebot"
PYTHON_BIN="python3"
# --------------------------------------------------------------

echo ""
echo "=========================================="
echo "  IDX Swing Trading Bot — VM Setup"
echo "=========================================="
echo ""

# 1. Update system & install dependencies
echo "[1/8] Updating system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip git curl
echo "      Done."

# 2. Create a dedicated system user (no login shell, for security)
echo "[2/8] Creating service user '$SERVICE_USER'..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
    echo "      User '$SERVICE_USER' created."
else
    echo "      User '$SERVICE_USER' already exists, skipping."
fi

# 3. Clone or update repository
echo "[3/8] Setting up repository at $APP_DIR..."
if [ -d "$APP_DIR/.git" ]; then
    echo "      Repo exists — pulling latest changes..."
    git -C "$APP_DIR" pull
else
    git clone "$REPO_URL" "$APP_DIR"
fi

# 4. Create Python virtual environment
echo "[4/8] Creating Python virtual environment..."
$PYTHON_BIN -m venv "$APP_DIR/.venv"
echo "      Done."

# 5. Install Python dependencies
echo "[5/8] Installing Python dependencies..."
"$APP_DIR/.venv/bin/pip" install --upgrade pip -q
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q
echo "      All packages installed."

# 6. Create secrets directory scaffold & check files
echo "[6/8] Checking secrets..."
mkdir -p "$APP_DIR/secrets"

SECRETS_OK=true
for f in telegram_creds.json api_keys.json google_config.json; do
    if [ ! -f "$APP_DIR/secrets/$f" ]; then
        echo "      ??  MISSING: $APP_DIR/secrets/$f"
        SECRETS_OK=false
    else
        echo "      ? Found: $f"
    fi
done

if [ "$SECRETS_OK" = false ]; then
    echo ""
    echo "  +-----------------------------------------------------+"
    echo "  ¦  ACTION REQUIRED — Create these secrets files:      ¦"
    echo "  ¦                                                     ¦"
    echo "  ¦  /opt/tradestock-bot/secrets/telegram_creds.json:  ¦"
    echo "  ¦  { \"bot_token\": \"...\", \"chat_id\": \"...\" }           ¦"
    echo "  ¦                                                     ¦"
    echo "  ¦  /opt/tradestock-bot/secrets/api_keys.json:         ¦"
    echo "  ¦  { \"api_key\": \"gemini-key\",                         ¦"
    echo "  ¦    \"finnhub_api_key\": \"...\",                        ¦"
    echo "  ¦    \"polygon_api_key\": \"...\",                        ¦"
    echo "  ¦    \"marketaux_api_key\": \"...\",                      ¦"
    echo "  ¦    \"newsapi_key\": \"...\",                            ¦"
    echo "  ¦    \"newsdata_key\": \"...\" }                          ¦"
    echo "  ¦                                                     ¦"
    echo "  ¦  /opt/tradestock-bot/secrets/google_config.json:   ¦"
    echo "  ¦  { \"sheet_id\": \"...\",                               ¦"
    echo "  ¦    \"json_keyfile\": \"/opt/tradestock-bot/xxx.json\", ¦"
    echo "  ¦    \"sheet_name\": \"Sheet1\" }                         ¦"
    echo "  ¦                                                     ¦"
    echo "  ¦  Then place your Google Service Account .json in:  ¦"
    echo "  ¦  /opt/tradestock-bot/                              ¦"
    echo "  ¦                                                     ¦"
    echo "  ¦  Then run: sudo systemctl start tradestock-bot     ¦"
    echo "  +-----------------------------------------------------+"
fi

# 7. Set correct file ownership
echo "[7/8] Setting file ownership to '$SERVICE_USER'..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"
echo "      Done."

# 8. Install and enable systemd service
echo "[8/8] Installing systemd service..."
cp "$APP_DIR/tradestock-bot.service" /etc/systemd/system/tradestock-bot.service
systemctl daemon-reload
systemctl enable tradestock-bot.service
echo "      Service registered and set to start on boot."

echo ""
echo "=========================================="
echo "  ? Setup Complete!"
echo "=========================================="
echo ""
echo "  Commands:"
echo "  • Start :  sudo systemctl start tradestock-bot"
echo "  • Stop  :  sudo systemctl stop tradestock-bot"
echo "  • Status:  sudo systemctl status tradestock-bot"
echo "  • Logs  :  sudo journalctl -u tradestock-bot -f"
echo ""
