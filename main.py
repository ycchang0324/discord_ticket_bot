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
maintainer_env = os.getenv('MAINTAINER')
maintainer_id_env = os.getenv('MAINTAINER_ID')
bot_name_env = os.getenv('BOT_NAME')

# 定義 WebDriver 管理類
class WebDriverManager:
    def __init__(self, options):
        self.options = options
        self.driver = self.create_driver()

    def create_driver(self):
        # 建立新的 WebDriver 實例
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def get_driver(self):
        try:
            # 嘗試使用當前的 WebDriver
            self.driver.title  # 檢查 driver 是否存活
        except Exception:
            # 如果 driver 不可用，重新創建
            self.driver.quit()
            self.driver = self.create_driver()
        return self.driver

# 初始化 Selenium WebDriver 選項
chrome_options = Options()
chrome_options.add_argument("--headless")  # 啟用無頭模式
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 渲染
chrome_options.add_argument("--window-size=1920,1080")  # 模擬螢幕解析度
chrome_options.add_argument("--no-sandbox")  # 避免權限問題
chrome_options.add_argument("--disable-dev-shm-usage")  # 避免共享內存不足

# 建立 WebDriver 管理實例
driver_manager = WebDriverManager(chrome_options)


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
            f"""{message.author.mention} 你好！我是{bot_name_env}，很高興認識你 ▼・ᴥ・▼

我將提供 **台大游泳池票** 以及** 台大健身中心票** 給你喔~

在 **{target_channel_name}** 頻道中 (っ・Д・)っ

你可以發送 **`/給我游泳池票`** 以索取台大游泳池 QR Code (=^-ω-^=)

或是發送 **`/給我健身中心票`** 以索取台大健身中心 QR Code ฅ^•ﻌ•^ฅ

請在給泳驗刷票前就把 QR Code 生成好喔，不然泳驗可能會覺得很奇怪(◉３◉)

也可以發送 **`/help`** 來得到更多資訊喔 (´･ω･`)

運動真的很開心呢，希望能跟大家一起開心游泳和健身 (^_っ^)
            """
        )

    # 2. 檢查訊息作者是否為特定使用者
    if int(message.author.id) == int(maintainer_id_env):
        
        # 3. 檢查訊息內容是否與特定觸發訊息相符 (不區分大小寫)
        # 使用 .strip().lower() 處理前後空白和大小寫
        if message.content.strip().lower() == "welcome":
            
            # 4. 取得目標頻道
            for channel_id in target_channel_ids:
                channel = bot.get_channel(int(channel_id))
                if channel :
                    await channel.send(f"""你好！我是{bot_name_env}，很高興認識你 ▼・ᴥ・▼

我將提供 **台大游泳池票** 以及** 台大健身中心票** 給你喔~

在 **{target_channel_name}** 頻道中 (っ・Д・)っ

你可以發送 **`/給我游泳池票`** 以索取台大游泳池 QR Code (=^-ω-^=)

或是發送 **`/給我健身中心票`** 以索取台大健身中心 QR Code ฅ^•ﻌ•^ฅ

小小的提醒~~請在給泳驗刷票前就把 QR Code 生成好喔，不然泳驗可能會覺得很奇怪(◉３◉)

也可以發送 **`/help`** 來得到更多資訊喔 (´･ω･`)

運動真的很開心呢，希望能跟大家一起開心游泳和健身 (^_っ^)
            """
        )
                else:
                    print(f'無法找到頻道 {channel_id}') 

# 3. 檢查訊息內容是否與特定觸發訊息相符 (不區分大小寫)
        # 使用 .strip().lower() 處理前後空白和大小寫
        if message.content.strip().lower() == "swimming":
            # 4. 取得目標頻道
            for channel_id in target_channel_ids:
                channel = bot.get_channel(int(channel_id))
                if channel :
                    await channel.send(f"""呆呆獸的游泳池票卷補足了喔喔好開心 ><
            """
        )
                else:
                    print(f'無法找到頻道 {channel_id}') 
                    
                    
        if message.content.strip().lower() == "gym":
             # 4. 取得目標頻道
            for channel_id in target_channel_ids:
                channel = bot.get_channel(int(channel_id))
                if channel :
                    await channel.send(f"""呆呆獸的健身中心票卷補足了喔喔好開心 ><
            """
        )
                else:
                    print(f'無法找到頻道 {channel_id}') 
                    
        if message.content.strip().lower() == "fixed":
             # 4. 取得目標頻道
            for channel_id in target_channel_ids:
                channel = bot.get_channel(int(channel_id))
                if channel :
                    await channel.send(f"""呆呆獸回復正常了喔可以呼叫我了喔 ฅ^•ﻌ•^ฅ
            """
        )
                else:
                    print(f'無法找到頻道 {channel_id}') 
    # 处理其他命令
    await bot.process_commands(message)

# 定义一个 Slash 命令
@bot.slash_command(name="給我游泳池票", description="索取台大游泳池票卷 QR Code ><")
async def swimming_ticket(ctx: discord.ApplicationContext):
    driver = driver_manager.get_driver()  # 獲取可用的 driver
    await get_ticket(bot, ctx, "游泳池", driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name, maintainer_id_env)

# 定义一个 Slash 命令
@bot.slash_command(name="給我健身中心票", description="索取台大健身中心票卷 QR Code ><")
async def swimming_ticket(ctx: discord.ApplicationContext):
    driver = driver_manager.get_driver()  # 獲取可用的 driver
    await get_ticket(bot, ctx, "健身中心", driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name, maintainer_id_env)
    
    

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

        #如果沒有付款碼，請把下面程式碼的註解消除，並註解掉上一行
        #qrcode = discord.File(qrcode_path, filename="empty.png")
        
        # 發送消息並附加文件
        await ctx.followup.send(
            f"""請在 **{target_channel_name}** 頻道中

**發送 `/給我游泳池票`** 以索取台大游泳池 QR Code

**發送 `/給我健身中心票`** 以索取台大健身中心 QR Code

**QR Code** 請在三分鐘之內使用

請在給泳驗刷票前就把 QR Code 生成好喔，不然泳驗可能會覺得很奇怪(◉３◉)

台大游泳池票卷費用：**30 元**

健身中心票卷費用：**25 元**

在使用 QR Code 成功後，可以用 **街口支付** 、 **Line Pay** 或是 **轉帳**

轉帳資料：**(700) 中華郵政 00610490236328**

請幫我在轉帳備註欄填上 **姓名** 或是 **Discord 暱稱** 喔

Line pay 帳號 ID： **ycchang0324**

街口支付可以儲存下面的付款碼，再使用 APP 付款

如果有其他問題，歡迎私訊 **{maintainer_env}** (´･ω･`)
            """,
            file=qrcode,
            ephemeral=True
        )
    else:
        await ctx.respond(f"請在 {target_channel_name} 頻道中發送 /help 來獲取使用說明以及匯款資訊喔~", ephemeral=True)

bot.run(token)