import discord
from discord.ext import commands
import os
import datetime
import asyncio
from flask import Flask
from threading import Thread

# --- ส่วนของ Web Server (แก้เรื่อง Port สำหรับ Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render จะส่ง Port มาให้ผ่าน Environment Variable ชื่อ PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ตั้งค่าบอท ---
TARGET_CHANNEL_ID = 1069137562213552128 # ไอดีห้องที่คุณกำหนด

intents = discord.Intents.default()
intents.voice_states = True      # สำคัญ: ต้องเปิดใน Discord Developer Portal ด้วย
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
active_users = {}

@bot.event
async def on_ready():
    await bot.wait_until_ready() # เพิ่มบรรทัดนี้: รอให้ระบบโหลดข้อมูลเซิร์ฟเวอร์ให้ครบก่อน
    print(f'✅ ออนไลน์แล้ว: {bot.user}')
    
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel:
        try:
            # เช็คว่าบอทอยู่ในห้องอยู่แล้วหรือเปล่า (กันบัคเข้าซ้อน)
            voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not voice_client:
                await channel.connect()
                print(f"🏠 บอทเข้าห้อง {channel.name} เรียบร้อยแล้ว")
        except Exception as e:
            print(f"❌ เข้าห้องไม่ได้ Error: {e}")
    else:
        print(f"❌ หาห้อง ID {TARGET_CHANNEL_ID} ไม่เจอ! (เช็คสิทธิ์การมองเห็น)")

@bot.event
async def on_voice_state_update(member, before, after):
    # เช็คว่าสถานะที่เปลี่ยนคือตัวบอทเอง ไม่ใช่คนอื่น
    if member.id == bot.user.id:
        
        # กรณีที่ 1: หลุดจากห้อง หรือถูกเตะออก (before มีห้อง แต่ after ไม่มีห้อง)
        if before.channel is not None and after.channel is None:
            print("⚠️ บอทหลุดจากห้อง! กำลังเช็คสถานะเพื่อกลับไปห้องเดิม...")
            # รอ 10 วินาทีให้ Discord เคลียร์ Error 4006 (ห้ามปรับให้น้อยกว่านี้)
            await asyncio.sleep(10)
            
            # เช็คว่า ณ ตอนนี้ บอทยังไม่ได้ต่อใช่มั้ย? (กันโค้ดทำงานซ้อนกัน)
            vc = member.guild.voice_client
            if vc is None or not vc.is_connected():
                try:
                    print("🔄 กำลังพยายามเชื่อมต่อใหม่...")
                    await before.channel.connect()
                    print("🏠 กลับเข้าห้องเป้าหมายสำเร็จ")
                except Exception as e:
                    print(f"❌ เข้าห้องไม่ได้: {e}")

        # กรณีที่ 2: มีแอดมินลากบอทไปห้องอื่น (before มีห้อง, after มีห้อง แต่คนละห้อง)
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            print(f"⚠️ บอทถูกลากไปห้อง: {after.channel.name}")
            # ถ้าอยากให้บอทดื้อ ดึงกลับห้องเดิมเสมอ ให้ลบเครื่องหมาย # สองบรรทัดล่างออกครับ
            # await asyncio.sleep(3)
            # await before.channel.connect()

# เริ่มทำงาน
keep_alive()
token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ ไม่พบ DISCORD_TOKEN")