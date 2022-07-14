import re
import requests
import fake_useragent
from bs4 import BeautifulSoup
HEADERS = {'user-agent': fake_useragent.UserAgent(verify_ssl=False).random}

def run(url: str) -> str:
    response = requests.get(url=url,headers=HEADERS)
    return response.text

def show_all_links() -> list[str]:
    alphabet = 'А Б В Г Д Е Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Э Ю Я'.split(' ')
    for char in alphabet:
        data = {'title': 'Категория:Города_по_алфавиту',
                'from' : char,
        }
        response = requests.post(' https://ru.wikinews.org/w/index.php?', data=data, headers=HEADERS)
        yield response.text

def parse_cities() -> None:
    all_cities:list[str] = []
    for source in show_all_links():
        soup = BeautifulSoup(source, 'lxml')
        cities = soup.find('div', class_="mw-category-group").\
            find_all('a', title=re.compile(r'\bКатегория:.+'))
        all_cities.extend([re.search(r'[\w-]+(?=\s*.*)', city.text).group() + '\n' for city in cities])
    print(all_cities)
    all_cities.sort()
    with open('cities.txt', 'w', encoding='utf-8') as file:
        file.writelines(all_cities)

def main() -> None:
    parse_cities()

if __name__ == '__main__':
    main()
