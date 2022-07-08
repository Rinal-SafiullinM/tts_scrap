from multiprocessing.sharedctypes import Value
import os
from random import betavariate
import time
import csv
import json
import bs4
import requests
from bs4 import BeautifulSoup
from datetime import datetime
# from pprint import pprint


def get_all_pages():
    headers = {
        "Accept":"*/*",
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"
    }
    r = requests.get(url="https://www.tts.ru/sprobegom", headers = headers)

        
    if not os.path.exists("data"):
        os.mkdir("data")
  
    with open("data/page_1.html", "w", encoding="utf-8") as file:
        file.write(r.text)

    with open("data/page_1.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    pages_count = 100

    for i in range(1, pages_count):
        url = f"https://www.tts.ru/sprobegom/?PAGEN_1={i}"

        req = requests.get(url= url, headers=headers)

        with open(f"data/page_{i}.html", "w", encoding="utf-8") as file:
            file.write(req.text)
        time.sleep(2)
    
    return pages_count

def collect_data(pages_count):
    cur_date = datetime.now().strftime("%d_%m_%Y")

    with open(f"data_{cur_date}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Модель_автомобиля",
                "Ссылка",
                "Год_выпуска",
                "Пробег",
                "Цена"
            )
        )

    data = []
    for page in range(1, pages_count):
        with open(f"data/page_{page}.html", encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        items_cards = soup.find_all("div", class_="preview-card_auto-wrapper vers2")
        for item in items_cards:
            auto_model = item.find("div", class_="descriprion-model").text.strip()
            auto_photo = item.find("div", class_="preview-card_auto-img_wrapper").find("img").get("src")
            try:
                auto_price = f'{item.find("div", class_="now-price-text").find("span").text} руб.'
            except AttributeError as err:
                auto_price = ''
            auto_url = item.find("a", class_="preview-card_auto used-auto").get("href").startswith('https')
            if auto_url == True:
                auto_url = item.find("a", class_="preview-card_auto used-auto").get("href")
            else: 
                auto_url = f'https://www.tts.ru{item.find("a", class_="preview-card_auto used-auto").get("href")}' 
            auto_year = f'{item.find("div", class_="descriprion-yearMileage_year semibold").text[-4:]} г.'
            auto_milage = item.find("div", class_="descriprion-yearMileage_mileage semibold").text[7:].strip()
            
            # print(f"Article: {auto_model}\n- Price: {auto_price}\n- Year: {auto_year}\n -Milage: {auto_milage}\n- URL: {auto_url}")

            data.append(
                {
                    "auto-photo": auto_photo,
                    "auto_model": auto_model,
                    "auto_url": auto_url,
                    "auto_year": auto_year,
                    "auto_milage": auto_milage,
                    "auto_price": auto_price
                }
            )
            # pprint(data)
            with open(f"data_{cur_date}.csv", "a",encoding="utf-8", newline='') as file:
                write = csv.writer(file)

                write.writerow(
                [
                    auto_model,
                    auto_url,
                    auto_year,
                    auto_milage,
                    auto_price
                ]
            )


    with open(f"data_{cur_date}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    pages_count = get_all_pages()
    collect_data(pages_count = pages_count)

if __name__ == '__main__':
    main()