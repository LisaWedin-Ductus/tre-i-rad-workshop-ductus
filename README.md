# Tre-i-rad Prompt Engineering Workshop, Ductus 2026

Välkommen till workshopen. Ni ska bygga ut ett enkelt 3-i-rad-spel i fem
faser (med en valfri sjätte) genom att använda **prompt engineering** för
att låta Claude/ChatGPT generera koden åt er.

Målet är inte att ni ska skriva all kod själva, det är att lära er hur
man **promptar fram** kod effektivt.

## Vad ni får

- **`starter-code/`** — En fungerande terminal-version av 3-i-rad. Detta
  är er utgångspunkt.
- **`uppgifter/`** — Fem (sex) uppgiftsbeskrivningar att jobba igenom i ordning.

## Krav på er dator

- **WSL2 med Ubuntu** (Windows) eller Linux/macOS direkt
- **VS Code** med WSL-extension
- **Python 3.10+**
- **Claude Pro** *eller* **ChatGPT Plus** för att kunna skapa Projects/Custom GPT
- **Anthropic API-nyckel** — delas ut av workshopledaren under workshopen
  (krävs först i Fas 5)

### Om ni inte har WSL2 installerat

Öppna PowerShell som administratör och kör:

```powershell
wsl --install
```

Starta om datorn. Öppna sedan Ubuntu från startmenyn och följ guiden.
Total tid: ~10-15 minuter.

Mer info: https://learn.microsoft.com/en-us/windows/wsl/install

## Setup

### 1. Klona repot

I WSL-terminalen:

```bash
git clone <repo-url>
cd tre-i-rad-workshop-ductus/starter-code
```

### 2. Installera python3-venv (engångskommando)

```bash
sudo apt update
sudo apt install python3-venv
```

### 3. Skapa `.env`-fil med API-nyckeln

API-nyckeln behövs först i Fas 5. När ni får den från workshopledaren,
skapa en fil som heter `.env` i `starter-code/`-mappen med innehållet:

```
ANTHROPIC_API_KEY=sk-ant-nyckeln-ni-fick
```

### 4. Kör setup

```bash
source setup.sh
```

Du borde se:
```
✓ Virtual environment aktiverad
✓ Dependencies installerade
✓ API-nyckel laddad från .env
```

### 5. Verifiera att starter-koden fungerar

```bash
python tic_tac_toe.py
```

Spelet startar i terminalen. Ni kan spela mot varandra. Funkar det?
Då är ni redo.

## Varje gång ni öppnar terminalen igen

```bash
cd tre-i-rad-workshop-ductus/starter-code
source setup.sh
```

## Vid problem

- **`No module named 'venv'`** → kör `sudo apt install python3-venv`
- **`ANTHROPIC_API_KEY saknas`** → kontrollera att `.env` är korrekt skapad
  i `starter-code/`-mappen och innehåller en giltig nyckel
- **`pip install` säger "externally-managed-environment"** → kör
  `source setup.sh` istället för att installera direkt

Om något annat strular — fråga workshopledaren.

## Lycka till