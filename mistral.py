import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import html2text  # HTML to Markdown dönüştürme için html2text modülünü ekliyoruz

# Tarayıcı seçenekleri
options = uc.ChromeOptions()
options.add_argument(r"--user-data-dir=C:\Users\Onur\AppData\Local\Google\Chrome\User Data")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-popup-blocking")

# Tarayıcıyı başlat
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def wait_for_page_load(driver, timeout=15):
    """Sayfanın tamamen yüklenmesini bekler."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def wait_for_complete_response(driver, class_name, old_texts, timeout=30, check_interval=2):
    """Yeni cevabın tamamen yüklenmesini bekler ve HTML içeriğini döndürür."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, class_name)) > len(old_texts)
        )
        element = driver.find_elements(By.CLASS_NAME, class_name)[-1]

        previous_html = ""
        elapsed_time = 0

        while elapsed_time < timeout:
            current_html = element.get_attribute("outerHTML")

            # Yavaş yüklenmiş cevabı beklemek için kontrol yapıyoruz
            if current_html.strip() and current_html != previous_html:
                previous_html = current_html
                time.sleep(check_interval)
                elapsed_time += check_interval
            else:
                break  

        # Eğer cevabın tam olarak yüklenmesini beklediysen, bu html'i döndürür
        return previous_html if previous_html.strip() else None
    except:
        return None

# Mistral'dan cevap al
driver.get("https://chat.mistral.ai/chat")
wait_for_page_load(driver)

# Mesaj gönderme
with open("messagetobesent.txt", "r", encoding="utf-8") as file:
    mesaj = file.read().strip()

textarea = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
textarea.send_keys(mesaj)
textarea.send_keys(Keys.ENTER)

previous_responses = driver.find_elements(By.CLASS_NAME, "prose")
mistral_html = wait_for_complete_response(driver, "prose", previous_responses)

driver.quit()

# Yanıtı kaydetme
html_output_dir = "answer/html_responses"
os.makedirs(html_output_dir, exist_ok=True)

if mistral_html:
    # HTML'yi Markdown'a dönüştür
    markdown_text = html2text.html2text(mistral_html)  # html2md yerine html2text kullanılıyor
    
    # HTML cevabını kaydet
    with open(f"{html_output_dir}/mistral_answer.html", "w", encoding="utf-8") as file:
        file.write(mistral_html)

    # Markdown cevabını kaydet
    markdown_output_dir = "answer/markdown_responses"
    os.makedirs(markdown_output_dir, exist_ok=True)

    with open(f"{markdown_output_dir}/mistral_answer.md", "w", encoding="utf-8") as file:
        file.write(markdown_text)
else:
    print("Mistral yanıtı alınamadı.")