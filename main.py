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

# 初始化 bot，並啟用必要的 intents
intents = discord.Intents.default()
intents.messages = True  # 啟用處理訊息的 intents
intents.dm_messages = True  # 啟用接收私訊的 intents

bot = commands.Bot(command_prefix="!", intents=intents)

# 載入 .env 檔案中的環境變數
load_dotenv()
target_channel_id = os.getenv('CHANNEL_ID')
target_channel_name = os.getenv('CHANNEL_NAME')
admin_user_id = os.getenv('ADMIN_USER_ID')
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

**發送 `/給我泳池票`** 以索取台大泳池 QR Code

**發送 `/給我健身中心票`** 以索取台大健身中心 QR Code

**QR Code** 請在三分鐘之內使用

台大泳池票卷費用：**30 元**

健身中心票卷費用：**25 元**

在使用 QR Code 成功後，可以用 **街口支付** 或是 **轉帳**

轉帳資料：**(700) 中華郵政 00610490236328**

街口支付可以儲存下面的付款碼，使用 APP 付款

付款成功後再麻煩把匯款證明私訊呆呆獸喔 (´･ω･`)
        """,
        file=qrcode,
        ephemeral=True
    )

@bot.event
async def on_message(message):
    # 檢查是否為私訊 (DM)，且不是機器人自己發的訊息
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        try:
            # 使用 fetch_user 來獲取您自己（admin_user_id）
            target_user = await bot.fetch_user(admin_user_id)

            # 如果有文字訊息，則轉發文字
            if message.content:
                forward_message = f"來自 {message.author}: {message.content}"
                await target_user.send(forward_message)

            # 檢查訊息中是否有附件
            if message.attachments:
                for attachment in message.attachments:
                    # 發送附件（例如圖片）給目標使用者
                    await target_user.send(content=f"來自 {message.author} 的附件:", file=await attachment.to_file())

            # 回覆發送者，確認已收到並轉發
            await message.channel.send(
                f"""{message.author} 你好！謝謝你使用呆呆獸！希望你有個愉快的使用體驗(ゝ∀･)
        
歡迎再次使用我喔~祝你有個美好的一天⋛⋋( ‘Θ’)⋌⋚
                """
            )
        except discord.NotFound:
            await message.channel.send("無法找到目標使用者。")
        except discord.HTTPException:
            await message.channel.send("發送訊息時出現問題。")
    
    # 讓其他的命令繼續被處理
    await bot.process_commands(message)


bot.run(token)