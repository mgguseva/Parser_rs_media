import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from datetime import datetime
import os


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


def main():
    categories_links = ["gazeta/politika/", "gazeta/socijum/", "gazeta/svijet/",  "gazeta/ekonomija/", "gazeta/sport/", "magazin/kultura/", "magazin/tema-nedelje/", "magazin/nauka/", "magazin/scena/", "magazin/analize/"]

    # Initialize an empty dataframe
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    "https://www.frontal.rs/k/gazeta/politika/page/2/"

    for item in categories_links:
        for page_number in tqdm(range(1,500)):
            url = f'https://www.frontal.rs/k/{item}page/{page_number}/'
            response = requests.get(url)
            soup = bs(response.content, 'html.parser')
            div_container = soup.find('div', class_='col-md-8 mt-3')
            links = [a['href'] for a in div_container.find_all('a', href=True)][:-1]
            for link in links:
                response_child = requests.get(link)
                soup_child = bs(response_child.content, 'html.parser')
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
                
                temp_df = pd.DataFrame([{
                            'date': parced_date,
                            'headline': headline,
                            'author_name': np.nan,
                            'cleaned_text': news_text,
                            'link': link,
                            'category': category,
                            'tags': tags
                        }])

                df = pd.concat([df, temp_df], ignore_index=True)
                
            if parced_date < datetime(2023, 9, 28):
                break

    # Save to temporary file after each category is processed
        temp_file_name = f"temp_data_{item}.csv"
        df.to_csv(temp_file_name, sep="|")

    # Finally, save all data to the main file
    file_path = os.path.join('Parser_rs_media/data', "frontal_data.csv")
    df.to_csv(file_path, index=False, sep="|")

if __name__ == "__main__":
    main()