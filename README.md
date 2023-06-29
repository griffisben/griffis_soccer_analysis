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

Here is an example of how to load the package.
``` python
from griffis_soccer_analysis.fbref_code import *
from griffis_soccer_analysis.similarity import *
```
## FBRef Code Examples

#### Download the latest FBRef data (via Opta) for UEFA top 5 players
``` python
scrape_fbref_t5_leagues_players()
```

#### Make a quick scouting card of 12 key stats for a player
``` python
fbref_scout_report(season = '22-23',
            program = 'mf',
            player_pos = 'Central Midfield',
            playerPrompt = 'Branco van den Boomen',
            SquadPrompt = '',
            minutesPlayed = 900,
            compP = 'ligue 1',
            saveinput = 'n',
            signature = '@BeGriffis',
            data_date = 'Data final for 22/23',
            fbref_file_path = 'C:/Users/You/File Path Here/'
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
# This is how to grab all outputs
df, info, dist_fig = player_similarity(
    player = "C. Nieuwenhof (22, Western Sydney Wanderers, A-League Men 22-23)",
    position = "CM",
    nplayers = 20,
    t5_leagues = 'y',  # 'y', 'Y', 'yes', 'Yes' will only show similar players that currently (22/23) play in the T5 UEFA leagues
    min_age = 1,   # Minimum age of similar players (always still inside the top 2%)
    max_age = 99,   # Maximum age of similar players
    similar_lg_team = False,
    mean_sim = False
)
# This is one way to print the information and then the similarity dataframe
for i in range(len(info)):
    print(info[i])
df
```
