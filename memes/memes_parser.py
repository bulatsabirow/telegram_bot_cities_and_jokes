import json
import re
import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
HEADERS: dict = {'fake_useragent': fake_useragent.UserAgent(verify_ssl=False).random}
TEMPLATE_URL: str = 'https://www.anekdot.ru/last/mem_non_video/'

def run(url: str) -> str:
    response: requests.Response = requests.get(url=url,headers=HEADERS)
    return response.text

def main() -> None:
    for i in range(1,2):
        date: str = time.strftime('%Y-%m-%d', time.gmtime(time.time() - 3600 * 24 * i))
        source_code: str = run(TEMPLATE_URL + date + '/')
        soup: BeautifulSoup = BeautifulSoup(source_code, 'lxml')
        memes: list[BeautifulSoup] = soup.find_all('div', class_='topicbox', id=re.compile(r'\d+'))
        captions: dict[str, str] = {}
        for meme in memes:
            meme_src: str = meme.find('img', title=re.compile('.*мем.*', re.IGNORECASE)).get('src')
            print(meme_src)
            regex:re.Pattern = re.compile(r'\d+(?=.(?:jpg|png))')
            print(regex.search(meme_src).group())
            meme_index: str = regex.search(meme_src).group()
            # with open(f"memes_storage/{regex.search(meme_src).group()}.jpg", 'wb') as meme_photo:
            #     meme_photo.write(requests.get(meme_src).content)
            meme_caption: str = meme.find('div', class_='text').get_text()
            if meme.find('div', class_='text').get_text() != "":
                captions[meme_index] = meme_caption
        with open('memes_captions.json', 'w', encoding='utf-8') as json_file:
            json.dump(captions,json_file,ensure_ascii=False,indent=4)

if __name__ == '__main__':
    main()