"""
I wrote a quick API to interact with basketball-reference.com
Not all are used for this project, I decided to toss some, but kept the methods here anyway.
"""

import requests
from bs4 import BeautifulSoup

def get_player_ids_for_season(season):
  page = requests.get('https://www.basketball-reference.com/leagues/NBA_' + str(season) + '_totals.html')
  soup = BeautifulSoup(page.text, 'html.parser')
  table = soup.find("table", { "id": "totals_stats" })
  body = table.find("tbody")
  rows = body.find_all("tr", class_=lambda x: x != 'thead')

  player_id_set = set()
  for player in rows:
    player_id = player.find("td", {"class":"left"})['data-append-csv']
    player_id_set.add(player_id)
  
  return player_id_set

def get_stats_by_id_and_season(player_id, season):
  url = 'https://www.basketball-reference.com/players/' + player_id[0] + '/' + player_id + '/splits/' + str(season)
  print(url)
  page = requests.get(url)
  
  soup = BeautifulSoup(page.text, 'html.parser')
  table = soup.find("table", {"id": "splits"})
  parent = table.find("th", text="All-Star").parent
  
  # Check if it's really pre all-star
  stats = parent.find_all("td")
  stats_dict = {}
  for s in stats:
    if s.get("data-stat") == "split_value" and s.text != "Pre":
      print("Yo this row is not pre:", stats)
      return -1
    else:
      if s.text != "Pre":
        stats_dict[s.get("data-stat")] = s.text
  return stats_dict

def get_list_of_all_stars(season):

  if season == 2020:
    return []

  url = "https://www.basketball-reference.com/allstar/NBA_" + str(season) + ".html"
  print(url)
  if season == 1999:
    print("There was no ASG in 1999")
    return None

  page = requests.get(url)
  soup = BeautifulSoup(page.text, 'html.parser')
  
  divs = soup.find_all("div", {"class": "overthrow table_container"})
  east = divs[1].find("tbody")
  west = divs[2].find("tbody")

  east_all_stars = [th.get('data-append-csv') for th in east.find_all("th", {"data-stat": "player"})]
  west_all_stars = [th.get('data-append-csv') for th in west.find_all("th", {"data-stat": "player"})]
  
  # Remove Nones
  east_all_stars = [p for p in east_all_stars if p] 
  west_all_stars = [p for p in west_all_stars if p] 
  all_stars = east_all_stars + west_all_stars

  # Get all the injured players
  injured = soup.find("ul", {"class": "page_index"})
  if injured:
    injured_players = [p.get("href").split("/")[-1].split(".")[0] for p in injured.find_all("a")]
    all_stars = all_stars + injured_players
  else:
    print("No injured players in", season)

  return all_stars

def get_standings_and_win_pct_by_date(season, date):
  standings = {}

  for conf in ["eastern", "western"]:
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(season) + "_standings_by_date_" + conf + "_conference.html"
    print(url)
  
    if season == 1999:
      print("There was no ASG in 1999")
      return None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find("table", {"id": "standings_by_date"})
    row = table.find("a", text=date).parent.parent
    teams = row.find_all("td")
    for t in teams:
      team_name = t.get("class")[1]
      position = int(t.get("data-stat")[:-2])
      record = t.find("small").text[1:-1].split("-")
      wins = int(record[0])
      losses = int(record[1])
      win_pct = float(wins)/float(wins + losses)
      standings[team_name] = {
        "conference": "East" if conf == "eastern" else "West",
        "name": team_name,
        "rank": position,
        "record": win_pct
      }
  
  return standings

def get_player_team_by_season(season):
  page = requests.get('https://www.basketball-reference.com/leagues/NBA_' + str(season) + '_totals.html')
  soup = BeautifulSoup(page.text, 'html.parser')
  table = soup.find("table", { "id": "totals_stats" })
  body = table.find("tbody")
  rows = body.find_all("tr", class_=lambda x: x != 'thead')

  player_team_mapping = {}
  for player in rows:
    player_id = player.find("td", {"class":"left"})['data-append-csv']
    player_team = player.find("td", {"class":"left", "data-stat": "team_id"})
    team_a = player_team.find("a")
    if not team_a:
      # This player changed teams halfway during the season
      continue

    team_name = team_a.text
    gp_for_team = player.find("td", {"data-stat": "g"}).text

    if not player_id in player_team_mapping:
      player_team_mapping[player_id] = (team_name, gp_for_team)
    else:
      # player_id --> team mapping already exists.
      # this means that this player has 2 or more teams
      mapping = player_team_mapping[player_id]
      if isinstance(mapping, list):
        player_team_mapping[player_id] = mapping + [(team_name, gp_for_team)]
      else:
        player_team_mapping[player_id] = [mapping, (team_name, gp_for_team)]
  
  # For each player with 2 or more teams, we need to make a choice
  # Criteria is if first team played > 20 games, we pick the first.
  # Otherwise, if second team > 20 games, we pick the second.
  # Continue this way, and pick the last remaining if all fails.
  for player, team in player_team_mapping.items():
    if not isinstance(team, list):
      player_team_mapping[player] = team[0]
    else:
      final_team = team[-1][0]
      for t in team:
        if int(t[1]) > 20:
          final_team = t[0]
          break
      player_team_mapping[player] = final_team

  return player_team_mapping

def get_player_info_by_id(player_id, season):
  url = 'https://www.basketball-reference.com/players/' + player_id[0] + '/' + player_id + '.html'
  print(url)
  page = requests.get(url)
  
  soup = BeautifulSoup(page.text, 'html.parser')
  name = soup.find("h1", {"itemprop": "name"}).text

  table = soup.find("table", {"id": "per_game"})
  tbody = table.find("tbody")
  trs = tbody.find_all("tr", {"class": ["full_table", "partial_table"]})

  for tr in trs:
    year = tr.get("id").split(".")[1]

    if year == str(season):
      position = tr.find("td", {"data-stat": "pos"}).text
      td = tr.find("td", {"data-stat": "team_id"})
      if td.find("a"):
        team = td.find("a").text

  return name, position, team

def get_player_name_by_id(player_id):
  url = 'https://www.basketball-reference.com/players/' + player_id[0] + '/' + player_id + '.html'
  print(url)
  page = requests.get(url)
  
  soup = BeautifulSoup(page.text, 'html.parser')
  name = soup.find("h1", {"itemprop": "name"}).text
  return name

def get_player_position_by_id(player_id):
  url = 'https://www.basketball-reference.com/players/' + player_id[0] + '/' + player_id + '.html'
  print(url)
  page = requests.get(url)
  
  soup = BeautifulSoup(page.text, 'html.parser')
  table = soup.find("table", {"id": "per_game"})
  tbody = table.find("tbody")
  trs = tbody.find_all("tr", {"class": "full_table"})

  positions_by_year = {}

  for tr in trs:
    year = tr.get("id").split(".")[1]
    position = tr.find("td", {"data-stat": "pos"}).text
    positions_by_year[year] = position

  return positions_by_year
