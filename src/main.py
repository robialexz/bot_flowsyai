import asyncio
import sys
import os
import importlib
from datetime import time
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .blockchain import SolanaMonitor

from .config import TOKEN, logger, SOLANA_WS_URL, FLOWSY_TOKEN_MINT, CHAT_ID
from .database import setup_database
from .handlers import (
    start, about, features, help_command, coin, stats, broadcast, poll_command,
    handle_message, weekly_tip, alert_command, alerts_command, delete_alert_command, check_alerts,
    add_celebration_command, delete_celebration_command
)

async def handle_solana_transaction(transaction_data):
    """Procesează o tranzacție Solana și trimite o celebrare dacă este o achiziție."""
    try:
        logs = transaction_data.get('value', {}).get('logs', [])
        # Verifică dacă este o tranzacție de transfer
        is_buy = any("Instruction: Transfer" in log for log in logs)
        
        if is_buy:
            logger.info("Detected Flowsy token purchase, sending celebration")
            # Trimite celebrarea în grupul principal
            # Notă: Contextul aplicației este disponibil global
            await send_celebration(app, 'buy', CHAT_ID)
    except Exception as e:
        logger.error(f"Error processing Solana transaction for celebration: {e}")

async def main() -> None:
    await setup_database()
    global app  # Folosim o variabilă globală pentru a accesa aplicația în callback-ul Solana
    app = Application.builder().token(TOKEN).build()

    # Încarcă și înregistrează comenzile generate dinamic
    generated_commands_file = os.path.join(os.path.dirname(__file__), 'generated_commands.py')
    if os.path.exists(generated_commands_file):
        try:
            spec = importlib.util.spec_from_file_location("generated_commands", generated_commands_file)
            generated_commands = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generated_commands)

            for name, func in generated_commands.__dict__.items():
                if asyncio.iscoroutinefunction(func) and not name.startswith("__"):
                    command_name = name.replace('_command', '')
                    app.add_handler(CommandHandler(command_name, func))
                    logger.info(f"Loaded generated command: /{command_name}")
        except Exception as e:
            logger.error(f"Failed to load generated commands: {e}")

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("features", features))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("sondaj", poll_command))
    app.add_handler(CommandHandler("alerta", alert_command))
    app.add_handler(CommandHandler("alerte", alerts_command))
    app.add_handler(CommandHandler("stergealerta", delete_alert_command))
    app.add_handler(CommandHandler("addcelebration", add_celebration_command))
    app.add_handler(CommandHandler("deletecelebration", delete_celebration_command))

    # Register message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register scheduled jobs
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_daily(weekly_tip, time=time(hour=9, minute=0), days=(0,)) # Monday at 9:00 AM

        # Schedule alert checks
        job_queue.run_repeating(check_alerts, interval=60, first=10)

    # Configurează și pornește monitorul Solana
    solana_monitor = SolanaMonitor(
        ws_url=SOLANA_WS_URL,
        token_mint_address=FLOWSY_TOKEN_MINT,
        transaction_callback=handle_solana_transaction
    )

    logger.info("Starting bot and Solana monitor...")
    async with app:
        await app.start()
        await app.updater.start_polling()
        
        # Pornește monitorizarea Solana într-un task separat
        monitor_task = asyncio.create_task(solana_monitor.start())
        
        # Așteaptă la infinit
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("Stopping Solana monitor...")
            await solana_monitor.stop()
            await monitor_task