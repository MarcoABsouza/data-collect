import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
"""
        Curl to Python
"""
headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.residentevildatabase.com/personagens/',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

def get_content(url):
    response = requests.get(url, headers=headers)
    return response


def get_basic_infos(soup):
    
    # From an HTML element <div> and whose class is td-page-content. Gets all the HTML content of that div
    div_page = soup.find('div', class_= 'td-page-content')

    # Take the desired section paragraph
    paragraph = div_page.find_all('p')[1]

    # take the desired section ems
    ems = paragraph.find_all('em')

    # Segment the desired data
    data = dict()
    for i in ems:
        key, value, *_ = i.text.split(":")
        key = key.strip(' ')
        data[key] = value.strip(' ')
    
    return data


def get_appearances_info(soup):
    # From an HTML element <div> and whose class is td-page-content. Gets all the HTML content of that div
    lis = (soup.find('div', class_= 'td-page-content')
                .find('h4')
                .find_next()
                .find_all('li'))

    appearances = [i.text for i in lis]
    return appearances


def get_character_info(url):    
    response = get_content(url)

    if response.status_code != 200:
        print('Não foi possivel obter os dados')
        return {}
    else:
        # Converting the raw text of the page into a structured object that allows navigation between elements
        soup = BeautifulSoup(response.text)
        data = get_basic_infos(soup)
        data['Appearances'] = get_appearances_info(soup)
        return data
    

def get_links():    
    url = 'https://www.residentevildatabase.com/personagens/'
    resp = requests.get(url, headers=headers)
    soup_characters = BeautifulSoup(resp.text)
    anchors = (
                soup_characters.find('div', class_='td-page-content')
                .find_all('a')
            )
    links = [i['href'] for i in anchors]
    return links


links = get_links()
data = []
for i in tqdm(links):
    d = get_character_info(i)
    d['link'] = i
    nome = i.strip('/').split('/')[-1].replace('-', ' ').title()
    d['Nome'] = nome
    data.append(d)
    
df = pd.DataFrame(data)
df.to_parquet('dados_re.parquet', index=False)
df_new = pd.read_parquet('dados_re.parquet')