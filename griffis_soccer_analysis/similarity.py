from functools import lru_cache
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statistics
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")

@lru_cache(maxsize=10)
def read_parquet(link):
    return pd.read_parquet(link)

def league_similarity(league, season, nlgs=20):
    # League input
    league_input = f"{league} {season}"

    # Read the CSV file
    data = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/league%20style%20similarity.parquet')

    # Calculate cosine similarity between leagues
    similarity_matrix = cosine_similarity(data.iloc[:, 1:])

    # Create a DataFrame to store league pairs and similarity scores
    similarities = []
    num_leagues = len(data)
    for i in range(num_leagues):
        for j in range(i + 1, num_leagues):
            league1 = data.iloc[i, 0]
            league2 = data.iloc[j, 0]
            similarity = similarity_matrix[i, j]
            similarities.append([league1, league2, similarity*100])

    similarity_df = pd.DataFrame(similarities, columns=['League 1', 'League 2', 'Similarity'])

    final = similarity_df[(similarity_df['League 1']==league_input) | (similarity_df['League 2']==league_input)].sort_values(by=['Similarity'],ascending=False).reset_index(drop=True)
    final['League'] = ''
    for i in range(len(final)):
        l = [final['League 1'].values[i],final['League 2'].values[i]]
        l.remove(league_input)
        final.League[i] = l[0]

    final = final[['League','Similarity']]

    # Basic notes
    title = f'\033[1mLeague Style Similarity to {league_input}\033[0;0m\n'
    mean = f'Mean similarity score: {round(np.mean(final.Similarity),2)}'
    stddev = f'1.5 Standard Deviation similarity score: {round(np.mean(final.Similarity)+(1.5*(np.std(final.Similarity))),2)}'
    sample = f'Includes data from 161 leagues'
    score_note = "All similarity values are between -100 (as opposite as possible) & 100 (the exact same)"
    sim_note = "Similarity is purely style based on over 35 metrics, not that each league is the same quality"
    signature = "Data via Wyscout  |  Model by Ben Griffis (@BeGriffis)"

    information = [title,mean,stddev,sample,score_note,sim_note,signature]

    # Make the graph
    sns.set(rc={'figure.dpi': 200, 'axes.grid': False, 'text.color': '#4A2E19',
                'axes.facecolor': '#fbf9f4', 'figure.facecolor':'#fbf9f4', 'figure.figsize':(4,3),
                'axes.labelsize': 4, 'ytick.labelsize': 4, 'xtick.labelsize': 4,
               })

    plt.hist(final.Similarity, bins=25, color='teal', alpha=.3)
    plt.axvline(x=(np.mean(final.Similarity)+(1.5*(np.std(final.Similarity)))),
                color='teal', ymax=.1, lw=1.5, alpha=.8)
    plt.text(x=(np.mean(final.Similarity)+(1.5*(np.std(final.Similarity))))-1, y=0.2,
             s='1.5 Std. Dev\nAbove Mean', ha='right', va='bottom', color='darkslategrey', size=6)
    plt.title(f'League Style Similarity to {league_input}\nDistribution of all team similarities\nData via Wyscout | Model by @BeGriffis',
              color='#4A2E19', size=8)

    fig = plt.gcf()
    plt.close(fig)

    return final.head(nlgs), information, fig

def team_similarity(team, league, season, nteams=20):
    # Team input
    team_input = f"{team} - {league} {season}"

    # Load the data
    similarity_df = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/team%20similarities.parquet')
    df1 = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/Team%20and%20League%20Similarity%20Rankings%20Together.parquet')
    
    base = similarity_df[(similarity_df['League 1']==team_input) | (similarity_df['League 2']==team_input)].sort_values(by=['Similarity'],ascending=False).reset_index(drop=True)
    base['Team'] = ''
    for i in range(len(base)):
        l = [base['League 1'].values[i],base['League 2'].values[i]]
        l.remove(team_input)
        base.Team[i] = l[0]
    base = base[['Team','Similarity']]

    # Basic notes
    title = f'\033[1mTeam Style Similarity to {team_input}\033[0;0m\n'
    mean = f'Mean similarity score: {round(np.mean(base.Similarity),2)}'
    stddev = f'1.5 Standard Deviation similarity score: {round(np.mean(base.Similarity)+(1.5*(np.std(base.Similarity))),2)}'
    sample = f'Includes 2,640 teams from 161 leagues'
    score_note = "All similarity values are between -100 (as opposite as possible) & 100 (the exact same)"
    sim_note = "Similarity is purely style based on over 35 metrics, not that each team is the same quality"
    signature = "Data via Wyscout  |  Model by Ben Griffis (@BeGriffis)"
    
    information = [title,mean,stddev,sample,score_note,sim_note,signature]
    
    # Only include teams at least 1 standard deviation above the mean score
    final = base[base.Similarity >= (np.mean(base.Similarity)+(1.5*(np.std(base.Similarity))))].head(nteams)

    # Calculate & add league style similarity
    final['League Style Similarity'] = 0.0
    foc_team_input = team_input.split(" - ")[1]
    for i in range(len(final)):
        c_team_input = final.Team[i].split(" - ")[1]
        s = df1[((df1['League1']==foc_team_input) | (df1['League2']==foc_team_input)) & ((df1['League1']==c_team_input) | (df1['League2']==c_team_input))].copy()
        final['League Style Similarity'][i] = s.LeagueSimilarity.values[0]
        if foc_team_input == c_team_input:
            final['League Style Similarity'][i] = 100
    final.rename(columns={'Similarity':'Team Style Similarity'},inplace=True)
    
    # Make the graph
    sns.set(rc={'figure.dpi': 200, 'axes.grid': False, 'text.color': '#4A2E19',
                'axes.facecolor': '#fbf9f4', 'figure.facecolor':'#fbf9f4', 'figure.figsize':(4,3),
                'axes.labelsize': 4, 'ytick.labelsize': 4, 'xtick.labelsize': 4,
               })

    plt.hist(base.Similarity, bins=50, color='teal', alpha=.3)
    plt.axvline(x=(np.mean(base.Similarity)+(1.5*(np.std(base.Similarity)))),
                color='teal', ymax=.1, lw=1.5, alpha=.8)
    plt.text(x=(np.mean(base.Similarity)+(1.5*(np.std(base.Similarity))))-1, y=1,
             s='1.5 Std. Dev\nAbove Mean', ha='right', va='bottom', color='darkslategrey', size=6)
    plt.title(f'Team Style Similarity to {team_input}\nDistribution of all team similarities\nData via Wyscout | Model by @BeGriffis',
              color='#4A2E19', size=8)
    
    fig = plt.gcf()
    plt.close(fig)

    return final, information, fig

def player_similarity(player, position, nplayers=20, t5_leagues='n', min_age=1, max_age=99, similar_lg_team=False, mean_sim=False):
    if position == 'GK':
        print('Sorry... GKs unavailable right now.')
        return ['Sorry'], ['Sorry'], ['Sorry']
    else:
        # Load the data
        df1 = read_parquet(f'https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/Player%20Similarity/{position}_1.parquet')
        df2 = read_parquet(f'https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/Player%20Similarity/{position}_2.parquet')
        df3 = read_parquet(f'https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/Player%20Similarity/{position}_3.parquet')
        df4 = read_parquet(f'https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/Player%20Similarity/{position}_4.parquet')
        df = pd.concat([df1,df2,df3,df4]).reset_index(drop=True)
        del df1
        del df2
        del df3
        del df4

        df1 = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/Team%20and%20League%20Similarity%20Rankings%20Together.parquet')
        base = df[(df['Player 1']==player) | (df['Player 2']==player)].sort_values(by=['Similarity'],ascending=False).reset_index(drop=True)
        base['Player'] = (base['Player 2']).where(base['Player 1'] == player, base['Player 1'])
        base = base.loc[:, ['Player', 'Similarity']]
        top2pct = base.Similarity.quantile(.98)
        
        if similar_lg_team == True:
            if t5_leagues in ['y','Y','yes','Yes','YES']:
                extra = " in UEFA T5 leagues that are also in teams & leagues with relatively similar styles"
            else:
                extra = " that are also in teams & leagues with relatively similar styles"
        else:
            if t5_leagues in ['y','Y','yes','Yes','YES']:
                extra = " in UEFA T5 leagues"
            else:
                extra = ""

        # Basic notes
        title = f'\033[1mPlayer Style/Profile Similarity to: {player}\033[0;0m\n'
        pct98 = f'98th Percentile similarity score: {round(top2pct,2)}'
        sample = f'Includes {position}s from 161 leagues, minimum 450 mins  |  Sample size: {len(base)} players'
        score_note = "All similarity values are between -100 (as opposite as possible) & 100 (the exact same)"
        sim_note = "Similarity is purely style/profile based on over 35 metrics, not that each player is the same quality"
        sim_lg_team_note = f"Showing top {nplayers} players, ages {min_age}-{max_age}, in top 2% of similarity{extra}"
        signature = "Data via Wyscout  |  Model by Ben Griffis (@BeGriffis)"

        information = [title,pct98,sample,score_note,sim_note,sim_lg_team_note,signature]

        final = base[base.Similarity >= top2pct].reset_index(drop=True)

        foc_p = player.split(", ")[2].split(')')[0]
        foc_t = player.split(', ')[1]

        final['League 1'] = [" - ".join(x.split(', ')[1:]).rstrip(')') for x in final['Player']]
        final['League 2'] = f'{foc_t} - {foc_p}'

        final.loc[:, ['League 1', 'League 2']] = final.loc[:, ['League 1', 'League 2']].apply(lambda x: sorted(x), axis=1).to_list()

        final = final.merge(df1.rename(columns={'Similarity': 'Team Style Similarity',
                                                'LeagueSimilarity': 'League Style Similarity'}),
                    on=['League 1', 'League 2'], how='inner')\
        .loc[:, ['Player', 'Similarity', 'League Style Similarity', 'Team Style Similarity', 
                 'League1', 'League2', 'Team1', 'Team2']]\
        .rename(columns={'Similarity': 'Player Style Similarity'})\
        .sort_values(by='Player Style Similarity', ascending=False).reset_index(drop=True)
        final['Team Style Similarity'] = pd.Series([100 if t1 == t2 else tss \
                                                      for (t1, t2, tss) in zip(final['Team1'],
                                                                               final['Team2'],
                                                                               final['Team Style Similarity'])])
        final['League Style Similarity'] = pd.Series([100 if l1 == l2 else lss \
                                                      for (l1, l2, lss) in zip(final['League1'],
                                                                               final['League2'],
                                                                               final['League Style Similarity'])])
        final = final.loc[:, ['Player', 'Player Style Similarity', 
                              'League Style Similarity', 'Team Style Similarity']]

        if mean_sim == True:
            similar_lg_team = True
        if similar_lg_team == True:
            final = final[(final['League Style Similarity']>0) & (final['Team Style Similarity']>0)].reset_index(drop=True)

            if mean_sim == True:
                final['Mean Similarity'] = final.loc[:, ['Player Style Similarity', 'League Style Similarity', 'Team Style Similarity']].mean(axis=1)
                final = final.sort_values(by=['Mean Similarity'],ascending=False).reset_index(drop=True)

        # Make the graph
        sns.set(rc={'figure.dpi': 200, 'axes.grid': False, 'text.color': '#4A2E19',
                    'axes.facecolor': '#fbf9f4', 'figure.facecolor':'#fbf9f4', 'figure.figsize':(4,3),
                    'axes.labelsize': 4, 'ytick.labelsize': 4, 'xtick.labelsize': 4,
                   })

        plt.hist(base.Similarity, bins=100, color='teal', alpha=.3)
        plt.axvline(x=base.Similarity.quantile(.98),
                    color='teal', ymax=.1, lw=1.5, alpha=.8)
        plt.text(x=base.Similarity.quantile(.98)-1, y=1,
                 s='98th Percentile', ha='right', va='bottom', color='darkslategrey', size=6)
        plt.title(f'Player Style/Profile Similarity to\n{player}\nDistribution of all {position} similarities\nData via Wyscout | Model by @BeGriffis',
                  color='#4A2E19', size=8)

        fig = plt.gcf()
        plt.close(fig)
        
        final['Age'] = [int(final.iloc[x,0].split('(')[1].split(',')[0])\
                       for x in range(len(final))]
        
        final = final[final['Age'].between(min_age,max_age)]

        final['T5'] = [1 if final.iloc[x,0].split(", ")[2].split(')')[0] == 'Premier League 23-24' or final.iloc[x,0].split(", ")[2].split(')')[0] == 'Ligue 1 23-24' or final.iloc[x,0].split(", ")[2].split(')')[0] == 'Bundesliga 23-24' or final.iloc[x,0].split(", ")[2].split(')')[0] == 'La Liga 23-24' or final.iloc[x,0].split(", ")[2].split(')')[0] == 'Serie A 23-24' else 0\
                       for x in range(len(final))]
        if t5_leagues in ['y','Y','yes','Yes','YES']:
            final = final.loc[final.T5==1][['Player','Player Style Similarity','League Style Similarity','Team Style Similarity']]
        else:
            final = final[['Player','Player Style Similarity','League Style Similarity','Team Style Similarity']]

        return final.head(nplayers).reset_index(drop=True), information, fig

def available_leagues():
    data = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/league%20style%20similarity.parquet')
    lgs = data['League'].unique().tolist()
    
    return lgs

def teams_in_league(league):
    data = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/league%20style%20similarity%20teams.parquet')
    data = data[['Team within selected timeframe']]
    data['League'] = ''
    data['Team'] = ''
    for i in range(len(data)):
        tl = data['Team within selected timeframe'][i]
        data['Team'][i] = tl.split(" - ")[0]
        data['League'][i] = tl.split(" - ")[1]
    data = data[['League','Team']]
    
    teams = data[data.League == league].Team.unique().tolist()
    
    return teams

def available_players(league, team):
    pd.set_option('display.max_colwidth', None)
    df = read_parquet('https://github.com/griffisben/Griffis-Soccer-Analysis/raw/main/Files/league%20style%20similarity%20players.parquet')
    df = df[(df['League']==league) & (df['Team within selected timeframe']==team)][['Player_Team','Player','Age','Real Position']]
    
    return df
