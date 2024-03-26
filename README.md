# Griffis-Soccer-Analysis <img src="images/Ben Logo Round.png" align="right" width="150" height="150"/>

## Overview

This package includes several of the functions I use to analyze football data. More functions will be added as I get everything situated.

Currently, I just have functions to generated style/profile similarities between players, teams, and leagues. As this is the first time I'm publishing a package, I needed to start small.

## Similarity Scores

Similarity scores are purely based on the *style*, not *quality* of a player, league, or team. They are generated from over 35 variales (all z-scores so they are the same scale) and use Cosine Similarity. This is a pretty standard method, and StatsBomb uses Cosine Similarity as one method for their similar player search.

## Installation

To install the package, you can type or copy/paste this into you command line:

``` python
pip install git+https://github.com/griffisben/griffis_soccer_analysis.git
```
If you want to update the package, you can first uninstall the old package by entering this line into your command line:
``` python
pip uninstall griffis_soccer_analysis
```

Here is an example of how to load the package.
``` python
from griffis_soccer_analysis.fbref_code import *
from griffis_soccer_analysis.similarity import *
from griffis_soccer_analysis.whoscored_match_report import *
```
## Whoscored Match Report Example

#### Please note that you are welcome to take some of the raw code and modify to your needs. If you do that, though, please ensure that you give me credit no matter how much you modify. thank you.

#### Download a csv of events for a given match on the Detailed Tournaments section of Whoscored, and make a post-match report image
``` python
whoscored_match_report(
    # The URL of the Whoscored match (detailed tournamnets only)
    url = 'https://www.whoscored.com/Matches/1735525/Live/Belgium-Jupiler-Pro-League-2023-2024-Union-St-Gilloise-Eupen',
    # The match name
    match = 'Union St. Gilloise 4-1 Eupen',
    
    # Home team name
    team_h = 'Union St. Gilloise',
    # Whoscored's ID for the home team (can find in the html slug of the team's page)
    teamId_h = 2647,
    
    # Away team name
    team_a = 'Eupen',
    # Away team ID
    teamId_a = 2166,
    
    # League name
    lg = 'Belgian Pro League',
    # Game date
    date = 'Oct 20, 2023',
    # Your signature
    sig = '@BeGriffis',
    # Language for the image (English, Spanish, Portuguese, French)
    language = 'English',
    
    # Location of your Chromedriver
    chrome_driver_loc = r"C:\Users\Ben\chromedriver.exe",
    # Where you want the data to download to
    data_download_loc = "C:/users/ben/downloads",

    # Where you want the final image to export to
    img_save_loc = "C:/users/ben/downloads",
    # Path to home team's image
    home_img = "C:/users/ben/club images/Union St. Gilloise.png",
    # Path to away team's image
    away_img = "C:/users/ben/club images/Eupen.png"
)
```

## FBRef Code Examples

#### Download the latest FBRef data (via Opta) for UEFA top 5 players (note, will only work for the current, ongoing season)
``` python
scrape_fbref_t5_leagues_players(season = '2023-2024')
```

#### Download the latest FBRef data (via Opta) for all other leagues FBRef has advanced data for (note, will only work for the current, ongoing season)
``` python
# Comment out any leagues (and their respective season) that you don't want to download
# Also make sure to update the season if a change in season occurs... only changes file name, not the season that's scraped
comps = [
        '2. Bundesliga',
        'Ligue 2',
        'Serie B',
        'La Liga 2',
        'Belgian Pro League',
        'Liga MX',
        'Eredivisie',
        'Primeira Liga',
        'Championship',
    
        'Argentine Primera División',
        'Argentina Copa de la Liga'
        'MLS',
        'Brasileirão',

        'NWSL',
        'WSL',
        'Liga F',
        'A-League Women',
        'Division 1 Féminine',
        'Frauen-Bundesliga',
        'Serie A Femminile'
]
ssns = [
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
    
        '2024',
        '2024',
        '2024',
        '2024',

        '2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024',
        '2023-2024'
       ]

scrape_fbref_next12_leagues_players(comps = comps, seasons = ssns)
```

#### Combine all FBRef scraped leagues into one file
``` python
combine_t5_next12_fbref(t5_season = '2023-2024')
```


#### Make a quick scouting card of 12 key stats for a player
``` python
fbref_scout_report(season = '2023-2024',
            program = 'mf',   # gk, df, mf, fw (each has 12 selected metrics for the position)
            player_pos = 'MF',  # GK, DF, MF, FW (FBRef positions)
            playerPrompt = 'Lucas Besozzi',
            SquadPrompt = '',
            minutesPlayed = 700,
            compP = 'Argentine Primera División',
            saveinput = 'n',
            signature = '@BeGriffis',
            data_date = 'Data as of 9/29/23',
            fbref_file_path = 'C:/Users/Ben/From Mac/Python/'
           )
```

## Similarity Examples
For a Juypter Notebook file with example code & output and more info on each variable, please [see this file](https://github.com/griffisben/griffis_soccer_analysis/blob/main/griffis_soccer_analysis%20examples.ipynb)

#### See available leagues
```Python
available_leagues()
```
#### See available teams in a league
```Python
teams_in_league(
    league = "A-League Men 22-23"
)
```
#### See available players in a team
```Python
available_players(
    league = "A-League Men 22-23",
    team = 'Western Sydney Wanderers'
)
```
#### League Similarities
```Python
# This is how to grab all outputs
df, info, dist_fig = league_similarity(
    league = "A-League Men",
    season = "22-23",
    nlgs = 15
)
# This is one way to print the information and then the similarity dataframe
for i in range(len(info)):
    print(info[i])
df
```
#### Team similarities
```Python
# This is how to grab all outputs
df, info, dist_fig = team_similarity(
    team = "Western Sydney Wanderers",
    league = "A-League Men",
    season = "22-23",
    nlgs = 15
)
# This is one way to print the information and then the similarity dataframe
for i in range(len(info)):
    print(info[i])
df
```
#### Player similarities
```Python
"""
CHOICES FOR compare_league VARIABLE

All
UEFA T5
UEFA Next 10
UEFA Next 20
UEFA T5 2nd Tiers
8 AFC
CONMEBOL Top 4
Argentina & Brazil
Scandinavia (note: this only includes top tiers from Denmark, Norway, Sweden, and Finland)

Or, make your own by writing each league-season name (can find with available_leagues()) separated by a space & comma:
    'MLS 2023, Liga MX 23-24'
    'Premier League 23-24, Championship 23-24, League One 23-24, League Two 23-24'

"""

df, info, dist_fig = player_similarity(
    player = "E. Spertsyan (23, Krasnodar, Russian Premier League 23-24)",
    position = "CM",
    nplayers = 20,
    compare_leagues = 'All',
    min_age = 16,   # Minimum age of similar players (always still inside the top 5%)
    max_age = 40,   # Maximum age of similar players (always still inside the top 5%)
    similar_lg_team = False,
    mean_sim = False,
)

# This is one way to print the information and then the similarity dataframe
for i in range(len(info)):
    print(info[i])
df
```
