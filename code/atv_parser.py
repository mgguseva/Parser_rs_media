import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from datetime import datetime
import os

def main():
    categories_links = ["republika-srpska", "vijesti/drustvo", "vijesti/region",  "vijesti/svijet", "vijesti/ekonomija","vijesti/bih", "vijesti/banja-luka", "vijesti/srbija", "vijesti/gradovi-i-opstine"]


    # Initialize an empty dataframe
    df = pd.DataFrame(columns=['date', 'headline', 'author_name', 'cleaned_text', 'link', 'category', 'tags'])

    for item in categories_links:
        for page_number in tqdm(range(1,500)):
            url = f'https://www.atvbl.rs/{item}?page={page_number}'
            response = requests.get(url)
            soup = bs(response.content, 'html')
            div_container = soup.find('div', class_='row -mx-2 articles-list-container') 
            links = [a['href'] for a in div_container.find_all('a', href=True)]
            for link in links:
                response_child = requests.get(link)
                soup_child = bs(response_child.content, 'lxml')
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

                temp_df = pd.DataFrame([{
                            'date': parsed_date,
                            'headline': headline,
                            'author_name': author,
                            'cleaned_text': news_text,
                            'link': link,
                            'category': item,
                            'tags': tags
                        }])

                df = pd.concat([df, temp_df], ignore_index=True)

            if parsed_date < datetime(2023, 10, 4):
                break
    # Save to temporary file after each category is processed
        temp_file_name = f"temp_data_{item}.csv"
        df.to_csv(temp_file_name, sep="|")

    # Finally, save all data to the main file
    file_path = os.path.join('Parser_rs_media/data', "atv_data.csv")
    df.to_csv(file_path, index=False, sep="|")

if __name__ == "__main__":
    main()