import requests
import os
import time
import json
import sys
import argparse
import pathlib

from bs4 import BeautifulSoup
from selenium import webdriver
from dotenv import load_dotenv

import clear_data
import json_read_write
# Futuramente
# import concurrent.futures


BASE_URL = "https://myanimelist.net"

parser = argparse.ArgumentParser(description='Crawler MyAnimeList')
parser.add_argument('-n', '--name', required=False)
args = parser.parse_args()

load_dotenv()

DRIVER_PATH = os.getenv('DRIVER_PATH')
USERNAME = args.name

pathlib.Path('output').mkdir(exist_ok=True)
pathlib.Path('output/anime').mkdir(exist_ok=True)
pathlib.Path('output/user').mkdir(exist_ok=True)

# USERNAME = "khalil04uzumaki"
# USERNAME = "Abajur"
# USERNAME = "MarcosInja"

# Get the user's main page,
# the friends page and the anime page
def url_format(url_part_name, opc):
    """Set the URL type
    0 - user
    1 - frind
    2 - anime
    3 - anime info
    """
    url_format = ''
    if opc == 0:
        url_format = f'{BASE_URL}/profile/{url_part_name}'
    elif opc == 1:
        url_format = f'{BASE_URL}/profile/{url_part_name}/friends'
    elif opc == 2:
        url_format = f'{BASE_URL}/animelist/{url_part_name}?status=7'
    else:
        url_format = f'{BASE_URL}/{url_part_name}'
    return url_format


# Get a page to be scraped
def get_page_user_friend_anime(url_format):
    page_source = requests.get(url_format)
    soup = BeautifulSoup(page_source.text, 'html.parser')
    
    return soup


# Configure selenium
def setup_driver():
    # Seting the directorys to be used by selenium
    current_directory = os.getcwd()
    path_chrome = DRIVER_PATH

    # Attributing the paths to the webdriver
    chrome_options = webdriver.ChromeOptions()

    # chrome_options.add_argument('--headless') # Modo invisivel
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')

    return webdriver.Chrome(executable_path = path_chrome, chrome_options = chrome_options)


# Get the user information
def user_info(soup):
    user_status = soup.find(class_ = 'user-status').find_all("li")
    info = []
    for i in user_status:
        tag = i.find_all(text=True)
        info.append(tag)
        
    return info


# Get the user's friends
def user_friends(soup):
    info = []
    try:
        user_status = soup.find(class_ = 'friend').find_all(class_ = 'boxlist')
        for i in user_status:
            tag = i.find(class_ = 'title').find('a')
            name = tag.text
            info.append(name)
    except:
        pass
    return info


# Get the names and links of each anime
def user_anime(url):
    data = []
    browser = setup_driver()

    browser.get(url)
    time.sleep(1)

    SCROLL_PAUSE_TIME = 4
    # Get the scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # scroll down
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    anime = soup.find(class_ = 'list-block').find_all(class_ = 'list-item')
    for i in anime:
        tag = i.find(class_ = 'title').find('a')
        url = tag.get("href")
        name = tag.text
        data.append([name, url])

    return data


# Get the raw data from the anime, clean it and save it in a json
def anime_data(animes):
    data = {}
    file_names = []
    if animes:
        for anime in animes:
            data[anime[0]] = []
            soup = get_page_user_friend_anime(url_format(anime[1], 3))
            dado = soup.find(class_ = 'borderClass').find_all(class_ = 'spaceit_pad')

            for i in dado:
                tag = i.find_all(text=True)
                data[anime[0]].append(tag)

            file_names.append(f"output/anime/{anime[0].replace('/', ' ')}.json")

            json_read_write.write_json(f"output/anime/{anime[0].replace('/', ' ')}.json", data[anime[0]])
    
    # Clear the data
    clear_data.saned_anime_data(file_names)
    return file_names


# Get the information of the user's friends
def friends_data(friends):
    if friends:
        for f in friends:
            soup = get_page_user_friend_anime(url_format(f, 0))
            infos_user = user_info(soup)

            soup = get_page_user_friend_anime(url_format(f, 1))
            friends = user_friends(soup)

            anime = user_anime(url_format(f, 2))
            file_names = anime_data(anime)

            file = clear_data.user_info(infos_user, f, anime, friends)


def main(user):
    # User info
    soup = get_page_user_friend_anime(url_format(user, 0))
    infos_user = user_info(soup)

    # User friends
    soup = get_page_user_friend_anime(url_format(user, 1))
    friends = user_friends(soup)

    # Get the anime information
    anime = user_anime(url_format(user, 2))
    file_names = anime_data(anime)

    file = clear_data.user_info(infos_user, user, anime, friends)

    # foff == friends of friends
    foff = friends_data(friends) 


main(USERNAME)
