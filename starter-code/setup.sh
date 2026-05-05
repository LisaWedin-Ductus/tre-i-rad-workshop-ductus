#!/bin/bash
# setup.sh — Aktiverar virtual environment och laddar API-nyckel.
#
# Användning:
#   source setup.sh
#
# OBS: Måste köras med 'source' (eller '.'), INTE som './setup.sh'.
# Annars dör miljövariablerna när scriptet avslutas.

# Hitta mappen där detta script ligger (oavsett varifrån det körs)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# --- Steg 1: Skapa venv om den inte finns ---
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "→ Skapar virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# --- Steg 2: Aktivera venv ---
source "$SCRIPT_DIR/venv/bin/activate"
echo "✓ Virtual environment aktiverad"

# --- Steg 3: Installera dependencies om anthropic saknas ---
if ! python -c "import anthropic" 2>/dev/null; then
    echo "→ Installerar anthropic-paketet..."
    pip install --quiet anthropic
fi
echo "✓ Dependencies installerade"

# --- Steg 4: Ladda API-nyckel från .env ---
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a              # auto-exportera variabler
    source "$SCRIPT_DIR/.env"
    set +a
    echo "✓ API-nyckel laddad från .env"
else
    echo "⚠ Ingen .env-fil hittad. Skapa en med:"
    echo "    echo 'ANTHROPIC_API_KEY=sk-ant-din-nyckel' > .env"
fi

echo ""
echo "Klar! Nu kan du köra dina Python-skript som använder Anthropic API."