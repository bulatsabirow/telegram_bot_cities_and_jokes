"""telegram-bot for training project"""
import sys
import logging
import json
import os
import random
import re
from typing import Optional
from cities.db_functions import *
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Updater, CommandHandler, \
    CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
with open('id/id.txt', 'r', encoding='utf-8') as file:
    TOKEN = file.read().replace('\n', '')
LAST_CITY: Optional[str] = None

def start_messaging(update: Update, context: CallbackContext) -> None:
    """first method called during bot is working"""
    username = update.effective_user.username
    update.message.reply_text(f'Привет, {username}!')
    suggest_games(update, context)

def template_method(update: Update, context: CallbackContext) -> None:
    buttons_text: tuple[str, str, str] = ('Рассказать анекдот', 'Показать мем', 'Поиграть в города')
    buttons_callback_data: tuple[str, str, str] = ('jokes', 'memes', 'cities')
    inline_buttons: list[list[Optional[InlineKeyboardButton]]] = [[None], [None], [None]]
    for index, text, callback_data in zip((0, 1, 2), buttons_text, buttons_callback_data):
        inline_buttons[index][0] = InlineKeyboardButton(text=text, callback_data=callback_data)
    inline_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_buttons,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True)
    update.message.reply_text('Бот полностью к вашим услугам:', reply_markup=inline_markup)

def suggest_games(update: [Update,Optional[CallbackQuery]], context: CallbackContext):
    """method gives the user a choice of which bot functionality they prefer"""
    template_method(update, context)

def suggest_games_after_cities(update: [Update,Optional[CallbackQuery]], context: CallbackContext):
    reload_database()
    template_method(update, context)
    return ConversationHandler.END

def send_random_meme(update:[Update, Optional[CallbackQuery]], context: CallbackContext) -> None:
    path_to_directory: str = '/Users/bulat/PycharmProjects/' \
                             'telegram_bot_cities_and_jokes/memes/memes_storage'
    chosen_meme_index: str = random.choice(os.listdir(path_to_directory))
    with open('memes/memes_captions.json', 'r', encoding='utf-8') as json_source:
        meme_captions: dict = json.load(json_source)
    key: str = re.search(r'\d+', chosen_meme_index).group()
    caption = ""
    if key in meme_captions:
        caption = meme_captions[key]
    with open(f'memes/memes_storage/{chosen_meme_index}', 'rb') as meme:
        update.message.reply_photo(meme,caption=caption)

def send_random_joke(update: [Update, Optional[CallbackQuery]], context: CallbackContext) -> None:
    with open('jokes/jokes.txt', 'r', encoding='utf-8') as jokes_file:
        jokes_list: list[str] = jokes_file.read().replace('\n', '').split('-' * 10)
    update.message.reply_text(random.choice(jokes_list))

def start_playing(update: [Update, Optional[CallbackQuery]], context: CallbackContext):
    global LAST_CITY
    alphabet: str = 'йцукенгшщзхфвапролджэёячсмитбю'
    random_city: str = choose_random_city(random.choice(alphabet))
    update.message.reply_text(random_city)
    set_is_called_to_one(random_city)
    LAST_CITY = random_city
    logger.info(random_city)
    return 'bot_turn'

def bot_turn(update: [Update, Optional[CallbackQuery]], context: CallbackContext):
    global LAST_CITY
    user_city: str = update.message.text
    if user_city == '/stop':
        return user_city
    if not does_city_exist(user_city):
        response_text: str = 'Такого города не существует!'
    elif not have_not_city_been_chosen(user_city):
        response_text: str = 'Город уже был назван!'
    elif (LAST_CITY[-2] if LAST_CITY[-1] in ('ъ','ы','ь') else LAST_CITY[-1]) != user_city[0].lower():
        response_text: str = 'Первая буква текущего названного города' \
                             ' должна совпадать с последней буквой предыдущего!'
    else:
        set_is_called_to_one(user_city)
        response_text: str = choose_random_city(user_city)
        LAST_CITY = response_text
        set_is_called_to_one(response_text)
    update.message.reply_text(response_text)
    logger.info(user_city+' '+response_text)
    return 'bot_turn'

def handle_some_scenarios(update: Update, context: CallbackContext) -> Optional[str]:
    """methods handle all user choices"""
    callback = update.callback_query
    callback_data: Optional[str] = update.callback_query.data
    callback.answer()
    callback.delete_message()
    if callback_data == 'cities':
        return start_playing(callback, context)
    if callback_data == 'jokes':
        send_random_joke(callback, context)
    else:
        send_random_meme(callback, context)
    suggest_games(callback, context)
    return ConversationHandler.END

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(message)s'))
    logger.addHandler(handler)
    bot = Updater(TOKEN)
    dispatcher = bot.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_messaging))
    conv_handler: ConversationHandler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_some_scenarios)],
        states={'bot_turn': [MessageHandler(Filters.text & (~Filters.command), bot_turn)]},
        fallbacks=[CommandHandler('stop', suggest_games_after_cities)]
    )
    dispatcher.add_handler(conv_handler)
    bot.start_polling()
    bot.idle()
