import datetime
import os
import requests
import time
from flask import render_template


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def get_game_data():
    url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

    # query API
    while True:
        try:
            response = requests.get(
                url,
                verify=False
            )
            return response.json()
    
        except (requests.RequestException, ValueError, KeyError, IndexError):
            # Try again every 5 seconds
            print(f'{datetime.datetime.now()} | Not in Game rn')
            time.sleep(5)
            continue

def get_champion_data():
    url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"


    # query API
    response = requests.get(
        url,
        verify=False
    )
    return response.json()

def get_champion_icons(champion):

    if os.path.isfile(f"static/champion_icons/{champion}.png"):
        return


    url = f"http://ddragon.leagueoflegends.com/cdn/13.18.1/img/champion/{champion}.png"
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # save image
            image_name = f"{champion}.png"
            folder_name = "static/champion_icons"
            with open(os.path.join(folder_name, image_name), "wb") as f:
                f.write(response.content)
        else:
            print(f"HTTP GET request failed with status code {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def get_item_icons(item_id):

    if os.path.isfile(f"static/item_icons/{item_id}.png"):
        return

    if item_id == 0:
        return
    url = f"http://ddragon.leagueoflegends.com/cdn/13.18.1/img/item/{item_id}.png"
    response = requests.get(url)
    image_name = f"{item_id}.png"
    folder_name = "static/item_icons"
    with open(os.path.join(folder_name, image_name), "wb") as f:
        f.write(response.content)

def get_rune_icons(rune_id):
    if os.path.isfile(f"static/rune_icons/{rune_id}.png"):
        return
    
    url = f"http://ddragon.leagueoflegends.com/cdn/13.19.1/data/en_US/runesReforged.json"
    response = requests.get(url)
    image_name = f"{rune_id}.png"
    folder_name = "static/rune_icons"
    for path in response.json():
        for slot in path["slots"]:
            for rune in slot["runes"]:
                if rune_id == rune['id']:
                    url = f"https://ddragon.canisback.com/img/{rune['icon']}"
                    rune_page = requests.get(url)
                    with open(os.path.join(folder_name, image_name), "wb") as f:
                        f.write(rune_page.content)

def get_style_icons(rune_id):
    if os.path.isfile(f"static/rune_icons/{rune_id}.png"):
        return
    
    url = f"http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/runesReforged.json"
    response = requests.get(url)
    image_name = f"{rune_id}.png"
    folder_name = "static/rune_icons"
    for rune in response.json():
        if rune_id == rune['id']:
            url = f"https://ddragon.canisback.com/img/{rune['icon']}"
            rune_page = requests.get(url)
            with open(os.path.join(folder_name, image_name), "wb") as f:
                f.write(rune_page.content)

def get_summoner_spell_icons(summoner_spell_id):
    id_to_name = {
        21: "SummonerBarrier",
        1: "SummonerBoost",
        2202: "Summoner CherryFlash",
        2201: "SummonerCherryHold",
        14: "SummonerDot",
        3: "SummonerExhaust",
        4: "SummonerFlash",
        6: "SummonerHaste",
        7: "SummonerHeal",
        13: "SummonerMana",
        30: "SummonerPoroRecall",
        31: "SummonerPoroThrow",
        11: "SummonerSmite",
        39: "SummonerSnowURFSnowball_Mark",
        32: "SummonerSnowball",
        12: "SummonerTeleport",
        54: "Summoner_UltBookPlaceholder",
        55: "Summoner_UltBookSmitePlaceholder",

    }

    spell_name = id_to_name[summoner_spell_id]
    if os.path.isfile(f"static/summoner_spell_icons/{summoner_spell_id}.png"):
        return
    
    url = f"http://ddragon.leagueoflegends.com/cdn/13.19.1/img/spell/{spell_name}.png"
    response = requests.get(url)
    image_name = f"{summoner_spell_id}.png"
    folder_name = "static/summoner_spell_icons"
    with open(os.path.join(folder_name, image_name), "wb") as f:
        f.write(response.content)


def get_match_info_by_id(region, match_id, api_key):
    if region in ['NA']:
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    response = requests.get(url)
    return response.json()

def get_summoner_by_username(region, summoner_id, api_key):
    url = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_id}?api_key={api_key}"
    response = requests.get(url)
    return response.json()

def get_summoner_by_puuid(region, puuid, api_key):
    url = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    response = requests.get(url)
    return response.json()

def get_summoner_history(puuid, region, api_key):
    if region in ['NA']:
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={api_key}"
    response = requests.get(url)
    return response.json()

# api = 'RGAPI-f73a9741-0e50-413e-8c7a-4b366a958c7b'
# sum = get_summoner_by_username("NA", "hapnn", api)
# # print(sum)
# summ = get_summoner_history("hjUDJye2l53lVakM-vzSxUDprckzGKBCE3McPTqhZSGGy0hmAErcAOWNwkUx95D2kGluIEVXlUxKgg", "NA", api)
# # print(summ)
# game = get_match_info_by_id("NA", "NA1_4767732253", api)
# keys = game['info']["participants"][1]["perks"]["styles"][0]
# # print(keys)

# keys = game['info']["participants"][1].keys()
# print(keys)

