import numpy as np
import pandas as pd
import aiohttp
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
import asyncio

async def get_soup(url):
    async with aiohttp.ClientSession() as session:
        try: 
            async with session.get(url, timeout=10) as response:  
                charset = response.headers.get('Content-Type', '').split('charset=')[-1]
                try:
                    content = await response.text(encoding=charset)
                except UnicodeDecodeError:
                    print(f"Error decoding content from {url} with charset {charset}. Trying default 'utf-8'...")
                    try:
                        content = await response.text()
                    except UnicodeDecodeError:
                        print(f"Decoding with 'utf-8' also failed for {url}. Trying 'iso-8859-1'...")
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
    parsed_date = datetime.now()

    for page_number in range(1,2000):
        url = f'https://patriotesrpske.com/najnovije/page/{page_number}/'
        soup = await get_soup(url)
        try:
            div_container = soup.find_all('div', class_='ps-najcitanije-grid-text')
            links = [a.find('a', href=True)['href'] for a in div_container]
            for link in links:
                    soup_child = await get_soup(link)
                    try:
                        container = soup_child.find('div', class_='ps-najnovije')
                        headline = container.find('h1').text
                    except:
                        headline = np.nan
                    try:
                        parsed_date = datetime.strptime(container.find('p', class_='ps-date').text, "%d/%m/%Y")
                    except:
                        parsed_date = np.nan
                    try:
                        news_text = container.find('h2').text
                    except:
                        news_text = np.nan
                    try:
                        for p in soup_child.find('div', class_='ps-content').find_all('p'):
                            news_text = news_text + p.text
                    except:
                        news_text = np.nan
                    
                    category = link.split("/")[3]

                    temp_df = pd.DataFrame([{
                                'date': parsed_date,
                                'headline': headline,
                                'author_name': np.nan,
                                'cleaned_text': news_text,
                                'link': link,
                                'category': category,
                                'tags': np.nan
                            }])

                    df = pd.concat([df, temp_df], ignore_index=True)
        except:
            continue

        if isinstance(parsed_date, datetime) and parsed_date < datetime(2022, 1, 1):
            break
            
    
    file_path = os.path.join('Parser_rs_media/data', 'patriotesrpske_data.csv')
    df.to_csv(file_path, index=False, sep="|") 

def run():
    asyncio.run(main())