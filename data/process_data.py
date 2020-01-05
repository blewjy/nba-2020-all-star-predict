"""
From the raw data, this script will extract only the features that we want and proccess into csv.

For each player, these are the following features that we want:

Individual stats:
- Games Played (g)
- Games Started (gs)
- Minutes per Game (mp_per_g)
- Points per Game (pts_per_g)
- Total Rebounds per Game (trb_per_g)
- Assists per Game (ast_per_g)
- Steals per Game (stl_per_g)
- Blocks per Game (blk_per_g)
- Field Goal Percentage (fg_pct)
- 3-point Field Goal Percentage (fg3_pct)
- Free Throw Percentage (ft_pct)
- Usage Rate (usg_pct)

Team stats:
- Win Percentage (win_pct)
- Conference Seed (seed)

Output:
- All-star 

Our csv will be as follows:

g, gs, mp_per_g, pts_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g, fg_pct, fg3_pct, ft_pct, usg_pct, win_pct, seed, all-star

Also, to keep our dataset more balanced, we will be filtering out for only the the players that have Usage Rate >= 8 and Minutes Per Game >= 18. Using this filter restricts our dataset to include only players that perform better for their team.
"""

import json
import csv

for year in range(1985, 2020):
  
  if year == 1999:
    continue

  players = []
  year_str = str(year)
  with open("./raw/" + year_str + ".json") as players_data_file:
    players_data = json.load(players_data_file)

    for p, data in players_data.items():

      # Individual stats
      g = data["stats"]["g"]
      gs = data["stats"]["gs"]
      mp_per_g = data["stats"]["mp_per_g"]
      pts_per_g = data["stats"]["pts_per_g"]
      trb_per_g = data["stats"]["trb_per_g"]
      ast_per_g = data["stats"]["ast_per_g"]
      stl_per_g = str(float(data["stats"]["stl"])/float(g))
      blk_per_g = str(float(data["stats"]["blk"])/float(g))
      fg_pct = data["stats"]["fg_pct"]
      fg3_pct = data["stats"]["fg3_pct"]
      ft_pct = data["stats"]["ft_pct"]
      # fga_per_g = str(float(data["stats"]["fga"])/float(g))
      # fg3a_per_g = str(float(data["stats"]["fg3a"])/float(g))
      # fta_per_g = str(float(data["stats"]["fta"])/float(g))
      usg_pct = data["stats"]["usg_pct"]
      
      # Team stats
      win_pct = data["team"]["record"]
      seed = data["team"]["rank"]

      # Output
      all_star = data["stats"]["all_star"]

      final_stats = [g, gs, mp_per_g, pts_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g, fg_pct, fg3_pct, ft_pct, usg_pct, win_pct, seed, all_star]
      # final_stats = [g, gs, mp_per_g, pts_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g, fg_pct, fg3_pct, ft_pct, fga_per_g, fg3a_per_g, fta_per_g, usg_pct, win_pct, seed, all_star]

      # if float(mp_per_g) >= 18 and float(usg_pct) >= 8:
      players.append(final_stats)
  
  with open("./processed/" + year_str + ".csv", "w", newline="") as output_file:
    wr = csv.writer(output_file)
    wr.writerows(players)
