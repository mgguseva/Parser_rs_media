import numpy as np
import pandas as pd
import aiohttp
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
import asyncio

async def get_soup(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return bs(content, 'html.parser')

def serbian_str_to_datetime(data):
    months_serbian = {
        "јануара": "01",
        "фебруара": "02",
        "марта": "03",
        "априла": "04",
        "маја": "05",
        "јуна": "06",
        "јула": "07",
        "августа": "08",
        "септембра": "09",
        "октобра": "10",
        "новембра": "11",
        "децембра": "12"
    }

    day = data.split(',')[1].strip().split()[0]
    month_name = data.split(',')[1].strip().split()[1]
    year = data.split(',')[2].strip().split()[0]
    time = data.split('/')[1].strip()

    month = months_serbian.get(month_name, "")

    if not month:
        raise ValueError("wrong data")

    dt = datetime.strptime(f"{day} {month} {year} {time}", "%d %m %Y %H:%M")
    return dt

async def main():
    categories_links = [
        "gazeta/politika/", "gazeta/socijum/", "gazeta/svijet/",
        "gazeta/ekonomija/", "gazeta/sport/", "magazin/kultura/",
        "magazin/tema-nedelje/", "magazin/nauka/", "magazin/scena/",
        "magazin/analize/"
    ]

    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    for item in categories_links:
        for page_number in range(1, 1000):
            url = f'https://www.frontal.rs/k/{item}page/{page_number}/'
            soup = await get_soup(url)
            div_container = soup.find('div', class_='col-md-8 mt-3')
            links = [a['href'] for a in div_container.find_all('a', href=True)][:-1]
            for link in links:
                soup_child = await get_soup(link)
                try:
                    headline = soup_child.find('h1').text
                except:
                    headline = np.nan
                try:
                    category = soup_child.find_all('div', class_='col-md-8')[0].text
                    news_text = ""
                    for p in soup_child.find('article').find_all('p'):
                        news_text = news_text + " " + p.text
                except:
                    news_text = np.nan
                try:
                    date = soup_child.find('figcaption', class_='figure-caption').text
                    parced_date = serbian_str_to_datetime(date)
                except:
                    parced_date

                try:
                    tags_container = soup_child.find('span', class_='tags-links').find_all('a', href=True)
                    tags = [tag.text for tag in tags_container]
                except:
                    tags = np.nan

                category_name = item.split("/")[1]
                
                temp_df = pd.DataFrame([{
                            'date': parced_date,
                            'headline': headline,
                            'author_name': np.nan,
                            'cleaned_text': news_text,
                            'link': link,
                            'category': category_name,
                            'tags': tags
                        }])

                df = pd.concat([df, temp_df], ignore_index=True)
                

            if parced_date < datetime(2022, 1, 1):
                break

        temp_file_name = f"temp_data_{category_name}.csv"
        df.to_csv(temp_file_name, sep="|")

    file_path = os.path.join('Parser_rs_media/data', "frontal_data.csv")
    df.to_csv(file_path, index=False, sep="|")

def run():
    asyncio.run(main())
