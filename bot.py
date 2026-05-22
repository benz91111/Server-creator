"""
Server Creator Pro v2.0 - Bot avancado para criacao de servidores Discord
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import os
import logging
import aiosqlite
import aiohttp
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Carregar variaveis de ambiente
load_dotenv()

# Carregar configuracoes
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# Cores do bot
COLORS = {
    "primary": discord.Color(CONFIG["colors"]["primary"]),
    "success": discord.Color(CONFIG["colors"]["success"]),
    "warning": discord.Color(CONFIG["colors"]["warning"]),
    "error": discord.Color(CONFIG["colors"]["error"]),
    "info": discord.Color(CONFIG["colors"]["info"]),
}

# Emojis
EMOJIS = CONFIG["emojis"]

# Muda de "logs" para "bot_logs"
for folder in ["bot_logs", "bot_databases", "bot_assets", "bot_templates", "bot_backups"]:
    if os.path.exists(folder) and not os.path.isdir(folder):
        os.remove(folder)
    os.makedirs(folder, exist_ok=True)


# Configuracao de logging
log_file = os.path.join("bot_logs", "bot.log")
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ServerCreator")

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Bot
class ServerCreatorBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=CONFIG["bot"]["prefix"],
            intents=intents,
            help_command=None
        )
        self.db_path = "bot_databases/server_creator.db"
        self.templates_cache = {}
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        await self.init_database()
        await self.load_templates()
        await self.tree.sync()
        logger.info(f"Bot {CONFIG['bot']['name']} v{CONFIG['bot']['version']} iniciado!")

    async def init_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    user_id TEXT,
                    theme TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    channels_count INTEGER,
                    roles_count INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    user_id TEXT,
                    backup_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    name TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    theme TEXT,
                    data TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    user_id TEXT,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()

    async def load_templates(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT name, data FROM templates") as cursor:
                async for row in cursor:
                    self.templates_cache[row[0]] = json.loads(row[1])

    async def log_action(self, guild_id, user_id, action, details=""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO logs (guild_id, user_id, action, details) VALUES (?, ?, ?, ?)",
                (str(guild_id), str(user_id), action, details)
            )
            await db.commit()
        logger.info(f"[{guild_id}] {action} by {user_id}: {details}")

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

bot = ServerCreatorBot()

# =============================================================================
# SISTEMA DE TEMAS - 30+ TEMAS PRONTOS
# =============================================================================

THEMES = {
    "anime": {
        "name": "Anime",
        "description": "Servidor tematico de anime e cultura japonesa",
        "color": 0xFF6B9D,
        "icon": "🎌",
        "roles": [
            {"name": "👑 Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "🛡️ Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "⚔️ Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "🎨 Designer", "color": 0xFF69B4, "hoist": True},
            {"name": "📝 Tradutor", "color": 0x9370DB, "hoist": True},
            {"name": "⭐ VIP", "color": 0xFFD700, "hoist": True},
            {"name": "🎭 Cosplayer", "color": 0xFF1493, "hoist": True},
            {"name": "📺 Otaku", "color": 0x00CED1, "hoist": False},
            {"name": "🎮 Gamer", "color": 0x32CD32, "hoist": False},
            {"name": "🎵 Musico", "color": 0xFF6347, "hoist": False},
            {"name": "📚 Leitor", "color": 0x8B4513, "hoist": False},
            {"name": "🆕 Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "📢 INFORMACOES",
                "channels": [
                    {"name": "📢-anuncios", "type": "announcement"},
                    {"name": "📋-regras", "type": "text"},
                    {"name": "🎉-boas-vindas", "type": "text"},
                    {"name": "📰-noticias-anime", "type": "text"},
                    {"name": "🗳️-votacoes", "type": "text"},
                ]
            },
            {
                "name": "💬 GERAL",
                "channels": [
                    {"name": "💬-chat-geral", "type": "text"},
                    {"name": "🎭-cosplay", "type": "text"},
                    {"name": "🎨-fanarts", "type": "text"},
                    {"name": "📸-memes", "type": "text"},
                    {"name": "🎵-musica", "type": "text"},
                    {"name": "🎙️-geral", "type": "voice"},
                    {"name": "🎙️-musica", "type": "voice"},
                ]
            },
            {
                "name": "🎌 ANIME",
                "channels": [
                    {"name": "📺-recomendacoes", "type": "text"},
                    {"name": "💬-discussao", "type": "text"},
                    {"name": "📖-manga", "type": "text"},
                    {"name": "🎬-filmes", "type": "text"},
                    {"name": "🔥-spoilers", "type": "text", "slowmode": 60},
                    {"name": "🎙️-anime-talk", "type": "voice"},
                ]
            },
            {
                "name": "🎮 GAMING",
                "channels": [
                    {"name": "🎮-games", "type": "text"},
                    {"name": "🏆-ranking", "type": "text"},
                    {"name": "🎁-sorteios", "type": "text"},
                    {"name": "🎙️-gaming-voice", "type": "voice"},
                    {"name": "🎙️-party", "type": "voice"},
                ]
            },
            {
                "name": "🔧 SUPORTE",
                "channels": [
                    {"name": "❓-ajuda", "type": "text"},
                    {"name": "🐛-bugs", "type": "text"},
                    {"name": "💡-sugestoes", "type": "text"},
                    {"name": "🎙️-suporte-voz", "type": "voice"},
                ]
            },
        ],
        "emojis": ["🎌", "⭐", "🔥", "💎", "🌸", "⚡", "🎭", "🎨"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "gaming": {
        "name": "Gaming",
        "description": "Servidor para gamers e comunidades de jogos",
        "color": 0x5865F2,
        "icon": "🎮",
        "roles": [
            {"name": "👑 Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "🛡️ Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "⚔️ Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "🏆 Pro Player", "color": 0xFFD700, "hoist": True},
            {"name": "🎯 Streamer", "color": 0x9146FF, "hoist": True},
            {"name": "🎨 Designer", "color": 0xFF69B4, "hoist": True},
            {"name": "💎 VIP", "color": 0x00FFFF, "hoist": True},
            {"name": "🎮 Gamer", "color": 0x32CD32, "hoist": False},
            {"name": "🔫 FPS", "color": 0xFF4500, "hoist": False},
            {"name": "⚔️ Moba", "color": 0x8A2BE2, "hoist": False},
            {"name": "🧩 Puzzle", "color": 0x20B2AA, "hoist": False},
            {"name": "🆕 Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "📢 INFORMACOES",
                "channels": [
                    {"name": "📢-anuncios", "type": "announcement"},
                    {"name": "📋-regras", "type": "text"},
                    {"name": "🎉-boas-vindas", "type": "text"},
                    {"name": "📅-eventos", "type": "text"},
                    {"name": "🏆-torneios", "type": "text"},
                ]
            },
            {
                "name": "💬 GERAL",
                "channels": [
                    {"name": "💬-chat-geral", "type": "text"},
                    {"name": "🎭-memes", "type": "text"},
                    {"name": "🎵-musica", "type": "text"},
                    {"name": "📸-screenshots", "type": "text"},
                    {"name": "🎙️-lobby", "type": "voice"},
                    {"name": "🎙️-musica", "type": "voice"},
                ]
            },
            {
                "name": "🎮 JOGOS",
                "channels": [
                    {"name": "🎯-fps", "type": "text"},
                    {"name": "⚔️-moba", "type": "text"},
                    {"name": "🏰-rpg", "type": "text"},
                    {"name": "🧩-casual", "type": "text"},
                    {"name": "🎁-sorteios", "type": "text"},
                    {"name": "🎙️-squad-1", "type": "voice"},
                    {"name": "🎙️-squad-2", "type": "voice"},
                    {"name": "🎙️-squad-3", "type": "voice"},
                ]
            },
            {
                "name": "🏆 COMPETITIVO",
                "channels": [
                    {"name": "📊-ranking", "type": "text"},
                    {"name": "🏅-campeonatos", "type": "text"},
                    {"name": "🤝-procurando-time", "type": "text"},
                    {"name": "🎙️-scrims", "type": "voice"},
                    {"name": "🎙️-review", "type": "voice"},
                ]
            },
            {
                "name": "🔧 SUPORTE",
                "channels": [
                    {"name": "❓-ajuda", "type": "text"},
                    {"name": "🐛-bugs", "type": "text"},
                    {"name": "💡-sugestoes", "type": "text"},
                    {"name": "🎙️-suporte-voz", "type": "voice"},
                ]
            },
        ],
        "emojis": ["🎮", "🏆", "⚡", "🔥", "💎", "🎯", "⚔️", "🛡️"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "minecraft": {
        "name": "Minecraft",
        "description": "Servidor dedicado ao universo Minecraft",
        "color": 0x55AA55,
        "icon": "⛏️",
        "roles": [
            {"name": "👑 Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "🛡️ Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "⚔️ Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "💎 VIP", "color": 0x00CED1, "hoist": True},
            {"name": "🏗️ Builder", "color": 0x8B4513, "hoist": True},
            {"name": "⚒️ Minerador", "color": 0x696969, "hoist": True},
            {"name": "🌾 Fazendeiro", "color": 0x228B22, "hoist": True},
            {"name": "🏹 PVP", "color": 0xDC143C, "hoist": True},
            {"name": "🧙 Mago", "color": 0x9400D3, "hoist": False},
            {"name": "🆕 Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "📢 INFORMACOES",
                "channels": [
                    {"name": "📢-anuncios", "type": "announcement"},
                    {"name": "📋-regras", "type": "text"},
                    {"name": "🎉-boas-vindas", "type": "text"},
                    {"name": "📰-noticias-mc", "type": "text"},
                    {"name": "📅-eventos", "type": "text"},
                ]
            },
            {
                "name": "💬 GERAL",
                "channels": [
                    {"name": "💬-chat-geral", "type": "text"},
                    {"name": "🎭-memes", "type": "text"},
                    {"name": "📸-screenshots", "type": "text"},
                    {"name": "🎙️-lobby", "type": "voice"},
                ]
            },
            {
                "name": "⛏️ MINECRAFT",
                "channels": [
                    {"name": "🌍-survival", "type": "text"},
                    {"name": "🏗️-construcoes", "type": "text"},
                    {"name": "⚔️-pvp", "type": "text"},
                    {"name": "🔴-redstone", "type": "text"},
                    {"name": "🎁-sorteios", "type": "text"},
                    {"name": "🎙️-minecraft-voice", "type": "voice"},
                    {"name": "🎙️-squad-1", "type": "voice"},
                    {"name": "🎙️-squad-2", "type": "voice"},
                ]
            },
            {
                "name": "🛒 LOJA",
                "channels": [
                    {"name": "💰-vendas", "type": "text"},
                    {"name": "🤝-trocas", "type": "text"},
                    {"name": "📦-encomendas", "type": "text"},
                ]
            },
            {
                "name": "🔧 SUPORTE",
                "channels": [
                    {"name": "❓-ajuda", "type": "text"},
                    {"name": "🐛-bugs", "type": "text"},
                    {"name": "💡-sugestoes", "type": "text"},
                    {"name": "🎙️-suporte-voz", "type": "voice"},
                ]
            },
        ],
        "emojis": ["⛏️", "💎", "🏰", "🌳", "⚔️", "🔥", "⭐", "🎁"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },
}

# =============================================================================
# SISTEMA DE EMOJIS PERSONALIZADOS - API EMOJI.GG
# =============================================================================

class EmojiManager:
    """Gerenciador de emojis personalizados usando emoji.gg API"""

    BASE_URL = "https://emoji.gg/api"

    # Emojis personalizados por tema (usando URLs do emoji.gg)
    CUSTOM_EMOJIS = {
        "anime": [
            {"name": "anime_heart", "url": "https://emoji.gg/assets/emoji/heart.png"},
            {"name": "anime_star", "url": "https://emoji.gg/assets/emoji/star.png"},
            {"name": "anime_fire", "url": "https://emoji.gg/assets/emoji/fire.png"},
        ],
        "gaming": [
            {"name": "gaming_controller", "url": "https://emoji.gg/assets/emoji/controller.png"},
            {"name": "gaming_trophy", "url": "https://emoji.gg/assets/emoji/trophy.png"},
            {"name": "gaming_sword", "url": "https://emoji.gg/assets/emoji/sword.png"},
        ],
        "minecraft": [
            {"name": "mc_pickaxe", "url": "https://emoji.gg/assets/emoji/pickaxe.png"},
            {"name": "mc_diamond", "url": "https://emoji.gg/assets/emoji/diamond.png"},
            {"name": "mc_creeper", "url": "https://emoji.gg/assets/emoji/creeper.png"},
        ],
    }

    @classmethod
    async def fetch_emojis_by_category(cls, category: str, limit: int = 10):
        """Busca emojis da API emoji.gg por categoria"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{cls.BASE_URL}?request=category&category={category}&limit={limit}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    return []
        except Exception as e:
            logger.error(f"Erro ao buscar emojis: {e}")
            return []

    @classmethod
    async def download_emoji(cls, emoji_url: str, name: str, save_path: str = "assets/emojis/"):
        """Baixa um emoji da URL e salva localmente"""
        try:
            os.makedirs(save_path, exist_ok=True)
            async with aiohttp.ClientSession() as session:
                async with session.get(emoji_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        file_path = os.path.join(save_path, f"{name}.png")
                        with open(file_path, "wb") as f:
                            f.write(content)
                        return file_path
            return None
        except Exception as e:
            logger.error(f"Erro ao baixar emoji: {e}")
            return None

    @classmethod
    async def upload_to_guild(cls, guild: discord.Guild, emoji_path: str, name: str, roles: list = None):
        """Faz upload de um emoji para o servidor"""
        try:
            with open(emoji_path, "rb") as f:
                image_data = f.read()
            emoji = await guild.create_custom_emoji(
                name=name,
                image=image_data,
                roles=roles or []
            )
            return emoji
        except Exception as e:
            logger.error(f"Erro ao fazer upload do emoji: {e}")
            return None

# Emojis decorativos personalizados (Unicode bonitos, não Android)
DECORATIVE_EMOJIS = {
    "crown": "👑",
    "shield": "🛡️",
    "sword": "⚔️",
    "star": "⭐",
    "fire": "🔥",
    "diamond": "💎",
    "sparkles": "✨",
    "magic": "🪄",
    "rocket": "🚀",
    "gem": "💠",
    "crystal": "🔮",
    "medal": "🏅",
    "trophy": "🏆",
    "crown2": "👸",
    "crown3": "🤴",
    "flag": "🚩",
    "banner": "🎌",
    "scroll": "📜",
    "book": "📖",
    "scroll2": "📃",
    "parchment": "📄",
    "bell": "🔔",
    "horn": "📯",
    "drum": "🥁",
    "trumpet": "🎺",
    "violin": "🎻",
    "guitar": "🎸",
    "microphone": "🎤",
    "headphones": "🎧",
    "radio": "📻",
    "tv": "📺",
    "computer": "💻",
    "keyboard": "⌨️",
    "mouse": "🖱️",
    "floppy": "💾",
    "cd": "💿",
    "dvd": "📀",
    "camera": "📷",
    "video": "📹",
    "movie": "🎬",
    "clapper": "🎬",
    "ticket": "🎫",
    "map": "🗺️",
    "compass": "🧭",
    "anchor": "⚓",
    "ship": "🚢",
    "airplane": "✈️",
    "rocket2": "🚀",
    "ufo": "🛸",
    "satellite": "🛰️",
    "telescope": "🔭",
    "microscope": "🔬",
    "dna": "🧬",
    "atom": "⚛️",
    "gear2": "⚙️",
    "tools": "🛠️",
    "hammer": "🔨",
    "wrench": "🔧",
    "screwdriver": "🪛",
    "link": "🔗",
    "chain": "⛓️",
    "lock": "🔒",
    "unlock": "🔓",
    "key": "🔑",
    "door": "🚪",
    "window": "🪟",
    "bed": "🛏️",
    "chair": "🪑",
    "couch": "🛋️",
    "lamp": "🪔",
    "candle": "🕯️",
    "bulb": "💡",
    "flashlight": "🔦",
    "battery": "🔋",
    "plug": "🔌",
    "magnet": "🧲",
    "thermometer": "🌡️",
    "hourglass": "⏳",
    "clock": "🕐",
    "alarm": "⏰",
    "stopwatch": "⏱️",
    "timer": "⏲️",
    "calendar": "📅",
    "chart": "📊",
    "graph": "📈",
    "chart_down": "📉",
    "clipboard": "📋",
    "pushpin": "📌",
    "pin": "📍",
    "scissors": "✂️",
    "package": "📦",
    "mailbox": "📬",
    "postbox": "📮",
    "balloon": "🎈",
    "tada": "🎉",
    "confetti": "🎊",
    "dice": "🎲",
    "puzzle": "🧩",
    "teddy": "🧸",
    "piñata": "🪅",
    "mirror": "🪞",
    "nesting": "🪆",
    "sewing": "🪡",
    "knot": "🪢",
    "yarn": "🧶",
    "thread": "🧵",
    "shopping": "🛍️",
    "gift": "🎁",
    "ribbon": "🎀",
    "trophy2": "🏆",
    "medal2": "🏅",
    "medal3": "🥇",
    "medal4": "🥈",
    "medal5": "🥉",
    "flag2": "🏁",
    "flag3": "🎌",
    "flag4": "🏴",
    "flag5": "🏳️",
    "rainbow": "🌈",
    "sparkle": "✨",
    "zap": "⚡",
    "fire2": "🔥",
    "droplet": "💧",
    "ocean": "🌊",
    "earth": "🌍",
    "globe": "🌐",
    "sun": "☀️",
    "moon": "🌙",
    "star2": "⭐",
    "star3": "🌟",
    "cloud": "☁️",
    "umbrella": "☂️",
    "snowflake": "❄️",
    "snowman": "☃️",
    "comet": "☄️",
    "volcano": "🌋",
    "mountain": "⛰️",
    "camping": "🏕️",
    "beach": "🏖️",
    "desert": "🏜️",
    "island": "🏝️",
    "park": "🏞️",
    "city": "🏙️",
    "sunrise": "🌅",
    "sunset": "🌇",
    "night": "🌃",
    "bridge": "🌉",
    "foggy": "🌁",
    "hot": "🥵",
    "cold": "🥶",
    "sweat": "😅",
    "thinking": "🤔",
    "facepalm": "🤦",
    "shrug": "🤷",
    "wave": "👋",
    "clap": "👏",
    "pray": "🙏",
    "muscle": "💪",
    "fist": "✊",
    "point": "👉",
    "ok": "👌",
    "v": "✌️",
    "crossed": "🤞",
    "love": "🤟",
    "call": "🤙",
    "pinch": "🤏",
    "writing": "✍️",
    "selfie": "🤳",
    "nail": "💅",
    "lipstick": "💄",
    "ring": "💍",
    "gem2": "💎",
    "crown4": "👑",
    "hat": "🎩",
    "cap": "🧢",
    "helmet": "⛑️",
    "graduation": "🎓",
    "crown5": "👑",
    "crown6": "👸",
    "crown7": "🤴",
    "crown8": "🫅",
    "superhero": "🦸",
    "supervillain": "🦹",
    "ninja": "🥷",
    "mage": "🧙",
    "fairy": "🧚",
    "vampire": "🧛",
    "merperson": "🧜",
    "elf": "🧝",
    "genie": "🧞",
    "zombie": "🧟",
    "troll": "🧌",
    "ogre": "👹",
    "goblin": "👺",
    "ghost": "👻",
    "alien": "👽",
    "robot": "🤖",
    "clown": "🤡",
    "poop": "💩",
    "skull": "💀",
    "skull2": "☠️",
    "pirate": "🏴‍☠️",
    "bomb": "💣",
    "boom": "💥",
    "dash": "💨",
    "dizzy": "💫",
    "speech": "💬",
    "thought": "💭",
    "zzz": "💤",
    "sweat2": "💦",
    "money": "💰",
    "money2": "💵",
    "credit": "💳",
    "receipt": "🧾",
    "chart2": "💹",
    "yen": "💴",
    "dollar": "💵",
    "euro": "💶",
    "pound": "💷",
    "money3": "🤑",
    "coin": "🪙",
    "envelope": "✉️",
    "email": "📧",
    "incoming": "📨",
    "outgoing": "📩",
    "phone": "📱",
    "telephone": "☎️",
    "pager": "📟",
    "fax": "📠",
    "satellite2": "📡",
    "loudspeaker": "📢",
    "megaphone": "📣",
    "bell2": "🔔",
    "bell3": "🔕",
    "musical": "🎵",
    "notes": "🎶",
    "microphone2": "🎤",
    "headphones2": "🎧",
    "radio2": "📻",
    "saxophone": "🎷",
    "accordion": "🪗",
    "guitar2": "🎸",
    "banjo": "🪕",
    "violin2": "🎻",
    "drum2": "🥁",
    "long_drum": "🪘",
    "maracas": "🪇",
    "flute": "🪈",
    "phone2": "📲",
    "calling": "📲",
    "vibrate": "📳",
    "off": "📴",
    "recycle": "♻️",
    "trident": "🔱",
    "name_badge": "📛",
    "fleur": "⚜️",
    "beginner": "🔰",
    "o": "⭕",
    "white_check": "✅",
    "check": "☑️",
    "ballot": "☑️",
    "heavy_check": "✔️",
    "x": "❌",
    "heavy_x": "✖️",
    "plus": "➕",
    "minus": "➖",
    "divide": "➗",
    "infinity": "♾️",
    "question": "❓",
    "grey_question": "❔",
    "grey_exclamation": "❕",
    "exclamation": "❗",
    "bangbang": "‼️",
    "interrobang": "⁉️",
    "information": "ℹ️",
    "id": "🆔",
    "sos": "🆘",
    "up": "🆙",
    "vs": "🆚",
    "cool": "🆒",
    "new": "🆕",
    "free": "🆓",
    "zero": "0️⃣",
    "one": "1️⃣",
    "two": "2️⃣",
    "three": "3️⃣",
    "four": "4️⃣",
    "five": "5️⃣",
    "six": "6️⃣",
    "seven": "7️⃣",
    "eight": "8️⃣",
    "nine": "9️⃣",
    "ten": "🔟",
    "input": "🔠",
    "abc": "🔤",
    "arrow_up": "⬆️",
    "arrow_down": "⬇️",
    "arrow_left": "⬅️",
    "arrow_right": "➡️",
    "arrow_up_right": "↗️",
    "arrow_down_right": "↘️",
    "arrow_down_left": "↙️",
    "arrow_up_left": "↖️",
    "arrow_up_down": "↕️",
    "arrow_left_right": "↔️",
    "arrow_right_hook": "↪️",
    "arrow_left_hook": "↩️",
    "arrow_heading_up": "⤴️",
    "arrow_heading_down": "⤵️",
    "arrows_clockwise": "🔃",
    "arrows_counterclockwise": "🔄",
    "back": "🔙",
    "end": "🔚",
    "on": "🔛",
    "soon": "🔜",
    "top": "🔝",
    "place_of_worship": "🛐",
    "atom2": "⚛️",
    "om": "🕉️",
    "star_of_david": "✡️",
    "wheel_of_dharma": "☸️",
    "yin_yang": "☯️",
    "latin_cross": "✝️",
    "orthodox_cross": "☦️",
    "star_and_crescent": "☪️",
    "peace": "☮️",
    "menorah": "🕎",
    "six_pointed_star": "🔯",
    "aries": "♈",
    "taurus": "♉",
    "gemini": "♊",
    "cancer": "♋",
    "leo": "♌",
    "virgo": "♍",
    "libra": "♎",
    "scorpius": "♏",
    "sagittarius": "♐",
    "capricorn": "♑",
    "aquarius": "♒",
    "pisces": "♓",
    "ophiuchus": "⛎",
    "shuffle": "🔀",
    "repeat": "🔁",
    "repeat_one": "🔂",
    "arrow_forward": "▶️",
    "fast_forward": "⏩",
    "next_track": "⏭️",
    "play_pause": "⏯️",
    "arrow_backward": "◀️",
    "rewind": "⏪",
    "previous_track": "⏮️",
    "arrow_up_small": "🔼",
    "arrow_down_small": "🔽",
    "pause_button": "⏸️",
    "stop_button": "⏹️",
    "record_button": "⏺️",
    "eject": "⏏️",
    "cinema": "🎦",
    "dim": "🔅",
    "bright": "🔆",
    "antenna": "📶",
    "vibration": "📳",
    "mobile_off": "📴",
    "female_sign": "♀️",
    "male_sign": "♂️",
    "transgender": "⚧️",
    "heavy_multiplication": "✖️",
    "heavy_plus": "➕",
    "heavy_minus": "➖",
    "heavy_division": "➗",
    "heavy_equals": "🟰",
    "medical": "⚕️",
    "recycling": "♻️",
    "fleur_de_lis": "⚜️",
    "trident2": "🔱",
    "name_badge2": "📛",
    "beginner2": "🔰",
    "o2": "⭕",
    "white_check2": "✅",
    "ballot_box": "☑️",
    "heavy_check2": "✔️",
    "x2": "❌",
    "heavy_x2": "✖️",
    "curly_loop": "➰",
    "loop": "➿",
    "part_alternation": "〽️",
    "eight_spoked": "✳️",
    "eight_pointed": "✴️",
    "sparkle2": "❇️",
    "copyright": "©️",
    "registered": "®️",
    "tm": "™️",
    "hash": "#️⃣",
    "asterisk": "*️⃣",
    "zero2": "0️⃣",
    "one2": "1️⃣",
    "two2": "2️⃣",
    "three2": "3️⃣",
    "four2": "4️⃣",
    "five2": "5️⃣",
    "six2": "6️⃣",
    "seven2": "7️⃣",
    "eight2": "8️⃣",
    "nine2": "9️⃣",
    "ten2": "🔟",
    "capital_abcd": "🔠",
    "abcd2": "🔡",
    "abc2": "🔤",
    "a": "🅰️",
    "ab": "🆎",
    "b": "🅱️",
    "cl": "🆑",
    "cool2": "🆒",
    "free2": "🆓",
    "information2": "ℹ️",
    "id2": "🆔",
    "m": "Ⓜ️",
    "new2": "🆕",
    "ng": "🆖",
    "o3": "🅾️",
    "ok2": "🆗",
    "parking": "🅿️",
    "sos2": "🆘",
    "up2": "🆙",
    "vs2": "🆚",
    "koko": "🈁",
    "sa": "🈂️",
    "u6708": "🈷️",
    "u6709": "🈶",
    "u6307": "🈯",
    "ideograph_advantage": "🉐",
    "u5272": "🈹",
    "u7121": "🈚",
    "u7981": "🈲",
    "accept": "🉑",
    "u7533": "🈸",
    "u5408": "🈴",
    "u7a7a": "🈳",
    "congratulations": "㊗️",
    "secret": "㊙️",
    "u55b6": "🈺",
    "u6e80": "🈵",
    "red_circle": "🔴",
    "orange_circle": "🟠",
    "yellow_circle": "🟡",
    "green_circle": "🟢",
    "blue_circle": "🔵",
    "purple_circle": "🟣",
    "brown_circle": "🟤",
    "black_circle": "⚫",
    "white_circle": "⚪",
    "red_square": "🟥",
    "orange_square": "🟧",
    "yellow_square": "🟨",
    "green_square": "🟩",
    "blue_square": "🟦",
    "purple_square": "🟪",
    "brown_square": "🟫",
    "black_large_square": "⬛",
    "white_large_square": "⬜",
    "black_medium_square": "◼️",
    "white_medium_square": "◻️",
    "black_medium_small_square": "◾",
    "white_medium_small_square": "◽",
    "black_small_square": "▪️",
    "white_small_square": "▫️",
    "large_orange_diamond": "🔶",
    "large_blue_diamond": "🔷",
    "small_orange_diamond": "🔸",
    "small_blue_diamond": "🔹",
    "red_triangle_up": "🔺",
    "red_triangle_down": "🔻",
    "diamond_with_a_dot": "💠",
    "radio_button": "🔘",
    "white_button": "🔳",
    "black_button": "🔲",
}

# Mapeamento de emojis por tema
THEME_EMOJIS = {
    "anime": ["star", "sparkles", "magic", "fire", "diamond", "crystal", "heart", "ribbon"],
    "gaming": ["trophy", "sword", "shield", "crown", "zap", "fire2", "diamond", "rocket"],
    "minecraft": ["pickaxe", "diamond", "gem", "trophy", "crown", "fire2", "star", "shield"],
    "roblox": ["robot", "game", "trophy", "crown", "star", "diamond", "fire2", "zap"],
    "tecnologia": ["computer", "gear", "zap", "satellite", "rocket", "atom", "microscope", "dna"],
    "programacao": ["computer", "keyboard", "gear", "zap", "rocket", "atom", "link", "chain"],
    "rpg": ["sword", "shield", "crown", "crystal", "magic", "fire2", "skull", "dragon"],
    "streaming": ["tv", "microphone", "camera", "trophy", "star", "fire2", "zap", "diamond"],
    "e-girl": ["crown", "diamond", "sparkles", "heart", "lipstick", "nail", "ribbon", "star"],
    "dark": ["skull", "skull2", "crystal", "moon", "fire2", "zap", "diamond", "ghost"],
    "neon": ["zap", "star", "fire2", "diamond", "sparkles", "rocket", "crystal", "gem"],
    "cyberpunk": ["robot", "computer", "zap", "satellite", "rocket", "atom", "gear", "dna"],
    "musica": ["musical", "notes", "microphone", "headphones", "guitar", "drum", "saxophone", "radio"],
    "otaku": ["star", "sparkles", "magic", "fire", "diamond", "crystal", "heart", "ribbon"],
    "k-pop": ["musical", "notes", "microphone", "star", "sparkles", "heart", "diamond", "crown"],
    "estudo": ["book", "scroll", "graduation", "light_bulb", "pencil", "pen", "memo", "bookmark"],
    "marketplace": ["money", "money2", "credit", "receipt", "chart", "shopping", "gift", "package"],
    "nft": ["diamond", "gem", "crystal", "money", "chart", "fire2", "rocket", "star"],
    "startup": ["rocket", "gear", "computer", "chart", "light_bulb", "zap", "satellite", "atom"],
    "influencer": ["crown", "star", "fire2", "diamond", "camera", "microphone", "tv", "trophy"],
    "youtube": ["tv", "camera", "microphone", "trophy", "star", "fire2", "zap", "diamond"],
    "tiktok": ["musical", "notes", "camera", "star", "fire2", "zap", "diamond", "trophy"],
    "roleplay": ["scroll", "crown", "sword", "shield", "crystal", "magic", "fire2", "skull"],
    "militar": ["shield", "sword", "crown", "trophy", "medal", "flag", "banner", "scroll"],
    "fantasia": ["magic", "crystal", "crown", "sword", "shield", "dragon", "fire2", "star"],
    "terror": ["skull", "skull2", "ghost", "crystal", "moon", "fire2", "zap", "diamond"],
    "space": ["rocket", "satellite", "earth", "moon", "star", "comet", "telescope", "atom"],
    "medieval": ["crown", "sword", "shield", "scroll", "crystal", "magic", "fire2", "trophy"],
    "minimalista": ["circle", "square", "diamond", "star", "zap", "fire2", "crown", "shield"],
}

# =============================================================================
# COMPLETAR TEMAS (30+ TEMAS PRONTOS)
# =============================================================================

# Adicionar mais temas ao dicionario THEMES
ADDITIONAL_THEMES = {
    "roblox": {
        "name": "Roblox",
        "description": "Servidor dedicado ao universo Roblox",
        "color": 0xFF0000,
        "icon": "🎮",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Dev", "color": 0x0000FF, "hoist": True},
            {"name": "Builder", "color": 0x8B4513, "hoist": True},
            {"name": "VIP", "color": 0x00CED1, "hoist": True},
            {"name": "Player", "color": 0x32CD32, "hoist": False},
            {"name": "Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "noticias", "type": "text"},
                ]
            },
            {
                "name": "GERAL",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "screenshots", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
            {
                "name": "ROBLOX",
                "channels": [
                    {"name": "games", "type": "text"},
                    {"name": "scripts", "type": "text"},
                    {"name": "modelos", "type": "text"},
                    {"name": "tutoriais", "type": "text"},
                    {"name": "sorteios", "type": "text"},
                    {"name": "roblox-voice", "type": "voice"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "bugs", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["trophy", "sword", "shield", "crown", "star", "diamond", "fire2", "zap"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "tecnologia": {
        "name": "Tecnologia",
        "description": "Servidor para entusiastas de tecnologia",
        "color": 0x00BFFF,
        "icon": "💻",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Dev Senior", "color": 0x0000FF, "hoist": True},
            {"name": "Dev Junior", "color": 0x4169E1, "hoist": True},
            {"name": "Designer UI", "color": 0xFF69B4, "hoist": True},
            {"name": "Cyberseguranca", "color": 0xDC143C, "hoist": True},
            {"name": "Hardware", "color": 0x32CD32, "hoist": True},
            {"name": "Redes", "color": 0xFF8C00, "hoist": True},
            {"name": "IA", "color": 0x9400D3, "hoist": True},
            {"name": "Entusiasta", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "noticias-tech", "type": "text"},
                ]
            },
            {
                "name": "GERAL",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "off-topic", "type": "text"},
                    {"name": "memes-tech", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
            {
                "name": "DESENVOLVIMENTO",
                "channels": [
                    {"name": "frontend", "type": "text"},
                    {"name": "backend", "type": "text"},
                    {"name": "mobile", "type": "text"},
                    {"name": "devops", "type": "text"},
                    {"name": "database", "type": "text"},
                    {"name": "code-review", "type": "text"},
                    {"name": "dev-voice", "type": "voice"},
                ]
            },
            {
                "name": "HARDWARE",
                "channels": [
                    {"name": "pc-builds", "type": "text"},
                    {"name": "overclock", "type": "text"},
                    {"name": "perifericos", "type": "text"},
                    {"name": "setup", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "bugs", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["computer", "gear", "zap", "satellite", "rocket", "atom", "microscope", "dna"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "programacao": {
        "name": "Programacao",
        "description": "Servidor para desenvolvedores e programadores",
        "color": 0x2D2D2D,
        "icon": "💻",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Senior Dev", "color": 0x0000FF, "hoist": True},
            {"name": "Full Stack", "color": 0x4169E1, "hoist": True},
            {"name": "Frontend", "color": 0xFF69B4, "hoist": True},
            {"name": "Backend", "color": 0x32CD32, "hoist": True},
            {"name": "Mobile", "color": 0xFF8C00, "hoist": True},
            {"name": "DevOps", "color": 0x9400D3, "hoist": True},
            {"name": "Data Science", "color": 0x00CED1, "hoist": True},
            {"name": "Estudante", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "recursos", "type": "text"},
                ]
            },
            {
                "name": "LINGUAGENS",
                "channels": [
                    {"name": "python", "type": "text"},
                    {"name": "javascript", "type": "text"},
                    {"name": "java", "type": "text"},
                    {"name": "csharp", "type": "text"},
                    {"name": "cpp", "type": "text"},
                    {"name": "rust", "type": "text"},
                    {"name": "go", "type": "text"},
                    {"name": "ruby", "type": "text"},
                ]
            },
            {
                "name": "PROJETOS",
                "channels": [
                    {"name": "showcase", "type": "text"},
                    {"name": "code-review", "type": "text"},
                    {"name": "pair-programming", "type": "text"},
                    {"name": "open-source", "type": "text"},
                    {"name": "dev-voice", "type": "voice"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "duvidas", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["computer", "keyboard", "gear", "zap", "rocket", "atom", "link", "chain"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "rpg": {
        "name": "RPG",
        "description": "Servidor para jogadores de RPG de mesa e digital",
        "color": 0x8B0000,
        "icon": "🎲",
        "roles": [
            {"name": "Mestre", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Mestre NPC", "color": 0x9400D3, "hoist": True},
            {"name": "Guerreiro", "color": 0xDC143C, "hoist": True},
            {"name": "Mago", "color": 0x4169E1, "hoist": True},
            {"name": "Ladino", "color": 0x32CD32, "hoist": True},
            {"name": "Clerigo", "color": 0xFFD700, "hoist": True},
            {"name": "Ranger", "color": 0x228B22, "hoist": True},
            {"name": "Bardo", "color": 0xFF69B4, "hoist": True},
            {"name": "Aventureiro", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "calendario", "type": "text"},
                ]
            },
            {
                "name": "MESAS",
                "channels": [
                    {"name": "procurando-mesa", "type": "text"},
                    {"name": "mesas-ativas", "type": "text"},
                    {"name": "dnd", "type": "text"},
                    {"name": "pathfinder", "type": "text"},
                    {"name": "vampire", "type": "text"},
                    {"name": "call-of-cthulhu", "type": "text"},
                    {"name": "mesa-voice-1", "type": "voice"},
                    {"name": "mesa-voice-2", "type": "voice"},
                ]
            },
            {
                "name": "RECURSOS",
                "channels": [
                    {"name": "fichas", "type": "text"},
                    {"name": "mapas", "type": "text"},
                    {"name": "itens", "type": "text"},
                    {"name": "historias", "type": "text"},
                    {"name": "dice-rolls", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["sword", "shield", "crown", "crystal", "magic", "fire2", "skull", "dragon"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "streaming": {
        "name": "Streaming",
        "description": "Servidor para streamers e criadores de conteudo",
        "color": 0x9146FF,
        "icon": "📺",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Streamer", "color": 0x9146FF, "hoist": True},
            {"name": "Editor", "color": 0xFF69B4, "hoist": True},
            {"name": "Designer", "color": 0x00CED1, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Sub", "color": 0x32CD32, "hoist": True},
            {"name": "Viewer", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "horarios", "type": "text"},
                ]
            },
            {
                "name": "CHAT",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "clips", "type": "text"},
                    {"name": "art", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
            {
                "name": "STREAM",
                "channels": [
                    {"name": "live-chat", "type": "text"},
                    {"name": "sugestoes-stream", "type": "text"},
                    {"name": "sorteios", "type": "text"},
                    {"name": "stream-voice", "type": "voice"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "bugs", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["tv", "microphone", "camera", "trophy", "star", "fire2", "zap", "diamond"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "dark": {
        "name": "Dark",
        "description": "Servidor com estetica dark e misteriosa",
        "color": 0x1A1A2E,
        "icon": "🌑",
        "roles": [
            {"name": "Sombra", "color": 0x000000, "hoist": True, "permissions": "admin"},
            {"name": "Observador", "color": 0x333333, "hoist": True, "permissions": "mod"},
            {"name": "Guardiao", "color": 0x555555, "hoist": True, "permissions": "mod"},
            {"name": "Eclipse", "color": 0x777777, "hoist": True},
            {"name": "Nocturno", "color": 0x999999, "hoist": True},
            {"name": "Sombrio", "color": 0xAAAAAA, "hoist": False},
            {"name": "Penumbra", "color": 0xBBBBBB, "hoist": False},
        ],
        "categories": [
            {
                "name": "VOID",
                "channels": [
                    {"name": "void-anuncios", "type": "announcement"},
                    {"name": "void-regras", "type": "text"},
                    {"name": "void-boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "SHADOWS",
                "channels": [
                    {"name": "shadow-chat", "type": "text"},
                    {"name": "shadow-memes", "type": "text"},
                    {"name": "shadow-art", "type": "text"},
                    {"name": "shadow-voice", "type": "voice"},
                ]
            },
            {
                "name": "ABYSS",
                "channels": [
                    {"name": "abyss-general", "type": "text"},
                    {"name": "abyss-music", "type": "text"},
                    {"name": "abyss-gaming", "type": "text"},
                ]
            },
        ],
        "emojis": ["skull", "skull2", "crystal", "moon", "fire2", "zap", "diamond", "ghost"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "neon": {
        "name": "Neon",
        "description": "Servidor com estetica neon e vibrante",
        "color": 0xFF00FF,
        "icon": "⚡",
        "roles": [
            {"name": "Neon King", "color": 0xFF00FF, "hoist": True, "permissions": "admin"},
            {"name": "Neon Admin", "color": 0x00FFFF, "hoist": True, "permissions": "mod"},
            {"name": "Neon Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Neon VIP", "color": 0xFFFF00, "hoist": True},
            {"name": "Neon User", "color": 0xFF00FF, "hoist": False},
        ],
        "categories": [
            {
                "name": "NEON HUB",
                "channels": [
                    {"name": "neon-anuncios", "type": "announcement"},
                    {"name": "neon-regras", "type": "text"},
                    {"name": "neon-welcome", "type": "text"},
                ]
            },
            {
                "name": "NEON CHAT",
                "channels": [
                    {"name": "neon-general", "type": "text"},
                    {"name": "neon-memes", "type": "text"},
                    {"name": "neon-music", "type": "text"},
                    {"name": "neon-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["zap", "star", "fire2", "diamond", "sparkles", "rocket", "crystal", "gem"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "cyberpunk": {
        "name": "Cyberpunk",
        "description": "Servidor futurista cyberpunk",
        "color": 0x00FF41,
        "icon": "🤖",
        "roles": [
            {"name": "SysAdmin", "color": 0x00FF41, "hoist": True, "permissions": "admin"},
            {"name": "NetRunner", "color": 0x00FFFF, "hoist": True, "permissions": "mod"},
            {"name": "Fixer", "color": 0xFF00FF, "hoist": True, "permissions": "mod"},
            {"name": "Solo", "color": 0xFF0000, "hoist": True},
            {"name": "Techie", "color": 0xFFFF00, "hoist": True},
            {"name": "Corpo", "color": 0x00CED1, "hoist": True},
            {"name": "StreetKid", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "NET",
                "channels": [
                    {"name": "net-anuncios", "type": "announcement"},
                    {"name": "net-regras", "type": "text"},
                    {"name": "net-welcome", "type": "text"},
                ]
            },
            {
                "name": "DATA",
                "channels": [
                    {"name": "data-general", "type": "text"},
                    {"name": "data-hacking", "type": "text"},
                    {"name": "data-tech", "type": "text"},
                    {"name": "data-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["robot", "computer", "zap", "satellite", "rocket", "atom", "gear", "dna"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "musica": {
        "name": "Musica",
        "description": "Servidor para amantes da musica",
        "color": 0xFF1493,
        "icon": "🎵",
        "roles": [
            {"name": "Produtor", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "DJ", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Vocalista", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Instrumentista", "color": 0x0000FF, "hoist": True},
            {"name": "Compositor", "color": 0xFF69B4, "hoist": True},
            {"name": "Fan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "STAGE",
                "channels": [
                    {"name": "stage-anuncios", "type": "announcement"},
                    {"name": "stage-regras", "type": "text"},
                    {"name": "stage-welcome", "type": "text"},
                ]
            },
            {
                "name": "STUDIO",
                "channels": [
                    {"name": "studio-general", "type": "text"},
                    {"name": "studio-releases", "type": "text"},
                    {"name": "studio-collab", "type": "text"},
                    {"name": "studio-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["musical", "notes", "microphone", "headphones", "guitar", "drum", "saxophone", "radio"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "estudo": {
        "name": "Estudo",
        "description": "Servidor para estudantes e aprendizado",
        "color": 0x4169E1,
        "icon": "📚",
        "roles": [
            {"name": "Professor", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Monitor", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Aluno", "color": 0x4169E1, "hoist": True},
            {"name": "Tutor", "color": 0xFF69B4, "hoist": True},
            {"name": "Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "ESCOLA",
                "channels": [
                    {"name": "escola-anuncios", "type": "announcement"},
                    {"name": "escola-regras", "type": "text"},
                    {"name": "escola-welcome", "type": "text"},
                ]
            },
            {
                "name": "MATERIAS",
                "channels": [
                    {"name": "matematica", "type": "text"},
                    {"name": "fisica", "type": "text"},
                    {"name": "quimica", "type": "text"},
                    {"name": "biologia", "type": "text"},
                    {"name": "historia", "type": "text"},
                    {"name": "geografia", "type": "text"},
                    {"name": "portugues", "type": "text"},
                    {"name": "ingles", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "duvidas", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["book", "scroll", "graduation", "light_bulb", "pencil", "pen", "memo", "bookmark"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "marketplace": {
        "name": "Marketplace",
        "description": "Servidor para compras e vendas",
        "color": 0x32CD32,
        "icon": "🛒",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Vendedor", "color": 0x00CED1, "hoist": True},
            {"name": "Comprador", "color": 0x32CD32, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Cliente", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "LOJA",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "VENDAS",
                "channels": [
                    {"name": "produtos", "type": "text"},
                    {"name": "servicos", "type": "text"},
                    {"name": "trocas", "type": "text"},
                    {"name": "leiloes", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "reclamacoes", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["money", "money2", "credit", "receipt", "chart", "shopping", "gift", "package"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "nft": {
        "name": "NFT",
        "description": "Servidor para colecionadores de NFT",
        "color": 0xFFD700,
        "icon": "💎",
        "roles": [
            {"name": "Fundador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Whale", "color": 0x00CED1, "hoist": True},
            {"name": "Collector", "color": 0x32CD32, "hoist": True},
            {"name": "Artist", "color": 0xFF69B4, "hoist": True},
            {"name": "Holder", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "GALLERY",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "COLLECTION",
                "channels": [
                    {"name": "showcase", "type": "text"},
                    {"name": "drops", "type": "text"},
                    {"name": "trades", "type": "text"},
                    {"name": "auctions", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["diamond", "gem", "crystal", "money", "chart", "fire2", "rocket", "star"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "startup": {
        "name": "Startup",
        "description": "Servidor para startups e empreendedores",
        "color": 0xFF6B35,
        "icon": "🚀",
        "roles": [
            {"name": "CEO", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "CTO", "color": 0x0000FF, "hoist": True, "permissions": "mod"},
            {"name": "COO", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Dev", "color": 0x4169E1, "hoist": True},
            {"name": "Marketing", "color": 0xFF69B4, "hoist": True},
            {"name": "Sales", "color": 0x32CD32, "hoist": True},
            {"name": "Investor", "color": 0x00CED1, "hoist": True},
            {"name": "Intern", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "OFFICE",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "TEAMS",
                "channels": [
                    {"name": "dev-team", "type": "text"},
                    {"name": "marketing-team", "type": "text"},
                    {"name": "sales-team", "type": "text"},
                    {"name": "general-team", "type": "text"},
                ]
            },
            {
                "name": "PROJECTS",
                "channels": [
                    {"name": "roadmap", "type": "text"},
                    {"name": "sprints", "type": "text"},
                    {"name": "backlog", "type": "text"},
                    {"name": "meetings", "type": "voice"},
                ]
            },
        ],
        "emojis": ["rocket", "gear", "computer", "chart", "light_bulb", "zap", "satellite", "atom"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "influencer": {
        "name": "Influencer",
        "description": "Servidor para influencers e criadores",
        "color": 0xE1306C,
        "icon": "👑",
        "roles": [
            {"name": "Influencer", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Manager", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Editor", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Designer", "color": 0xFF69B4, "hoist": True},
            {"name": "VIP", "color": 0x00CED1, "hoist": True},
            {"name": "Fan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "HUB",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "COMMUNITY",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "fan-art", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
        ],
        "emojis": ["crown", "star", "fire2", "diamond", "camera", "microphone", "tv", "trophy"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "youtube": {
        "name": "YouTube",
        "description": "Servidor para criadores do YouTube",
        "color": 0xFF0000,
        "icon": "📺",
        "roles": [
            {"name": "Criador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Editor", "color": 0xFF69B4, "hoist": True},
            {"name": "Thumbnail", "color": 0x00CED1, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Subscriber", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CHANNEL",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "uploads", "type": "text"},
                ]
            },
            {
                "name": "STUDIO",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "video-ideas", "type": "text"},
                    {"name": "feedback", "type": "text"},
                    {"name": "collab", "type": "text"},
                    {"name": "studio-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["tv", "camera", "microphone", "trophy", "star", "fire2", "zap", "diamond"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "tiktok": {
        "name": "TikTok",
        "description": "Servidor para criadores do TikTok",
        "color": 0x000000,
        "icon": "🎵",
        "roles": [
            {"name": "Criador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Editor", "color": 0xFF69B4, "hoist": True},
            {"name": "Dancer", "color": 0x00CED1, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Fan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "FOR YOU",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "FYP",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "trends", "type": "text"},
                    {"name": "duet", "type": "text"},
                    {"name": "sounds", "type": "text"},
                    {"name": "fyp-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["musical", "notes", "camera", "star", "fire2", "zap", "diamond", "trophy"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "roleplay": {
        "name": "Roleplay",
        "description": "Servidor para roleplay e interpretacao",
        "color": 0x800080,
        "icon": "🎭",
        "roles": [
            {"name": "Narrador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Veterano", "color": 0x00CED1, "hoist": True},
            {"name": "Personagem", "color": 0x32CD32, "hoist": True},
            {"name": "Novo", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CENARIO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "lore", "type": "text"},
                ]
            },
            {
                "name": "HISTORIA",
                "channels": [
                    {"name": "rp-geral", "type": "text"},
                    {"name": "rp-cidade", "type": "text"},
                    {"name": "rp-floresta", "type": "text"},
                    {"name": "rp-castelo", "type": "text"},
                    {"name": "rp-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["scroll", "crown", "sword", "shield", "crystal", "magic", "fire2", "skull"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "militar": {
        "name": "Militar",
        "description": "Servidor com tema militar",
        "color": 0x556B2F,
        "icon": "🛡️",
        "roles": [
            {"name": "General", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Coronel", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Major", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Capitao", "color": 0x0000FF, "hoist": True},
            {"name": "Sargento", "color": 0xFF8C00, "hoist": True},
            {"name": "Soldado", "color": 0x32CD32, "hoist": True},
            {"name": "Recruta", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "QUARTEL",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "OPERACOES",
                "channels": [
                    {"name": "missao", "type": "text"},
                    {"name": "estrategia", "type": "text"},
                    {"name": "intel", "type": "text"},
                    {"name": "comando-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["shield", "sword", "crown", "trophy", "medal", "flag", "banner", "scroll"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "fantasia": {
        "name": "Fantasia",
        "description": "Servidor com tema fantasia medieval",
        "color": 0x9932CC,
        "icon": "🐉",
        "roles": [
            {"name": "Rei", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Mago Supremo", "color": 0x9400D3, "hoist": True, "permissions": "mod"},
            {"name": "Cavaleiro", "color": 0xC0C0C0, "hoist": True, "permissions": "mod"},
            {"name": "Arqueiro", "color": 0x228B22, "hoist": True},
            {"name": "Feiticeiro", "color": 0x4169E1, "hoist": True},
            {"name": "Ladino", "color": 0x32CD32, "hoist": True},
            {"name": "Bardo", "color": 0xFF69B4, "hoist": True},
            {"name": "Campones", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "REINO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "lore", "type": "text"},
                ]
            },
            {
                "name": "AVENTURA",
                "channels": [
                    {"name": "taverna", "type": "text"},
                    {"name": "mercado", "type": "text"},
                    {"name": "guilda", "type": "text"},
                    {"name": "masmorra", "type": "text"},
                    {"name": "aventura-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["magic", "crystal", "crown", "sword", "shield", "dragon", "fire2", "star"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "terror": {
        "name": "Terror",
        "description": "Servidor com tema horror e terror",
        "color": 0x8B0000,
        "icon": "💀",
        "roles": [
            {"name": "Mestre do Medo", "color": 0x8B0000, "hoist": True, "permissions": "admin"},
            {"name": "Cacador", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Sobrevivente", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Cacador de Fantasmas", "color": 0x9400D3, "hoist": True},
            {"name": "Vitima", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CEMITERIO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "HORROR",
                "channels": [
                    {"name": "historias", "type": "text"},
                    {"name": "filmes", "type": "text"},
                    {"name": "jogos-terror", "type": "text"},
                    {"name": "cemiterio-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["skull", "skull2", "ghost", "crystal", "moon", "fire2", "zap", "diamond"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "space": {
        "name": "Space",
        "description": "Servidor com tema espacial",
        "color": 0x000080,
        "icon": "🚀",
        "roles": [
            {"name": "Comandante", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Piloto", "color": 0x0000FF, "hoist": True, "permissions": "mod"},
            {"name": "Engenheiro", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Cientista", "color": 0x9400D3, "hoist": True},
            {"name": "Astronauta", "color": 0x00CED1, "hoist": True},
            {"name": "Cadete", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "BASE",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "GALAXY",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "astronomia", "type": "text"},
                    {"name": "foguetes", "type": "text"},
                    {"name": "space-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["rocket", "satellite", "earth", "moon", "star", "comet", "telescope", "atom"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "medieval": {
        "name": "Medieval",
        "description": "Servidor com tema medieval",
        "color": 0x8B4513,
        "icon": "🏰",
        "roles": [
            {"name": "Rei", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Rainha", "color": 0xFF69B4, "hoist": True, "permissions": "mod"},
            {"name": "Cavaleiro", "color": 0xC0C0C0, "hoist": True, "permissions": "mod"},
            {"name": "Arqueiro", "color": 0x228B22, "hoist": True},
            {"name": "Ferreiro", "color": 0x696969, "hoist": True},
            {"name": "Mercenario", "color": 0x8B0000, "hoist": True},
            {"name": "Campones", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CASTELO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "lore", "type": "text"},
                ]
            },
            {
                "name": "REINO",
                "channels": [
                    {"name": "taverna", "type": "text"},
                    {"name": "mercado", "type": "text"},
                    {"name": "arena", "type": "text"},
                    {"name": "castelo-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["crown", "sword", "shield", "scroll", "crystal", "magic", "fire2", "trophy"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "minimalista": {
        "name": "Minimalista",
        "description": "Servidor com design minimalista e clean",
        "color": 0xFFFFFF,
        "icon": "◻️",
        "roles": [
            {"name": "Admin", "color": 0x000000, "hoist": True, "permissions": "admin"},
            {"name": "Mod", "color": 0x333333, "hoist": True, "permissions": "mod"},
            {"name": "Membro", "color": 0x666666, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "welcome", "type": "text"},
                ]
            },
            {
                "name": "CHAT",
                "channels": [
                    {"name": "geral", "type": "text"},
                    {"name": "media", "type": "text"},
                    {"name": "voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["circle", "square", "diamond", "star", "zap", "fire2", "crown", "shield"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "comunidade": {
        "name": "Comunidade",
        "description": "Servidor de comunidade geral",
        "color": 0x5865F2,
        "icon": "🤝",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "VIP", "color": 0x00CED1, "hoist": True},
            {"name": "Membro", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "GERAL",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "media", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
        ],
        "emojis": ["star", "fire2", "diamond", "heart", "sparkles", "rocket", "crown", "shield"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "e-girl": {
        "name": "E-Girl",
        "description": "Servidor com estetica e-girl",
        "color": 0xFF69B4,
        "icon": "💕",
        "roles": [
            {"name": "Queen", "color": 0xFF69B4, "hoist": True, "permissions": "admin"},
            {"name": "Princess", "color": 0xFF1493, "hoist": True, "permissions": "mod"},
            {"name": "Kawaii", "color": 0xFFB6C1, "hoist": True},
            {"name": "Aesthetic", "color": 0xDDA0DD, "hoist": True},
            {"name": "Soft Girl", "color": 0xF0E68C, "hoist": False},
        ],
        "categories": [
            {
                "name": "AESTHETIC",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "SOFT",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "aesthetic", "type": "text"},
                    {"name": "makeup", "type": "text"},
                    {"name": "fashion", "type": "text"},
                    {"name": "soft-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["crown", "diamond", "sparkles", "heart", "lipstick", "nail", "ribbon", "star"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "k-pop": {
        "name": "K-Pop",
        "description": "Servidor para fas de K-Pop",
        "color": 0xFF69B4,
        "icon": "🎤",
        "roles": [
            {"name": "Presidente", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Ult Bias", "color": 0xFF69B4, "hoist": True},
            {"name": "Bias Wrecker", "color": 0x00CED1, "hoist": True},
            {"name": "Stan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "STAGE",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "FANDOM",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "comebacks", "type": "text"},
                    {"name": "fanarts", "type": "text"},
                    {"name": "mv-reactions", "type": "text"},
                    {"name": "kpop-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["musical", "notes", "microphone", "star", "sparkles", "heart", "diamond", "crown"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "otaku": {
        "name": "Otaku",
        "description": "Servidor para otakus e fas de cultura japonesa",
        "color": 0xFF1493,
        "icon": "🌸",
        "roles": [
            {"name": "Sensei", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Senpai", "color": 0xFF69B4, "hoist": True},
            {"name": "Kouhai", "color": 0x00CED1, "hoist": True},
            {"name": "Weeb", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "DOJO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "ANIME",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "recomendacoes", "type": "text"},
                    {"name": "manga", "type": "text"},
                    {"name": "cosplay", "type": "text"},
                    {"name": "otaku-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["star", "sparkles", "magic", "fire", "diamond", "crystal", "heart", "ribbon"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },
}

# Mesclar temas adicionais
THEMES.update(ADDITIONAL_THEMES)

# Lista de todos os temas disponiveis
ALL_THEMES = list(THEMES.keys())

# =============================================================================
# COMPLETAR TEMAS (30+ TEMAS PRONTOS)
# =============================================================================

# Adicionar mais temas ao dicionario THEMES
ADDITIONAL_THEMES = {
    "roblox": {
        "name": "Roblox",
        "description": "Servidor dedicado ao universo Roblox",
        "color": 0xFF0000,
        "icon": "🎮",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Dev", "color": 0x0000FF, "hoist": True},
            {"name": "Builder", "color": 0x8B4513, "hoist": True},
            {"name": "VIP", "color": 0x00CED1, "hoist": True},
            {"name": "Player", "color": 0x32CD32, "hoist": False},
            {"name": "Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "noticias", "type": "text"},
                ]
            },
            {
                "name": "GERAL",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "screenshots", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
            {
                "name": "ROBLOX",
                "channels": [
                    {"name": "games", "type": "text"},
                    {"name": "scripts", "type": "text"},
                    {"name": "modelos", "type": "text"},
                    {"name": "tutoriais", "type": "text"},
                    {"name": "sorteios", "type": "text"},
                    {"name": "roblox-voice", "type": "voice"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "bugs", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["trophy", "sword", "shield", "crown", "star", "diamond", "fire2", "zap"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "tecnologia": {
        "name": "Tecnologia",
        "description": "Servidor para entusiastas de tecnologia",
        "color": 0x00BFFF,
        "icon": "💻",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Dev Senior", "color": 0x0000FF, "hoist": True},
            {"name": "Dev Junior", "color": 0x4169E1, "hoist": True},
            {"name": "Designer UI", "color": 0xFF69B4, "hoist": True},
            {"name": "Cyberseguranca", "color": 0xDC143C, "hoist": True},
            {"name": "Hardware", "color": 0x32CD32, "hoist": True},
            {"name": "Redes", "color": 0xFF8C00, "hoist": True},
            {"name": "IA", "color": 0x9400D3, "hoist": True},
            {"name": "Entusiasta", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "noticias-tech", "type": "text"},
                ]
            },
            {
                "name": "GERAL",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "off-topic", "type": "text"},
                    {"name": "memes-tech", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
            {
                "name": "DESENVOLVIMENTO",
                "channels": [
                    {"name": "frontend", "type": "text"},
                    {"name": "backend", "type": "text"},
                    {"name": "mobile", "type": "text"},
                    {"name": "devops", "type": "text"},
                    {"name": "database", "type": "text"},
                    {"name": "code-review", "type": "text"},
                    {"name": "dev-voice", "type": "voice"},
                ]
            },
            {
                "name": "HARDWARE",
                "channels": [
                    {"name": "pc-builds", "type": "text"},
                    {"name": "overclock", "type": "text"},
                    {"name": "perifericos", "type": "text"},
                    {"name": "setup", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "bugs", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["computer", "gear", "zap", "satellite", "rocket", "atom", "microscope", "dna"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "programacao": {
        "name": "Programacao",
        "description": "Servidor para desenvolvedores e programadores",
        "color": 0x2D2D2D,
        "icon": "💻",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Senior Dev", "color": 0x0000FF, "hoist": True},
            {"name": "Full Stack", "color": 0x4169E1, "hoist": True},
            {"name": "Frontend", "color": 0xFF69B4, "hoist": True},
            {"name": "Backend", "color": 0x32CD32, "hoist": True},
            {"name": "Mobile", "color": 0xFF8C00, "hoist": True},
            {"name": "DevOps", "color": 0x9400D3, "hoist": True},
            {"name": "Data Science", "color": 0x00CED1, "hoist": True},
            {"name": "Estudante", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "recursos", "type": "text"},
                ]
            },
            {
                "name": "LINGUAGENS",
                "channels": [
                    {"name": "python", "type": "text"},
                    {"name": "javascript", "type": "text"},
                    {"name": "java", "type": "text"},
                    {"name": "csharp", "type": "text"},
                    {"name": "cpp", "type": "text"},
                    {"name": "rust", "type": "text"},
                    {"name": "go", "type": "text"},
                    {"name": "ruby", "type": "text"},
                ]
            },
            {
                "name": "PROJETOS",
                "channels": [
                    {"name": "showcase", "type": "text"},
                    {"name": "code-review", "type": "text"},
                    {"name": "pair-programming", "type": "text"},
                    {"name": "open-source", "type": "text"},
                    {"name": "dev-voice", "type": "voice"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "duvidas", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["computer", "keyboard", "gear", "zap", "rocket", "atom", "link", "chain"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "rpg": {
        "name": "RPG",
        "description": "Servidor para jogadores de RPG de mesa e digital",
        "color": 0x8B0000,
        "icon": "🎲",
        "roles": [
            {"name": "Mestre", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Mestre NPC", "color": 0x9400D3, "hoist": True},
            {"name": "Guerreiro", "color": 0xDC143C, "hoist": True},
            {"name": "Mago", "color": 0x4169E1, "hoist": True},
            {"name": "Ladino", "color": 0x32CD32, "hoist": True},
            {"name": "Clerigo", "color": 0xFFD700, "hoist": True},
            {"name": "Ranger", "color": 0x228B22, "hoist": True},
            {"name": "Bardo", "color": 0xFF69B4, "hoist": True},
            {"name": "Aventureiro", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "calendario", "type": "text"},
                ]
            },
            {
                "name": "MESAS",
                "channels": [
                    {"name": "procurando-mesa", "type": "text"},
                    {"name": "mesas-ativas", "type": "text"},
                    {"name": "dnd", "type": "text"},
                    {"name": "pathfinder", "type": "text"},
                    {"name": "vampire", "type": "text"},
                    {"name": "call-of-cthulhu", "type": "text"},
                    {"name": "mesa-voice-1", "type": "voice"},
                    {"name": "mesa-voice-2", "type": "voice"},
                ]
            },
            {
                "name": "RECURSOS",
                "channels": [
                    {"name": "fichas", "type": "text"},
                    {"name": "mapas", "type": "text"},
                    {"name": "itens", "type": "text"},
                    {"name": "historias", "type": "text"},
                    {"name": "dice-rolls", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["sword", "shield", "crown", "crystal", "magic", "fire2", "skull", "dragon"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "streaming": {
        "name": "Streaming",
        "description": "Servidor para streamers e criadores de conteudo",
        "color": 0x9146FF,
        "icon": "📺",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Streamer", "color": 0x9146FF, "hoist": True},
            {"name": "Editor", "color": 0xFF69B4, "hoist": True},
            {"name": "Designer", "color": 0x00CED1, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Sub", "color": 0x32CD32, "hoist": True},
            {"name": "Viewer", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "horarios", "type": "text"},
                ]
            },
            {
                "name": "CHAT",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "clips", "type": "text"},
                    {"name": "art", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
            {
                "name": "STREAM",
                "channels": [
                    {"name": "live-chat", "type": "text"},
                    {"name": "sugestoes-stream", "type": "text"},
                    {"name": "sorteios", "type": "text"},
                    {"name": "stream-voice", "type": "voice"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "bugs", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["tv", "microphone", "camera", "trophy", "star", "fire2", "zap", "diamond"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "dark": {
        "name": "Dark",
        "description": "Servidor com estetica dark e misteriosa",
        "color": 0x1A1A2E,
        "icon": "🌑",
        "roles": [
            {"name": "Sombra", "color": 0x000000, "hoist": True, "permissions": "admin"},
            {"name": "Observador", "color": 0x333333, "hoist": True, "permissions": "mod"},
            {"name": "Guardiao", "color": 0x555555, "hoist": True, "permissions": "mod"},
            {"name": "Eclipse", "color": 0x777777, "hoist": True},
            {"name": "Nocturno", "color": 0x999999, "hoist": True},
            {"name": "Sombrio", "color": 0xAAAAAA, "hoist": False},
            {"name": "Penumbra", "color": 0xBBBBBB, "hoist": False},
        ],
        "categories": [
            {
                "name": "VOID",
                "channels": [
                    {"name": "void-anuncios", "type": "announcement"},
                    {"name": "void-regras", "type": "text"},
                    {"name": "void-boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "SHADOWS",
                "channels": [
                    {"name": "shadow-chat", "type": "text"},
                    {"name": "shadow-memes", "type": "text"},
                    {"name": "shadow-art", "type": "text"},
                    {"name": "shadow-voice", "type": "voice"},
                ]
            },
            {
                "name": "ABYSS",
                "channels": [
                    {"name": "abyss-general", "type": "text"},
                    {"name": "abyss-music", "type": "text"},
                    {"name": "abyss-gaming", "type": "text"},
                ]
            },
        ],
        "emojis": ["skull", "skull2", "crystal", "moon", "fire2", "zap", "diamond", "ghost"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "neon": {
        "name": "Neon",
        "description": "Servidor com estetica neon e vibrante",
        "color": 0xFF00FF,
        "icon": "⚡",
        "roles": [
            {"name": "Neon King", "color": 0xFF00FF, "hoist": True, "permissions": "admin"},
            {"name": "Neon Admin", "color": 0x00FFFF, "hoist": True, "permissions": "mod"},
            {"name": "Neon Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Neon VIP", "color": 0xFFFF00, "hoist": True},
            {"name": "Neon User", "color": 0xFF00FF, "hoist": False},
        ],
        "categories": [
            {
                "name": "NEON HUB",
                "channels": [
                    {"name": "neon-anuncios", "type": "announcement"},
                    {"name": "neon-regras", "type": "text"},
                    {"name": "neon-welcome", "type": "text"},
                ]
            },
            {
                "name": "NEON CHAT",
                "channels": [
                    {"name": "neon-general", "type": "text"},
                    {"name": "neon-memes", "type": "text"},
                    {"name": "neon-music", "type": "text"},
                    {"name": "neon-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["zap", "star", "fire2", "diamond", "sparkles", "rocket", "crystal", "gem"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "cyberpunk": {
        "name": "Cyberpunk",
        "description": "Servidor futurista cyberpunk",
        "color": 0x00FF41,
        "icon": "🤖",
        "roles": [
            {"name": "SysAdmin", "color": 0x00FF41, "hoist": True, "permissions": "admin"},
            {"name": "NetRunner", "color": 0x00FFFF, "hoist": True, "permissions": "mod"},
            {"name": "Fixer", "color": 0xFF00FF, "hoist": True, "permissions": "mod"},
            {"name": "Solo", "color": 0xFF0000, "hoist": True},
            {"name": "Techie", "color": 0xFFFF00, "hoist": True},
            {"name": "Corpo", "color": 0x00CED1, "hoist": True},
            {"name": "StreetKid", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "NET",
                "channels": [
                    {"name": "net-anuncios", "type": "announcement"},
                    {"name": "net-regras", "type": "text"},
                    {"name": "net-welcome", "type": "text"},
                ]
            },
            {
                "name": "DATA",
                "channels": [
                    {"name": "data-general", "type": "text"},
                    {"name": "data-hacking", "type": "text"},
                    {"name": "data-tech", "type": "text"},
                    {"name": "data-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["robot", "computer", "zap", "satellite", "rocket", "atom", "gear", "dna"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "musica": {
        "name": "Musica",
        "description": "Servidor para amantes da musica",
        "color": 0xFF1493,
        "icon": "🎵",
        "roles": [
            {"name": "Produtor", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "DJ", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Vocalista", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Instrumentista", "color": 0x0000FF, "hoist": True},
            {"name": "Compositor", "color": 0xFF69B4, "hoist": True},
            {"name": "Fan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "STAGE",
                "channels": [
                    {"name": "stage-anuncios", "type": "announcement"},
                    {"name": "stage-regras", "type": "text"},
                    {"name": "stage-welcome", "type": "text"},
                ]
            },
            {
                "name": "STUDIO",
                "channels": [
                    {"name": "studio-general", "type": "text"},
                    {"name": "studio-releases", "type": "text"},
                    {"name": "studio-collab", "type": "text"},
                    {"name": "studio-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["musical", "notes", "microphone", "headphones", "guitar", "drum", "saxophone", "radio"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "estudo": {
        "name": "Estudo",
        "description": "Servidor para estudantes e aprendizado",
        "color": 0x4169E1,
        "icon": "📚",
        "roles": [
            {"name": "Professor", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Monitor", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Aluno", "color": 0x4169E1, "hoist": True},
            {"name": "Tutor", "color": 0xFF69B4, "hoist": True},
            {"name": "Novato", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "ESCOLA",
                "channels": [
                    {"name": "escola-anuncios", "type": "announcement"},
                    {"name": "escola-regras", "type": "text"},
                    {"name": "escola-welcome", "type": "text"},
                ]
            },
            {
                "name": "MATERIAS",
                "channels": [
                    {"name": "matematica", "type": "text"},
                    {"name": "fisica", "type": "text"},
                    {"name": "quimica", "type": "text"},
                    {"name": "biologia", "type": "text"},
                    {"name": "historia", "type": "text"},
                    {"name": "geografia", "type": "text"},
                    {"name": "portugues", "type": "text"},
                    {"name": "ingles", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "duvidas", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["book", "scroll", "graduation", "light_bulb", "pencil", "pen", "memo", "bookmark"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "marketplace": {
        "name": "Marketplace",
        "description": "Servidor para compras e vendas",
        "color": 0x32CD32,
        "icon": "🛒",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Vendedor", "color": 0x00CED1, "hoist": True},
            {"name": "Comprador", "color": 0x32CD32, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Cliente", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "LOJA",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "VENDAS",
                "channels": [
                    {"name": "produtos", "type": "text"},
                    {"name": "servicos", "type": "text"},
                    {"name": "trocas", "type": "text"},
                    {"name": "leiloes", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "reclamacoes", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["money", "money2", "credit", "receipt", "chart", "shopping", "gift", "package"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "nft": {
        "name": "NFT",
        "description": "Servidor para colecionadores de NFT",
        "color": 0xFFD700,
        "icon": "💎",
        "roles": [
            {"name": "Fundador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Whale", "color": 0x00CED1, "hoist": True},
            {"name": "Collector", "color": 0x32CD32, "hoist": True},
            {"name": "Artist", "color": 0xFF69B4, "hoist": True},
            {"name": "Holder", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "GALLERY",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "COLLECTION",
                "channels": [
                    {"name": "showcase", "type": "text"},
                    {"name": "drops", "type": "text"},
                    {"name": "trades", "type": "text"},
                    {"name": "auctions", "type": "text"},
                ]
            },
            {
                "name": "SUPORTE",
                "channels": [
                    {"name": "ajuda", "type": "text"},
                    {"name": "sugestoes", "type": "text"},
                ]
            },
        ],
        "emojis": ["diamond", "gem", "crystal", "money", "chart", "fire2", "rocket", "star"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "startup": {
        "name": "Startup",
        "description": "Servidor para startups e empreendedores",
        "color": 0xFF6B35,
        "icon": "🚀",
        "roles": [
            {"name": "CEO", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "CTO", "color": 0x0000FF, "hoist": True, "permissions": "mod"},
            {"name": "COO", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Dev", "color": 0x4169E1, "hoist": True},
            {"name": "Marketing", "color": 0xFF69B4, "hoist": True},
            {"name": "Sales", "color": 0x32CD32, "hoist": True},
            {"name": "Investor", "color": 0x00CED1, "hoist": True},
            {"name": "Intern", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "OFFICE",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "TEAMS",
                "channels": [
                    {"name": "dev-team", "type": "text"},
                    {"name": "marketing-team", "type": "text"},
                    {"name": "sales-team", "type": "text"},
                    {"name": "general-team", "type": "text"},
                ]
            },
            {
                "name": "PROJECTS",
                "channels": [
                    {"name": "roadmap", "type": "text"},
                    {"name": "sprints", "type": "text"},
                    {"name": "backlog", "type": "text"},
                    {"name": "meetings", "type": "voice"},
                ]
            },
        ],
        "emojis": ["rocket", "gear", "computer", "chart", "light_bulb", "zap", "satellite", "atom"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "influencer": {
        "name": "Influencer",
        "description": "Servidor para influencers e criadores",
        "color": 0xE1306C,
        "icon": "👑",
        "roles": [
            {"name": "Influencer", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Manager", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Editor", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Designer", "color": 0xFF69B4, "hoist": True},
            {"name": "VIP", "color": 0x00CED1, "hoist": True},
            {"name": "Fan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "HUB",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "COMMUNITY",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "fan-art", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
        ],
        "emojis": ["crown", "star", "fire2", "diamond", "camera", "microphone", "tv", "trophy"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "youtube": {
        "name": "YouTube",
        "description": "Servidor para criadores do YouTube",
        "color": 0xFF0000,
        "icon": "📺",
        "roles": [
            {"name": "Criador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Editor", "color": 0xFF69B4, "hoist": True},
            {"name": "Thumbnail", "color": 0x00CED1, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Subscriber", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CHANNEL",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "uploads", "type": "text"},
                ]
            },
            {
                "name": "STUDIO",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "video-ideas", "type": "text"},
                    {"name": "feedback", "type": "text"},
                    {"name": "collab", "type": "text"},
                    {"name": "studio-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["tv", "camera", "microphone", "trophy", "star", "fire2", "zap", "diamond"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "tiktok": {
        "name": "TikTok",
        "description": "Servidor para criadores do TikTok",
        "color": 0x000000,
        "icon": "🎵",
        "roles": [
            {"name": "Criador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Editor", "color": 0xFF69B4, "hoist": True},
            {"name": "Dancer", "color": 0x00CED1, "hoist": True},
            {"name": "VIP", "color": 0xFFD700, "hoist": True},
            {"name": "Fan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "FOR YOU",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "FYP",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "trends", "type": "text"},
                    {"name": "duet", "type": "text"},
                    {"name": "sounds", "type": "text"},
                    {"name": "fyp-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["musical", "notes", "camera", "star", "fire2", "zap", "diamond", "trophy"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "roleplay": {
        "name": "Roleplay",
        "description": "Servidor para roleplay e interpretacao",
        "color": 0x800080,
        "icon": "🎭",
        "roles": [
            {"name": "Narrador", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Veterano", "color": 0x00CED1, "hoist": True},
            {"name": "Personagem", "color": 0x32CD32, "hoist": True},
            {"name": "Novo", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CENARIO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "lore", "type": "text"},
                ]
            },
            {
                "name": "HISTORIA",
                "channels": [
                    {"name": "rp-geral", "type": "text"},
                    {"name": "rp-cidade", "type": "text"},
                    {"name": "rp-floresta", "type": "text"},
                    {"name": "rp-castelo", "type": "text"},
                    {"name": "rp-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["scroll", "crown", "sword", "shield", "crystal", "magic", "fire2", "skull"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "militar": {
        "name": "Militar",
        "description": "Servidor com tema militar",
        "color": 0x556B2F,
        "icon": "🛡️",
        "roles": [
            {"name": "General", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Coronel", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Major", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Capitao", "color": 0x0000FF, "hoist": True},
            {"name": "Sargento", "color": 0xFF8C00, "hoist": True},
            {"name": "Soldado", "color": 0x32CD32, "hoist": True},
            {"name": "Recruta", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "QUARTEL",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "OPERACOES",
                "channels": [
                    {"name": "missao", "type": "text"},
                    {"name": "estrategia", "type": "text"},
                    {"name": "intel", "type": "text"},
                    {"name": "comando-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["shield", "sword", "crown", "trophy", "medal", "flag", "banner", "scroll"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "fantasia": {
        "name": "Fantasia",
        "description": "Servidor com tema fantasia medieval",
        "color": 0x9932CC,
        "icon": "🐉",
        "roles": [
            {"name": "Rei", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Mago Supremo", "color": 0x9400D3, "hoist": True, "permissions": "mod"},
            {"name": "Cavaleiro", "color": 0xC0C0C0, "hoist": True, "permissions": "mod"},
            {"name": "Arqueiro", "color": 0x228B22, "hoist": True},
            {"name": "Feiticeiro", "color": 0x4169E1, "hoist": True},
            {"name": "Ladino", "color": 0x32CD32, "hoist": True},
            {"name": "Bardo", "color": 0xFF69B4, "hoist": True},
            {"name": "Campones", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "REINO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "lore", "type": "text"},
                ]
            },
            {
                "name": "AVENTURA",
                "channels": [
                    {"name": "taverna", "type": "text"},
                    {"name": "mercado", "type": "text"},
                    {"name": "guilda", "type": "text"},
                    {"name": "masmorra", "type": "text"},
                    {"name": "aventura-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["magic", "crystal", "crown", "sword", "shield", "dragon", "fire2", "star"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "terror": {
        "name": "Terror",
        "description": "Servidor com tema horror e terror",
        "color": 0x8B0000,
        "icon": "💀",
        "roles": [
            {"name": "Mestre do Medo", "color": 0x8B0000, "hoist": True, "permissions": "admin"},
            {"name": "Cacador", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Sobrevivente", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Cacador de Fantasmas", "color": 0x9400D3, "hoist": True},
            {"name": "Vitima", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CEMITERIO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "HORROR",
                "channels": [
                    {"name": "historias", "type": "text"},
                    {"name": "filmes", "type": "text"},
                    {"name": "jogos-terror", "type": "text"},
                    {"name": "cemiterio-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["skull", "skull2", "ghost", "crystal", "moon", "fire2", "zap", "diamond"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "space": {
        "name": "Space",
        "description": "Servidor com tema espacial",
        "color": 0x000080,
        "icon": "🚀",
        "roles": [
            {"name": "Comandante", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Piloto", "color": 0x0000FF, "hoist": True, "permissions": "mod"},
            {"name": "Engenheiro", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Cientista", "color": 0x9400D3, "hoist": True},
            {"name": "Astronauta", "color": 0x00CED1, "hoist": True},
            {"name": "Cadete", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "BASE",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "GALAXY",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "astronomia", "type": "text"},
                    {"name": "foguetes", "type": "text"},
                    {"name": "space-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["rocket", "satellite", "earth", "moon", "star", "comet", "telescope", "atom"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "medieval": {
        "name": "Medieval",
        "description": "Servidor com tema medieval",
        "color": 0x8B4513,
        "icon": "🏰",
        "roles": [
            {"name": "Rei", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Rainha", "color": 0xFF69B4, "hoist": True, "permissions": "mod"},
            {"name": "Cavaleiro", "color": 0xC0C0C0, "hoist": True, "permissions": "mod"},
            {"name": "Arqueiro", "color": 0x228B22, "hoist": True},
            {"name": "Ferreiro", "color": 0x696969, "hoist": True},
            {"name": "Mercenario", "color": 0x8B0000, "hoist": True},
            {"name": "Campones", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "CASTELO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                    {"name": "lore", "type": "text"},
                ]
            },
            {
                "name": "REINO",
                "channels": [
                    {"name": "taverna", "type": "text"},
                    {"name": "mercado", "type": "text"},
                    {"name": "arena", "type": "text"},
                    {"name": "castelo-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["crown", "sword", "shield", "scroll", "crystal", "magic", "fire2", "trophy"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "minimalista": {
        "name": "Minimalista",
        "description": "Servidor com design minimalista e clean",
        "color": 0xFFFFFF,
        "icon": "◻️",
        "roles": [
            {"name": "Admin", "color": 0x000000, "hoist": True, "permissions": "admin"},
            {"name": "Mod", "color": 0x333333, "hoist": True, "permissions": "mod"},
            {"name": "Membro", "color": 0x666666, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "welcome", "type": "text"},
                ]
            },
            {
                "name": "CHAT",
                "channels": [
                    {"name": "geral", "type": "text"},
                    {"name": "media", "type": "text"},
                    {"name": "voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["circle", "square", "diamond", "star", "zap", "fire2", "crown", "shield"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "comunidade": {
        "name": "Comunidade",
        "description": "Servidor de comunidade geral",
        "color": 0x5865F2,
        "icon": "🤝",
        "roles": [
            {"name": "Dono", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "VIP", "color": 0x00CED1, "hoist": True},
            {"name": "Membro", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "INFORMACOES",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "GERAL",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "memes", "type": "text"},
                    {"name": "media", "type": "text"},
                    {"name": "lobby", "type": "voice"},
                ]
            },
        ],
        "emojis": ["star", "fire2", "diamond", "heart", "sparkles", "rocket", "crown", "shield"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "e-girl": {
        "name": "E-Girl",
        "description": "Servidor com estetica e-girl",
        "color": 0xFF69B4,
        "icon": "💕",
        "roles": [
            {"name": "Queen", "color": 0xFF69B4, "hoist": True, "permissions": "admin"},
            {"name": "Princess", "color": 0xFF1493, "hoist": True, "permissions": "mod"},
            {"name": "Kawaii", "color": 0xFFB6C1, "hoist": True},
            {"name": "Aesthetic", "color": 0xDDA0DD, "hoist": True},
            {"name": "Soft Girl", "color": 0xF0E68C, "hoist": False},
        ],
        "categories": [
            {
                "name": "AESTHETIC",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "SOFT",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "aesthetic", "type": "text"},
                    {"name": "makeup", "type": "text"},
                    {"name": "fashion", "type": "text"},
                    {"name": "soft-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["crown", "diamond", "sparkles", "heart", "lipstick", "nail", "ribbon", "star"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "k-pop": {
        "name": "K-Pop",
        "description": "Servidor para fas de K-Pop",
        "color": 0xFF69B4,
        "icon": "🎤",
        "roles": [
            {"name": "Presidente", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Ult Bias", "color": 0xFF69B4, "hoist": True},
            {"name": "Bias Wrecker", "color": 0x00CED1, "hoist": True},
            {"name": "Stan", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "STAGE",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "FANDOM",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "comebacks", "type": "text"},
                    {"name": "fanarts", "type": "text"},
                    {"name": "mv-reactions", "type": "text"},
                    {"name": "kpop-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["musical", "notes", "microphone", "star", "sparkles", "heart", "diamond", "crown"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },

    "otaku": {
        "name": "Otaku",
        "description": "Servidor para otakus e fas de cultura japonesa",
        "color": 0xFF1493,
        "icon": "🌸",
        "roles": [
            {"name": "Sensei", "color": 0xFFD700, "hoist": True, "permissions": "admin"},
            {"name": "Admin", "color": 0xFF0000, "hoist": True, "permissions": "mod"},
            {"name": "Mod", "color": 0x00FF00, "hoist": True, "permissions": "mod"},
            {"name": "Senpai", "color": 0xFF69B4, "hoist": True},
            {"name": "Kouhai", "color": 0x00CED1, "hoist": True},
            {"name": "Weeb", "color": 0x808080, "hoist": False},
        ],
        "categories": [
            {
                "name": "DOJO",
                "channels": [
                    {"name": "anuncios", "type": "announcement"},
                    {"name": "regras", "type": "text"},
                    {"name": "boas-vindas", "type": "text"},
                ]
            },
            {
                "name": "ANIME",
                "channels": [
                    {"name": "chat-geral", "type": "text"},
                    {"name": "recomendacoes", "type": "text"},
                    {"name": "manga", "type": "text"},
                    {"name": "cosplay", "type": "text"},
                    {"name": "otaku-voice", "type": "voice"},
                ]
            },
        ],
        "emojis": ["star", "sparkles", "magic", "fire", "diamond", "crystal", "heart", "ribbon"],
        "server_settings": {
            "default_notifications": discord.NotificationLevel.only_mentions,
            "verification_level": discord.VerificationLevel.medium,
            "explicit_content_filter": discord.ContentFilter.all_members,
        }
    },
}

# Mesclar temas adicionais
THEMES.update(ADDITIONAL_THEMES)

# Lista de todos os temas disponiveis
ALL_THEMES = list(THEMES.keys())

# =============================================================================
# VIEWS, MODALS E SISTEMA DE INTERACAO
# =============================================================================

class ServerNameModal(discord.ui.Modal, title="Nome do Servidor"):
    """Modal para alterar o nome do servidor"""
    name = discord.ui.TextInput(
        label="Novo nome do servidor",
        placeholder="Digite o nome desejado...",
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"{EMOJIS['success']} Nome definido: **{self.name.value}**",
            ephemeral=True
        )

class ServerDescriptionModal(discord.ui.Modal, title="Descricao do Servidor"):
    """Modal para adicionar descricao ao servidor"""
    description = discord.ui.TextInput(
        label="Descricao do servidor",
        placeholder="Descreva seu servidor...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"{EMOJIS['success']} Descricao definida com sucesso!",
            ephemeral=True
        )

class CustomThemeModal(discord.ui.Modal, title="Tema Personalizado"):
    """Modal para tema personalizado"""
    theme = discord.ui.TextInput(
        label="Descreva seu tema",
        placeholder="Ex: Servidor hacker vermelho futurista...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"{EMOJIS['success']} Tema personalizado recebido: **{self.theme.value}**",
            ephemeral=True
        )

class ColorSelectView(discord.ui.View):
    """View para selecionar cores principais"""
    def __init__(self):
        super().__init__(timeout=120)
        self.selected_color = None

    @discord.ui.select(
        placeholder="Escolha a cor principal...",
        options=[
            discord.SelectOption(label="Vermelho", value="0xFF0000", emoji="🔴"),
            discord.SelectOption(label="Azul", value="0x0000FF", emoji="🔵"),
            discord.SelectOption(label="Verde", value="0x00FF00", emoji="🟢"),
            discord.SelectOption(label="Roxo", value="0x800080", emoji="🟣"),
            discord.SelectOption(label="Laranja", value="0xFFA500", emoji="🟠"),
            discord.SelectOption(label="Amarelo", value="0xFFFF00", emoji="🟡"),
            discord.SelectOption(label="Rosa", value="0xFF69B4", emoji="🩷"),
            discord.SelectOption(label="Preto", value="0x000000", emoji="⚫"),
            discord.SelectOption(label="Branco", value="0xFFFFFF", emoji="⚪"),
            discord.SelectOption(label="Ciano", value="0x00FFFF", emoji="🔷"),
        ]
    )
    async def color_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_color = int(select.values[0], 16)
        await interaction.response.send_message(
            f"{EMOJIS['success']} Cor selecionada!",
            ephemeral=True
        )

class QuantitySelectView(discord.ui.View):
    """View para selecionar quantidade de canais e cargos"""
    def __init__(self):
        super().__init__(timeout=120)
        self.channels_count = 10
        self.roles_count = 5

    @discord.ui.select(
        placeholder="Quantidade de canais...",
        options=[
            discord.SelectOption(label="Minimo (5)", value="5"),
            discord.SelectOption(label="Basico (10)", value="10"),
            discord.SelectOption(label="Padrao (15)", value="15"),
            discord.SelectOption(label="Completo (20)", value="20"),
            discord.SelectOption(label="Maximo (25)", value="25"),
        ]
    )
    async def channels_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.channels_count = int(select.values[0])
        await interaction.response.send_message(
            f"{EMOJIS['success']} {self.channels_count} canais selecionados!",
            ephemeral=True
        )

    @discord.ui.select(
        placeholder="Quantidade de cargos...",
        options=[
            discord.SelectOption(label="Minimo (3)", value="3"),
            discord.SelectOption(label="Basico (5)", value="5"),
            discord.SelectOption(label="Padrao (8)", value="8"),
            discord.SelectOption(label="Completo (10)", value="10"),
            discord.SelectOption(label="Maximo (15)", value="15"),
        ]
    )
    async def roles_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.roles_count = int(select.values[0])
        await interaction.response.send_message(
            f"{EMOJIS['success']} {self.roles_count} cargos selecionados!",
            ephemeral=True
        )
class ThemeSelectView(discord.ui.View):
    """View principal para selecao de temas"""
    def __init__(self):
        super().__init__(timeout=300)
        self.selected_theme = None
        self.custom_theme = None
        self.server_name = None
        self.server_description = None
        self.server_color = None
        self.channels_count = 10
        self.roles_count = 5

    @discord.ui.select(
        placeholder="Escolha um tema pronto...",
        options=[
            discord.SelectOption(label="Anime", value="anime", emoji="🎌", description="Cultura japonesa e anime"),
            discord.SelectOption(label="Gaming", value="gaming", emoji="🎮", description="Comunidade gamer"),
            discord.SelectOption(label="Minecraft", value="minecraft", emoji="⛏️", description="Universo Minecraft"),
            discord.SelectOption(label="Roblox", value="roblox", emoji="🎮", description="Universo Roblox"),
            discord.SelectOption(label="Tecnologia", value="tecnologia", emoji="💻", description="Tech e inovacao"),
            discord.SelectOption(label="Programacao", value="programacao", emoji="💻", description="Dev e codigo"),
            discord.SelectOption(label="RPG", value="rpg", emoji="🎲", description="RPG de mesa"),
            discord.SelectOption(label="Streaming", value="streaming", emoji="📺", description="Streamers"),
            discord.SelectOption(label="Dark", value="dark", emoji="🌑", description="Estetica dark"),
            discord.SelectOption(label="Neon", value="neon", emoji="⚡", description="Estetica neon"),
            discord.SelectOption(label="Cyberpunk", value="cyberpunk", emoji="🤖", description="Futurista"),
            discord.SelectOption(label="Musica", value="musica", emoji="🎵", description="Amantes da musica"),
            discord.SelectOption(label="Estudo", value="estudo", emoji="📚", description="Aprendizado"),
            discord.SelectOption(label="Marketplace", value="marketplace", emoji="🛒", description="Compras e vendas"),
            discord.SelectOption(label="NFT", value="nft", emoji="💎", description="Colecionadores"),
            discord.SelectOption(label="Startup", value="startup", emoji="🚀", description="Empreendedores"),
            discord.SelectOption(label="Influencer", value="influencer", emoji="👑", description="Criadores"),
            discord.SelectOption(label="YouTube", value="youtube", emoji="📺", description="YouTubers"),
            discord.SelectOption(label="TikTok", value="tiktok", emoji="🎵", description="TikTokers"),
            discord.SelectOption(label="Roleplay", value="roleplay", emoji="🎭", description="Interpretacao"),
            discord.SelectOption(label="Militar", value="militar", emoji="🛡️", description="Tema militar"),
            discord.SelectOption(label="Fantasia", value="fantasia", emoji="🐉", description="Medieval fantasy"),
            discord.SelectOption(label="Terror", value="terror", emoji="💀", description="Horror"),
            discord.SelectOption(label="Space", value="space", emoji="🚀", description="Espacial"),
            discord.SelectOption(label="Medieval", value="medieval", emoji="🏰", description="Era medieval"),
        ]
    )
    async def theme_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_theme = select.values[0]
        theme_data = THEMES.get(self.selected_theme)
        if theme_data:
            embed = discord.Embed(
                title="Tema Selecionado",
                description=f"**{theme_data['name']}** - {theme_data['description']}",
                color=theme_data['color']
            )
            embed.add_field(name="Cargos", value=str(len(theme_data['roles'])), inline=True)
            embed.add_field(name="Canais", value=str(sum(len(c['channels']) for c in theme_data['categories'])), inline=True)
            embed.add_field(name="Categorias", value=str(len(theme_data['categories'])), inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "Tema nao encontrado!",
                ephemeral=True
            )
    @discord.ui.button(label="Tema Personalizado", style=discord.ButtonStyle.secondary, emoji="🎨")
    async def custom_theme_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CustomThemeModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Mudar Nome", style=discord.ButtonStyle.secondary, emoji="✏️")
    async def name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ServerNameModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Descricao", style=discord.ButtonStyle.secondary, emoji="📝")
    async def description_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ServerDescriptionModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Cores", style=discord.ButtonStyle.secondary, emoji="🎨")
    async def color_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ColorSelectView()
        await interaction.response.send_message(
            "Escolha a cor principal:",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(label="Quantidades", style=discord.ButtonStyle.secondary, emoji="📊")
    async def quantity_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = QuantitySelectView()
        await interaction.response.send_message(
            "Escolha as quantidades:",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(label="Criar Servidor!", style=discord.ButtonStyle.success, emoji="🚀")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_theme:
            await interaction.response.send_message(
                f"{EMOJIS['error']} Selecione um tema primeiro!",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    f"{EMOJIS['error']} Este comando so funciona em servidores!",
                    ephemeral=True
                )
                return

            # Verificar permissoes
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    f"{EMOJIS['error']} Voce precisa ser administrador!",
                    ephemeral=True
                )
                return

            # Verificar cooldown
            cooldown_key = f"create_{interaction.user.id}"
            if hasattr(bot, '_cooldowns') and cooldown_key in bot._cooldowns:
                if (datetime.now() - bot._cooldowns[cooldown_key]).seconds < CONFIG["limits"]["creation_cooldown"]:
                    await interaction.followup.send(
                        f"{EMOJIS['warning']} Aguarde o cooldown!",
                        ephemeral=True
                    )
                    return

            if not hasattr(bot, '_cooldowns'):
                bot._cooldowns = {}
            bot._cooldowns[cooldown_key] = datetime.now()

            # Iniciar criacao
            theme_data = THEMES[self.selected_theme]

            embed = discord.Embed(
                title=f"{EMOJIS['rocket']} Criando Servidor...",
                description=f"Aplicando tema: **{theme_data['name']}**",
                color=COLORS["info"]
            )
            progress_msg = await interaction.followup.send(embed=embed, ephemeral=True)

            # Criar cargos
            created_roles = {}
            for role_data in theme_data['roles']:
                try:
                    role = await guild.create_role(
                        name=role_data['name'],
                        color=discord.Color(role_data['color']),
                        hoist=role_data.get('hoist', False),
                        mentionable=True
                    )
                    created_roles[role_data['name']] = role
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Erro ao criar cargo {role_data['name']}: {e}")

            # Atualizar progresso
            embed.description = f"Cargos criados: {len(created_roles)}"
            await progress_msg.edit(embed=embed)

            # Criar categorias e canais
            created_channels = []
            for category_data in theme_data['categories']:
                try:
                    # Criar categoria
                    category = await guild.create_category(
                        name=category_data['name'],
                        reason=f"Server Creator - Tema: {theme_data['name']}"
                    )

                    # Criar canais na categoria
                    for channel_data in category_data['channels']:
                        try:
                            if channel_data['type'] == 'text':
                                channel = await guild.create_text_channel(
                                    name=channel_data['name'],
                                    category=category,
                                    reason=f"Server Creator"
                                )
                            elif channel_data['type'] == 'voice':
                                channel = await guild.create_voice_channel(
                                    name=channel_data['name'],
                                    category=category,
                                    reason=f"Server Creator"
                                )
                            elif channel_data['type'] == 'announcement':
                                channel = await guild.create_text_channel(
                                    name=channel_data['name'],
                                    category=category,
                                    reason=f"Server Creator",
                                    news=True
                                )
                            created_channels.append(channel)
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            logger.error(f"Erro ao criar canal {channel_data['name']}: {e}")

                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Erro ao criar categoria {category_data['name']}: {e}")

            # Configurar servidor
            try:
                if theme_data.get('server_settings'):
                    settings = theme_data['server_settings']
                    await guild.edit(
                        default_notifications=settings.get('default_notifications', discord.NotificationLevel.only_mentions),
                        verification_level=settings.get('verification_level', discord.VerificationLevel.medium),
                        explicit_content_filter=settings.get('explicit_content_filter', discord.ContentFilter.all_members)
                    )
            except Exception as e:
                logger.error(f"Erro ao configurar servidor: {e}")

            # Salvar no banco de dados
            async with aiosqlite.connect(bot.db_path) as db:
                await db.execute(
                    "INSERT INTO creations (guild_id, user_id, theme, channels_count, roles_count) VALUES (?, ?, ?, ?, ?)",
                    (str(guild.id), str(interaction.user.id), self.selected_theme, len(created_channels), len(created_roles))
                )
                await db.commit()

            # Log
            await bot.log_action(guild.id, interaction.user.id, "SERVER_CREATED", f"Tema: {self.selected_theme}")

            # Embed final
            final_embed = discord.Embed(
                title=f"{EMOJIS['success']} Servidor Criado!",
                description=f"O tema **{theme_data['name']}** foi aplicado com sucesso!",
                color=COLORS["success"]
            )
            final_embed.add_field(name="Cargos", value=str(len(created_roles)), inline=True)
            final_embed.add_field(name="Canais", value=str(len(created_channels)), inline=True)
            final_embed.add_field(name="Categorias", value=str(len(theme_data['categories'])), inline=True)
            final_embed.set_footer(text=f"Criado por {interaction.user.name}")

            await progress_msg.edit(embed=final_embed)

        except Exception as e:
            logger.error(f"Erro na criacao do servidor: {e}")
            await interaction.followup.send(
                f"{EMOJIS['error']} Erro ao criar servidor: {str(e)}",
                ephemeral=True
            )
class IdeasView(discord.ui.View):
    """View para sugestoes de ideias"""
    
    IDEAS = [
        ("Comunidade Gamer", "gaming", "Uma comunidade para jogadores se conectarem"),
        ("Servidor de Estudos", "estudo", "Ambiente focado em aprendizado"),
        ("Fandom Anime", "anime", "Para fas de anime e manga"),
        ("Servidor de Musica", "musica", "Para musicos e amantes da musica"),
        ("Cla de Jogos", "gaming", "Organizacao de times e clans"),
        ("Servidor de Edicao", "streaming", "Para editores de video"),
        ("Comunidade Dev", "programacao", "Para desenvolvedores"),
        ("RPG Medieval", "rpg", "Aventuras de RPG de mesa"),
        ("Roleplay Moderno", "roleplay", "Interpretacao em cenario moderno"),
        ("Servidor Tech", "tecnologia", "Tecnologia e inovacao"),
        ("Canal de Arte", "comunidade", "Para artistas e criativos"),
        ("Servidor Fitness", "comunidade", "Saude e bem-estar"),
        ("Comunidade K-Pop", "k-pop", "Para fas de K-Pop"),
        ("Servidor Crypto", "nft", "Criptomoedas e NFTs"),
        ("Startup Hub", "startup", "Para empreendedores"),
    ]

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        placeholder="Clique para ver ideias...",
        options=[
            discord.SelectOption(label=idea[0], value=idea[1], description=idea[2])
            for idea in IDEAS[:25]
        ]
    )
    async def idea_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        theme = select.values[0]
        theme_data = THEMES.get(theme)
        if theme_data:
            embed = discord.Embed(
                title="Ideia Selecionada",
                description=f"**{theme_data['name']}** - {theme_data['description']}",
                color=theme_data['color']
            )
            embed.add_field(
                name="Como criar",
                value="Use /create e selecione este tema!",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
# =============================================================================
# COMANDOS SLASH
# =============================================================================

@bot.tree.command(name="create", description="Crie um servidor completo automaticamente")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: i.guild_id)
async def create_command(interaction: discord.Interaction):
    """Comando principal para criar servidor"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title=f"{EMOJIS['rocket']} Server Creator Pro",
        description="Bem-vindo ao criador de servidores! Escolha um tema abaixo para comecar.",
        color=COLORS["primary"]
    )
    embed.add_field(
        name="Como funciona",
        value="1. Selecione um tema pronto ou personalize\n2. Ajuste nome, descricao e cores\n3. Clique em 'Criar Servidor!'",
        inline=False
    )
    embed.add_field(
        name="Temas disponiveis",
        value=f"{len(ALL_THEMES)} temas prontos!",
        inline=True
    )
    embed.set_footer(text="Use os botoes abaixo para personalizar")

    view = ThemeSelectView()
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="ideas", description="Obtenha ideias criativas para servidores")
async def ideas_command(interaction: discord.Interaction):
    """Comando para sugestoes de ideias"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title=f"{EMOJIS['bulb']} Ideias de Servidores",
        description="Selecione uma ideia abaixo para ver mais detalhes!",
        color=COLORS["info"]
    )

    view = IdeasView()
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="backup", description="Crie um backup do servidor atual")
@app_commands.checks.has_permissions(administrator=True)
async def backup_command(interaction: discord.Interaction, name: str = None):
    """Comando para criar backup"""
    await interaction.response.defer(ephemeral=True)

    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send(
                f"{EMOJIS['error']} Este comando so funciona em servidores!",
                ephemeral=True
            )
            return

        # Coletar dados do servidor
        backup_data = {
            "name": guild.name,
            "description": guild.description,
            "roles": [],
            "categories": [],
            "channels": [],
            "created_at": datetime.now().isoformat()
        }

        # Salvar cargos
        for role in guild.roles:
            if role.is_default():
                continue
            backup_data["roles"].append({
                "name": role.name,
                "color": role.color.value,
                "hoist": role.hoist,
                "permissions": role.permissions.value,
                "mentionable": role.mentionable
            })

        # Salvar categorias e canais
        for category in guild.categories:
            cat_data = {
                "name": category.name,
                "position": category.position,
                "channels": []
            }
            for channel in category.channels:
                cat_data["channels"].append({
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position
                })
            backup_data["categories"].append(cat_data)

        # Salvar no banco
        backup_name = name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        async with aiosqlite.connect(bot.db_path) as db:
            await db.execute(
                "INSERT INTO backups (guild_id, user_id, backup_data, name) VALUES (?, ?, ?, ?)",
                (str(guild.id), str(interaction.user.id), json.dumps(backup_data), backup_name)
            )
            await db.commit()

        await bot.log_action(guild.id, interaction.user.id, "BACKUP_CREATED", f"Nome: {backup_name}")

        embed = discord.Embed(
            title=f"{EMOJIS['success']} Backup Criado!",
            description=f"Backup **{backup_name}** salvo com sucesso!",
            color=COLORS["success"]
        )
        embed.add_field(name="Cargos", value=str(len(backup_data["roles"])), inline=True)
        embed.add_field(name="Categorias", value=str(len(backup_data["categories"])), inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        await interaction.followup.send(
            f"{EMOJIS['error']} Erro ao criar backup: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="restore", description="Restaure um backup do servidor")
@app_commands.checks.has_permissions(administrator=True)
async def restore_command(interaction: discord.Interaction, backup_id: int = None):
    """Comando para restaurar backup"""
    await interaction.response.defer(ephemeral=True)

    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send(
                f"{EMOJIS['error']} Este comando so funciona em servidores!",
                ephemeral=True
            )
            return

        # Buscar backups
        async with aiosqlite.connect(bot.db_path) as db:
            if backup_id:
                cursor = await db.execute(
                    "SELECT backup_data, name FROM backups WHERE id = ? AND guild_id = ?",
                    (backup_id, str(guild.id))
                )
            else:
                cursor = await db.execute(
                    "SELECT backup_data, name FROM backups WHERE guild_id = ? ORDER BY created_at DESC LIMIT 1",
                    (str(guild.id),)
                )
            row = await cursor.fetchone()

        if not row:
            await interaction.followup.send(
                f"{EMOJIS['error']} Nenhum backup encontrado!",
                ephemeral=True
            )
            return

        backup_data = json.loads(row[0])

        # Restaurar cargos
        for role_data in backup_data.get("roles", []):
            try:
                await guild.create_role(
                    name=role_data["name"],
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    permissions=discord.Permissions(role_data["permissions"]),
                    mentionable=role_data["mentionable"]
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Erro ao restaurar cargo: {e}")

        await bot.log_action(guild.id, interaction.user.id, "BACKUP_RESTORED", f"Nome: {row[1]}")

        embed = discord.Embed(
            title=f"{EMOJIS['success']} Backup Restaurado!",
            description=f"Backup **{row[1]}** restaurado com sucesso!",
            color=COLORS["success"]
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {e}")
        await interaction.followup.send(
            f"{EMOJIS['error']} Erro ao restaurar backup: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="template", description="Salve o servidor atual como template")
@app_commands.checks.has_permissions(administrator=True)
async def template_command(interaction: discord.Interaction, name: str):
    """Comando para salvar template"""
    await interaction.response.defer(ephemeral=True)

    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send(
                f"{EMOJIS['error']} Este comando so funciona em servidores!",
                ephemeral=True
            )
            return

        # Coletar estrutura
        template_data = {
            "name": guild.name,
            "roles": [],
            "categories": [],
            "created_at": datetime.now().isoformat()
        }

        for role in guild.roles:
            if role.is_default():
                continue
            template_data["roles"].append({
                "name": role.name,
                "color": role.color.value,
                "hoist": role.hoist,
                "permissions": role.permissions.value
            })

        for category in guild.categories:
            cat_data = {"name": category.name, "channels": []}
            for channel in category.channels:
                cat_data["channels"].append({
                    "name": channel.name,
                    "type": str(channel.type)
                })
            template_data["categories"].append(cat_data)

        # Salvar no banco
        async with aiosqlite.connect(bot.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO templates (name, theme, data, created_by) VALUES (?, ?, ?, ?)",
                (name, "custom", json.dumps(template_data), str(interaction.user.id))
            )
            await db.commit()

        bot.templates_cache[name] = template_data

        await bot.log_action(guild.id, interaction.user.id, "TEMPLATE_SAVED", f"Nome: {name}")

        embed = discord.Embed(
            title=f"{EMOJIS['success']} Template Salvo!",
            description=f"Template **{name}** salvo com sucesso!",
            color=COLORS["success"]
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Erro ao salvar template: {e}")
        await interaction.followup.send(
            f"{EMOJIS['error']} Erro ao salvar template: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="logs", description="Veja os logs do servidor")
@app_commands.checks.has_permissions(administrator=True)
async def logs_command(interaction: discord.Interaction, limit: int = 10):
    """Comando para ver logs"""
    await interaction.response.defer(ephemeral=True)

    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send(
                f"{EMOJIS['error']} Este comando so funciona em servidores!",
                ephemeral=True
            )
            return

        async with aiosqlite.connect(bot.db_path) as db:
            cursor = await db.execute(
                "SELECT action, details, timestamp FROM logs WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
                (str(guild.id), limit)
            )
            rows = await cursor.fetchall()

        if not rows:
            await interaction.followup.send(
                f"{EMOJIS['info']} Nenhum log encontrado!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{EMOJIS['gear']} Logs do Servidor",
            color=COLORS["info"]
        )

        for row in rows:
            embed.add_field(
                name=f"{row[0]} - {row[2]}",
                value=row[1] or "Sem detalhes",
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Erro ao buscar logs: {e}")
        await interaction.followup.send(
            f"{EMOJIS['error']} Erro ao buscar logs: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="stats", description="Estatisticas do bot")
async def stats_command(interaction: discord.Interaction):
    """Comando para estatisticas"""
    try:
        async with aiosqlite.connect(bot.db_path) as db:
            # Total de criacoes
            cursor = await db.execute("SELECT COUNT(*) FROM creations")
            total_creations = (await cursor.fetchone())[0]

            # Total de backups
            cursor = await db.execute("SELECT COUNT(*) FROM backups")
            total_backups = (await cursor.fetchone())[0]

            # Total de templates
            cursor = await db.execute("SELECT COUNT(*) FROM templates")
            total_templates = (await cursor.fetchone())[0]

        embed = discord.Embed(
            title=f"{EMOJIS['info']} Estatisticas",
            description=f"**{CONFIG['bot']['name']}** v{CONFIG['bot']['version']}",
            color=COLORS["info"]
        )
        embed.add_field(name="Servidores Criados", value=str(total_creations), inline=True)
        embed.add_field(name="Backups", value=str(total_backups), inline=True)
        embed.add_field(name="Templates", value=str(total_templates), inline=True)
        embed.add_field(name="Temas Disponiveis", value=str(len(ALL_THEMES)), inline=True)
        embed.add_field(name="Servidores", value=str(len(bot.guilds)), inline=True)
        embed.add_field(name="Latencia", value=f"{round(bot.latency * 1000)}ms", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Erro ao buscar stats: {e}")
        await interaction.response.send_message(
            f"{EMOJIS['error']} Erro ao buscar estatisticas: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="help", description="Ajuda do bot")
async def help_command(interaction: discord.Interaction):
    """Comando de ajuda"""
    embed = discord.Embed(
        title=f"{EMOJIS['info']} Ajuda - {CONFIG['bot']['name']}",
        description="Bot avancado para criacao automatica de servidores Discord",
        color=COLORS["primary"]
    )

    commands_info = [
        ("/create", "Cria um servidor completo automaticamente"),
        ("/ideas", "Sugestoes criativas de servidores"),
        ("/backup", "Cria backup do servidor atual"),
        ("/restore", "Restaura um backup"),
        ("/template", "Salva servidor como template"),
        ("/logs", "Veja logs do servidor"),
        ("/stats", "Estatisticas do bot"),
        ("/help", "Mostra esta mensagem"),
    ]

    for cmd, desc in commands_info:
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.add_field(
        name="Temas disponiveis",
        value=f"{len(ALL_THEMES)} temas prontos + tema personalizado",
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

# =============================================================================
# EVENTOS
# =============================================================================

@bot.event
async def on_ready():
    """Evento quando o bot esta pronto"""
    logger.info(f"Bot conectado como {bot.user.name} ({bot.user.id})")
    logger.info(f"Servidores: {len(bot.guilds)}")

    # Status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"/create | {len(ALL_THEMES)} temas"
        ),
        status=discord.Status.online
    )

@bot.event
async def on_guild_join(guild):
    """Evento quando o bot entra em um servidor"""
    logger.info(f"Entrou no servidor: {guild.name} ({guild.id})")
    await bot.log_action(guild.id, bot.user.id, "BOT_JOINED", f"Servidor: {guild.name}")

@bot.event
async def on_guild_remove(guild):
    """Evento quando o bot sai de um servidor"""
    logger.info(f"Saiu do servidor: {guild.name} ({guild.id})")

@bot.event
async def on_command_error(ctx, error):
    """Tratamento de erros"""
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{EMOJIS['warning']} Aguarde {error.retry_after:.1f}s para usar novamente!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{EMOJIS['error']} Voce nao tem permissao para usar este comando!")
    else:
        logger.error(f"Erro no comando: {error}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Tratamento de erros em slash commands"""
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"{EMOJIS['warning']} Aguarde {error.retry_after:.1f}s para usar novamente!",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            f"{EMOJIS['error']} Voce nao tem permissao para usar este comando!",
            ephemeral=True
        )
    else:
        logger.error(f"Erro no slash command: {error}")
        try:
            await interaction.response.send_message(
                f"{EMOJIS['error']} Ocorreu um erro! Tente novamente.",
                ephemeral=True
            )
        except:
            pass

# =============================================================================
# INICIALIZACAO
# =============================================================================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("Token do Discord nao encontrado! Configure o arquivo .env")
        exit(1)

    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
