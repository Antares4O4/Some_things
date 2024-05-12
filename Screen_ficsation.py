from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import datetime
import random
import PyPDF2
import whois
import time
import os


def trace(url):
    url_2 = "https://2whois.ru/?t=traceroute" + f"&data={url[8:]}"

    response = requests.get(url_2)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    traceroute = str(soup.find('pre'))
    traceroute = traceroute.replace("  ", "   ")
    return traceroute


def capture_full_page_pdf(url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Запуск Chrome в безголовом режиме (без GUI) (Не работает)
    chrome_options.add_argument("--window-size=1600,1200")  # Установка широких размеров окна
    chrome_options.add_argument("--start-maximized")  # Максимизация окна браузера
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    # Создаем экземпляр браузера
    driver = webdriver.Chrome(options=chrome_options)

    # Открываем страницу
    driver.get(url)

    # Максимизируем окно браузера для лучшего скриншота
    driver.maximize_window()

    # Ожидаем загрузки элемента body
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Определяем высоту страницы
    total_height = driver.execute_script("return document.body.scrollHeight")
    output_file = "screenshot.pdf"

    # Задаем размеры окна браузера, чтобы сделать скриншот всей страницы
    driver.set_window_size(1920, total_height)
    c = canvas.Canvas(output_file, pagesize=A4)

    # Прокручиваем страницу и сохраняем скриншоты
    scroll_height = 0
    screenshot_count = 0

    while scroll_height < total_height:
        # Прокручиваем страницу на один экран
        driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_height)
        time.sleep(1)  # Подождем немного после прокрутки
        scroll_height += driver.execute_script("return window.innerHeight;")

        # Сохраняем скриншот
        screenshot_count += 1

        screenshot_path = f"screenshot_{screenshot_count}.png"

        driver.save_screenshot(screenshot_path)

        # Добавление скриншота в PDF с масштабированием
        c.drawImage(screenshot_path, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True)

        # Добавление URL-адреса и даты фиксации над скриншотом
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        c.setFont('FreeSans', 9)
        c.drawString(10, A4[1] - 20, f"URL: {url}")
        c.drawString(A4[0] - 180, A4[1] - 20,
                     f"Дата фиксации: {datetime.datetime.today().strftime('%d.%m.%Y %H:%M')}")

        # Переход на следующую страницу
        c.showPage()

    # Закрытие холста PDF
    c.save()

    # Закрываем браузер
    driver.quit()

    i = 0
    while i < screenshot_count:
        i += 1
        os.remove(f"screenshot_{i}.png")


def create_pdf(url):
    num = str(random.randint(0, 9999999999999))
    now = str(datetime.datetime.today().strftime('%d.%m.%Y %H:%M'))


    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf', 'UTF-8'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf', 'UTF-8'))



    content = []

    body_style_normal = ParagraphStyle('Body', fontName="FreeSans", fontSize=12, alignment=TA_JUSTIFY)
    body_style_bold = ParagraphStyle('Body', fontName="FreeSansBold", fontSize=15, alignment=TA_CENTER)
    body_style_for_Appendix = ParagraphStyle('Body', fontName="FreeSansBold", fontSize=9, alignment=TA_RIGHT)



    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"ПРОТОКОЛ " + "№ " + f"{num} от {now} UTC+06:00<br/>автоматизированного осмотра информации в сети интернет<br/>",
            body_style_bold))
    content.append(Spacer(1, 50))

    content.append(Paragraph(
        "Автоматизированной системой LABA_3 (далее по тексту «Система») была произведена фиксация следующей информации в сети Интернет:<br/>",body_style_normal))

    content.append(Paragraph(
        f"<br/><b> Страница в сети интернет расположенная по адресу:</b> {url}<br/>",body_style_normal))

    content.append(Paragraph(
        "<br/>Задачи осмотра: зафиксировать информацию, размещенную по указанной выше ссылке.<br/>",body_style_normal))

    content.append(Paragraph(
        "<br/>Оборудование и используемое программное обеспечение: Программный комплекс по фиксации информации в сети Интернет LABA_3<br/>",body_style_normal))

    a = str(whois.whois(url))
    symb_to_rem = "[,]{}\""

    for symbol in symb_to_rem:
        a = a.replace(symbol, "")
    a = a.replace("\n", "<br/>")
    a = a.replace("_", " ")

    doc = SimpleDocTemplate("report.pdf", pagesize=A4)
    doc.build(content)

    content1 = []

    content1.append(Paragraph(
        f"<br/>Приложение 1 <br/> к протоколу автоматизированного осмотра информации в сети интернет " + "№ " + f"{num} <br/>Запрос сведений WHOIS и протокол технической проверки в отношении {url}<br/>",
        body_style_for_Appendix))

    content1.append(Paragraph(
        f"<br/>{a}<br/>",
        body_style_normal))

    doc = SimpleDocTemplate("report1.pdf", pagesize=A4)
    doc.build(content1)

    content2 = []

    content2.append(Paragraph(
        f"<br/> Приложение 2 <br/> к протоколу автоматизированного осмотра информации в сети интернет " + "№ " + f"{num} <br/> Запрос сведений DNS и протокол технической проверки в отношении {url} <br/>",
        body_style_for_Appendix))

    content2.append(Paragraph(
        f"<br/><br/>{trace(url)}<br/><br/>",
        body_style_normal))

    doc = SimpleDocTemplate("report2.pdf", pagesize=A4)
    doc.build(content2)


if __name__ == "__main__":
    url = "https://qna.habr.com/q/1129656"
    create_pdf(url)

    capture_full_page_pdf(url)

    # Объединение PDF-файлов
    mergeFile = PyPDF2.PdfFileMerger()
    mergeFile.append(PyPDF2.PdfFileReader('report.pdf', 'rb'))
    mergeFile.append(PyPDF2.PdfFileReader('report1.pdf', 'rb'))
    mergeFile.append(PyPDF2.PdfFileReader('report2.pdf', 'rb'))
    mergeFile.append(PyPDF2.PdfFileReader('screenshot.pdf', 'rb'))
    mergeFile.write("output.pdf")

    os.remove("report.pdf")
    os.remove("report1.pdf")
    os.remove("report2.pdf")
    os.remove("screenshot.pdf")

    print("PDF успешно создан.")
