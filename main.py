from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pytesseract
import io
import cv2
import numpy as np
import re
import unicodedata
import os
from multiprocessing import Process
import time
from selenium.webdriver.chrome.options import Options
import sys
from datetime import datetime
from config import BOOKING_CONFIG






def save_image_matplotlib(img, path):
    path = os.path.expanduser(path)
    img.save(path)



# Verification code
def verification(driver):

    # 取得圖片
    time.sleep(1)
    captcha_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_imgValidateCode")
    catcha_png =  captcha_element.screenshot_as_png    # OCR 辨識
    raw_image = Image.open(io.BytesIO(catcha_png))
    save_image_matplotlib(raw_image, "~/alishan/original.png")
    open_cv_image = np.array(raw_image.convert('RGB'))[:, :, ::-1].copy()
    # ✅ 轉 HSV 空間
    hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)

    # ✅ 篩選低亮度（暗色字元，例如黑、深藍、深紅）
    # H: 全部, S: 全部, V: 亮度限制（數值愈小愈暗）
    lower_hsv = np.array([0, 0, 0])
    upper_hsv = np.array([180, 255, 80])  # V<=80 比較穩

    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # ✅ 模糊 + 腐蝕（讓文字更乾淨）
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.erode(blurred, kernel, iterations=1)
    pil_img = Image.fromarray(processed) 
    save_image_matplotlib(pil_img, "~/alishan/filtered.png")
    captcha_text = pytesseract.image_to_string(pil_img, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    normalized = unicodedata.normalize('NFKC', captcha_text)
    filtered = re.sub(r'[^A-Z0-9]', '', normalized)[:4]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 辨識驗證碼為：{filtered}")

     # 每次都重新抓 input（避免 stale）
    try:
        captcha_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_ValidateCode")
        captcha_input.clear()
        captcha_input.send_keys(filtered)
    except Exception as e:
        print("⚠️ 無法填入驗證碼：", e)
def wait_until_site_ready(driver, wait):
     while True:
        try:
            driver.get("https://afrts.forest.gov.tw/OT01_1.aspx")
            confirm_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='確定']")))
            driver.execute_script("arguments[0].click();", confirm_btn)
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSave")
            return
                            
        except:
            print(f"重整網頁")
            time.sleep(1)

def first_page(driver, wait):
    try:

        # ====== 選擇日期：2025/04/26 ======
        date_input = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_Field_SDate')
        driver.execute_script(f"""
            const input = document.getElementById('ctl00_ContentPlaceHolder1_Field_SDate');
            input.removeAttribute('min');
            input.removeAttribute('max');
            input.value = '{BOOKING_CONFIG["date"]}';
            input.dispatchEvent(new Event('change'));
        """)



        # ====== 選擇起點：嘉義 ======
        wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='ctl00_ContentPlaceHolder1_Field_StartStation']/option[@value='360']")))
        start_station = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_StartStation"))
        start_station.select_by_value(BOOKING_CONFIG["start_station"])

        # ====== 選擇終點：阿里山 ======
        wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='ctl00_ContentPlaceHolder1_Field_StopStation']/option[@value='378']")))
        stop_station = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_StopStation"))
        stop_station.select_by_value(BOOKING_CONFIG["stop_station"])


        # 小火車票
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Field_F_FullTicket")))
        driver.execute_script(f"""
            const el = document.getElementById('ctl00_ContentPlaceHolder1_Field_AdultTicket');
            el.value = '{BOOKING_CONFIG["train_ticket_count"]}';
        """)

        # 園區票
        driver.execute_script(f"""
            const el = document.getElementById('ctl00_ContentPlaceHolder1_Field_F_FullTicket');
            el.value = '{BOOKING_CONFIG["train_ticket_count"]}';
        """)

        captcha_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_ValidateCode")
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", captcha_input)

        verification(driver)

        # 點查詢
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSave").click()

        time.sleep(1)
        error_msg = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblMsg").text
        while "驗證碼" in error_msg :
            print({error_msg})
            captcha_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_ValidateCode")
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", captcha_input)
            verification(driver)
            # 點查詢
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSave").click()
            time.sleep(1)
            error_msg = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblMsg").text
        if "查無可售車次" in error_msg:
            print({error_msg})
            return False
        return True
    except:
        return False  # 沒有錯誤，繼續往下走
  

def second_page(driver):
    try:
        print(f"second page")
        radio = driver.find_element(By.ID, "Field_Outbound00")
        driver.execute_script("arguments[0].click();", radio)
        button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSave")
        button.click()
    except:
        print("⚠️ second_page 失敗，找不到車次選項，可能是驗證碼錯 or 無車次")
        return False
    return True

def third_page(driver):
    id_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_ID")
    id_input.clear()
    id_input.send_keys(BOOKING_CONFIG["id"])  # 改成你要輸入的字串
    phone_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_Phone")
    phone_input.clear()
    phone_input.send_keys(BOOKING_CONFIG["phone"])
    phone_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_Email")
    phone_input.clear()
    phone_input.send_keys(BOOKING_CONFIG["email"])
    checkbox = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Field_ConfirmTerms")
    if not checkbox.is_selected():
        checkbox.click()
    submit_btn = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSave")
    submit_btn.click()

def booking_flow(process_id):
    log_path = f"/home/w6522873/alishan/log/process_{process_id}.log"
    sys.stdout = open(log_path, "a", buffering=1)
    sys.stderr = sys.stdout
    print(f"start{process_id}")

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # ✅ 無頭模式
    chrome_options.add_argument('--disable-gpu')  # ⛔ 停用 GPU 加速（建議）
    chrome_options.add_argument('--no-sandbox')  # 🔐 Linux 容器化執行建議加上
    chrome_options.add_argument('--window-size=1280,800')  # ✅ 避免有些元素無法 render
    chrome_options.add_argument('--force-device-scale-factor=1')


    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )    
    wait = WebDriverWait(driver, 10)

    while True:
        # 第一步：進入主頁 + 填基本資料 + 辨識驗證碼
        wait_until_site_ready(driver, wait)
        first_ok = first_page(driver, wait)
        if not first_ok:
            print("⚠️ 第一步失敗，重試中...")
            driver.refresh()
            time.sleep(BOOKING_CONFIG["retry_interval_sec"])
            continue  # 回到 while 開頭，重新跑第一頁

        # 第二步：點選車次
        second_ok = second_page(driver)
        if not second_ok:
            driver.quit()
            print("⚠️ 第二步失敗（沒車次選項），回到第一頁重跑")
            time.sleep(1)
            driver = webdriver.Chrome(                   
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            wait = WebDriverWait(driver, 10)

            wait_until_site_ready(driver, wait)
            time.sleep(8)
            continue  # 回到 while 開頭，重新跑第一頁

        # 如果第一步、第二步都成功 → break
        break
    third_page(driver)


if __name__ == "__main__":
    processes = []
    for i in range(1):  # 🔁 你可以改這個數字來控制幾個流程
        p = Process(target= booking_flow, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    input("🎉 所有流程結束，按 Enter 離開...")
