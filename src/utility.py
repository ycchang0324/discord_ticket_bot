
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
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

def log_to_file(data, file_path):
    # 獲取當前 Python 檔案的路徑
    file_path = os.path.join(os.path.dirname(__file__), file_path)
    
    # 確保目錄存在，若不存在則創建
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # 獲取當前時間
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 將時間加到日誌資料中
    log_entry = f"{current_time} - {data}"
    
    # 以追加模式打開文件，若文件不存在則自動創建
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(log_entry + '\n')



def sync_login_process(driver, url, account, password):

    try:
        # 設定頁面加載超時，防止無限期等待
        driver.set_page_load_timeout(20) 
        driver.get(url)
        
        # 使用快速輪詢的等待 (0.1秒檢查一次)
        wait = WebDriverWait(driver, 10, poll_frequency=0.1)
        
        # 尋找學生登入按鈕
        student_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/sso2_go.php"]')))
        
        # 改用 JS 點擊：這比 .click() 更快，且不會因為瀏覽器鎖定而卡住底層通訊
        driver.execute_script("arguments[0].click();", student_button)

        # 填寫表單
        user_input = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$UsernameTextBox")))
        user_input.send_keys(account)
        
        pass_input = driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$PasswordTextBox")
        pass_input.send_keys(password)
        
        login_btn = driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$SubmitButton")
        driver.execute_script("arguments[0].click();", login_btn)
        
        return True

    except NoSuchElementException as e:
        # 記錄找不到元素的錯誤
        logging.error(f"登入過程中找不到元素: {e}")
        return False

        
    except TimeoutException as e:
        # 記錄超時錯誤
        logging.error(f"登入過程中操作超時: {e}")
        return False
        
    except UnexpectedAlertPresentException as e:
        # 記錄未預期的彈出框錯誤
        logging.error(f"未預期的彈出框: {e}")
        return False
        
    except WebDriverException as e:
        # 記錄 driver 被關閉或無法運行的錯誤
        logging.error(f"WebDriver 無法運行或已被關閉: {e}")
        return False
        
    except Exception as e:
        # 捕捉所有其他未知錯誤並記錄
        logging.error(f"登入過程中發生未知錯誤: {e}")
        return False
    

async def login(driver, url, account, password):
    # 使用 asyncio.to_thread 將同步工作丟到別的 Thread
    # 這樣你的 Discord Bot (主 Thread) 才能繼續跳動心跳 (Heartbeat)
    success = await asyncio.to_thread(sync_login_process, driver, url, account, password)
    return success

def sync_logout_process(driver):
    """
    純同步的登出邏輯，處理 Selenium 的阻塞操作
    """
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

async def logout(driver):
    """
    供 Discord Bot 呼叫的非同步介面
    """
    # 丟到 Thread 執行，防止阻塞 Discord Heartbeat
    success = await asyncio.to_thread(sync_logout_process, driver)
    return success


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
    qr_button = driver.find_element(By.XPATH, f'//div[contains(text(), "{category}")]//following::button[text()="進場使用 ( QRCode )"][1]')
    qr_button.click()
    
    await asyncio.sleep(1)
    
    driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe'))
    
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 獲取當前 Python 檔案的路徑
    parent_dir = os.path.dirname(current_dir)

    image_path = os.path.join(parent_dir, 'img', 'screenshot.png')  # 設定保存的子資料夾和檔名
    image_path_crop = os.path.join(parent_dir, 'img', 'screenshot_crop.png')  # 設定保存的子資料夾和檔名

    driver.save_screenshot(image_path)

    crop_center(image_path, image_path_crop, 400, 700)

    driver.refresh()


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

    
    