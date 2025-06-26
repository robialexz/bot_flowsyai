import os
import logging
import configparser
from dotenv import load_dotenv

# --- CONFIGURATION ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- API KEYS & TOKENS ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
FLOWSY_TOKEN_MINT = os.getenv('FLOWSY_TOKEN_MINT', 'GzfwLWcTyEWcC3D9SeaXQPvfCevjh5xce1iWsPJGpump')

# --- TELEGRAM SETTINGS ---
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
CHAT_ID = int(os.getenv('CHAT_ID', '0'))
GROUP_LINK = os.getenv('GROUP_LINK', '')

# --- APP SETTINGS ---
LOGO_PATH = os.getenv('LOGO_PATH', 'logo.png')
DB_FILE = os.getenv('DB_FILE', 'bot_data.db')
API_TIMEOUT = float(os.getenv('API_TIMEOUT', '30.0'))

# --- SOLANA SETUP ---
SOLANA_WS_URL = os.getenv('SOLANA_WS_URL', 'wss://api.mainnet-beta.solana.com')

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

HELP_MESSAGE = r'''*Comenzi disponibile:*

*Comenzi Generale:*
/start \- Pornește conversația cu mine\.
/features \- Află beneficiile grupului nostru\.
/about \- Citește mai multe despre misiunea FlowsyAI\.
/help \- Afișează acest mesaj de ajutor\.

*Funcționalități Crypto:*
/coin <simbol> \- Verifică prețul unei criptomonede\. Exemplu: `/coin btc`
/alerta <simbol> <peste/sub> <preț> \- Setează o alertă de preț\. Exemplu: `/alerta btc peste 50000`
/alerte \- Vezi alertele active\.
/stergealerta <ID> \- Șterge o alertă după ID\.

*Sondaje:*
/sondaj <întrebare> "<opțiune1>" "<opțiune2>" ... \- Creează un sondaj\.

*Comenzi Admin:*
/addcelebration <categorie> [mesaj] \- Adaugă un media de celebrare \(răspunde la un GIF/sticker\)\. Categorii: `buy`, `price_up`, `milestone`
/deletecelebration <ID> \- Șterge un media de celebrare\.'''

# --- GEMINI & PERSONALITY SETUP ---
SYSTEM_PROMPT = (
    "You are Flowsy, the AI assistant for the FlowsyAI project. Your tone is friendly, helpful, and enthusiastic about AI and the FlowsyAI community."
    "FlowsyAI is a community for developing AI, with its own cryptocurrency, FlowsyAI Coin."
    
    "**Core Directives:**"
    "1. **Language Match:** Detect the user's language and respond ONLY in that language."
    "2. **Promote Actively:** Your primary goal is to encourage users to join the community and learn about the FlowsyAI Coin. When relevant, you MUST provide the coin address: GzfwLWcTyEWcC3D9SeaXQPvfCevjh5xce1iWsPJGpump. Naturally integrate mentions of the community, Telegram group, and the coin's benefits into your responses."
    "3. **Handle Greetings Naturally:** For simple greetings ('hi', 'salut', etc.), respond with a warm, brief greeting and do not generate follow-up questions. You can add a small, engaging fact about FlowsyAI. Example: 'Salut! Ce mai faci? Comunitatea noastră e în plină expansiune!'"
    "4. **Project Context:** When asked about 'this project', assume they mean FlowsyAI. Be positive and informative about its mission and coin."
    "5. **Be Concise:** Keep answers helpful and to the point, but friendly."
)