import os
import threading
import time
from flask import Flask
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib
import ssl

url = 'https://ru.womensecret.com/ru/ru/%D0%B4%D0%BE%D0%BC%D0%B0%D1%88%D0%BD%D1%' \
      '8F%D1%8F-%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0/%D0%B4%D0%BB%D0%B8%D0%BD%D0%' \
      'BD%D1%8B%D0%B5-%D0%BF%D0%B8%D0%B6%D0%B0%D0%BC%D1%8B/%D0%B4%D0%BB%D0%B8%D0%BD' \
      '%D0%BD%D0%B0%D1%8F-%D0%BF%D0%B8%D0%B6%D0%B0%D0%BC%D0%B0-%D0%B1%D0%BE%D1%80%' \
      'D0%B4%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE-%D1%86%D0%B2%D0%B5%D1%82%D0%B0-%C2%AB%D0' \
      '%B3%D0%B0%D1%80%D1%80%D0%B8-%D0%BF%D0%BE%D1%82%D1%82%D0%B5%D1%80%C2%BB/31381' \
      '35.html?dwvar_3138135_color=69#start=1'
sender_email = os.environ.get('S_EMAIL')
receiver_email = os.environ.get('R_EMAIL')
host = "smtp.gmail.com"
message = """\
Subject: Reminder (Harry Potter sleepwear)

Andrey, sleepwear is available in the shop.\n{}""".format(url)
port = 465
password = os.environ.get('PSWD')

server = Flask(__name__)


@server.route('/')
def webhook():
    return '!', 200


def set_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    return driver


def send_mail():
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def main():
    upd_time = 3600
    start_time = time.time() - upd_time
    while True:
        if (time.time() - start_time) < upd_time:
            continue
        else:
            start_time = time.time()
            driver = set_driver()
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            content = soup.find_all('input', {'class': 'visuallyhidden js-stock-reservation', 'data-size-id': 'S'})
            send_mail()
            if 'disabled' in str(content):
                print('There is no size available for purchase')
            else:
                send_mail()
                driver.quit()
                break
            driver.quit()


if __name__ == '__main__':
    threading.Thread(target=server.run, args=("0.0.0.0", int(os.environ.get('PORT', 5000)))).start()
    main()
