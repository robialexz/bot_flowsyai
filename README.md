# FlowsyAI Telegram Bot 🤖

Un bot Telegram inteligent pentru comunitatea FlowsyAI, integrat cu Google Gemini AI pentru conversații naturale și promovarea FlowsyAI Coin.

## 🚀 Caracteristici

- **Inteligență Artificială**: Folosește Google Gemini 1.5 Flash pentru răspunsuri inteligente
- **Conversații Naturale**: Detectează limba utilizatorului și răspunde în aceeași limbă
- **Promovare Activă**: Promovează comunitatea FlowsyAI și FlowsyAI Coin
- **Comenzi Interactive**: Butoane inline pentru acțiuni rapide
- **Bază de Date**: Stochează utilizatorii și conversațiile
- **Funcții Admin**: Statistici și broadcast pentru administratori
- **Programare Automată**: Tips săptămânale automate

## 📋 Comenzi Disponibile

- `/start` - Pornește conversația cu bot-ul
- `/about` - Informații despre FlowsyAI
- `/features` - Beneficiile grupului FlowsyAI
- `/coin` - Detalii despre FlowsyAI Coin
- `/help` - Lista comenzilor disponibile
- `/stats` - Statistici bot (doar admin)
- `/broadcast` - Trimite mesaj tuturor utilizatorilor (doar admin)

## 🛠️ Instalare și Configurare

### Cerințe
- Python 3.8+
- Cont Telegram Bot (obținut de la @BotFather)
- Google Gemini API Key

### Pași de instalare

1. **Clonează repository-ul**
```bash
git clone https://github.com/robialexz/bot_flowsyai.git
cd bot_flowsyai
```

2. **Instalează dependențele**
```bash
pip install -r requirements.txt
```

3. **Configurează variabilele de mediu**
Creează un fișier `.env` cu:
```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Configurează setările**
Editează `config.ini` cu informațiile tale:
```ini
[telegram]
admin_id = your_telegram_user_id

[app]
group_link = https://t.me/your_group
logo_path = logo.png
db_file = bot_database.db
api_timeout = 20.0
```

5. **Pornește bot-ul**
```bash
python main.py
```

## 🏗️ Structura Proiectului

```
bot_flowsyai/
├── main.py              # Fișierul principal al bot-ului
├── requirements.txt     # Dependențele Python
├── config.ini          # Configurări aplicație
├── logo.png            # Logo-ul FlowsyAI
├── start_bot.bat       # Script Windows pentru pornire
├── stop_bot.bat        # Script Windows pentru oprire
├── check_bot_status.bat # Script Windows pentru verificare status
├── .env                # Variabile de mediu (nu e în Git)
├── bot_database.db     # Baza de date SQLite (nu e în Git)
├── .gitignore          # Fișiere excluse din Git
└── README.md           # Documentația proiectului
```

## 🔧 Management Bot

### Windows Batch Scripts
Pentru utilizatorii Windows, sunt disponibile script-uri simple:

- **`start_bot.bat`** - Pornește bot-ul (dublu-click)
- **`stop_bot.bat`** - Oprește bot-ul (dublu-click)
- **`check_bot_status.bat`** - Verifică statusul bot-ului (dublu-click)

### Funcționalități Tehnice

#### Integrare Gemini AI
- Model: `gemini-1.5-flash`
- Timeout configurat pentru API calls
- Gestionarea erorilor și fallback-uri
- Memorie conversațională (ultimele 10 mesaje)

#### Baza de Date
- SQLite pentru stocare locală
- Tabela `users` pentru tracking utilizatori
- Timestamps pentru prima vizită

#### Securitate
- Validare admin prin user ID
- Escape pentru Markdown V2
- Gestionarea erorilor de parsing

#### Programare Automată
- Tips săptămânale în fiecare joi la 12:00
- JobQueue pentru task-uri programate

## 🎯 FlowsyAI Coin

Bot-ul promovează activ FlowsyAI Coin:
- **Adresa Contract**: `GzfwLWcTyEWcC3D9SeaXQPvfCevjh5xce1iWsPJGpump`
- **Platform**: Solana
- **Cumpărare**: Raydium, Jupiter, DexScreener

## 👥 Contribuții

Contribuțiile sunt binevenite! Te rog să:
1. Faci fork la repository
2. Creezi o branch pentru feature-ul tău
3. Faci commit cu modificările
4. Deschizi un Pull Request

## 📄 Licență

Acest proiect este open source și disponibil sub [MIT License](LICENSE).

## 📞 Contact

- **Telegram**: [@FlowsyAIChat](https://t.me/FlowsyAIChat)
- **GitHub**: [robialexz](https://github.com/robialexz)

---

**Dezvoltat cu ❤️ pentru comunitatea FlowsyAI**