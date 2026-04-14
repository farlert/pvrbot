import discord
from discord.ext import commands, tasks
import os
import asyncio
from itertools import cycle

# --- ตั้งค่าพื้นฐาน (เหมือนเดิม) ---
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = 1069137562213552128

intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- ระบบ Rich Presence แบบ Dynamic (สลับทุก 30 วินาที) ---
@tasks.loop(seconds=30)
async def change_status():
    await bot.wait_until_ready()
    
    # --- สถานะที่ 1: FiveM Server Theme ---
    fivem_activity = discord.Activity(
        type=discord.ActivityType.playing, # เปลี่ยนเป็น Playing
        name="PVR Motorsport Server 🏎️", # ชื่อเกมที่โชว์
        details="Gosu's Garage - Customizing...", # รายละเอียดด้านล่าง
        state="Current Online: 24/64 👥", # สถานะ
        large_image_url="https://w7.pngwing.com/pngs/433/561/png-transparent-logo-gta-v-thumbnail.png", # ลิงก์ภาพใหญ่ หรือชื่อไฟล์ที่อัปโหลด (เช่น logo_pvr)
        large_image_text="PVR Motorsport 🔥", # ข้อความตอนเอาเมาส์ชี้ภาพใหญ่
        buttons=[ # ใส่ปุ่มได้สูงสุด 2 ปุ่ม
            {"label": "Join FiveM Server", "url": "fivem://connect/your_server_ip"},
            {"label": "Visit Website", "url": "https://pvrmotorsport.co"}
        ]
    )

    # --- สถานะที่ 2: F1 Live Timing Theme ---
    f1_activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="gosu.wav Live Broadcast 🎧",
        details="Listening to Pluggnb Chords",
        state="Source: F1 Data",
        large_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1200px-F1.svg.png", # ลิงก์ภาพ หรือชื่อไฟล์ (เช่น gosuwav_cover)
        large_image_text="F1 World Championship",
        buttons=[
            {"label": "Open Web Dev Kit", "url": "https://your_devkit_url.com"},
            {"label": "F1 Calendar 🏁", "url": "https://www.formula1.com/en/racing/2026.html"}
            
        ]
    )

    # วนลูปสลับสถานะ
    statuses = cycle([fivem_activity, f1_activity])
    await bot.change_presence(activity=next(statuses))

# --- Event เมื่อบอทพร้อม (เหมือนเดิม แต่อย่าลืม start tasks ใหม่) ---
@bot.event
async def on_ready():
    print(f'✅ ออนไลน์แล้วในชื่อ: {bot.user}')
    # เริ่มต้นระบบเช็คห้องเสียง
    if not hasattr(bot, 'voice_check_task') or not bot.voice_check_task.is_running():
        bot.voice_check_task = check_voice_status.start()
        print("🏠 Voice Check Loop Started")
        
    # เริ่มต้นระบบสลับสถานะ (Rich Presence)
    if not change_status.is_running():
        change_status.start()
        print("✨ Presence Loop Started")

# --- (โค้ด check_voice_status, on_voice_state_update เหมือนเดิมครับ) ---
@tasks.loop(seconds=5) # หรือปรับเวลาตามต้องการ
async def check_voice_status():
    # ... (โค้ดเก่าของคุณ) ...
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel is None: return
    guild = channel.guild
    vc = guild.voice_client
    try:
        if vc is None:
            await channel.connect(reconnect=True, timeout=20)
        elif vc.channel.id != TARGET_CHANNEL_ID:
            await vc.move_to(channel)
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and before.channel is not None and after.channel is None:
        print("ℹ️ บอทหลุดจากห้องเสียง (จะกลับเข้าที่ในรอบตรวจถัดไป)")

bot.run(TOKEN)