import requests
from bs4 import BeautifulSoup
import datetime
import os

# Script for determining which games of the day fit Prof MJ (David-MJ) NHL streak system
# System: Bet on team with losing streak >= 1 playing team with winning streak >= 4
# Script writes and/or prints (depending on global variable settings) all games that fit streak
# Will output strings in form of Away_Nickname,Home_Nickname,Home_Line,Bet_Team,Bet_Code
# Where Bet_Code = {0 if no bet (should not be shown), 1 if home team is losing streak, 2 if away team is losing streak}
__author__ = ["rssawyer"]

# Global variables that can be fine-tuned
LOSING_STREAK_MINIMUM = 1
WINNING_STREAK_MINIMUM = 4
WRITING = True
OUTPUT_FILENAME = "NHL-David-MJ-Streak-System.csv"
PRINTING = True
SPORT = 'nhl'


# Quick data structure for storing streak category (determined by minimums of global variables)
class NHL_Team:
    def __init__(self, input_name, streak_category):
        self.name = input_name
        self.category = streak_category


# Determining if a matchup should be bet given teams and their streak category
def system_matchup(Away_team, Home_team):
    if Away_team.category == "Losing" and Home_team.category == "Winning":
        return 2, Away_team.name
    elif Away_team.category == "Winning" and Home_team.category == "Losing":
        return 1, Home_team.name
    else:
        return 0, "No Bet"


# Function for converting teams from ESPN Standings names to ESPN Matchup names (essentially location -> nickname)
def map_name_standings_to_matchup(name):
    try:
        dash_index = name.index('-')
        name = name[dash_index+2:]
    except ValueError:
        pass
    NHL_dictionary = {"Montreal":"Canadiens",
                      "Toronto":"Maple Leafs",
                      "Ottawa":"Senators",
                      "Boston":"Bruins",
                      "Tampa Bay":"Lightning",
                      "Florida":"Panthers",
                      "Buffalo":"Sabres",
                      "Detroit":"Red Wings",
                      "Washington":"Capitals",
                      "Pittsburgh":"Penguins",
                      "Columbus":"Blue Jackets",
                      "NY Rangers":"Rangers",
                      "NY Islanders":"Islanders",
                      "Carolina":"Hurricanes",
                      "Philadelphia":"Flyers",
                      "New Jersey":"Devils",
                      "Chicago":"Blackhawks",
                      "Minnesota":"Wild",
                      "St. Louis":"Blues",
                      "Nashville":"Predators",
                      "Winnipeg":"Jets",
                      "Dallas":"Stars",
                      "Colorado":"Avalanche",
                      "Anaheim":"Ducks",
                      "Edmonton":"Oilers",
                      "San Jose":"Sharks",
                      "Calgary":"Flames",
                      "Los Angeles":"Kings",
                      "Vancouver":"Canucks",
                      "Arizona":"Coyotes"}
    try:
        mapped_name = NHL_dictionary[name]
    except KeyError:
        mapped_name = "Not Found"
    return mapped_name


# Using global streak minimums to determine team's streak category from ESPN Standings table (e.g. Won 5)
def convert_word_category(cell_text):
    if cell_text[0] == "L" and int(cell_text.split(" ")[1] >= LOSING_STREAK_MINIMUM):
        category = "Losing"
    elif cell_text[0] == "W" and int(cell_text.split(" ")[1]) >= WINNING_STREAK_MINIMUM:
        category = "Winning"
    else:
        category = "None"
    return category


# Returns dictionary of (Name, Team_object) for use in determining actionable matchups from ESPN Standings
def get_team_streak_data(sport="nhl"):
    return_dict = dict()
    url = "http://www.espn.com/%s/standings" % sport
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                 " Chrome/47.0.2526.111 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/webp,*/*;q=0.8"}
    req = session.get(url, headers=headers)
    bsObj = BeautifulSoup(req.text, "html.parser")

    standings = bsObj.find(name="table", class_="tablehead")
    rows = standings.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        team_name = map_name_standings_to_matchup(cols[0])
        if team_name != "Not Found":
            return_dict[team_name] = NHL_Team(team_name, convert_word_category(cols[15]))

    return return_dict


def convert_game_to_string(html_game, team_data):
    try:
        links = html_game.find_all(name='a')
        away_team = links[0].text.strip()
        home_team = links[1].text.strip()
        line = html_game.find(name="div", class_="expand-gameLinks").text.strip().split(" ")[-1]
        try:
            int(line)
        except ValueError:
            line = "None"
        bet_indicator, bet_team = system_matchup(team_data[away_team], team_data[home_team])
        return "%s,%s,%s,%s,%s" % (away_team, home_team, line, bet_team, bet_indicator)
    except AttributeError:
        return "N,N,N,N,0"
    except IndexError:
        return "N,N,N,N,0"


# Uses predetermined betting code (0 = None, 1 = Home is losing streak, 2 = Away is losing streak)
def actionable(game_string):
    split = game_string.split(",")
    if int(split[-1]) > 0:
        return True


# Gets today's matchups (and lines) from ESPN and returns actionable games
# Returns list of actionable games in format Away_Name,Home_Name,Line,Bet_Team,Bet_Amount
# Line is relative to home, if available on ESPN Matchup page
def get_matchup_data(team_data, sport="nhl"):
    url = "http://www.espn.com/%s/scoreboard" % sport
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                 " Chrome/47.0.2526.111 Safari/537.36",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/webp,*/*;q=0.8"}
    req = session.get(url, headers=headers)
    bsObj = BeautifulSoup(req.text, "html.parser")

    games = bsObj.find_all(name="div", class_="mod-content")
    actionable_games = []
    for game in games:
        game_string = convert_game_to_string(game, team_data)
        if actionable(game_string):
            actionable_games.append(game_string)

    return actionable_games


if __name__ == "__main__":
    team_info = get_team_streak_data(sport=SPORT)
    if len(team_info.keys()) != 30:
        print "Number of teams incorrect"
    bet_games = get_matchup_data(team_info, sport=SPORT)

    if WRITING:
        if not os.path.exists(OUTPUT_FILENAME):
            write_file = open(OUTPUT_FILENAME, mode='a')
            header = "Date,Sport,AwayNickname,HomeNickname,HomeLine,BetTeam,BetCode\n"
            write_file.write(header)
        else:
            write_file = open(OUTPUT_FILENAME, mode='a')
        date = datetime.date.today()
        for game in bet_games:
            write_file.write(str(date)+","+SPORT+","+game+"\n")
        write_file.close()

    if PRINTING:
        if len(bet_games) < 1:
            print "No Games Actionable"
        else:
            for game in bet_games:
                print "Bet Game: %s" % game
