import numpy as np
import pandas as pd
import aiohttp
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
import asyncio

import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs

async def get_soup(url):
    async with aiohttp.ClientSession() as session:
        try: 
            async with session.get(url, timeout=2) as response:
                content_type = response.headers.get('Content-Type', '')
                charset = None
                
                # Extract charset from content_type if exists
                if "charset=" in content_type:
                    charset = content_type.split('charset=')[-1]

                # Validate charset
                if charset and charset.lower() not in ('utf-8', 'iso-8859-1'):
                    print(f"Unexpected charset '{charset}' for {url}. Defaulting to 'utf-8'.")
                    charset = 'utf-8'

                try:
                    content = await response.text(encoding=charset)
                except UnicodeDecodeError:
                    print(f"Error decoding content from {url} with charset {charset}. Trying 'iso-8859-1'.")
                    content = await response.text(encoding="iso-8859-1")
                
                return bs(content, 'html.parser')

        except asyncio.TimeoutError:
            print(f"Request to {url} timed out.")
            return None
        except aiohttp.ClientPayloadError:
            print(f"Incomplete payload from {url}.")
            return None
        except Exception as e:
            print(f"Error while requesting {url}: {e}")
            return None



async def main():
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])
    date = datetime.now()
    url ='https://lat.rtrs.tv/index.php'

    soup = await get_soup(url)
    div_container = soup.find('div', class_='container main-width-fix z_fix')
    link = div_container.find('a', href=True)
    page_number = int(link['href'][link['href'].find("id=")+3:])
    
    while date >= datetime(2022, 1, 1):
        url_p = f'https://lat.rtrs.tv/vijesti/vijest.php?id={page_number}'
        soup_p = await get_soup(url_p)
        try:
            div_container_p = soup_p.find('div', class_='col-md-8 col-sm-8')
            headline = div_container_p.find('h1').text
        except:
            headline = np.nan
        try:
            info_time_author =  div_container_p.find('div', class_='vrijeme-izvor').text if div_container_p.find('div', class_='vrijeme-izvor') else np.nan
            date = datetime.strptime(info_time_author[:10], '%d/%m/%Y')
        except:
            date
        
        try:
            author = info_time_author[info_time_author.find("Аутор")+6:].strip()
        except:
            author = np.nan

        try:    
            news_text = div_container_p.find('div', class_='lead').text
            nws_body = div_container_p.find('div', class_='nwzbody').find_all('p')
            for p in nws_body:
                news_text = news_text + p.text
        except:
            news_text = np.nan
            
        try:
            category = soup_p.find('div', class_='col-md-12 col-sm-12').find('li', class_='sel').text
        except:
            category = np.nan


        temp_df = pd.DataFrame([{
                        'date': date,
                        'headline': headline,
                        'author_name': author,
                        'cleaned_text': news_text,
                        'link': url_p,
                        'category': category,
                        'tags': np.nan
                    }])
        
        df = pd.concat([df, temp_df], ignore_index=True)

        page_number -= 1

    file_path = os.path.join('Parser_rs_media/data', 'rtrs_data.csv')
    df.to_csv(file_path, index=False, sep="|") 

def run():
    asyncio.run(main())
