
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException, WebDriverException
import time
import re
import os
from PIL import Image
import logging
from datetime import datetime



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



def login(driver, url, account, password):
    success = True
    try:
        if driver.session_id is None:
            raise WebDriverException("Driver 已經被關閉。")
        # 導航到 URL
        driver.get(url)
        
        # 點擊學生登入按鈕
        student_button = driver.find_element(By.XPATH, '//a[@href="/sso2_go.php"]')
        student_button.click()

        # 輸入帳號
        account_field = driver.find_element(By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$UsernameTextBox']")
        account_field.send_keys(account)

        # 輸入密碼
        password_field = driver.find_element(By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$PasswordTextBox']")
        password_field.send_keys(password)

        # 點擊登入按鈕
        login_btn = driver.find_element(By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$SubmitButton']")
        login_btn.click()

        # 等待並處理可能的彈出框
        time.sleep(1)
        alert = Alert(driver)
        alert.accept()

    except NoSuchElementException as e:
        # 記錄找不到元素的錯誤
        logging.error(f"登入過程中找不到元素: {e}")
        success = False
    except TimeoutException as e:
        # 記錄超時錯誤
        logging.error(f"登入過程中操作超時: {e}")
        success = False
    except UnexpectedAlertPresentException as e:
        # 記錄未預期的彈出框錯誤
        logging.error(f"未預期的彈出框: {e}")
        success = False
    except WebDriverException as e:
        # 記錄 driver 被關閉或無法運行的錯誤
        logging.error(f"WebDriver 無法運行或已被關閉: {e}")
        success = False
        
    except Exception as e:
        # 捕捉所有其他未知錯誤並記錄
        logging.error(f"登入過程中發生未知錯誤: {e}")
        success = False
    return success

def logout(driver):
    success = True
    try:
        if driver.session_id is None:
            raise WebDriverException("Driver 已經被關閉。")

        logout_button = driver.find_element(By.XPATH, '//a[@title="登出"]')
        logout_button.click()
        time.sleep(1)

        # 處理登出後的彈出警告框
        alert = Alert(driver)
        alert.accept()
    except NoSuchElementException as e:
        # 記錄找不到登出按鈕的錯誤
        logging.error(f"找不到 '登出' 按鈕: {e}")
        success = False
    except TimeoutException as e:
        # 記錄彈出框超時的錯誤
        logging.error(f"處理彈出框超時: {e}")
        success = False
    except UnexpectedAlertPresentException as e:
        # 記錄未預期的彈出框錯誤
        logging.error(f"未預期的彈出框: {e}")
        success = False
    except WebDriverException as e:
        # 記錄 driver 被關閉或無法運行的錯誤
        logging.error(f"WebDriver 無法運行或已被關閉: {e}")
        success = False
    except Exception as e:
        # 記錄所有其他未知錯誤
        logging.error(f"登出過程中發生未知錯誤: {e}")
        success = False

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

def getImage(driver, category):   
    qr_button = driver.find_element(By.XPATH, f'//div[contains(text(), "{category}")]//following::button[text()="進場使用 ( QRCode )"][1]')
    qr_button.click()
    
    time.sleep(1)
    
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

def check_ticket_num(driver, ticket_num, category):
    success = False
    counter = 0
    while counter < 20:
        time.sleep(10)
        driver.refresh()
        system_ticket_num = get_ticket_num(driver, category)
        if system_ticket_num == None:
            success = "error"
            break
        elif int(system_ticket_num) == ticket_num - 1:
            success = True
            break
        counter += 1
    return success

async def send_message_to_maintainer(message, user):
    try:
        
        if user:
            # 2. 對 User 物件使用 send 方法發送私訊
            await user.send(message)
            print(f"成功發送私訊給 {user.name} ({user})")
        else:
            print(f"找不到 ID 為 {user} 的使用者。")

    except discord.Forbidden:
        # 如果使用者設定了隱私不接收來自非朋友的私訊，會拋出 Forbidden 錯誤
        print(f"無法發送私訊給 ID 為 {user} 的使用者，可能因為隱私設定阻擋。")
    except Exception as e:
        print(f"發送私訊時發生錯誤: {e}")
    # --- 私訊發送邏輯結束 ---