import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
HEADERS: dict = {'user-agent': fake_useragent.UserAgent(verify_ssl=False).random}

def init(url:str) -> str:
    response:requests.Response = requests.get(url, headers=HEADERS)
    return response.text

def prettify_current_time(timer: time.struct_time) -> str:
    return time.strftime('%Y-%m-%d',timer) + '/'

def parse_jokes(attempts: int):
    template: str = 'https://www.anekdot.ru/release/anekdot/day/'
    index:int = 0
    cur_time: float = time.time()
    with open('jokes.txt', 'w', encoding='utf-8') as file:
        while index != attempts:
            source = init(template + prettify_current_time(time.gmtime(cur_time)))
            soup = BeautifulSoup(source, 'lxml')
            for joke in soup.find_all('div', class_='text')[:-1]:
                file.write(joke.text + '\n' + '-' * 10 + '\n')
            index += 1
            cur_time -= 3600 * 24

def main() -> None:
    parse_jokes(365)

if __name__ == '__main__':
    main()





