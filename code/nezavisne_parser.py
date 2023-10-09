import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from datetime import datetime
import os


def main():
    categories = ["bih", "gradovi", "drustvo", "obrazovanje", "ex-yu", "svijet", "hronika", "banjaluka", "intervju", "kolumne", "nezavisnistav"]

    # Initialize an empty dataframe
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    for category_item in categories:
        for page_number in tqdm(range(1,1000)):
            url = f'https://www.nezavisne.com/novosti/{category_item}?strana={page_number}&ipp=15&'
            response = requests.get(url)

            # Parse the content using BeautifulSoup
            soup = bs(response.content, 'html.parser')
            div_container = soup.find('div', class_='col-12 col-sm-12 col-md-12 col-lg-8')

            # If the div is found, extract the links within it
            if div_container:
                links = [a['href'] for a in div_container.find_all('a', href=True)[:-7]]
                for i, link in enumerate(links):
                    if i % 2 == 0:  # Чётный индекс
                        link_to_article = "https:"+link
                        response_child = requests.get(link_to_article)
                        soup_child = bs(response_child.content, 'html.parser')

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

            if date < datetime(2022, 1, 1):
                            break

# Save to temporary file after each category is processed
        temp_file_name = f"temp_data_{category_item}.csv"
        df.to_csv(temp_file_name, sep="|")

    # Finally, save all data to the main file
    file_path = os.path.join('Parser_rs_media/data', "nezavisne_data.csv")
    df.to_csv(file_path, index=False, sep="|")

if __name__ == "__main__":
    main()