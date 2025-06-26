import asyncio
import httpx
import google.generativeai as genai
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .config import (
    logger, GEMINI_API_KEY, SYSTEM_PROMPT, API_TIMEOUT, 
    GROUP_LINK, LOGO_PATH, WELCOME_MESSAGE, ABOUT_MESSAGE, 
    FEATURES_MESSAGE, COIN_MESSAGE, HELP_MESSAGE, BUY_LINK, ADMIN_ID, DB_FILE, CHAT_ID
)
from .database import (
    update_user_in_db, create_price_alert, get_user_alerts, delete_alert, get_all_active_alerts,
    add_celebration_media, get_random_celebration_media, delete_celebration_media
)
import aiosqlite

# --- API CLIENT --- 
async def get_crypto_price(symbol: str) -> float | None:
    """Fetches the current price of a cryptocurrency from CoinGecko."""
    # CoinGecko uses IDs, not symbols. We need a mapping for common coins.
    # This can be expanded or moved to a config file.
    symbol_to_id = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        # Add other popular coins here
    }
    coin_id = symbol_to_id.get(symbol.upper())
    if not coin_id:
        return None # Symbol not supported

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            price = data.get(coin_id, {}).get('usd')
            return float(price) if price else None
    except (httpx.RequestError, ValueError, KeyError) as e:
        logger.error(f"CoinGecko API request failed for {symbol}: {e}")
        return None

# --- GEMINI INITIALIZATION ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini model 'gemini-1.5-flash' initialized.")
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {e}")
    gemini_model = None

# --- HELPERS ---
def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def send_reply(update: Update, text: str, markup=None, parse_mode=None):
    try:
        escaped_text = escape_markdown_v2(text) if parse_mode == ParseMode.MARKDOWN_V2 else text
        reply_target = update.callback_query.message if hasattr(update, 'callback_query') and update.callback_query else update.message
        if not reply_target:
            logger.error("Could not determine a valid reply target.")
            return
        await reply_target.reply_text(escaped_text, parse_mode=parse_mode, reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Failed to send message to {update.effective_chat.id}: {e}")
        if "Can't parse entities" in str(e):
            logger.warning("Markdown parse failed. Sending as plain text.")
            try:
                await reply_target.reply_text(text, reply_markup=markup, disable_web_page_preview=True)
            except Exception as fallback_e:
                logger.error(f"Fallback plain text send also failed: {fallback_e}")

# --- COMMAND HANDLERS ---
async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("💰 Cumpără FlowsyAI Coin Acum", url=BUY_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_reply(update, COIN_MESSAGE, markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update_user_in_db(update.effective_user)
    keyboard = [[InlineKeyboardButton("🚀 Alătură-te comunității FlowsyAI", url=GROUP_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(LOGO_PATH, 'rb'), caption=WELCOME_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"Sending photo failed: {e}. Sending text-only welcome.")
        await send_reply(update, WELCOME_MESSAGE, markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update_user_in_db(update.effective_user)
    await send_reply(update, ABOUT_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2)

async def features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update_user_in_db(update.effective_user)
    await send_reply(update, FEATURES_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update_user_in_db(update.effective_user)
    await send_reply(update, HELP_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2)

# --- MESSAGE HANDLER ---
async def generate_command_from_instruction(update: Update, context: ContextTypes.DEFAULT_TYPE, instruction: str) -> None:
    """Generează o nouă comandă bazată pe instrucțiunile în limbaj natural ale administratorului."""
    try:
        # Prompt special pentru Gemini pentru a genera codul comenzii
        command_prompt = f"""
        Creează o comandă nouă pentru un bot Telegram bazată pe următoarea instrucțiune:
        \"{instruction}\".

        Răspunde cu codul Python pentru comandă, urmând aceste reguli:
        1. Folosește async/await pentru operații asincrone
        2. Folosește tipurile Update și ContextTypes.DEFAULT_TYPE ca parametri
        3. Include gestionarea erorilor cu try/except
        4. Adaugă comentarii explicative în română
        5. Folosește funcția send_reply pentru răspunsuri
        6. Respectă formatul Markdown v2 pentru mesaje

        Exemplu de format:
        ```python
        async def nume_comanda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            # Descriere în română
            try:
                # Logica comenzii
                await send_reply(update, "Răspuns formatat")
            except Exception as e:
                logger.error(f"Eroare: {e}")
                await send_reply(update, "Mesaj de eroare")
        ```
        """

        # Generează codul comenzii folosind Gemini
        response = await asyncio.wait_for(
            asyncio.to_thread(gemini_model.generate_content, command_prompt),
            timeout=API_TIMEOUT
        )

        if not response.text:
            raise ValueError("API-ul nu a returnat niciun răspuns")

        # Extrage codul Python din răspuns
        code_match = re.search(r'```python\n(.+?)```', response.text, re.DOTALL)
        if not code_match:
            await send_reply(update, "Nu am putut genera codul comenzii\. Te rog reformulează instrucțiunea\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        command_code = code_match.group(1).strip()

        # Extrage numele funcției din cod
        func_name_match = re.search(r'async def ([a-zA-Z_][a-zA-Z0-9_]*)', command_code)
        if not func_name_match:
            await send_reply(update, "Nu am putut identifica numele comenzii\. Te rog reformulează instrucțiunea\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        command_name = func_name_match.group(1)

        # Salvează codul în fișierul de comenzi generate
        commands_file = os.path.join(os.path.dirname(__file__), 'generated_commands.py')
        
        # Verifică dacă fișierul există și citește conținutul existent
        existing_content = ""
        if os.path.exists(commands_file):
            with open(commands_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # Adaugă importurile necesare dacă fișierul este nou
        if not existing_content:
            existing_content = """from telegram import Update, ParseMode
from telegram.ext import ContextTypes
from .config import logger
from .handlers import send_reply

"""

        # Adaugă noua comandă la sfârșitul fișierului
        with open(commands_file, 'w', encoding='utf-8') as f:
            f.write(existing_content)
            if not existing_content.endswith('\n\n'):
                f.write('\n\n')
            f.write(command_code)

        # Trimite confirmarea către admin
        await send_reply(
            update,
            f"Am creat comanda nouă `/{command_name}`\. "
            f"Pentru a o activa, trebuie să:\n"
            f"1\. Adaugi în main\.py:\n"
            f"```python\n"
            f"from \.generated_commands import {command_name}\n"
            f"application\.add_handler\(CommandHandler\('{command_name}', {command_name}\)\)\n"
            f"```\n"
            f"2\. Repornești botul\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    except asyncio.TimeoutError:
        logger.error(f"Generarea comenzii a expirat după {API_TIMEOUT} secunde.")
        await send_reply(update, "Generarea comenzii a durat prea mult\. Te rog încearcă din nou\.", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Eroare la generarea comenzii: {e}")
        await send_reply(update, "A apărut o eroare la generarea comenzii\. Te rog încearcă din nou\.", parse_mode=ParseMode.MARKDOWN_V2)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    # Verifică dacă utilizatorul este admin și dacă mesajul este o comandă în limbaj natural
    if user.id == ADMIN_ID and update.message.text.lower().startswith("flowsy adaugă comanda"):
        instruction = update.message.text[len("flowsy adaugă comanda"):].strip()
        await generate_command_from_instruction(update, context, instruction)
        return

    message = update.message
    chat_type = message.chat.type

    # In a group, only respond if mentioned.
    if chat_type in ['group', 'supergroup']:
        bot_username = (await context.bot.get_me()).username
        if not (message.text and f'@{bot_username}' in message.text):
            return

    await update_user_in_db(user)

    if not gemini_model:
        await send_reply(update, "Serviciul de inteligență artificială nu este disponibil momentan.")
        return

    await context.bot.send_chat_action(chat_id=user.id, action='TYPING')

    try:
        if 'history' not in context.user_data:
            context.user_data['history'] = []

        history = context.user_data['history']
        history.append(f"User: {message.text}")
        context.user_data['history'] = history[-10:]

        conversation_history = "\n".join(history)
        full_prompt = f"{SYSTEM_PROMPT}\n\n---\n\nCONVERSATION HISTORY:\n{conversation_history}"
        
        response = await asyncio.wait_for(
            asyncio.to_thread(gemini_model.generate_content, full_prompt),
            timeout=API_TIMEOUT
        )
        
        if not response.text:
            raise ValueError("API returned an empty response")

        ai_response = response.text
        context.user_data['history'].append(f"Flowsy: {ai_response}")

    except asyncio.TimeoutError:
        logger.error(f"Gemini API call timed out after {API_TIMEOUT} seconds.")
        await send_reply(update, "Serviciul AI a durat prea mult pentru a răspunde. Te rog încearcă din nou.")
        return
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        await send_reply(update, "Am întâmpinat o eroare tehnică. Te rog să încerci din nou peste câteva momente.")
        return

    keyboard = [
        [InlineKeyboardButton("🚀 Alătură-te comunității", url=GROUP_LINK)],
        [InlineKeyboardButton("💰 Cumpără FlowsyAI Coin", url=BUY_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_reply(update, ai_response, markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

# --- ADMIN & SCHEDULED FUNCTIONS ---
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

async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /alerta command for setting price alerts."""
    try:
        if not context.args or len(context.args) != 3:
            await send_reply(
                update,
                r"Format invalid\. Folosește: `/alerta SIMBOL PREȚ peste/sub`\. Exemplu: `/alerta BTC 65000 peste`",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        symbol, price_str, direction = context.args
        symbol = symbol.upper()
        direction = direction.lower()

        if direction not in ['peste', 'sub']:
            await send_reply(update, r"Direcția trebuie să fie 'peste' sau 'sub'\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        try:
            target_price = float(price_str)
        except ValueError:
            await send_reply(update, r"Prețul trebuie să fie un număr valid\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        current_price = await get_crypto_price(symbol)
        if current_price is None:
            await send_reply(
                update,
                r"Simbolul nu este suportat sau a apărut o eroare la obținerea prețului\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        alert_id = await create_price_alert(
            user_id=update.effective_user.id,
            symbol=symbol,
            target_price=target_price,
            direction=direction
        )

        await send_reply(
            update,
            f"Alertă creată cu succes\! Vei fi notificat când prețul {symbol} va fi {direction} {target_price} USD\. Preț curent: {current_price} USD\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        logger.error(f"Error in alert_command: {e}")
        await send_reply(update, r"A apărut o eroare la crearea alertei\. Te rog încearcă din nou\.", parse_mode=ParseMode.MARKDOWN_V2)

async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows all active alerts for the user."""
    try:
        alerts = await get_user_alerts(update.effective_user.id)
        if not alerts:
            await send_reply(update, r"Nu ai nicio alertă activă\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        message = "*Alertele tale active:*\n\n"
        for alert_id, symbol, target_price, direction in alerts:
            current_price = await get_crypto_price(symbol)
            price_info = f"\(preț curent: {current_price} USD\)" if current_price else ""
            message += f"ID: `{alert_id}` \- {symbol} {direction} {target_price} USD {price_info}\n"

        message += "\n_Pentru a șterge o alertă, folosește_ `/stergealerta ID`"
        await send_reply(update, message, parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        logger.error(f"Error in alerts_command: {e}")
        await send_reply(update, r"A apărut o eroare la afișarea alertelor\.", parse_mode=ParseMode.MARKDOWN_V2)

async def delete_alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes a price alert by ID."""
    try:
        if not context.args or len(context.args) != 1:
            await send_reply(
                update,
                r"Format invalid\. Folosește: `/stergealerta ID`\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        try:
            alert_id = int(context.args[0])
        except ValueError:
            await send_reply(update, r"ID\-ul alertei trebuie să fie un număr\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        success = await delete_alert(alert_id, update.effective_user.id)
        if success:
            await send_reply(update, r"Alerta a fost ștearsă cu succes\.", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await send_reply(update, r"Nu am găsit o alertă cu acest ID\.", parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        logger.error(f"Error in delete_alert_command: {e}")
        await send_reply(update, r"A apărut o eroare la ștergerea alertei\.", parse_mode=ParseMode.MARKDOWN_V2)

async def send_celebration(context: ContextTypes.DEFAULT_TYPE, category: str, chat_id: int) -> None:
    """Trimite un media de celebrare aleatoriu pentru o categorie specifică."""
    try:
        media = await get_random_celebration_media(category)
        if not media:
            logger.warning(f"No celebration media found for category: {category}")
            return

        media_type, file_id, message = media
        if message:
            message = escape_markdown_v2(message)

        if media_type == 'sticker':
            await context.bot.send_sticker(chat_id=chat_id, sticker=file_id)
            if message:
                await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
        elif media_type in ['gif', 'animation']:
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=file_id,
                caption=message if message else None,
                parse_mode=ParseMode.MARKDOWN_V2 if message else None
            )
    except Exception as e:
        logger.error(f"Error sending celebration: {e}")

async def add_celebration_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adaugă un nou media de celebrare în baza de date."""
    if update.effective_user.id != ADMIN_ID:
        await send_reply(update, r"Nu ai permisiunea pentru această comandă\.")
        return

    try:
        # Verifică dacă mesajul este un reply la un sticker sau gif
        if not update.message.reply_to_message:
            await send_reply(
                update,
                r"Folosește această comandă ca răspuns la un sticker sau GIF\. Sintaxă: `/addcelebration categorie \[mesaj\]`\."
                r"\n\nCategorii disponibile: buy, price\_up, milestone",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        if not context.args:
            await send_reply(update, r"Te rog specifică categoria media\-ului\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        category = context.args[0].lower()
        if category not in ['buy', 'price_up', 'milestone']:
            await send_reply(update, r"Categorie invalidă\. Folosește: buy, price\_up, sau milestone\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        message = " ".join(context.args[1:]) if len(context.args) > 1 else None
        reply_msg = update.message.reply_to_message

        if reply_msg.sticker:
            media_type = 'sticker'
            file_id = reply_msg.sticker.file_id
        elif reply_msg.animation:
            media_type = 'animation'
            file_id = reply_msg.animation.file_id
        else:
            await send_reply(update, r"Te rog răspunde la un sticker sau GIF\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        media_id = await add_celebration_media(media_type, file_id, category, message)
        await send_reply(
            update,
            f"Media de celebrare adăugat cu succes\! ID: `{media_id}`\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        logger.error(f"Error in add_celebration_command: {e}")
        await send_reply(update, r"A apărut o eroare la adăugarea media\-ului\.", parse_mode=ParseMode.MARKDOWN_V2)

async def delete_celebration_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Șterge un media de celebrare din baza de date."""
    if update.effective_user.id != ADMIN_ID:
        await send_reply(update, r"Nu ai permisiunea pentru această comandă\.")
        return

    try:
        if not context.args or len(context.args) != 1:
            await send_reply(
                update,
                r"Format invalid\. Folosește: `/deletecelebration ID`\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        try:
            media_id = int(context.args[0])
        except ValueError:
            await send_reply(update, r"ID\-ul trebuie să fie un număr\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        success = await delete_celebration_media(media_id)
        if success:
            await send_reply(update, r"Media de celebrare a fost șters cu succes\.", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await send_reply(update, r"Nu am găsit un media cu acest ID\.", parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        logger.error(f"Error in delete_celebration_command: {e}")
        await send_reply(update, r"A apărut o eroare la ștergerea media\-ului\.", parse_mode=ParseMode.MARKDOWN_V2)

async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks all active alerts and notifies users when conditions are met."""
    try:
        alerts = await get_all_active_alerts()
        for alert_id, user_id, symbol, target_price, direction in alerts:
            current_price = await get_crypto_price(symbol)
            if current_price is None:
                continue

            condition_met = False
            celebration_category = None

            if direction == 'peste' and current_price >= target_price:
                condition_met = True
                celebration_category = 'price_up'
                message = f"🚀 *Alertă de preț!*\n\nPrețul {symbol} a ajuns la {current_price} USD, peste ținta de {target_price} USD\!"
            elif direction == 'sub' and current_price <= target_price:
                condition_met = True
                message = f"📉 *Alertă de preț!*\n\nPrețul {symbol} a scăzut la {current_price} USD, sub ținta de {target_price} USD\!"

            if condition_met:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                    if celebration_category:
                        await send_celebration(context, celebration_category, user_id)
                    await delete_alert(alert_id, user_id)
                except Exception as e:
                    logger.error(f"Failed to send alert notification to user {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error in check_alerts: {e}")

async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # E.g., /sondaj "Intrebare?" "Opt1" "Opt2"
        args = context.args
        if len(args) < 3:
            await send_reply(update, r"""Format invalid\. Te rog folosește: `/sondaj "Întrebare" "Opțiune 1" "Opțiune 2" \.\.\.`""", parse_mode=ParseMode.MARKDOWN_V2)
            return

        # Extrage argumentele
        text = update.message.text
        # Găsește toate string-urile dintre ghilimele
        import re
        parts = re.findall(r'"(.*?)"', text)
        
        if len(parts) < 3:
            await send_reply(update, r"""Format invalid\. Asigură-te că atât întrebarea, cât și opțiunile sunt între ghilimele\. Exemplu: `/sondaj "Ce preferi?" "Cafea" "Ceai"`""", parse_mode=ParseMode.MARKDOWN_V2)
            return

        question = parts[0]
        options = parts[1:]

        if len(options) > 10:
            await send_reply(update, r"Poți avea maxim 10 opțiuni pentru un sondaj\.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            is_anonymous=False,  # Sondajele nu vor fi anonime
            allows_multiple_answers=False
        )
    except Exception as e:
        logger.error(f"Failed to create poll: {e}")
        await send_reply(update, r"A apărut o eroare la crearea sondajului\. Te rog încearcă din nou\.", parse_mode=ParseMode.MARKDOWN_V2)

async def weekly_tip(context: ContextTypes.DEFAULT_TYPE):
    tip_message = rf"*Sfatul Săptămânii de la Flowsy* 💡\n\nȘtiai că poți folosi modele AI pentru a-ți genera idei de proiecte noi? Încearcă să-i ceri lui Gemini: `sugerează-mi 3 idei de aplicații web care folosesc Python și recunoaștere de imagini`\.\n\nHai pe [grupul nostru]({GROUP_LINK}) să ne arăți ce ai creat\!"
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        user_ids = await cursor.fetchall()
    
    logger.info(f"Sending weekly tip to {len(user_ids)} users.")
    tasks = [context.bot.send_message(user_id[0], tip_message, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True) for user_id in user_ids]
    await asyncio.gather(*tasks, return_exceptions=True)