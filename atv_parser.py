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
    categories_links = [
        "republika-srpska", "vijesti/drustvo", "vijesti/region",
        "vijesti/svijet", "vijesti/ekonomija", "vijesti/bih",
        "vijesti/banja-luka", "vijesti/srbija", "vijesti/gradovi-i-opstine"
    ]
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    for item in categories_links:
        for page_number in range(1, 1000):
            url = f'https://www.atvbl.rs/{item}?page={page_number}'
            soup = await get_soup(url)
            div_container = soup.find('div', class_='row -mx-2 articles-list-container') 
            links = [a['href'] for a in div_container.find_all('a', href=True)]
            for link in links:
                soup_child = await get_soup(link)
                container = soup_child.find('div', class_='col-12 p-0')
                try:
                    headline = container.find('h1').text
                except:
                    headline = np.nan

                try:
                    author = container.find('strong').text
                except:
                    author = np.nan
                try:           
                    parsed_date = datetime.strptime(container.find('span', class_='text-capitalize').text.strip(), "%d.%m.%Y.")
                except:
                    parsed_date = np.nan
                try:
                    news_text = ""
                    for p in soup_child.find('div', class_='article-content').find_all('p'):
                        news_text = news_text + " " + p.text
                except:
                    news_text = np.nan
                
                try:
                    tags_container = soup_child.find('ul', class_='tags-list').find_all('a', href=True)
                    tags = [tag.text for tag in tags_container]
                except:
                    tags = np.nan

                try:            
                    category = item.split("/")[1]
                except:        
                    category = item

                temp_df = pd.DataFrame([{
                            'date': parsed_date,
                            'headline': headline,
                            'author_name': author,
                            'cleaned_text': news_text,
                            'link': link,
                            'category': category,
                            'tags': tags
                        }])

                df = pd.concat([df, temp_df], ignore_index=True)

            if parsed_date < datetime(2022, 1, 1):
                break
        temp_file_name = f"temp_data_{category}.csv"
        df.to_csv(temp_file_name, sep="|")

    file_path = os.path.join('Parser_rs_media/data', "atv_data.csv")
    df.to_csv(file_path, index=False, sep="|")

def run():
    asyncio.run(main())
