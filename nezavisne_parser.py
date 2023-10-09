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
            try:
                charset = response.headers.get('Content-Type', '').split('charset=')[-1]
                content = await response.text(encoding=charset)
            except UnicodeDecodeError:
                print(f"Error decoding content from {url} with charset {charset}. Trying default 'utf-8'...")
                try:
                    content = await response.text()
                except UnicodeDecodeError:
                    print(f"Decoding with 'utf-8' also failed for {url}. Trying 'iso-8859-1'...")
                    content = await response.text(encoding="iso-8859-1")
            
            return bs(content, 'html.parser')


async def main():
    categories = ["bih", "gradovi", "drustvo", "obrazovanje", "ex-yu", "svijet", "hronika", "banjaluka", "intervju", "kolumne", "nezavisnistav"]
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    for category_item in categories:
        for page_number in range(1, 1000):
            url = f'https://www.nezavisne.com/novosti/{category_item}?strana={page_number}&ipp=15&'
            soup = await get_soup(url)
            div_container = soup.find('div', class_='col-12 col-sm-12 col-md-12 col-lg-8')

            if div_container:
                links = [a['href'] for a in div_container.find_all('a', href=True)[:-7]]
                for i, link in enumerate(links):
                    if i % 2 == 0:
                        link_to_article = "https:"+link
                        soup_child = await get_soup(link_to_article)
                        try:
                            headline = soup_child.find('h1').text
                        except:
                            headline = np.nan

                        try:
                            date = soup_child.find('time', class_='dateline text-muted')['datetime']
                            date = datetime.fromisoformat(date).replace(tzinfo=None)
                        except:
                            date = np.nan

                        try:
                            text = soup_child.find('div', class_='vijestTijelo clearfix').text
                            cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                        except:
                            cleaned_text = np.nan

                        try:
                            author_tag = soup_child.find('div', class_='col-lg-8 col-md-8 col-sm-12 col-xs-12').find('span', itemprop='name')
                            author_name = author_tag.get_text(strip=True)
                        except:
                            author_name = np.nan

                        category = category_item
                        tags = np.nan

                        temp_df = pd.DataFrame([{
                            'date': date,
                            'headline': headline,
                            'author_name': author_name,
                            'cleaned_text': cleaned_text,
                            'link': link_to_article,
                            'category': category,
                            'tags': tags
                        }])
                        df = pd.concat([df, temp_df], ignore_index=True)


            if isinstance(date, datetime) and date < datetime(2022, 1, 1):
                break

        temp_file_name = f"temp_data_{category_item}.csv"
        df.to_csv(temp_file_name, sep="|")

    file_path = os.path.join('Parser_rs_media/data', "nezavisne_data.csv")
    df.to_csv(file_path, index=False, sep="|")

def run():
    asyncio.run(main())
