# FlowsyAI Bot

Un bot Telegram avansat pentru comunitatea FlowsyAI, cu funcționalități de monitorizare crypto, sondaje și inteligență artificială.

## Funcționalități

### Comenzi de Bază
- `/start` - Pornește conversația cu botul
- `/features` - Află beneficiile grupului
- `/about` - Citește despre misiunea FlowsyAI
- `/help` - Afișează lista completă de comenzi

### Funcționalități Crypto
- `/coin <simbol>` - Verifică prețul unei criptomonede
- `/alerta <simbol> <peste/sub> <preț>` - Setează o alertă de preț
- `/alerte` - Vezi alertele active
- `/stergealerta <ID>` - Șterge o alertă

### Sondaje și Interacțiune
- `/sondaj <întrebare> "<opțiune1>" "<opțiune2>" ...` - Creează un sondaj

### Celebrări Automate
- Detectează și celebrează automat achizițiile de token Flowsy
- Trimite GIF-uri și stickere personalizate pentru evenimente importante

## Instalare

1. Clonează repozitoriul:
```bash
git clone https://github.com/yourusername/flowsyai-bot.git
cd flowsyai-bot
```

2. Instalează dependențele:
```bash
pip install -r requirements.txt
```

3. Creează un fișier `.env` cu următoarele variabile:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
ADMIN_ID=your_telegram_id
CHAT_ID=your_group_chat_id
GROUP_LINK=your_group_invite_link
FLOWSY_TOKEN_MINT=your_flowsy_token_mint_address
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com
```

4. Pornește botul:
```bash
python run.py
```

## Contribuție

Contribuțiile sunt binevenite! Te rugăm să deschizi un issue sau să creezi un pull request pentru orice îmbunătățiri.

## Licență

Acest proiect este licențiat sub termenii [MIT License](LICENSE).