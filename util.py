import json
import numpy as np
from tabulate import tabulate

def player_data_to_input(player_id, player_data):
  # Individual stats
  g = player_data["stats"]["g"]
  gs = player_data["stats"]["gs"]
  mp_per_g = player_data["stats"]["mp_per_g"]
  pts_per_g = player_data["stats"]["pts_per_g"]
  trb_per_g = player_data["stats"]["trb_per_g"]
  ast_per_g = player_data["stats"]["ast_per_g"]
  stl_per_g = str(float(player_data["stats"]["stl"])/float(g))
  blk_per_g = str(float(player_data["stats"]["blk"])/float(g))
  fg_pct = player_data["stats"]["fg_pct"]
  fg3_pct = player_data["stats"]["fg3_pct"]
  ft_pct = player_data["stats"]["ft_pct"]
  # fga_per_g = str(float(player_data["stats"]["fga"])/float(g))
  # fg3a_per_g = str(float(player_data["stats"]["fg3a"])/float(g))
  # fta_per_g = str(float(player_data["stats"]["fta"])/float(g))
  usg_pct = player_data["stats"]["usg_pct"]

  # Team stats
  player_team = player_data["team"]["name"]
  win_pct = player_data["team"]["record"]
  seed = player_data["team"]["rank"]

  final_stats = np.array([[g, gs, mp_per_g, pts_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g, fg_pct, fg3_pct, ft_pct, usg_pct, win_pct, seed]])
  # final_stats = np.array([[g, gs, mp_per_g, pts_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g, fg_pct, fg3_pct, ft_pct, fga_per_g, fg3a_per_g, fta_per_g, usg_pct, win_pct, seed]])

  final_stats[final_stats=='']='0'

  return np.nan_to_num(final_stats)

def get_input_and_details_for_player(player_id, season):
  year_str = str(season)
  with open("./data/raw/" + year_str + ".json") as players_data_file:
    players_data = json.load(players_data_file)
    try:
      data = players_data[player_id]
      return player_data_to_input(player_id, data), data
    except:
      return None, None
  return None, None

def format_single_result(pred, player_details, season):
  prob = round(pred,3)
  player_name = player_details["details"]["name"]
  player_position = player_details["details"]["position"]
  team_name = player_details["team"]["name"]
  if player_position == "PG" or player_position == "SG":
    player_position = "Backcourt"
  else:
    player_position = "Frontcourt"
  result = "{} [{}] ({}): {} probability of being an All-Star in {}".format(player_name, team_name, player_position, prob, str(season))
  return result

def format_season_results(results, season):
  final_results = []
  for r in results:
    result = format_single_result(r[1], r[0], season)
    final_results.append(result)
  return final_results

def print_result_as_table(west_all_stars, east_all_stars, season, answer):
  sorted_west_as = sorted(west_all_stars, key = lambda x: x[4], reverse=True)
  num_backcourt_starters = 0 # Max 2
  num_frontcourt_starters = 0 # Max 3
  west_starters = []
  west_reserves = []
  for r in sorted_west_as:
    player_position = r[2]
    if player_position == "PG" or player_position == "SG":
      player_position = "Backcourt"
    else:
      player_position = "Frontcourt"
    if player_position == "Backcourt" and num_backcourt_starters < 2:
      west_starters.append(r)
      num_backcourt_starters += 1
    elif player_position == "Frontcourt" and num_frontcourt_starters < 3:
      west_starters.append(r)
      num_frontcourt_starters += 1
    else:
      west_reserves.append(r)
  west_starters_table = []
  west_reserves_table = []
  for s in west_starters:
    row = [s[1], s[2], s[4]]
    if s[0] in answer:
      row.append(u'\u2713')
    west_starters_table.append(row)
  for r in west_reserves:
    row = [r[1], r[2], r[4]]
    if r[0] in answer:
      row.append(u'\u2713')
    west_reserves_table.append(row)
  
  sorted_east_as = sorted(east_all_stars, key = lambda x: x[4], reverse=True)
  num_backcourt_starters = 0 # Max 2
  num_frontcourt_starters = 0 # Max 3
  east_starters = []
  east_reserves = []
  for r in sorted_east_as:
    player_position = r[2]
    if player_position == "PG" or player_position == "SG":
      player_position = "Backcourt"
    else:
      player_position = "Frontcourt"
    if player_position == "Backcourt" and num_backcourt_starters < 2:
      east_starters.append(r)
      num_backcourt_starters += 1
    elif player_position == "Frontcourt" and num_frontcourt_starters < 3:
      east_starters.append(r)
      num_frontcourt_starters += 1
    else:
      east_reserves.append(r)
  east_starters_table = []
  east_reserves_table = []
  for s in east_starters:
    row = [s[1], s[2], s[4]]
    if s[0] in answer:
      row.append(u'\u2713')
    east_starters_table.append(row)
  for r in east_reserves:
    row = [r[1], r[2], r[4]]
    if r[0] in answer:
      row.append(u'\u2713')
    east_reserves_table.append(row)
  
  east_final_table = [["East Starters:", "", ""], ["--------------------------", "--", "-------------"]] + east_starters_table + [["--------------------------", "--", "-------------"], ["East Reserves:", "", ""], ["--------------------------", "--", "-------------"]] + east_reserves_table
  west_final_table = [["West Starters:", "", ""], ["--------------------------", "--", "-------------"]] + west_starters_table + [["--------------------------", "--", "-------------"], ["West Reserves:", "", ""], ["--------------------------", "--", "-------------"]] + west_reserves_table
  final_table = []
  for w, e in zip(west_final_table, east_final_table):
    final_table.append(e + w)
  print(tabulate(final_table))




  

  
