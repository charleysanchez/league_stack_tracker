from cs50 import SQL
from flask import Flask, redirect, render_template, request
from helpers import (apology, get_game_data, get_champion_data, get_champion_icons, get_item_icons,
                      get_rune_icons, get_style_icons, get_summoner_by_puuid, get_summoner_by_username, 
                      get_summoner_history, get_summoner_spell_icons, get_match_info_by_id)
import locale
import os
import urllib3

urllib3.disable_warnings()
app = Flask(__name__)

game_data = SQL("sqlite:///game_data.db")

game_data.execute(
    "DELETE FROM champions"
)

api_key = "RGAPI-f73a9741-0e50-413e-8c7a-4b366a958c7b"

# Set the locale to the user's default locale
locale.setlocale(locale.LC_ALL, '')

# active_player = get_game_data()["activePlayer"]
# all_players = get_game_data()["allPlayers"]
# champion_data = get_champion_data()

# for player in all_players:
#     game_data.execute(
#         "INSERT INTO champions (summoner_name, champion_name, level, kills, deaths, assists, creepscore) VALUES (?, ?, ?, ?, ?, ?, ?);",
#         player["summonerName"],
#         player["championName"],
#         player["level"],
#         player["scores"]["kills"],
#         player["scores"]["deaths"],
#         player["scores"]["assists"],
#         player["scores"]["creepScore"],
#         )
    

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/champions", methods=["GET", "POST"])
def champions():
    summoners = game_data.execute(
        "SELECT summoner_name FROM champions;"
    )
    champions = game_data.execute(
        "SELECT champion_name, level, kills, deaths, assists, creepscore FROM champions"
    )

    for champion in champions:
        champion_name = champion["champion_name"].replace(' ', '')
        if champion_name == "Cho'Gath":
            champion_name = "Chogath"

        get_champion_icons(champion_name)
        champion["champ_img"] = champion_name
    names = zip(summoners, champions)
    folder = "static/champion_icons"
    images_len = len([f for f in os.listdir(folder) if f.endswith('.png')])

    return render_template("champions.html", names=names, images_len=images_len)

@app.route("/summoner", methods=["GET", "POST"])
def summoner():
    if request.method == "POST":

        # reset database
        game_data.execute("DELETE FROM matches;")

        # get simple data like region, summoner_id (Username)
        region = request.form.get("region")
        summoner_id = request.form.get("summoner_id")

        # request more data on the summoner (puuid, and more)
        summoner_info = get_summoner_by_username(region, summoner_id, api_key)

        # check if there is an error code going on
        if 'status' in summoner_info.keys():
            status_code = summoner_info["status"]["status_code"]
            if status_code == 403:
                return apology("API key expired!", 403)
            elif status_code == 404:
                 return apology("Summoner not found!", 404)
        

        # assign puuid variable to make things easier
        puuid = summoner_info["puuid"]

        # pull the match history by game id using API
        match_history_by_id = get_summoner_history(puuid, region, api_key)

        # create empty list for match_history with all data to go in
        match_history = []
        match_history_id = []

        # add the most recent match to this list
        for match in match_history_by_id:
            match_history.append(get_match_info_by_id(region, match, api_key))

        # go through each match in match_history list
        for match_id in match_history:
            match = match_id["metadata"]["matchId"]
            match_history_id.append(match)
            game_mode = match_id["info"]["gameMode"]

            # grab each participant
            for participant in match_id["info"]["participants"]:
                
                # get their summoner name
                summoner_name  = participant["summonerName"]

                # get their champion played
                champion_played = participant["championName"]

                # get their score
                level = participant["champLevel"]
                kills = participant["kills"]
                assists = participant["assists"]
                deaths = participant["deaths"]
                creepscore = participant["totalMinionsKilled"]
                puuid = "poop"
                team_id = participant["teamId"]

                # get item information
                items = {}
                for i in range(7):
                    items[f"item{i}"] = participant[f"item{i}"]
                    get_item_icons(items[f"item{i}"])

                # get runes (riot calls them perks)
                primaries = participant["perks"]["styles"][0]
                primary_perks = {}
                for i in range(4):
                    primary_perks[f"primary{i+1}"] = primaries["selections"][i]['perk']
                    get_rune_icons(primary_perks[f"primary{i+1}"])

                secondaries = participant["perks"]["styles"][1]
                secondary_perks = {}
                for i in range(2):
                     secondary_perks[f"secondary{i+1}"] = secondaries["selections"][i]['perk']

                style1 = primaries["style"]
                style2 = secondaries["style"]
                get_style_icons(style2)


                # get summoner spells
                summoner1 = participant["summoner1Id"]
                summoner2 = participant["summoner2Id"]
                get_summoner_spell_icons(summoner1)
                get_summoner_spell_icons(summoner2)

                # get match outcome for each participant
                outcome = participant["win"]


                # get match time
                time_played = participant["timePlayed"]
                cs_per_m = '{:.1f}'.format(creepscore / time_played * 60)

                # damage stats
                # damage_to_champs = locale.format_string('%d', participant["totalDamageDealtToChampions"], grouping=True)
                # damage_taken = locale.format_string('%d', participant["totalDamageTaken"], grouping=True)
                damage_to_champs = participant["totalDamageDealtToChampions"]
                damage_taken = participant["totalDamageTaken"]
                
                # vision
                wards_placed = participant["wardsPlaced"]
                wards_killed = participant["wardsKilled"]
                control_wards = participant["visionWardsBoughtInGame"]


                # add to the database with match id as well
                game_data.execute(
                    "INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    summoner_name,
                    champion_played,
                    level,
                    kills,
                    deaths,
                    assists,
                    creepscore,
                    puuid,
                    match,
                    team_id,
                    game_mode,
                    items["item0"],
                    items["item1"],
                    items["item2"],
                    items["item3"],
                    items["item4"],
                    items["item5"],
                    items["item6"],
                    primary_perks["primary1"],
                    primary_perks["primary2"],
                    primary_perks["primary3"],
                    primary_perks["primary4"],
                    secondary_perks["secondary1"],
                    secondary_perks["secondary2"],
                    summoner1,
                    summoner2,
                    outcome,
                    time_played,
                    style2,
                    damage_to_champs,
                    damage_taken,
                    cs_per_m,
                    wards_placed,
                    wards_killed,
                    control_wards,
                )

                

        players=[]  
        for match in match_history:
            players.extend(game_data.execute("SELECT * FROM matches where match_id=?;", match["metadata"]["matchId"]))

            # Assuming players is a list of dictionaries
            max_dmg_dealt = max(player["damage_to_champs"] for player in players)
            max_dmg_taken = max(player["damage_taken"] for player in players)
            

            for player in players:
                        champion_name = player["champion_name"].replace(' ', '')
                        if champion_name == "Cho'Gath":
                            champion_name = "Chogath"

                        get_champion_icons(champion_name)
                        player["champ_img"] = champion_name
                        if player["deaths"] > 0:
                            player["ratio"] = '{:.2f}'.format(float((player["kills"] + player["assists"]) / player["deaths"]))
                        else:
                            player["ratio"] = 'Perfect'
                        player["formatted_time"] = f"{player['time_played'] // 60}m {player['time_played'] % 60}s"
                        player["damage_dealt_share"] = player["damage_to_champs"] / max_dmg_dealt * 100
                        # player["damage_dealt_share"] = int(player["damage_to_champs"].replace(',', '')) / max_dmg_dealt * 100
                        # player["damage_taken_share"] = int(player["damage_taken"].replace(',', '')) / max_dmg_taken * 100
                        player["damage_taken_share"] = player["damage_taken"] / max_dmg_taken * 100

                    
                    
        return render_template("summoner.html", summoner_id=summoner_id, players=players, unique_matches=match_history_id)

    return render_template("summoner.html")