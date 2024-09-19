# 導入Discord.py模組
import discord
# 導入commands指令模組
from discord.ext import commands
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from src.get_ticket import get_ticket
from dotenv import load_dotenv



bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# 載入 .env 檔案中的環境變數
load_dotenv()
target_channel_id = os.getenv('CHANNEL_ID')
target_channel_name = os.getenv('CHANNEL_NAME')
your_account = os.getenv('ACCOUNT')  # NTU COOL 帳號
your_password = os.getenv('PASSWORD')  # NTU COOL 密碼
your_web_url = os.getenv('URL')  # 租借系統網址
token = os.getenv('TOKEN')

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)



@bot.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    

# 定义一个 Slash 命令
@bot.slash_command(name="給我泳池票", description="索取台大泳池票卷 QR Code ><")
async def swimming_ticket(ctx: discord.ApplicationContext):
    await get_ticket(ctx, "游泳池", driver, your_web_url, your_account, your_password, target_channel_id, target_channel_name)

# 定义一个 Slash 命令
@bot.slash_command(name="給我健身中心票", description="索取台大健身中心票卷 QR Code ><")
async def swimming_ticket(ctx: discord.ApplicationContext):
    await get_ticket(ctx, "健身中心", driver, your_web_url, your_account, your_password, target_channel_id, target_channel_name)
    
    

@bot.slash_command(name="help", description="呆呆獸怎麼用")
async def ticket(ctx: discord.ApplicationContext):
    await ctx.respond(
        f"""請在 {target_channel_name} 頻道中\n
          
發送 /給我泳池票 以索取台大泳池 QR Code\n
            
發送 /給我健身中心票 以索取台大健身中心 QR Code

QR Code 請三分鐘之內使用

台大泳池票卷費用 30 元、健身中心票卷費用 25 元

在使用 QR Code 成功後，可以用 Line Pay、現金或是轉帳給張原嘉喔

轉帳資料 (700) 中華郵政 00610490236328

Line Pay 的 Line 帳號可以先在 Discord 上私訊 45 張原嘉~~
        """, 
        ephemeral=True
    )

bot.run(token)