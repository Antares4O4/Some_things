import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import datetime
import PyPDF2
import whois
import time
from bs4 import BeautifulSoup
import requests


def trace(url):
    url_2 = "https://2whois.ru/?t=traceroute" + f"&data={url[8:]}"

    response = requests.get(url_2)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    traceroute = str(soup.find('pre'))
    traceroute = traceroute.replace("  ", "   ")
    return traceroute


def capture_full_page_pdf(url):
    # Настройка параметров Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Запуск Chrome в безголовом режиме (без GUI)
    chrome_options.add_argument("--window-size=1600,1200")  # Установка широких размеров окна
    chrome_options.add_argument("--start-maximized")  # Максимизация окна браузера
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    # Инициализация драйвера Chrome
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Вычисление высоты страницы
    total_height = driver.execute_script("return document.body.scrollHeight")

    # Инициализация холста PDF
    output_file = "screenshot.pdf"
    c = canvas.Canvas(output_file, pagesize=A4)

    # Установка начальной позиции страницы
    current_height = 0

    # Вычисление коэффициента масштабирования
    scale_factor = A4[0] / 1600  # Ширина A4 разделенная на ширину браузера
    i = 0
    # Цикл по странице и добавление содержимого в PDF
    while current_height < total_height:
        # Прокручиваем страницу на один экран
        driver.execute_script("window.scrollTo(0, arguments[0]);", current_height)
        time.sleep(1)  # Подождем немного после прокрутки
        current_height += driver.execute_script("return window.innerHeight;")


        # Сохранение скриншота текущего вида
        screenshot_path = f"temp_{i}.png"
        driver.save_screenshot(screenshot_path)

        # Добавление скриншота в PDF с масштабированием
        c.drawImage(screenshot_path, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True)

        # Добавление URL-адреса и даты фиксации над скриншотом
        c.setFont("Helvetica", 8)
        c.drawString(10, A4[1] - 20, f"URL: {url}")
        c.drawString(A4[0] - 180, A4[1] - 20,
                     f"Date of fixation: {datetime.datetime.today().strftime('%m.%d.%Y %H:%M')}")

        # Переход на следующую страницу
        c.showPage()

        # Обновление текущей высоты
        current_height += int(A4[1] / scale_factor)
        i += 1

    # Закрытие холста PDF
    c.save()
    # Закрытие драйвера
    driver.quit()

    i_0 = 0

    while i_0 < i:
        os.remove(f"temp_{i_0}.png")
        i_0 += 1


def create_pdf(url):
    num = str(random.randint(0, 9999999999999))
    now = str(datetime.datetime.today().strftime('%m.%d.%Y %H:%M'))
    content = []

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"<b> PROTOCOL " + "No " + f"{num} on {now} UTC+06:00</b> <br/>Automated Inspection of Information on the Internet<br/>",
            ParagraphStyle(name='Name', fontFamily='Arial', fontSize=14, alignment=TA_CENTER)))
    content.append(Spacer(1, 50))

    content.append(Paragraph(
        "The following information was recorded by the automated system LABA_3:<br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=12, alignment=TA_JUSTIFY)))

    content.append(Paragraph(
        f" <ol><li>Web page located at: {url}</li></ol><br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=12, alignment=TA_JUSTIFY)))

    content.append(Paragraph(
        "<br/><b>Inspection tasks:</b> Record information from the specified link.<br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=12, alignment=TA_JUSTIFY)))

    content.append(Paragraph(
        "<br/><b>Equipment and software used:</b> <ul><li>Software complex LABA_3</li></ul><br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=12, alignment=TA_JUSTIFY)))

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
        f"<br/>Appendix 1 <br/> to the protocol of automated inspection of information on the Internet " + "No " + f"{num} <br/>Reques"
                                                                                                                   f"t for WHOIS information<br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=10, alignment=TA_RIGHT)))

    content1.append(Paragraph(
        f"<br/>{a}<br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=10, alignment=TA_JUSTIFY)))

    doc = SimpleDocTemplate("report1.pdf", pagesize=A4)
    doc.build(content1)

    content2 = []

    content2.append(Paragraph(
        f"<br/>Appendix 1 <br/> to the protocol of automated inspection of information on the Internet " + "No " + f"{num} <br/>Reques"
                                                                                                                   f"t for Tcp trace route information<br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=10, alignment=TA_RIGHT)))

    content2.append(Paragraph(
        f"<br/><br/>{trace(url)}<br/><br/>",
        ParagraphStyle(name='Name', fontFamily='Arial', fontSize=10, alignment=TA_JUSTIFY)))

    doc = SimpleDocTemplate("report2.pdf", pagesize=A4)
    doc.build(content2)


if __name__ == "__main__":
    url = "https://omsu.ru"
    create_pdf(url)

    # Инициализация общего прогресс-бара

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