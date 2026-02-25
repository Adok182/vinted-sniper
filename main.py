import os
import discord
import requests
from discord.ext import tasks, commands

# --- CONFIGURATION ---
TOKEN = " os.getenv("DISCORD_TOKEN")" # <--- METS TON VRAI TOKEN ICI
CHANNEL_ID = 1459927872209686611 
SEARCH_QUERY = "lego star wars"   
ALREADY_SEEN = set() 

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def get_vinted_items(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
    }
    try:
        session = requests.Session()
        session.get("https://www.vinted.fr", headers=headers, timeout=10)
        url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={query}&order=newest_first&per_page=20"
        response = session.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"❌ Vinted bloqué (Code {response.status_code})")
            return []
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
        return []

@tasks.loop(seconds=60)
async def scan_vinted():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return
    items = get_vinted_items(SEARCH_QUERY)
    if not items: return
    for item in reversed(items):
        item_id = item['id']
        if item_id not in ALREADY_SEEN:
            if len(ALREADY_SEEN) == 0:
                for i in items: ALREADY_SEEN.add(i['id'])
                print("📥 Monitoring lancé sur Render (60s)...")
                break
            title = item.get('title', 'Sans titre')
            price = item.get('price', '??')
            url = f"https://www.vinted.fr/items/{item_id}"
            embed = discord.Embed(title=f"✨ {title}", url=url, color=0x0091ff)
            embed.add_field(name="💰 Prix", value=f"**{price} €**", inline=True)
            if item.get('photo', {}).get('url'):
                embed.set_image(url=item['photo']['url'])
            await channel.send(embed=embed)
            ALREADY_SEEN.add(item_id)
            print(f"🔥 Trouvé : {title}")

@bot.event
async def on_ready():
    print(f"✅ Sniper opérationnel !")
    if not scan_vinted.is_running():
        scan_vinted.start()

bot.run(TOKEN)
