from typing import Generator, Any
import sqlite3

def database_template_function(string: str, *args) -> sqlite3.Cursor:
    with sqlite3.connect('cities/cities.sqlite3') as con:
        cur = con.cursor()
        sql_request_result = cur.execute(string, *args)
        con.commit()
    return sql_request_result

def database_init() -> None:
    string = """
        CREATE TABLE IF NOT EXISTS cities(
        CITY TEXT,
        IS_CALLED BOOL DEFAULT 0
        )
        """
    database_template_function(string)

def open_file(file_name: str) -> Generator:
    with open(file_name, 'r', encoding='utf-8') as file:
        yield from file

def set_is_called_to_one(city: str) -> None:
    string = f"""
    UPDATE cities SET is_called = 1 WHERE
    city = '{city}'
    """
    database_template_function(string)

def choose_random_city(city: str) -> str:
    last_char = city[-1]
    if city[-1] in 'ъьы':
        last_char = city[-2]
    string = f"""
    SELECT city FROM cities WHERE city LIKE '{last_char.capitalize()}%'
    AND IS_CALLED = 0 ORDER BY RANDOM() LIMIT 1
    """
    return database_template_function(string).fetchone()[0]

def does_city_exist(city: str) -> bool:
    string = f"""SELECT city FROM cities WHERE city = '{city}'"""
    return database_template_function(string).fetchone() is not None

def have_not_city_been_chosen(city: str) -> bool:
    string = f"""SELECT city FROM cities WHERE city = '{city}' AND IS_CALLED = 0"""
    return database_template_function(string).fetchone() is not None

def insert_values(value: Any) -> None:
    string = """
    INSERT INTO cities(city) VALUES (?)
    """
    database_template_function(string, (value,))

def reload_database() -> None:
    string = """UPDATE cities
    SET is_called = 0
    """
    database_template_function(string)

if __name__ == '__main__':
    print(does_city_exist('v'))
    reload_database()
