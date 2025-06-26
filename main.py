#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
import aiosqlite
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import google.generativeai as genai
from dotenv import load_dotenv
import configparser

# Load environment variables
load_dotenv()

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ADMIN_ID = int(config.get('telegram', 'admin_id'))
GROUP_LINK = config.get('app', 'group_link')
LOGO_PATH = config.get('app', 'logo_path')
DB_FILE = config.get('app', 'db_file')
API_TIMEOUT = float(config.get('app', 'api_timeout'))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Gemini AI will be configured in main()
model = None

# Initialize conversation history
conversation_history = {}

# Database setup
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def add_user(user_id, username, first_name, last_name):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        await db.commit()

# Helper functions
def escape_markdown_v2(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def send_reply(update: Update, text: str, parse_mode=None, reply_markup=None):
    try:
        if update.message:
            await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=True)
        elif update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error sending reply: {e}")
        try:
            await update.message.reply_text("A apărut o eroare la trimiterea răspunsului.")
        except:
            pass

# --- STATIC MESSAGES ---
WELCOME_MESSAGE = r"*Bun venit la FlowsyAI\!*\n\nSunt asistentul tău virtual, gata să răspund la orice întrebare despre AI sau tehnologie\.\n\nPentru discuții aprofundate și pentru a te conecta cu comunitatea, apasă butonul de mai jos\!"
ABOUT_MESSAGE = r"*Despre FlowsyAI*\n\nFlowsyAI este o comunitate dedicată explorării și dezvoltării inteligenței artificiale\. Misiunea noastră este să creăm un mediu deschis unde oricine poate învăța, colabora și inova\."
FEATURES_MESSAGE = r"*Ce găsești în grupul nostru?*\n\n✅ *Discuții libere:* Vorbim despre cele mai noi trenduri din AI\.\n✅ *Suport:* O comunitate gata să te ajute cu întrebări tehnice\.\n✅ *Resurse exclusive:* Partajăm articole, tutoriale și unelte utile\.\n✅ *Networking:* Conectează\-te cu experți și alți entuziaști din domeniu\."
COIN_ADDRESS = "GzfwLWcTyEWcC3D9SeaXQPvfCevjh5xce1iWsPJGpump"
BUY_LINK = f"https://dexscreener.com/solana/{COIN_ADDRESS}"

COIN_MESSAGE = (
    rf"🚀 *Investește în Viitorul AI cu FlowsyAI Coin\!* 🚀\n\n"
    rf"FlowsyAI Coin este mai mult decât o monedă – este cheia către o comunitate inovatoare care modelează viitorul inteligenței artificiale\. Prin deținerea de \$FLOWSY, susții direct dezvoltarea proiectului și te alături unei mișcări globale\.\n\n"
    rf"✨ *De ce să cumperi acum?*\n"
    rf"\- *Fii parte din revoluție:* Contribuie la un proiect cu potențial uriaș\.\n"
    rf"\- *Acces exclusiv:* Beneficiază de acces la unelte și resurse premium în curând\.\n"
    rf"\- *Creștere exponențială:* Intră devreme într\-un ecosistem cu perspective de creștere pe termen lung\.\n\n"
    rf"👇 *Copiază adresa de mai jos și cumpără acum pe Raydium sau Jupiter\!* 👇\n\n"
    rf"`{COIN_ADDRESS}`"
)

HELP_MESSAGE = r"*Comenzi disponibile:*\n\n/start \- Pornește conversația cu mine\.\n/features \- Află beneficiile grupului nostru\.\n/about \- Citește mai multe despre misiunea FlowsyAI\.\n/coin \- Vezi detalii despre FlowsyAI Coin\.\n/help \- Afișează acest mesaj de ajutor\."

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await add_user(user.id, user.username, user.first_name, user.last_name)
    
    keyboard = [
        [InlineKeyboardButton("🚀 Alătură-te Comunității FlowsyAI", url=GROUP_LINK)],
        [InlineKeyboardButton("💰 Cumpără FlowsyAI Coin", url=BUY_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as logo:
            await update.message.reply_photo(
                photo=logo,
                caption=WELCOME_MESSAGE,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup
            )
    else:
        await send_reply(update, WELCOME_MESSAGE, ParseMode.MARKDOWN_V2, reply_markup)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("🚀 Alătură-te Comunității", url=GROUP_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_reply(update, ABOUT_MESSAGE, ParseMode.MARKDOWN_V2, reply_markup)

async def features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("🚀 Alătură-te Acum", url=GROUP_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_reply(update, FEATURES_MESSAGE, ParseMode.MARKDOWN_V2, reply_markup)

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("💰 Cumpără pe DexScreener", url=BUY_LINK)],
        [InlineKeyboardButton("🚀 Alătură-te Comunității", url=GROUP_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_reply(update, COIN_MESSAGE, ParseMode.MARKDOWN_V2, reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_reply(update, HELP_MESSAGE, ParseMode.MARKDOWN_V2)

# Language detection helper function
def detect_user_language(text: str) -> str:
    """Detect if user message is in Romanian or English"""
    romanian_indicators = ['să', 'și', 'cu', 'de', 'la', 'în', 'pe', 'pentru', 'este', 'sunt', 'ai', 'îmi', 'îți', 'că', 'dacă', 'când', 'unde', 'cum', 'ce', 'cine']
    english_indicators = ['the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'can', 'could', 'should', 'what', 'when', 'where', 'how', 'who']

    text_lower = text.lower()
    romanian_count = sum(1 for word in romanian_indicators if word in text_lower)
    english_count = sum(1 for word in english_indicators if word in text_lower)

    if romanian_count > english_count:
        return 'romanian'
    elif english_count > romanian_count:
        return 'english'
    else:
        # Default to English if unclear
        return 'english'

# AI conversation handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text
    chat_type = update.message.chat.type  # 'private', 'group', 'supergroup', 'channel'

    await add_user(update.effective_user.id, update.effective_user.username,
                   update.effective_user.first_name, update.effective_user.last_name)

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append(f"User: {user_message}")

    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id] = conversation_history[user_id][-10:]

    try:
        context_prompt = "\n".join(conversation_history[user_id][-5:])

        # Determine response language based on chat type
        if chat_type == 'private':
            # Private chat: detect and respond in user's language
            user_language = detect_user_language(user_message)
            if user_language == 'romanian':
                language_instruction = "Răspunde EXCLUSIV în limba română."
                error_message = "Îmi pare rău, am întâmpinat o problemă tehnică. Te rog încearcă din nou."
                keyboard_text = ["🚀 Alătură-te Comunității FlowsyAI", "💰 Cumpără FlowsyAI Coin"]
            else:
                language_instruction = "Respond EXCLUSIVELY in English."
                error_message = "I'm sorry, I encountered a technical problem. Please try again."
                keyboard_text = ["🚀 Join FlowsyAI Community", "💰 Buy FlowsyAI Coin"]
        else:
            # Group chat: always respond in English
            language_instruction = "Respond EXCLUSIVELY in English, regardless of what language the user writes in."
            error_message = "I'm sorry, I encountered a technical problem. Please try again."
            keyboard_text = ["🚀 Join FlowsyAI Community", "💰 Buy FlowsyAI Coin"]

        system_prompt = f"""You are FlowsyAI, a friendly and intelligent AI assistant for the FlowsyAI community.

{language_instruction}

Subtly promote the FlowsyAI community and FlowsyAI Coin when relevant, but don't be pushy.

FlowsyAI Information:
- It's a community dedicated to AI and technology
- FlowsyAI Coin ($FLOWSY) is the community token
- Contract address: {COIN_ADDRESS}
- Group link: {GROUP_LINK}

Recent conversation:
{context_prompt}

Respond helpfully and friendly to the user's latest question."""

        response = model.generate_content(system_prompt)
        ai_response = response.text

        conversation_history[user_id].append(f"FlowsyAI: {ai_response}")

        keyboard = [
            [InlineKeyboardButton(keyboard_text[0], url=GROUP_LINK)],
            [InlineKeyboardButton(keyboard_text[1], url=BUY_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await send_reply(update, ai_response, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        await send_reply(update, error_message)

# Admin commands
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await send_reply(update, r"Nu ai permisiunea pentru această comandă\.")
        return
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        total_users = (await cursor.fetchone())[0]
    await send_reply(update, f"*Statistici Bot*\n\nTotal utilizatori unici: *{total_users}*", parse_mode=ParseMode.MARKDOWN_V2)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await send_reply(update, r"Nu ai permisiunea pentru această comandă\.")
        return
    message_to_send = " ".join(context.args)
    if not message_to_send:
        await send_reply(update, r"Te rog specifică un mesaj\. Exemplu: `/broadcast Salutare tuturor\!`", parse_mode=ParseMode.MARKDOWN_V2)
        return

    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        user_ids = await cursor.fetchall()

    tasks = [context.bot.send_message(user_id[0], message_to_send, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True) for user_id in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    sent_count = sum(1 for r in results if not isinstance(r, Exception))
    failed_count = len(results) - sent_count

    await send_reply(update, rf"*Broadcast Terminat*\n\nMesaj trimis către *{sent_count}* utilizatori\.\nEșuat pentru *{failed_count}* utilizatori\.", parse_mode=ParseMode.MARKDOWN_V2)

async def weekly_tip(context: ContextTypes.DEFAULT_TYPE):
    tip_message = rf"*Sfatul Săptămânii de la Flowsy* 💡\n\nȘtiai că poți folosi modele AI pentru a-ți genera idei de proiecte noi? Încearcă să-i ceri lui Gemini: `sugerează-mi 3 idei de aplicații web care folosesc Python și recunoaștere de imagini`\.\n\nHai pe [grupul nostru]({GROUP_LINK}) să ne arăți ce ai creat\!"
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        user_ids = await cursor.fetchall()
    
    logger.info(f"Sending weekly tip to {len(user_ids)} users.")
    tasks = [context.bot.send_message(user_id[0], tip_message, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True) for user_id in user_ids]
    await asyncio.gather(*tasks, return_exceptions=True)

def main() -> None:
    # Configure Gemini AI
    genai.configure(api_key=GEMINI_API_KEY)
    global model
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini model 'gemini-1.5-flash' initialized.")

    # Initialize database
    asyncio.run(init_db())
    logger.info("Database initialized successfully.")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("features", features))
    application.add_handler(CommandHandler("coin", coin))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule weekly tips
    job_queue = application.job_queue
    job_queue.run_repeating(weekly_tip, interval=timedelta(weeks=1), first=timedelta(seconds=10))

    logger.info("Starting bot...")

    # Fix for Python 3.13+ compatibility
    try:
        application.run_polling()
    except RuntimeError as e:
        if "There is no current event loop" in str(e):
            # Create new event loop for Python 3.13+
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            application.run_polling()
        else:
            raise

if __name__ == '__main__':
    main()
