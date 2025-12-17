# 導入Discord.py模組
import discord
# 導入commands指令模組
from discord.ext import commands
from discord import app_commands 
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


from src.get_ticket import get_ticket
from dotenv import load_dotenv

import time
from pathlib import Path
import asyncio

# 1. 建立 Bot 類別來處理同步 (這樣最穩)
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # 確保可以讀取訊息 (on_message 需要)
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 這行是關鍵：將斜線指令同步到 Discord 伺服器
        await self.tree.sync()
        print(f"Slash 指令同步完成！")

bot = MyBot()
bot.is_ticket_generating = False

# 載入 .env 檔案中的環境變數
load_dotenv()
target_channel_ids = os.getenv('CHANNEL_IDS').split(',')
target_channel_name = os.getenv('CHANNEL_NAME')
your_account = os.getenv('ACCOUNT')  # NTU COOL 帳號
your_password = os.getenv('PASSWORD')  # NTU COOL 密碼
your_web_url = os.getenv('URL')  # 租借系統網址
token = os.getenv('TOKEN')
maintainer_id_env = os.getenv('MAINTAINER_ID')
bot_name_env = os.getenv('BOT_NAME')

class WebDriverManager:
    def __init__(self, options):
        self.options = options
        self.driver = None # 延遲初始化，等真正需要或 healthcheck 時再建立

    def create_driver(self):
        print("正在啟動新的 Chrome 實例...")
        # 這裡不需要 ChromeDriverManager，因為 Dockerfile 已經裝好固定路徑的 Chrome
        return webdriver.Chrome(options=self.options)

    def get_driver(self):
        if self.driver is None:
            self.driver = self.create_driver()
            return self.driver
        
        try:
            # 檢查 driver 是否還能通訊
            _ = self.driver.window_handles 
        except Exception:
            print("偵測到 WebDriver 失效，嘗試重啟...")
            try:
                self.driver.quit()
            except:
                pass
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


async def health_check_task():
    """獨立的背景任務，每分鐘執行一次"""
    while True:
        try:
            # 1. 嘗試與 WebDriver 通訊，確認 Chrome 是否崩潰
            # 即使 get_ticket 正在運行，這裡獲取同一個 driver 實例通常也能讀取屬性
            driver = driver_manager.get_driver()
            _ = driver.title  # 輕量檢查
            
            # 2. 如果沒噴錯，更新心跳檔案
            with open("/tmp/heartbeat", "w") as f:
                f.write(str(time.time()))
            
        except Exception as e:
            # 如果 Chrome 真的卡死了，這裡會噴錯，就不會更新檔案
            print(f"Healthcheck 偵測到異常: {e}")
            
        # 每 60 秒跑一次檢查
        await asyncio.sleep(60)

# 在 on_ready 加入
@bot.event
async def on_ready():
    print(f"{bot.user} 已上線")
    bot.loop.create_task(health_check_task())

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
                    await channel.send(f"""我是{bot_name_env}，很高興認識你 ▼・ᴥ・▼

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
        if message.content.strip().lower() == "swim":
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
@bot.tree.command(name="給我游泳池票", description="索取台大游泳池票卷 QR Code ><")
async def swimming_ticket(interaction: discord.Interaction):
    driver = driver_manager.get_driver()  # 獲取可用的 driver
    await get_ticket(bot, interaction, "游泳池", driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name, maintainer_id_env)

# 定义一个 Slash 命令
@bot.tree.command(name="給我健身中心票", description="索取台大健身中心票卷 QR Code ><")
async def gym_ticket(interaction: discord.Interaction):
    driver = driver_manager.get_driver()  # 獲取可用的 driver
    await get_ticket(bot, interaction, "健身中心", driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name, maintainer_id_env)
    
    

@bot.tree.command(name="help", description="呆呆獸怎麼用")
async def ticket(interaction: discord.Interaction):
    if str(interaction.channel_id) in target_channel_ids:
        # 告訴 Discord 正在處理，延遲回應
        await interaction.response.defer(ephemeral=True)

        qrcode_path = os.path.join('img', 'payment_qrcode.png')
        
        # 檢查文件是否存在，防止出錯
        if not os.path.exists(qrcode_path):
            qrcode_path = os.path.join('img', 'payment_qrcode_example.png')
        
        if not os.path.exists(qrcode_path):
            await interaction.followup.send("出錯了，請聯絡管理員")
            return
        
        
        qrcode = discord.File(qrcode_path, filename="payment_qrcode.png")

        #如果沒有付款碼，請把下面程式碼的註解消除，並註解掉上一行
        #qrcode = discord.File(qrcode_path, filename="empty.png")
        
        # 發送消息並附加文件
        await interaction.followup.send(
            f"""請在 **{target_channel_name}** 頻道中

**發送 `/給我游泳池票`** 以索取台大游泳池 QR Code

**發送 `/給我健身中心票`** 以索取台大健身中心 QR Code

**QR Code** 請在三分鐘之內使用

請在給泳驗刷票前就把 QR Code 生成好喔，不然泳驗可能會覺得很奇怪(◉３◉)

台大游泳池票卷費用：**30 元**

健身中心票卷費用：**25 元**

在使用 QR Code 成功後，可以用 **轉帳** 、 **Line Pay** 或是 **街口支付** 

轉帳資料：**(700) 中華郵政 00610490236328**

請幫我在轉帳備註欄填上 **姓名** 或是 **Discord 暱稱** 喔

Line pay 帳號 ID： **ycchang0324**

街口支付可以儲存下面的付款碼，再使用 APP 付款

如果有其他問題，歡迎私訊 **張原嘉** (´･ω･`)
            """,
            file=qrcode,
            ephemeral=True
        )
    else:
        await interaction.response.send_message(f"請在 {target_channel_name} 頻道中發送 /help 來獲取使用說明以及匯款資訊喔~", ephemeral=True)

bot.run(token)