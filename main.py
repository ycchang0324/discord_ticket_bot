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
target_channel_ids = os.getenv('CHANNEL_IDS').split(',')
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
    
@bot.event
async def on_message(message):
    # 防止机器人回复自己
    if message.author == bot.user:
        return

    # 检测消息是否提及了机器人
    if bot.user in message.mentions:
        await message.channel.send(
            f"""{message.author.mention} 你好！我是呆呆獸，很高興認識你 ▼・ᴥ・▼

我將提供 **台大游泳池票** 以及** 台大健身中心票** 給你喔~

在 **小幫手** 頻道中 (っ・Д・)っ

你可以發送 **`/給我游泳池票`** 以索取台大游泳池 QR Code (=^-ω-^=)

或是在 **小幫手** 頻道中發送 **`/給我健身中心票`** 以索取台大健身中心 QR Code ฅ^•ﻌ•^ฅ

可以在 **小幫手** 頻道中發送 **`/help`** 來得到更多資訊喔 (´･ω･`)

運動真的很開心呢，希望能跟大家一起開心游泳和健身 (^_っ^)
            """
        )

    # 处理其他命令
    await bot.process_commands(message)

# 定义一个 Slash 命令
@bot.slash_command(name="給我游泳池票", description="索取台大游泳池票卷 QR Code ><")
async def swimming_ticket(ctx: discord.ApplicationContext):
    await get_ticket(bot, ctx, "游泳池", driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name)

# 定义一个 Slash 命令
@bot.slash_command(name="給我健身中心票", description="索取台大健身中心票卷 QR Code ><")
async def swimming_ticket(ctx: discord.ApplicationContext):
    await get_ticket(bot, ctx, "健身中心", driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name)
    
    

@bot.slash_command(name="help", description="呆呆獸怎麼用")
async def ticket(ctx: discord.ApplicationContext):
    if str(ctx.channel.id) in target_channel_ids:
        # 告訴 Discord 正在處理，延遲回應
        await ctx.defer(ephemeral=True)

        qrcode_path = os.path.join('img', 'payment_qrcode.png')
        
        # 檢查文件是否存在，防止出錯
        if not os.path.exists(qrcode_path):
            qrcode_path = os.path.join('img', 'payment_qrcode_example.png')
        
        if not os.path.exists(qrcode_path):
            await ctx.followup.send("出錯了，請聯絡管理員")
            return
        
        qrcode = discord.File(qrcode_path, filename="payment_qrcode.png")
        
        # 發送消息並附加文件
        await ctx.followup.send(
            f"""請在 **{target_channel_name}** 頻道中

**發送 `/給我游泳池票`** 以索取台大游泳池 QR Code

**發送 `/給我健身中心票`** 以索取台大健身中心 QR Code

**QR Code** 請在三分鐘之內使用

台大游泳池票卷費用：**30 元**

健身中心票卷費用：**25 元**

在使用 QR Code 成功後，可以用 **街口支付** 或是 **轉帳**

轉帳資料：**(700) 中華郵政 00610490236328**

請幫我在轉帳備註欄填上 **姓名** 或是 **Discord 暱稱** 喔

街口支付可以儲存下面的付款碼，再使用 APP 付款

如果有其他問題，歡迎私訊 **45 張原嘉** (´･ω･`)
            """,
            file=qrcode,
            ephemeral=True
        )
    else:
        await ctx.respond(f"請在 {target_channel_name} 頻道中發送 /help 來獲取使用說明以及匯款資訊喔~", ephemeral=True)

bot.run(token)