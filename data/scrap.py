"""
This script will scrap all pre-ASG stats for all players for a particular season, and write them to a JSON file.
This script takes in the target season as the only argument.
"""

import sys
import json
from bb_ref import *

ASG_DATES = {
  "2020": "Feb 16, 2020",
  "2019": "Feb 17, 2019",	
  "2018": "Feb 18, 2018",	
  "2017": "Feb 19, 2017",	
  "2016": "Feb 14, 2016",	
  "2015": "Feb 15, 2015",	
  "2014": "Feb 16, 2014",	
  "2013": "Feb 17, 2013",	
  "2012": "Feb 26, 2012",	
  "2011": "Feb 20, 2011",	
  "2010": "Feb 14, 2010",	
  "2009": "Feb 15, 2009",	
  "2008": "Feb 17, 2008",	
  "2007": "Feb 18, 2007",	
  "2006": "Feb 19, 2006",	
  "2005": "Feb 20, 2005",	
  "2004": "Feb 15, 2004",	
  "2003": "Feb 9, 2003",	
  "2002": "Feb 10, 2002",	
  "2001": "Feb 11, 2001",	
  "2000": "Feb 13, 2000",	
  "1998": "Feb 8, 1998",	
  "1997": "Feb 9, 1997",	
  "1996": "Feb 11, 1996",	
  "1995": "Feb 12, 1995",	
  "1994": "Feb 13, 1994",	
  "1993": "Feb 21, 1993",	
  "1992": "Feb 9, 1992",	
  "1991": "Feb 10, 1991",	
  "1990": "Feb 11, 1990",	
  "1989": "Feb 12, 1989",	
  "1988": "Feb 7, 1988",	
  "1987": "Feb 8, 1987",	
  "1986": "Feb 9, 1986",	
  "1985": "Feb 10, 1985"
}

# Checking argument

if len(sys.argv) > 2:
  print("Detected more than 1 argument. Exiting.")
  exit(1)

SEASON = sys.argv[1]

if not SEASON.isnumeric():
  print("Provided year is not a number. Exiting.")
  exit(1)

if int(SEASON) < 1980 or int(SEASON) > 2020:
  print("Provided year must between 1980 and 2020 inclusive. Exiting.")
  exit(1)

## Begin ##

# Convert to integer season
season = int(SEASON)

# Get the ASG date
asg_date = ASG_DATES[SEASON]

# If 2020, pick today's date if it is before Feb 16, 2020
if season == 2020:
  from datetime import datetime, timedelta
  today = datetime.today()
  asg_2020 = datetime(2020, 2, 16) 
  if today < asg_2020:
    today = today - timedelta(days=2)
    asg_date = today.strftime("%b %d, %Y")

# Get the standings for all teams just before ASG
standings = get_standings_and_win_pct_by_date(SEASON, asg_date)

# Get all player_ids that were active during this season
player_ids = get_player_ids_for_season(season)

# Initialise dictionary for all players this season
all_players = {}

# We first obtain the list of all stars for this season
all_stars = get_list_of_all_stars(season)

# For each player
for p in player_ids:

  # Get the player info
  name, position, team = get_player_info_by_id(p, season)

  # Get the player individual stats
  stats = get_stats_by_id_and_season(p, season)

  # Get the player team stats
  team_stats = standings[team]
  print(team_stats)
  
  if stats == -1:
    # This row is not pre for some reason. 
    # Could be injury, hence the player has no pre-ASG stats
    pass
  else:
    # Indicate whether player was an all-star this season
    stats["all_star"] = 1 if p in all_stars else 0

    # Add the stats
    all_players[p] = {
      "details": {
        "name": name,
        "position": position
      },
      "stats": stats,
      "team": team_stats
    }

# Write to file
with open("./raw/" + SEASON + '.json', 'w') as fp:
    json.dump(all_players, fp, sort_keys=True, indent=2, separators=(',', ': '))
