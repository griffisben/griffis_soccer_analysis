# Griffis-Soccer-Analysis <img src="images/Ben Logo Round.png" align="right" width="150" height="150"/>
STILL BUILDING
## Overview

This package includes several of the functions I use to analyze football data. More functions will be added as I get everything situated.

Currently, I just have functions to generated style/profile similarities between players, teams, and leagues. As this is the first time I'm publishing a package, I needed to start small.

## Installation

To install the package, you can type this into you command line:

``` python
pip install Griffis-Soccer-Analysis
```

Here is an example of how to load the package.
``` python
import Griffis_Soccer_Analysis
```

## Examples

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
    "Western Sydney Wanderers",
    "A-League Men",
    "22-23",
    15
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
    similar_lg_team = False,
    mean_sim = False
)
# This is one way to print the information and then the similarity dataframe
for i in range(len(info)):
    print(info[i])
df
```
