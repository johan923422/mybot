import json
import asyncio
import requests
import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from deep_translator import GoogleTranslator

# ============ CONFIG ============
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = 7887055769   # your telegram id

ADMINS_FILE = "admins.json"
USERS_FILE = "users.json"
role_text = "Default role text"

debate_scores = {}  # per chat memory

# ============ SHOW TEXT ============
SHOW_TEXT = """\
================Date================
             14.Nov.2025
=================Us=================
         Paing Thu Rain Kyaw
            Phoo Phoo San
====================================
I truly love you my wife and I will
love you both now and in the future.
I will give you more of my time,
care even more about you in the days
ahead. Please stay with me always.
"""

FORMAT_TEXT = """\
𝐅𝐨𝐫𝐦𝐚𝐭


Telekinesis

Pyrokinesis

Cryokinesis

Electrokinesis

Hydrokinesis

Geokinesis

Aerokinesis

Chronokinesis

Biokinesis

Umbrakinesis

Photokinesis

Technokinesis

Magnetokinesis

Gravikinesis

Psychokinesis

Atmokinesis

Hemokinesis

Plantkinesis

Soundkinesis

Dimensiokinesis

BlackHole
"""

# ===================================

# ---------- FILE HELPERS ----------
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ---------- USER CACHE ----------
users = load_json(USERS_FILE)

def cache_user(user):
    users[str(user.id)] = user.first_name
    save_json(USERS_FILE, users)

# ---------- ADMIN SYSTEM ----------
admins = load_json(ADMINS_FILE)

# always add owner
admins[str(OWNER_ID)] = "OWNER"
save_json(ADMINS_FILE, admins)

def is_admin(user_id):
    return str(user_id) in admins

# ---------- /START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is running!")

# ---------- /INFO (reply required) ----------
async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user with /info")
        return

    target = update.message.reply_to_message.from_user
    username = target.username if target.username else "NoUsername"
    text = f"👤 Username: @{username}\n🆔 User ID: {target.id}"
    await update.message.reply_text(text)

# ---------- /ADD_ADMIN ----------
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/add_admin USER_ID")
        return

    user_id = context.args[0]
    admins[str(user_id)] = "ADMIN"
    save_json(ADMINS_FILE, admins)

    await update.message.reply_text(f"✅ {user_id} added as admin")

# ---------- /RMADMIN ----------
async def rmadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/rmadmin USER_ID")
        return

    user_id = context.args[0]

    if user_id == str(OWNER_ID):
        await update.message.reply_text("❌ Cannot remove owner")
        return

    if user_id in admins:
        del admins[user_id]
        save_json(ADMINS_FILE, admins)
        await update.message.reply_text("✅ Admin removed")

# ---------- /LIST ----------
async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    text = "👑 Bot Admins:\n\n"
    for uid, role in admins.items():
        if role == "OWNER":
            text += f"• 👑 OWNER ({uid})\n"
        else:
            text += f"• ADMIN ({uid})\n"

    await update.message.reply_text(text)

# ---------- /ALL ----------
async def all_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not users:
        await update.message.reply_text("No cached users.")
        return

    mention_list = []
    for uid, name in users.items():
        mention = f"<a href='tg://user?id={uid}'>{name}</a>"
        mention_list.append(mention)

    batch_size = 7
    for i in range(0, len(mention_list), batch_size):
        batch = mention_list[i:i+batch_size]
        text = " ".join(batch)
        await update.message.reply_text(text, parse_mode="HTML")
        await asyncio.sleep(1)

# ====== /role COMMAND ======
async def role_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global role_text
    # Monobox (Markdown code block) နဲ့ပြ
    await update.message.reply_text(f"```\n{role_text}\n```", parse_mode="Markdown")

# ====== /editrole COMMAND ======
async def editrole_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global role_text

    if not context.args:
        await update.message.reply_text(
            "⚠️ Type your new role text after /editrole using \\n for line breaks.\n"
            "Example:\n/editrole Hi\\nI'm Johan\\nWelcome"
        )
        return

    # Join args and replace \n with actual line breaks
    new_text = " ".join(context.args).replace("\\n", "\n")
    role_text = new_text

    await update.message.reply_text("✅ Role text updated!")

# ---------- /SHOW ----------
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"```\n{SHOW_TEXT}\n```"
    await update.message.reply_text(text, parse_mode="Markdown")

from telegram import ChatPermissions

# ---------- /FORMAT ----------
async def format_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"```\n{FORMAT_TEXT}\n```"
    await update.message.reply_text(text, parse_mode="Markdown")

# ---------- /TOPIC ----------
async def topic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reply လုပ်ထားတဲ့ message ကို target လို့ယူ
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a format name to get its topics!")
        return

    # Reply လုပ်ထားတဲ့ text ကို format name အနေနဲ့ယူ
    format_name = update.message.reply_to_message.text.strip()

    # Formatted topics dictionary
    FORMATS = {
        "Telekinesis": [

            "Telekinesis can move objects without touching them, making it stronger than physical combat skills.\n\n",

            "Skilled telekinetics could dominate modern warfare with ranged control.\n\n",

            "Telekinesis should be legally restricted to prevent misuse in public.\n\n",

            "Compared to elemental powers, telekinesis is more versatile in combat.\n\n",

            "A trained telekinetic can counter a pyrokinesis user effectively.\n\n",

            "Telekinesis allows strategic control of the battlefield from a distance.\n\n",

            "In sports, telekinesis would disrupt fairness and competition.\n\n",

            "Telekinesis is superior in rescue operations and moving heavy debris.\n\n",

            "It can replace heavy machinery in industrial or emergency scenarios.\n\n",

            "Governments may require telekinetics to register for safety reasons.\n\n",

            "Telekinesis is dangerous in crowded areas without strict control.\n\n",

            "Against magnetokinesis, telekinesis can manipulate objects independently.\n\n",

            "Telekinesis requires high intelligence and concentration to be effective.\n\n",

            "Defensive abilities using telekinesis can block attacks from multiple opponents.\n\n",

            "Military balance could be disrupted by powerful telekinetics.\n\n",

            "Telekinesis is more useful than biokinesis in neutral situations.\n\n",

            "It can counter gravikinesis by controlling object trajectories.\n\n",

            "Without mental interference, telekinesis is unstoppable.\n\n",

            "Telekinetics can lead special operations due to their unique abilities.\n\n",

            "Telekinesis is widely feared due to its control over the environment.\n\n"

        ],

        "Pyrokinesis": [

            "Pyrokinesis can control fire, making it the most destructive elemental power.\n\n",

            "It is stronger than cryokinesis in terms of offensive capability.\n\n",

            "Uncontrolled pyrokinesis is extremely dangerous in urban areas.\n\n",

            "On the battlefield, pyrokinesis can dominate due to area damage.\n\n",

            "Pyrokinesis is more dangerous than electrokinesis in direct combat.\n\n",

            "Public pyrokinesis should be banned to avoid accidents.\n\n",

            "It is ineffective underwater where fire cannot exist.\n\n",

            "Pyrokinesis beats aerokinesis when raw damage is needed quickly.\n\n",

            "It causes environmental damage that is often irreversible.\n\n",

            "Emotional control is required to prevent unintended fires.\n\n",

            "Pyrokinesis is excellent for intimidation in combat.\n\n",

            "Despite its power, it is weaker than gravikinesis in controlling objects.\n\n",

            "Energy industries could be influenced by powerful pyrokinesis users.\n\n",

            "In close combat, pyrokinesis provides overwhelming offense.\n\n",

            "Weaponization of pyrokinesis is a serious ethical issue.\n\n",

            "Pyrokinesis can defeat plantkinesis by burning vegetation.\n\n",

            "It is considered one of the hardest powers to master.\n\n",

            "Pyrokinesis is better for offense than defense.\n\n",

            "Leaders with pyrokinesis inspire fear and authority.\n\n",

            "It is widely regarded as the most feared elemental ability.\n\n"

],

"Cryokinesis": [

    "Cryokinesis can freeze opponents, making it highly tactical.\n\n",

    "It is superior in defense because frozen barriers are hard to break.\n\n",

    "Cryokinesis can counter hydrokinesis by freezing water attacks.\n\n",

    "It provides excellent crowd-control abilities in combat.\n\n",

    "Users would dominate polar or cold regions efficiently.\n\n",

    "Cryokinesis offers more precision than geokinesis in manipulation.\n\n",

    "It is less destructive than pyrokinesis, reducing collateral damage.\n\n",

    "City use should be regulated to avoid freezing hazards.\n\n",

    "Cryokinesis is ideal for prison security or containment.\n\n",

    "It can counter biokinesis by freezing or slowing body functions.\n\n",

    "Cryokinesis is more stable than electrokinesis due to fewer variables.\n\n",

    "Climate change and weather can be influenced in combat scenarios.\n\n",

    "It is considered safe compared to fire-based powers.\n\n",

    "Cryokinesis is stronger than aerokinesis in controlling dense matter.\n\n",

    "Its defensive applications make it underrated in combat ranking.\n\n",

    "Cryokinesis can permanently disable opponents if used strategically.\n\n",

    "Mastery requires more discipline than pyrokinesis.\n\n",

    "It is used for disaster control, like freezing lava or floods.\n\n",

    "Cryokinesis beats plantkinesis by freezing vegetation quickly.\n\n",

    "Overall, cryokinesis is one of the most balanced elemental abilities.\n\n"

],

"Electrokinesis": [

    "Electrokinesis allows control of electricity for offense and defense.\n\n",

    "It can disable electronic devices instantly.\n\n",

    "Electrokinesis is stronger in storms or conductive environments.\n\n",

    "It is dangerous in wet conditions without safety measures.\n\n",

    "Electrokinesis can paralyze opponents temporarily.\n\n",

    "Users dominate high-tech warfare.\n\n",

    "Electrokinesis is more tactical than pyrokinesis in some scenarios.\n\n",

    "It requires precise control to avoid collateral damage.\n\n",

    "Electrokinesis can power machinery without batteries.\n\n",

    "It is highly effective against robotic enemies.\n\n",

    "Electrokinesis can manipulate magnetic fields indirectly.\n\n",

    "It can be used to create electrical barriers.\n\n",

    "Electrokinesis mastery requires deep knowledge of physics.\n\n",

    "It can short-circuit enemy devices in combat.\n\n",

    "Electrokinesis beats cryokinesis in raw energy control.\n\n",

    "It is risky if uncontrolled due to unintended shocks.\n\n",

    "Electrokinesis can disrupt communications effectively.\n\n",

    "It is superior in urban combat where wires and metal are abundant.\n\n",

    "Electrokinesis can energize allies’ weapons or defenses.\n\n",

    "Overall, electrokinesis is one of the most versatile kinesis powers.\n\n"

],

"Hydrokinesis": [

    "Hydrokinesis allows control of water in all forms.\n\n",

    "It can create waves, manipulate rivers, and stop fires.\n\n",

    "Hydrokinesis is effective in rescue operations.\n\n",

    "It can counter pyrokinesis efficiently.\n\n",

    "Hydrokinesis can flood or redirect water sources strategically.\n\n",

    "Users dominate aquatic combat zones.\n\n",

    "Hydrokinesis is less effective in dry areas without water.\n\n",

    "It can generate water shields for defense.\n\n",

    "Hydrokinesis requires energy proportional to water volume.\n\n",

    "It is versatile in both offense and support roles.\n\n",

    "Hydrokinesis can help in agriculture or irrigation.\n\n",

    "Flood control is possible using hydrokinesis powers.\n\n",

    "Hydrokinesis mastery requires environmental awareness.\n\n",

    "Users can manipulate ice indirectly through freezing.\n\n",

    "Hydrokinesis can disable fire-based attacks.\n\n",

    "It is effective in combination with cryokinesis.\n\n",

    "Hydrokinesis can create barriers or trap opponents.\n\n",

    "It can purify water or create potable supplies.\n\n",

    "Hydrokinesis is vulnerable to extreme cold freezing the water.\n\n",

    "Overall, hydrokinesis is highly versatile and defensive.\n\n"
],

"Geokinesis": [

    "Geokinesis allows control over earth, rocks, and soil.\n\n",

    "It can create walls, barriers, or earthquakes.\n\n",

    "Geokinesis is excellent for defense in mountainous regions.\n\n",

    "Users can manipulate terrain to gain strategic advantage.\n\n",

    "Geokinesis can counter aerokinesis by controlling solid ground.\n\n",

    "Mining and construction could be revolutionized with geokinesis.\n\n",

    "Geokinesis requires physical stamina to manipulate large volumes.\n\n",

    "It can trap or immobilize opponents effectively.\n\n",

    "Geokinesis can redirect natural disasters like landslides.\n\n",

    "It is versatile for both offense and defense in combat.\n\n",

    "Geokinesis mastery demands precision and timing.\n\n",

    "It can support agriculture by reshaping soil.\n\n",

    "Geokinesis is less effective in unstable or loose terrain.\n\n",

    "It can counter gravikinesis by stabilizing objects.\n\n",

    "Geokinesis can create tunnels or protective bunkers.\n\n",

    "Overall, geokinesis is powerful for control of natural environments.\n\n",

    "It can manipulate minerals to craft weapons or tools.\n\n",

    "Geokinesis can trigger landslides to halt enemies.\n\n",

    "It works in combination with hydrokinesis for mudslides.\n\n",

    "Geokinesis can reshape battlefields to the user’s advantage.\n\n"

],

"Aerokinesis": [

    "Aerokinesis controls wind and air currents for movement and attacks.\n\n",

    "It can enhance mobility and dodge enemy attacks.\n\n",

    "Aerokinesis can disperse gases or toxins.\n\n",

    "It can lift objects or create powerful gusts.\n\n",

    "Aerokinesis is effective in open areas but limited indoors.\n\n",

    "It can counter fire-based attacks by blowing them away.\n\n",

    "Aerokinesis requires continuous focus to maintain wind control.\n\n",

    "It is useful for reconnaissance using wind currents.\n\n",

    "Aerokinesis can slow or block projectiles.\n\n",

    "Users can generate tornadoes for area attacks.\n\n",

    "Aerokinesis is less effective against gravikinesis.\n\n",

    "It can manipulate oxygen levels to affect opponents.\n\n",

    "Aerokinesis can aid in flight or levitation.\n\n",

    "It can create air shields to block attacks.\n\n",

    "Aerokinesis is highly tactical in terrain with vertical space.\n\n",

    "It can enhance allies’ speed and mobility.\n\n",

    "Aerokinesis can be combined with pyrokinesis for fire tornadoes.\n\n",

    "Mastery demands precise control of currents.\n\n",

    "Aerokinesis is excellent for crowd control.\n\n",

    "Overall, aerokinesis is versatile for both offense and defense.\n\n"

],

"Chronokinesis": [

    "Chronokinesis allows control over time, speeding up or slowing down events.\n\n",

    "It can provide tactical advantage in combat.\n\n",

    "Chronokinesis requires high concentration to avoid temporal errors.\n\n",

    "It can reverse minor events or prevent damage.\n\n",

    "Chronokinesis mastery can alter outcomes strategically.\n\n",

    "It is limited by the user’s mental stamina.\n\n",

    "Chronokinesis can be countered by strong mental focus opponents.\n\n",

    "Time manipulation allows perfect defense against attacks.\n\n",

    "Chronokinesis can accelerate healing or fatigue.\n\n",

    "It is highly versatile but potentially dangerous if abused.\n\n",

    "Chronokinesis can foresee short-term future events.\n\n",

    "It can synchronize team movements for maximum efficiency.\n\n",

    "Chronokinesis mastery demands strict discipline.\n\n",

    "Temporal control can affect both allies and enemies.\n\n",

    "It can prevent natural disasters temporarily.\n\n",

    "Chronokinesis is less effective without awareness of surroundings.\n\n",

    "It allows perfect timing for attacks or defenses.\n\n",

    "Chronokinesis can change minor past events to advantage.\n\n",

    "Misuse of chronokinesis can cause unintended consequences.\n\n",

    "Overall, chronokinesis is one of the most strategic kinesis powers.\n\n"

],

"Biokinesis": [

    "Biokinesis allows control over biological processes in living beings.\n\n",

    "It can enhance strength, healing, or speed.\n\n",

    "Biokinesis can counter other kinesis by weakening opponents.\n\n",

    "Users must respect ethical limits to avoid harm.\n\n",

    "Biokinesis is effective in both combat and medical situations.\n\n",

    "It requires deep understanding of anatomy and physiology.\n\n",

    "Biokinesis can manipulate animal or plant life.\n\n",

    "It is versatile but requires intense concentration.\n\n",

    "Biokinesis mastery can turn the tide of battle quickly.\n\n",

    "Improper use can cause permanent damage.\n\n",

    "Biokinesis can heal allies faster than conventional medicine.\n\n",

    "It is less effective against inanimate opponents.\n\n",

    "Biokinesis can boost immunity or stamina.\n\n",

    "It can influence behavior of living targets.\n\n",

    "Biokinesis is subtle and strategic compared to direct attacks.\n\n",

    "Users can control multiple targets with advanced skill.\n\n",

    "Biokinesis requires ethical responsibility.\n\n",

    "It can counter toxins and diseases.\n\n",

    "Biokinesis is less visible, making it ideal for stealth.\n\n",

    "Overall, biokinesis is powerful in combat support and strategy.\n\n"

],

"Umbrakinesis": [

    "Umbrakinesis allows manipulation of shadows and darkness.\n\n",

    "It can conceal movements or create illusions.\n\n",

    "Umbrakinesis is effective in stealth and reconnaissance.\n\n",

    "Users can immobilize opponents by surrounding them in darkness.\n\n",

    "Umbrakinesis can absorb light to create tactical advantage.\n\n",

    "It requires control over surrounding light sources.\n\n",

    "Umbrakinesis can enhance psychological warfare.\n\n",

    "It can be combined with aerokinesis or telekinesis for creative attacks.\n\n",

    "Umbrakinesis mastery demands focus in both dark and light areas.\n\n",

    "It can obscure locations from surveillance.\n\n",

    "Umbrakinesis can trap opponents in shadowy constructs.\n\n",

    "It is less effective in fully illuminated environments.\n\n",

    "Umbrakinesis can enhance stealth for strategic retreats.\n\n",

    "Users can manipulate shadow forms for distraction.\n\n",

    "Umbrakinesis is excellent for infiltration missions.\n\n",

    "It can counter photokinesis by neutralizing light.\n\n",

    "Umbrakinesis is subtle but psychologically intimidating.\n\n",

    "Advanced users can create shadow clones.\n\n",

    "It allows temporary concealment of allies.\n\n",

    "Overall, umbrakinesis is a versatile power for strategy and stealth.\n\n"

],

"Photokinesis": [

    "Photokinesis allows control over light for illumination and attacks.\n\n",

    "It can blind opponents temporarily.\n\n",

    "Photokinesis can create laser-like focused attacks.\n\n",

    "It is effective against shadow-based powers like umbrakinesis.\n\n",

    "Photokinesis can generate dazzling displays to distract enemies.\n\n",

    "Users can bend light to create illusions.\n\n",

    "Photokinesis is versatile in both offense and defense.\n\n",

    "It can amplify solar energy for devastating effects.\n\n",

    "Photokinesis requires intense concentration in low light.\n\n",

    "It can illuminate areas for tactical awareness.\n\n",

    "Photokinesis can disorient multiple opponents at once.\n\n",

    "It can be used to signal allies over long distances.\n\n",

    "Photokinesis can focus light to cut through materials.\n\n",

    "Users can generate blinding flashes to escape.\n\n",

    "It is less effective in complete darkness.\n\n",

    "Photokinesis can enhance morale by providing visibility.\n\n",

    "It can be combined with electrokinesis for energy attacks.\n\n",

    "Photokinesis requires fine control for precision attacks.\n\n",

    "It is excellent for psychological intimidation.\n\n",

    "Overall, photokinesis is powerful for both strategy and offense.\n\n"

],

"Technokinesis": [

    "Technokinesis allows manipulation of machines and electronics.\n\n",

    "Users can control devices remotely.\n\n",

    "Technokinesis is highly effective in modern warfare.\n\n",

    "It can override security systems.\n\n",

    "Technokinesis can repair or sabotage machinery.\n\n",

    "Users must understand engineering and technology.\n\n",

    "Technokinesis is versatile in both defense and offense.\n\n",

    "It can disable enemy weapons or drones.\n\n",

    "Technokinesis can be combined with electrokinesis for stronger effects.\n\n",

    "Users can optimize systems for speed and efficiency.\n\n",

    "Technokinesis requires precise control of circuits.\n\n",

    "It can manipulate vehicles for mobility advantage.\n\n",

    "Technokinesis is less effective in low-tech environments.\n\n",

    "It can disrupt communications and intelligence networks.\n\n",

    "Users can control AI systems or robots.\n\n",

    "Technokinesis can enhance production and manufacturing.\n\n",

    "It requires continuous practice to master advanced devices.\n\n",

    "Technokinesis can create defensive shields from machinery.\n\n",

    "It is excellent for tactical support operations.\n\n",

    "Overall, technokinesis is one of the most versatile kinesis powers.\n\n"

],

"Magnetokinesis": [

    "Magnetokinesis allows control over magnetic fields and metals.\n\n",

    "Users can attract or repel metallic objects.\n\n",

    "Magnetokinesis can disable enemy weapons or projectiles.\n\n",

    "It is effective in both offense and defense.\n\n",

    "Magnetokinesis can manipulate vehicles and machinery.\n\n",

    "Users must understand electromagnetic principles.\n\n",

    "Magnetokinesis can counter electrokinesis in some scenarios.\n\n",

    "It can create barriers or traps using metal.\n\n",

    "Magnetokinesis can levitate metallic objects.\n\n",

    "Users can disrupt electronic devices using magnetic pulses.\n\n",

    "Magnetokinesis can be combined with gravikinesis for powerful effects.\n\n",

    "It is highly effective against armored opponents.\n\n",

    "Magnetokinesis requires strong focus and coordination.\n\n",

    "It can interfere with navigation and communication systems.\n\n",

    "Magnetokinesis can generate metal projectiles.\n\n",

    "Users can create magnetic shields.\n\n",

    "Magnetokinesis is excellent for tactical manipulation.\n\n",

    "It can protect allies by controlling metallic cover.\n\n",

    "Magnetokinesis can disable enemy electronics quickly.\n\n",

    "Overall, magnetokinesis is versatile in battle control.\n\n"

],

"Gravikinesis": [

    "Gravikinesis allows manipulation of gravitational forces.\n\n",

    "Users can increase or decrease gravity on objects or opponents.\n\n",

    "Gravikinesis can immobilize enemies by increasing weight.\n\n",

    "It can enhance movement by reducing gravity.\n\n",

    "Gravikinesis is effective for both combat and transportation.\n\n",

    "Users must carefully control gravity to avoid collateral damage.\n\n",

    "Gravikinesis can counter telekinesis in object control.\n\n",

    "It can create defensive zones with altered gravity.\n\n",

    "Gravikinesis can be used to enhance allies’ mobility.\n\n",

    "It requires precise calculations for safe manipulation.\n\n",

    "Gravikinesis can create gravitational traps.\n\n",

    "It can manipulate planetary gravity in extreme cases.\n\n",

    "Gravikinesis can disrupt projectile attacks.\n\n",

    "Users can create floating platforms or barriers.\n\n",

    "Gravikinesis mastery requires strong mental focus.\n\n",

    "It can enhance or hinder object speed effectively.\n\n",

    "Gravikinesis is powerful for controlling battlefield dynamics.\n\n",

    "It can neutralize airborne attacks.\n\n",

    "Gravikinesis can manipulate terrain slightly by weight control.\n\n",

    "Overall, gravikinesis is a highly strategic kinesis ability.\n\n"

],

"Psychokinesis": [

    "Psychokinesis allows mental manipulation of objects and minds.\n\n",

    "Users can move objects with sheer willpower.\n\n",

    "Psychokinesis can influence opponents’ thoughts subtly.\n\n",

    "It is versatile in both combat and stealth.\n\n",

    "Psychokinesis requires intense concentration.\n\n",

    "Users can enhance mental agility or perception.\n\n",

    "Psychokinesis can counter physical kinesis effectively.\n\n",

    "It can create mental barriers to protect allies.\n\n",

    "Psychokinesis can manipulate small objects for distraction.\n\n",

    "Advanced users can manipulate multiple objects simultaneously.\n\n",

    "Psychokinesis mastery demands strong mental discipline.\n\n",

    "It can detect opponents’ intentions subtly.\n\n",

    "Psychokinesis can be combined with other kinesis for synergy.\n\n",

    "It can enhance strategic planning in real-time.\n\n",

    "Psychokinesis is less visible but psychologically powerful.\n\n",

    "Users can subtly alter perceptions.\n\n",

    "Psychokinesis can disrupt enemy coordination.\n\n",

    "It requires rest to maintain mental energy.\n\n",

    "Psychokinesis is excellent for stealth and precision.\n\n",

    "Overall, psychokinesis is highly versatile and strategic.\n\n"

],

"Atmokinesis": [

    "Atmokinesis allows control over weather and atmospheric conditions.\n\n",

    "Users can summon storms or calm weather.\n\n",

    "Atmokinesis is effective for large-scale strategic advantage.\n\n",

    "It can influence temperature, rain, wind, and lightning.\n\n",

    "Atmokinesis requires awareness of natural cycles.\n\n",

    "It can support agriculture or environmental control.\n\n",

    "Atmokinesis can counter aerokinesis or hydrokinesis.\n\n",

    "It can enhance or disrupt battles through environmental manipulation.\n\n",

    "Atmokinesis requires concentration to maintain stability.\n\n",

    "It can create fog or storms for tactical stealth.\n\n",

    "Atmokinesis can redirect rainfall to prevent flooding.\n\n",

    "Users can generate lightning strikes for offense.\n\n",

    "Atmokinesis is less effective indoors.\n\n",

    "It can control cloud formation for surveillance.\n\n",

    "Atmokinesis can enhance fire-based powers using heat and wind.\n\n",

    "It can be combined with cryokinesis to manipulate snow.\n\n",

    "Atmokinesis requires constant monitoring of atmospheric changes.\n\n",

    "It can create strong winds to block enemy movements.\n\n",

    "Atmokinesis mastery demands environmental awareness.\n\n",

    "Overall, atmokinesis is powerful for large-scale control.\n\n"

],

"Hemokinesis": [

    "Hemokinesis allows manipulation of blood in living beings.\n\n",

    "Users can enhance healing or cause temporary harm.\n\n",

    "Hemokinesis requires ethical responsibility.\n\n",

    "It can counter biokinesis in combat.\n\n",

    "Hemokinesis is subtle but potentially deadly.\n\n",

    "Users can detect wounds or injuries in others.\n\n",

    "Hemokinesis can improve endurance and strength temporarily.\n\n",

    "It can be used to incapacitate opponents without weapons.\n\n",

    "Hemokinesis mastery demands understanding of physiology.\n\n",

    "It can assist in medical situations.\n\n",

    "Hemokinesis can disrupt opponents’ circulation.\n\n",

    "Users must avoid misuse to prevent permanent damage.\n\n",

    "Hemokinesis can combine with biokinesis for enhanced healing.\n\n",

    "It can manipulate small or large blood volumes.\n\n",

    "Hemokinesis is powerful in stealth attacks.\n\n",

    "Users can detect emotions via blood flow.\n\n",

    "Hemokinesis can slow or weaken opponents subtly.\n\n",

    "It requires mental discipline to control accurately.\n\n",

    "Hemokinesis is strategic for both offense and support.\n\n",

    "Overall, hemokinesis is one of the most delicate kinesis powers.\n\n"

],

"Plantkinesis": [

    "Plantkinesis allows control over plants and vegetation.\n\n",

    "Users can grow or manipulate plants rapidly.\n\n",

    "Plantkinesis can entangle or block opponents.\n\n",

    "It is effective in forests or natural areas.\n\n",

    "Plantkinesis can heal allies using medicinal plants.\n\n",

    "It requires understanding of botany and plant growth.\n\n",

    "Plantkinesis can create barriers or traps.\n\n",

    "Users can camouflage themselves with plants.\n\n",

    "Plantkinesis can manipulate roots and vines for offense.\n\n",

    "It can improve environmental conditions.\n\n",

    "Plantkinesis can counter fire-based powers strategically.\n\n",

    "Users can control growth speed for tactical advantage.\n\n",

    "Plantkinesis is less effective in urban areas.\n\n",

    "It can produce fruits or medicinal herbs instantly.\n\n",

    "Plantkinesis mastery requires patience and timing.\n\n",

    "Users can create plant-based shields.\n\n",

    "Plantkinesis can spread vegetation to obstruct enemies.\n\n",

    "It is strategic for both offense and defense.\n\n",

    "Plantkinesis enhances stealth in natural terrain.\n\n",

    "Overall, plantkinesis is versatile and eco-friendly.\n\n"

],

"Soundkinesis": [

    "Soundkinesis allows control over sound waves.\n\n",

    "Users can amplify or mute sounds.\n\n",

    "Soundkinesis can disorient opponents.\n\n",

    "It can enhance communication or disrupt enemy signals.\n\n",

    "Soundkinesis is effective in crowd control.\n\n",

    "Users can generate concussive sound blasts.\n\n",

    "Soundkinesis requires precision in frequency and amplitude.\n\n",

    "It can mask movements or create auditory illusions.\n\n",

    "Soundkinesis can incapacitate enemies temporarily.\n\n",

    "Users can manipulate musical instruments or devices remotely.\n\n",

    "Soundkinesis mastery requires acute hearing.\n\n",

    "It can enhance morale through music or sound cues.\n\n",

    "Soundkinesis is less effective in soundproof areas.\n\n",

    "Users can detect hidden opponents via echolocation.\n\n",

    "Soundkinesis can counter stealth attacks effectively.\n\n",

    "It can amplify allies’ communications.\n\n",

    "Soundkinesis can create vibrations to destabilize structures.\n\n",

    "Users can subtly influence opponents with sound patterns.\n\n",

    "Soundkinesis is strategic for offense and defense.\n\n",

    "Overall, soundkinesis is versatile and tactical.\n\n"

],

"Dimensiokinesis": [

    "Dimensiokinesis allows manipulation of space and dimensions.\n\n",

    "Users can teleport themselves or objects.\n\n",

    "Dimensiokinesis can create pockets or rifts in space.\n\n",

    "It is highly effective in strategic positioning.\n\n",

    "Dimensiokinesis can trap enemies in alternate dimensions.\n\n",

    "Users can compress or expand space to advantage.\n\n",

    "Dimensiokinesis mastery demands high concentration.\n\n",

    "It can bypass physical barriers.\n\n",

    "Dimensiokinesis allows rapid movement across battlefields.\n\n",

    "Users can manipulate spatial distance for defense.\n\n",

    "Dimensiokinesis can counter gravikinesis in object control.\n\n",

    "It can store objects in pocket dimensions.\n\n",

    "Dimensiokinesis requires awareness to avoid spatial disorientation.\n\n",

    "Users can create shortcuts for allies.\n\n",

    "Dimensiokinesis can isolate targets strategically.\n\n",

    "It allows unique offensive tactics by warping space.\n\n",

    "Dimensiokinesis can enhance escape and infiltration.\n\n",

    "Users can manipulate spatial traps.\n\n",

    "It is excellent for both offense and support.\n\n",

    "Overall, dimensiokinesis is one of the most complex kinesis powers.\n\n"

        ],

        "BlackHole": [

            "BlackHole manipulation allows control of gravitational singularities.\n\n",

            "Users can pull objects or enemies into intense gravity zones.\n\n",

            "BlackHole powers can destroy or absorb matter.\n\n",

            "It is extremely dangerous and hard to control.\n\n",

            "Users can create temporary mini black holes for strategic attacks.\n\n",

            "BlackHole manipulation requires precise mental control.\n\n",

            "It can counter most physical kinesis powers.\n\n",

            "BlackHole powers can distort space around the user.\n\n",

            "It is one of the most destructive abilities known.\n\n",

            "Users must monitor energy output carefully.\n\n",

            "BlackHole manipulation can trap multiple opponents.\n\n",

            "It can neutralize projectile attacks by pulling them away.\n\n",

            "BlackHole powers require high intelligence and focus.\n\n",

            "Users can collapse areas temporarily for tactical advantage.\n\n",

            "BlackHole manipulation can disrupt gravitationally sensitive technologies.\n\n",

            "It is ideal for high-risk missions where maximum impact is required.\n\n",

            "BlackHole manipulation can destabilize opponents' formations.\n\n",

            "It can combine with gravikinesis for amplified gravitational effects.\n\n",

            "BlackHole users can control battlefield zones strategically.\n\n",

            "Overall, BlackHole manipulation is among the most powerful and feared kinesis abilities.\n\n"
        ]
    }

    if format_name not in FORMATS:
        await update.message.reply_text(f"❌ Format '{format_name}' not found!")
        return

    topics = FORMATS[format_name]
    text = "🔥 " + format_name + " Topics:\n\n"
    for i, t in enumerate(topics, 1):
        text += f"{i}. {t}\n"

    # Monobox style
    text = f"```\n{text}\n```"
    await update.message.reply_text(text, parse_mode="MarkdownV2")

# ---------- /TRANSLATE ----------
async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message to translate it!")
        return

    original_text = update.message.reply_to_message.text
    if not original_text:
        await update.message.reply_text("❌ The replied message has no text!")
        return

    # Translate to Myanmar
    translated_text = GoogleTranslator(source='auto', target='my').translate(original_text)

    # Monobox style
    reply_text = f"```\n{translated_text}\n```"
    await update.message.reply_text(reply_text, parse_mode="MarkdownV2")


# ---------- AUTO WELCOME ----------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_name = update.effective_chat.title

    for user in update.message.new_chat_members:
        cache_user(user)
        text = f"ဟိတ် {user.first_name}  {chat_name} မှကြိုဆိုပါတယ်"
        await update.message.reply_text(text)

# ---------- GOODBYE ----------
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.left_chat_member
    chat_name = update.effective_chat.title
    text = f"ဟုတ် {user.first_name} သည် {chat_name} မှထွက်သွားပါပြီ"
    await update.message.reply_text(text)

# ---------- TRACK USERS ----------
async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        cache_user(update.effective_user)


# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_cmd))
    app.add_handler(CommandHandler("add_admin", add_admin))
    app.add_handler(CommandHandler("rmadmin", rmadmin))
    app.add_handler(CommandHandler("list", list_admins))
    app.add_handler(CommandHandler("all", all_cmd))
    app.add_handler(CommandHandler("role", role_cmd))
    app.add_handler(CommandHandler("editrole", editrole_cmd))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler("format", format_cmd))
    app.add_handler(CommandHandler("topic", topic_cmd))
    app.add_handler(CommandHandler("translate", translate_cmd))

    # welcome / goodbye
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye))

    # cache users
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_users))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()


