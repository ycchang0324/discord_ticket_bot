
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException, WebDriverException
import time
import re
import os
from PIL import Image
import logging
from datetime import datetime
import asyncio




# 獲取當前 Python 檔案的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 設定保存的子資料夾和檔名
log_dir = os.path.join(parent_dir, 'log')
error_path = os.path.join(log_dir, 'error.txt')

# 如果目錄不存在，則創建該目錄
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 如果檔案不存在，則創建空檔案
if not os.path.exists(error_path):
    with open(error_path, 'w') as f:
        pass

# 配置 logging 模組，將日誌寫入 error.txt 文件
logging.basicConfig(filename=error_path, level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class BrowserCriticalError(Exception):
    """當 WebDriver 完全無法通訊或環境損壞時拋出"""
    pass




# 錯誤診斷函數
def handle_error_diagnostics(driver, error_summary):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("/app/log", exist_ok=True)
    screenshot_path = f"/app/log/login_error_{timestamp}.png"
    try:
        current_url = driver.current_url
        driver.save_screenshot(screenshot_path)
        log_msg = f"{error_summary} | 網址: {current_url} | 截圖: {screenshot_path}"
        logging.error(log_msg)
        print(log_msg, flush=True)
    except Exception as e:
        print(f"診斷失敗: {e}", flush=True)




async def logout(driver):
    try:
        if driver.session_id is None:
            raise WebDriverException("Driver 已經被關閉。")

        # 1. 使用 WebDriverWait 尋找登出按鈕
        wait = WebDriverWait(driver, 10, poll_frequency=0.1)
        logout_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@title="登出"]')))
        
        # 2. 使用 JS 點擊，避免點擊後彈窗出現導致 Selenium 通訊卡死
        driver.execute_script("arguments[0].click();", logout_button)

        # 3. 處理彈窗
        # 如果你已經設定了 unhandledPromptBehavior="accept"，
        # 其實可以不用寫這段，但為了保險起見保留顯式處理
        try:
            wait.until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            # 如果設定了自動 accept，這裡抓不到彈窗是正常的
            pass

        return True

    except NoSuchElementException as e:
        logging.error(f"找不到 '登出' 按鈕: {e}")
        return False
    except TimeoutException as e:
        logging.error(f"登出處理超時: {e}")
        return False
    except UnexpectedAlertPresentException as e:
        logging.error(f"登出時遇到未預期彈窗: {e}")
        # 如果遇到了就嘗試 accept 它
        try: driver.switch_to.alert.accept()
        except: pass
        return False
    except Exception as e:
        logging.error(f"登出過程中發生未知錯誤: {e}")
        return False


def crop_center(image_path, output_path, crop_width, crop_height):
    # 開啟截圖
    img = Image.open(image_path)

    # 獲取圖像尺寸
    img_width, img_height = img.size

    # 計算裁剪區域的左上角和右下角坐標 (以中心為基準)
    left = (img_width - crop_width) // 2
    top = (img_height - crop_height) // 2
    right = (img_width + crop_width) // 2
    bottom = (img_height + crop_height) // 2

    # 裁剪圖像
    cropped_img = img.crop((left, top, right, bottom))


    # 保存裁剪後的圖像
    cropped_img.save(output_path)

async def getImage(driver, category):
    # 建立等待工具，最多等 15 秒
    wait = WebDriverWait(driver, 15)
    
    try:
        # 1. 強化 XPath (使用 contains 避開空格與全半形問題)
        # 我們找包含 category 名稱的 div，後面第一個包含 "QRCode" 字樣的按鈕
        qr_xpath = f'//div[contains(text(), "{category}")]//following::button[contains(text(), "QRCode")][1]'
        
        print(f"DEBUG: 正在等待 [{category}] 的 QR Code 按鈕出現...", flush=True)
        
        # 2. 使用 WebDriverWait 確保按鈕「已出現」且「可點擊」
        # 這會解決你遇到的 NoneType 問題
        qr_button = wait.until(EC.element_to_be_clickable((By.XPATH, qr_xpath)))
        
        # 3. 強制捲動並點擊 (使用 JavaScript 點擊以無視任何圖層遮擋)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", qr_button)
        driver.execute_script("arguments[0].click();", qr_button)
        print(f"✅ 成功觸發 {category} 的 QR Code 彈窗")

        # 4. 等待 iframe 出現並切換 (取代 sleep(1))
        # wait.until 會在 iframe 一出現的瞬間就繼續，比 sleep(1) 快且穩
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe'))
        
        # 5. 設定路徑與存檔
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        img_dir = os.path.join(parent_dir, 'img')
        os.makedirs(img_dir, exist_ok=True) # 確保資料夾存在

        image_path = os.path.join(img_dir, 'screenshot.png')
        image_path_crop = os.path.join(img_dir, 'screenshot_crop.png')

        # 6. 截圖與裁切
        driver.save_screenshot(image_path)
        
        # 這裡假設你的 crop_center 已經在 utility.py 中定義好了
        from src.utility import crop_center
        crop_center(image_path, image_path_crop, 400, 700)
        
        print(f"✅ 截圖已儲存並裁切：{image_path_crop}")

        # 7. 清理狀態：切回主頁面並刷新，避免影響下次操作
        driver.switch_to.default_content()
        driver.refresh()

    except TimeoutException:
        print(f"❌ 錯誤：在 15 秒內找不到 {category} 的按鈕或 QR Code 視窗未彈出", flush=True)
        # 存下一張 debug 截圖看看當時發生了什麼
        driver.save_screenshot(os.path.join(parent_dir, 'log', 'debug_getimage_timeout.png'))
        raise Exception(f"無法在頁面上定位到 {category} 的 QR Code 按鈕")
    except Exception as e:
        print(f"❌ getImage 發生未知錯誤: {str(e)}", flush=True)
        raise e


def get_ticket_num(driver, category):
    try:
        # 嘗試找到與 category 匹配的父 div 元素
        parent_div = driver.find_element(By.XPATH, f'//div[contains(@class, "TL") and contains(text(), "{category}")]/ancestor::div[@class="TI"]')
        
        # 嘗試找到包含 "可使用" 字樣的 span
        available_span = parent_div.find_element(By.XPATH, './/div[@class="CI"]/span[contains(text(), "可使用")]')
        available_text = available_span.text
        
        # 從文本中提取可用票數
        available_tickets = re.search(r'可使用 (\d+) 張', available_text).group(1)
        return available_tickets
    except NoSuchElementException as e:
        # 記錄找不到元素的錯誤
        logging.error(f"未找到與 {category} 匹配的票卷資訊: {e}")
        return None
    except AttributeError as e:
        # 記錄文本格式錯誤的錯誤
        logging.error(f"票數文本格式錯誤或不存在: {e}")
        return None

async def check_ticket_num(driver, ticket_num, category):
    success = False
    counter = 0
    TIMEOUT_SECONDS = 5 * 60  # 5 分鐘
    start_time = time.time()
    while counter < 20 and (time.time() - start_time) < TIMEOUT_SECONDS:
        await asyncio.sleep(10)
        driver.refresh()
        system_ticket_num = get_ticket_num(driver, category)
        if system_ticket_num == None:
            success = "error"
            break
        elif int(system_ticket_num) == ticket_num - 1:
            success = True
            break
        counter += 1
        print(f"現在的 counter: {counter}")
    return success