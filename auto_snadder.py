import copy
import time

import datetime

from bs4 import BeautifulSoup
import ast

import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


min_path = [100, 0]


def play_snadder(pattern_sequence):
    url = "https://snadder.io"

    driver = webdriver.Safari()
    driver.get(url)

    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()

    for key in pattern_sequence:
        actions.send_keys(str(key)).perform()
        time.sleep(2)

    time.sleep(5)


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)

    return text


def get_metrics():
    url = "https://snadder.io"

    today_date = datetime.date.today()
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    sources = soup.find_all("script", {"src": True})
    url += sources[2]["src"][1:]

    tomorrow_date = today_date + datetime.timedelta(days=1)

    driver = webdriver.Safari()
    driver.get(url)
    time.sleep(3)

    todays_date_index = driver.page_source.find(f'"{today_date}"')
    tommorow_date_index = driver.page_source.find(f'"{tomorrow_date}"')

    todays_result = driver.page_source[todays_date_index:tommorow_date_index]
    todays_result = "{" + todays_result + "}"

    dict_mapper = {
        "ladders": '"ladders"',
        "snakes": '"snakes"',
        "optimumMove": '"optimumMove"',
        "difficulty": '"difficulty"',
        "dices": '"dices"',
        "id": '"id"',
    }

    todays_metrics = replace_all(todays_result, dict_mapper)
    todays_metrics = ast.literal_eval(todays_metrics)

    return todays_metrics[str(today_date)]


def main():
    snadders_metrics = get_metrics()

    dices = snadders_metrics["dices"]
    ladder = snadders_metrics["ladders"]
    snakes = snadders_metrics["snakes"]

    dice = {}
    for count, value in enumerate(dices, start=1):
        if value == 0:
            continue
        dice[count] = value

    # print("Dices "dices)

    step = 0
    tracked_route = []

    start_time = time.time()
    for key in dice:
        update(step, dice, ladder, snakes, key, tracked_route)

    end_time = time.time()

    print(f"No of dice used: {min_path[0]}")
    print(f"Dice Sequence: {min_path[1]}")
    print(f"Time Taken: {end_time-start_time}")

    play_snadder(min_path[1])


def update(step, dice, ladder, snakes, dice_no, tracked_route):
    dice = copy.copy(dice)
    ladder = copy.copy(ladder)
    snakes = copy.copy(snakes)
    tracked_route = copy.copy(tracked_route)

    tracked_route.append(dice_no)
    step += dice_no
    dice[dice_no] -= 1

    if len(tracked_route) >= min_path[0]:
        return

    if step in ladder.keys():
        temp = step
        step = ladder[step]
        del ladder[temp]

    elif step in snakes.keys():
        temp = step
        step = snakes[step]
        del snakes[temp]

    if dice[dice_no] == 0:
        del dice[dice_no]

    if step == 100:
        if len(tracked_route) < min_path[0]:
            min_path[0] = len(tracked_route)
            min_path[1] = tracked_route
        print(f"Route {min_path[1]}")
        return
    elif dice == {}:
        return

    for key in dice:
        update(step, dice, ladder, snakes, key, tracked_route)


if __name__ == "__main__":
    main()
