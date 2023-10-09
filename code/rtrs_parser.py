import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from datetime import datetime
import os


def main():

    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    date = datetime.now()
    url ='https://www.rtrs.tv/index.php'
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')
    div_container = soup.find('div', class_='container main-width-fix z_fix')
    link = div_container.find('a', href=True)
    page_number = int(link['href'][link['href'].find("id=")+3:])
    while date >= datetime(2023, 10, 4):
        url_p = f'https://www.rtrs.tv/vijesti/vijest.php?id={page_number}'
        response_p = requests.get(url_p)
        soup_p = bs(response_p.content, 'html.parser')
        div_container_p = soup_p.find('div', class_='col-md-8 col-sm-8')
        headline = div_container_p.find('h1').text if div_container_p.find('h1') else np.nan
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
        if page_number % 100 == 0:
            print(page_number)

    file_path = os.path.join('Parser_rs_media/data', 'rtrs_data.csv')
    df.to_csv(file_path, index=False, sep="|") 

if __name__ == "__main__":
    main()