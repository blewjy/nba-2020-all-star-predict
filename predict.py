import json
import numpy as np
from sklearn import metrics
from joblib import load
from util import *
from data.bb_ref import *

def predict_player(model, player_id, season):
  x, details = get_input_and_details_for_player(player_id, season)
  pred = model.predict_proba(x)[:,1][0]
  result = format_single_result(pred, details, season)
  return result

def predict_all_star_prob_for_season(models, season):
  year_str = str(season)
  with open("./data/raw/" + year_str + ".json") as players_data_file:
    players_data = json.load(players_data_file)
    results = []

    for p, data in players_data.items():
      x = player_data_to_input(p, data).astype(np.float)
      total_prob = 0
      for model in models:
        total_prob += model.predict_proba(x)[:,1][0] 
      results.append((p, data, total_prob/len(models)))
    
    sorted_results = sorted(results, key = lambda x: x[2], reverse=True)
    max_prob = sorted_results[0][2]
    sorted_results_simple = []
    for r in sorted_results:
      player_id = r[0]
      name = r[1]["details"]["name"]
      position = r[1]["details"]["position"]
      conf = r[1]["team"]["conference"]
      prob = round(r[2]/max_prob, 3) # Normalized and rounded
      sorted_results_simple.append([player_id, name, position, conf, prob])

    return sorted_results_simple
    
def get_all_star_predictions(prob_list):
  # For each conference, we have 4 Backcourt, 6 Frontcourt, and 2 wildcards
  # So this makes maximum 6 Backcourt and 8 Frontcourt, but maximum 12 players total
  east_backcourt = []
  east_frontcourt = []
  west_backcourt = []
  west_frontcourt = []

  for r in prob_list:
    conf = r[3]
    position = "Backcourt" if r[2] == "SG" or r[2] == "PG" else "Frontcourt"
    if conf == "East" and len(east_backcourt) + len(east_frontcourt) < 12:
      if position == "Backcourt" and len(east_backcourt) < 6:
        east_backcourt.append(r)
      elif position == "Frontcourt" and len(east_frontcourt) < 8:
        east_frontcourt.append(r)
    elif conf == "West" and len(west_backcourt) + len(west_frontcourt) < 12:
      if position == "Backcourt" and len(west_backcourt) < 6:
        west_backcourt.append(r)
      elif position == "Frontcourt" and len(west_frontcourt) < 8:
        west_frontcourt.append(r)
    
    if len(east_backcourt) + len(east_frontcourt) == 12 and len(west_backcourt) + len(west_frontcourt) == 12:
      break
    
  east_all_stars = east_backcourt + east_frontcourt
  west_all_stars = west_backcourt + west_frontcourt
  return east_all_stars, west_all_stars

svm_model = load('./models/svm.joblib')
nn_model = load('./models/nn.joblib')
abc_model = load('./models/abc.joblib')

SEASON = 2020

all_star_prob_list = predict_all_star_prob_for_season([svm_model, nn_model, abc_model], SEASON)
east_all_stars, west_all_stars = get_all_star_predictions(all_star_prob_list)
print_result_as_table(west_all_stars, east_all_stars, SEASON, get_list_of_all_stars(SEASON))
