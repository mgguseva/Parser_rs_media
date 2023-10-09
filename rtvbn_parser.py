import aiohttp
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime
import numpy as np
import os
import asyncio

async def get_soup(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return bs(content, 'html.parser')

async def main():
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    for page in range(2000):
        url = f'https://rtvbn.com/kategorija/vijesti/{page}'
        soup = await get_soup(url)
        div_container = soup.find('div', class_='tab-content')
        links = [a['href'] for a in div_container.find_all('a', href=True)]

        for i, link in enumerate(links):
            if i % 4 == 0 and link:  
                soup_child = await get_soup(link)

                headline = soup_child.find('h1').text if soup_child.find('h1') else np.nan
                texts = soup_child.find_all('p', class_='txt')
                article = " ".join(item.text for item in texts) if texts else np.nan
                date_text = soup_child.find('span', class_='date').text.strip() if soup_child.find('span', class_='date') else None
                category = soup_child.find('strong').text.strip() if soup_child.find('strong') else np.nan

                try:
                    parsed_date = datetime.strptime(date_text, '%d.%m.%Y | %H:%M')
                except:
                    parsed_date = np.nan

                temp_df = pd.DataFrame([{
                    'date': parsed_date,
                    'headline': headline,
                    'author_name': np.nan,
                    'cleaned_text': article,
                    'link': link,
                    'category': category,
                    'tags': np.nan
                }])
                df = pd.concat([df, temp_df], ignore_index=True)

        if parsed_date and parsed_date < datetime(2022, 1, 1):
            break

    file_path = os.path.join('Parser_rs_media/data', 'rtvbn_data.csv')
    df.to_csv(file_path, index=False, sep="|") 

def run():
    asyncio.run(main())
