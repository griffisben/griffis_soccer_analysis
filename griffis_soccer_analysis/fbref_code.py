from functools import lru_cache
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statistics
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup, Comment
import os
from pathlib import Path
import time
from scipy import stats
from statistics import mean
from math import pi

def scrape_fbref_t5_leagues_players(season):
    # File names to change if needed
    raw_nongk = f'Raw FBRef {season}'
    raw_gk = f'Raw FBRef GK {season}'
    final_nongk = f'Final FBRef {season}'
    final_gk = f'Final FBRef GK {season}'

    # this is the file path root, i.e. where this file is located
    root = str(Path(os.getcwd()).parents[0]).replace('\\','/')+'/'

    # This section creates the programs that gather data from FBRef.com... Data is from FBRef and Opta
    def _get_table(soup):
        return soup.find_all('table')[0]

    def _get_opp_table(soup):
        return soup.find_all('table')[1]

    def _parse_row(row):
        cols = None
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        return cols

    def get_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        return data

    def get_opp_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_opp_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        return data


    # this section gets the raw tables from FBRef.com

    standard = "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
    shooting = "https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats"
    passing = "https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats"
    pass_types = "https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats"
    gsca = "https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats"
    defense = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
    poss = "https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats"
    misc = "https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats"

    df_standard = get_df(standard)
    df_shooting = get_df(shooting)
    df_passing = get_df(passing)
    df_pass_types = get_df(pass_types)
    df_gsca = get_df(gsca)
    df_defense = get_df(defense)
    df_poss = get_df(poss)
    df_misc = get_df(misc)

    # this section sorts the raw tables then resets their indexes. Without this step, you will
    # run into issues with players who play minutes for 2 clubs in a season.

    df_standard.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_shooting.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_passing.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_pass_types.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_gsca.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_defense.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_poss.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_misc.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

    df_standard = df_standard.reset_index(drop=True)
    df_shooting = df_shooting.reset_index(drop=True)
    df_passing = df_passing.reset_index(drop=True)
    df_pass_types = df_pass_types.reset_index(drop=True)
    df_gsca = df_gsca.reset_index(drop=True)
    df_defense = df_defense.reset_index(drop=True)
    df_poss = df_poss.reset_index(drop=True)
    df_misc = df_misc.reset_index(drop=True)

    # Now the fun part... merging all raw tables into one.
    # Change any column name you want to change:
    # Example --   'Gls': 'Goals'  changes column "Gls" to be named "Goals", etc.
    ## Note that I inclide all columns but don't always change the names... this is useful to me when I need to update the columns, like when FBRef witched to Opta data haha. I got lucky as this made it easier on me!

    df = df_standard.iloc[:, 0:10]
    df = df.join(df_standard.iloc[:, 13])
    df = df.join(df_standard.iloc[:, 26])
    df = df.rename(columns={'G-PK': 'npGoals', 'Gls':'Glsxx'})
    df = df.join(df_shooting.iloc[:,8:25])
    df = df.rename(columns={'Gls': 'Goals', 'Sh': 'Shots', 'SoT': 'SoT', 'SoT%': 'SoT%', 'Sh/90': 'Sh/90', 'SoT/90': 'SoT/90', 'G/Sh': 'G/Sh', 'G/SoT': 'G/SoT', 'Dist': 'AvgShotDistance', 'FK': 'FKShots', 'PK': 'PK', 'PKatt': 'PKsAtt', 'xG': 'xG', 'npxG': 'npxG', 'npxG/Sh': 'npxG/Sh', 'G-xG': 'G-xG', 'np:G-xG': 'npG-xG'})

    df = df.join(df_passing.iloc[:,8:13])
    df = df.rename(columns={'Cmp': 'PassesCompleted', 'Att': 'PassesAttempted', 'Cmp%': 'TotCmp%', 'TotDist': 'TotalPassDist', 'PrgDist': 'ProgPassDist', })
    df = df.join(df_passing.iloc[:,13:16])
    df = df.rename(columns={'Cmp': 'ShortPassCmp', 'Att': 'ShortPassAtt', 'Cmp%': 'ShortPassCmp%', })
    df = df.join(df_passing.iloc[:,16:19])
    df = df.rename(columns={'Cmp': 'MedPassCmp', 'Att': 'MedPassAtt', 'Cmp%': 'MedPassCmp%', })
    df = df.join(df_passing.iloc[:,19:22])
    df = df.rename(columns={'Cmp': 'LongPassCmp', 'Att': 'LongPassAtt', 'Cmp%': 'LongPassCmp%', })
    df = df.join(df_passing.iloc[:,22:31])
    df = df.rename(columns={'Ast': 'Assists', 'xAG':'xAG', 'xA': 'xA', 'A-xAG': 'A-xAG', 'KP': 'KeyPasses', '1/3': 'Final1/3Cmp', 'PPA': 'PenAreaCmp', 'CrsPA': 'CrsPenAreaCmp', 'PrgP': 'ProgPasses', })

    df = df.join(df_pass_types.iloc[:, 9:23])
    df = df.rename(columns={'Live': 'LivePass', 'Dead': 'DeadPass', 'FK': 'FKPasses', 'TB': 'ThruBalls', 'Sw': 'Switches', 'Crs': 'Crs', 'CK': 'CK', 'In': 'InSwingCK', 'Out': 'OutSwingCK', 'Str': 'StrCK', 'TI': 'ThrowIn', 'Off': 'PassesToOff', 'Blocks':'PassesBlocked', 'Cmp':'Cmpxxx'})

    df = df.join(df_gsca.iloc[:, 8:16].rename(columns={'SCA': 'SCA', 'SCA90': 'SCA90', 'PassLive': 'SCAPassLive', 'PassDead': 'SCAPassDead', 'TO': 'SCADrib', 'Sh': 'SCASh', 'Fld': 'SCAFld', 'Def': 'SCADef'}))
    df = df.join(df_gsca.iloc[:, 16:24].rename(columns={'GCA': 'GCA', 'GCA90': 'GCA90', 'PassLive': 'GCAPassLive', 'PassDead': 'GCAPassDead', 'TO': 'GCADrib', 'Sh': 'GCASh', 'Fld': 'GCAFld', 'Def': 'GCADef'}))

    df = df.join(df_defense.iloc[:,8:13].rename(columns={'Tkl': 'Tkl', 'TklW': 'TklWinPoss', 'Def 3rd': 'Def3rdTkl', 'Mid 3rd': 'Mid3rdTkl', 'Att 3rd': 'Att3rdTkl'}))
    df = df.join(df_defense.iloc[:,13:24].rename(columns={'Tkl': 'DrbTkl', 'Att': 'DrbPastAtt', 'Tkl%': 'DrbTkl%', 'Lost': 'DrbPast', 'Blocks': 'Blocks', 'Sh': 'ShBlocks', 'Pass': 'PassBlocks', 'Int': 'Int', 'Tkl+Int': 'Tkl+Int', 'Clr': 'Clr', 'Err': 'Err'}))

    df = df.join(df_poss.iloc[:,8:30])
    df = df.rename(columns={'Touches': 'Touches', 'Def Pen': 'DefPenTouch', 'Def 3rd': 'Def3rdTouch', 'Mid 3rd': 'Mid3rdTouch', 'Att 3rd': 'Att3rdTouch', 'Att Pen': 'AttPenTouch', 'Live': 'LiveTouch', 'Succ': 'SuccDrb', 'Att': 'AttDrb', 'Succ%': 'DrbSucc%', 'Tkld':'TimesTackled', 'Tkld%':'TimesTackled%', 'Carries':'Carries', 'TotDist':'TotalCarryDistance', 'PrgDist':'ProgCarryDistance', 'PrgC':'ProgCarries', '1/3':'CarriesToFinalThird', 'CPA':'CarriesToPenArea', 'Mis': 'CarryMistakes', 'Dis': 'Disposesed', 'Rec': 'ReceivedPass', 'PrgR':'ProgPassesRec'})

    df = df.join(df_misc.iloc[:, 8:14])
    df = df.rename(columns={'CrdY': 'Yellows', 'CrdR': 'Reds', '2CrdY': 'Yellow2', 'Fls': 'Fls', 'Fld': 'Fld', 'Off': 'Off', })
    df = df.join(df_misc.iloc[:,17:24])
    df = df.rename(columns={'PKwon': 'PKwon', 'PKcon': 'PKcon', 'OG': 'OG', 'Recov': 'Recov', 'Won': 'AerialWins', 'Lost': 'AerialLoss', 'Won%': 'AerialWin%', })

    # Make sure to drop all blank rows (FBRef's tables have several)
    df.dropna(subset = ["Player"], inplace=True)

    # Turn the minutes columns to integers. So from '1,500' to '1500'. Otherwise it can't do calculations with minutes
    for i in range(0,len(df)):
        df.iloc[i][9] = df.iloc[i][9].replace(',','')
    df.iloc[:,9:] = df.iloc[:,9:].apply(pd.to_numeric)

    # Store the file
    df_raw_nongk = df.copy()


    ##################################################################################
    ############################## GK SECTION ########################################
    ##################################################################################

    gk = "https://fbref.com/en/comps/Big5/keepers/players/Big-5-European-Leagues-Stats"
    advgk = "https://fbref.com/en/comps/Big5/keepersadv/players/Big-5-European-Leagues-Stats"

    df_gk = get_df(gk)
    df_advgk = get_df(advgk)

    df_gk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_advgk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

    df_gk = df_gk.reset_index(drop=True)
    df_advgk = df_advgk.reset_index(drop=True)

    ###############################################################################

    df = df_raw_nongk.copy()
    df = df[df['Pos'].str.contains("GK")].reset_index().iloc[:,1:]
    df_gk['Pos'] = df_gk['Pos'].astype(str)
    df_gk = df_gk[df_gk['Pos'].str.contains('GK')]
    df_gk = df_gk.reset_index().iloc[:,1:]
    df_gk = df_gk.rename(columns={'PKatt':'PKsFaced'})

    df = df.join(df_gk.iloc[:, 11:26].astype(float), lsuffix='.1', rsuffix='.2')
    df = df.rename(columns={'GA': 'GA', 'GA90': 'GA90', 'SoTA': 'SoTA', 'Saves': 'Saves', 'Save%.1': 'Save%', 'W': 'W', 'D': 'D', 'L': 'L', 'CS': 'CS', 'CS%': 'CS%', 'PKsFaced': 'PKsFaced', 'PKA': 'PKA', 'PKsv': 'PKsv', 'PKm': 'PKm', 'Save%.2': 'PKSave%', })

    df_advgk['Pos'] = df_advgk['Pos'].astype(str)
    df_advgk = df_advgk[df_advgk['Pos'].str.contains('GK')]
    df_advgk = df_advgk.reset_index().iloc[:,1:]
    df = df.join(df_advgk.iloc[:,9:20].astype(float).rename(columns={'PKA': 'PKGA', 'FK': 'FKGA', 'CK': 'CKGA', 'OG': 'OGA', 'PSxG': 'PSxG', 'PSxG/SoT': 'PSxG/SoT', 'PSxG+/-': 'PSxG+/-', '/90': 'PSxG+/- /90', 'Cmp': 'LaunchCmp', 'Att': 'LaunchAtt', 'Cmp%': 'LaunchPassCmp%'}))
    df = df.join(df_advgk.iloc[:,20:24].astype(float).rename(columns={'Att': 'PassAtt', 'Thr': 'PassThr', 'Launch%': 'PassesLaunch%', 'AvgLen': 'AvgLenLaunch'}))
    df = df.join(df_advgk.iloc[:,24:33].astype(float).rename(columns={'Att': 'GoalKicksAtt', 'Launch%': 'GoalKicksLaunch%', 'AvgLen': 'AvgLen', 'Opp': 'OppCrs', 'Stp': 'StpCrs', 'Stp%': 'CrsStp%', '#OPA': '#OPA', '#OPA/90': '#OPA/90', 'AvgDist': 'AvgDistOPA'}))

    df_raw_gk = df.copy()

    ##################################################################################
    ##################### Final file for outfield data ###############################
    ##################################################################################

    df = df_raw_nongk.copy()
    df_90s = df_raw_nongk.copy()
    df_90s['90s'] = df_90s['Min']/90
    for i in range(10,125):
        df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
    df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
    df_new = df.join(df_90s)

    try:
        for i in range(len(df_new)):
            df_new['Age'][i] = int(df_new['Age'][i][:2])
    except:
        pass

    df_final_nongk = df_new.copy()


    ##################################################################################
    ##################### Final file for keeper data #################################
    ##################################################################################

    df = df_raw_gk.copy()
    df_90s = df_raw_gk.copy()
    df_90s['90s'] = df_90s['Min']/90
    for i in range(10,164):
        df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
    df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
    df_new = df.join(df_90s)

    try:
        for i in range(len(df_new)):
            df_new['Age'][i] = int(df_new['Age'][i][:2])
    except:
        pass

    df_final_gk = df_new.copy()


    ##################################################################################
    ################ Download team data, for possession-adjusting ####################
    ##################################################################################

    standard = "https://fbref.com/en/comps/Big5/stats/squads/Big-5-European-Leagues-Stats"
    poss = "https://fbref.com/en/comps/Big5/possession/squads/Big-5-European-Leagues-Stats"

    df_standard = get_df(standard)
    df_poss = get_df(poss)

    df_standard = df_standard.reset_index(drop=True)
    df_poss = df_poss.reset_index(drop=True)

    ############################################

    df = df_standard.iloc[:, 0:30]

    # Gets the number of touches a team has per 90
    df['TeamTouches90'] = float(0.0)
    for i in range(len(df)):
        df.iloc[i,30] = float(df_poss.iloc[i,5]) / float(df_poss.iloc[i,4])

    # Take out the comma in minutes like above
    for j in range(0,len(df)):
        df.at[j,'Min'] = df.at[j,'Min'].replace(',','')
    df.iloc[:,7:] = df.iloc[:,7:].apply(pd.to_numeric)

    df_final_nongk_teams = df.copy()


    ##################################################################################
    ################ Download opposition data, for possession-adjusting ##############
    ##################################################################################

    opp_poss = "https://fbref.com/en/comps/Big5/possession/squads/Big-5-European-Leagues-Stats"

    df_opp_poss = get_opp_df(opp_poss)
    df_opp_poss = df_opp_poss.reset_index(drop=True)

    ############################################

    df = df_opp_poss.iloc[:, 0:15]
    df = df.rename(columns={'Touches':'Opp Touches'})
    df = df.reset_index()

    #############################################

    df1 = df_final_nongk_teams.copy()

    df1['Opp Touches'] = 1
    for i in range(len(df1)):
        df1['Opp Touches'][i] = df['Opp Touches'][i]
    df1 = df1.rename(columns={'Min':'Team Min'})

    df_final_nongk_teams = df1.copy()

    ##################################################################################
    ################ Make the final, complete, outfield data file ####################
    ##################################################################################

    df = df_final_nongk.copy()
    teams = df_final_nongk_teams.copy()

    df['AvgTeamPoss'] = float(0.0)
    df['OppTouches'] = int(1)
    df['TeamMins'] = int(1)
    df['TeamTouches90'] = float(0.0)

    player_list = list(df['Player'])

    for i in range(len(player_list)):
        team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
        team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
        opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
        team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
        team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
        df.at[i, 'AvgTeamPoss'] = team_poss
        df.at[i, 'OppTouches'] = opp_touch
        df.at[i, 'TeamMins'] = team_mins
        df.at[i, 'TeamTouches90'] = team_touches

    df.iloc[:,9:] = df.iloc[:,9:].astype(float)
    # All of these are the possession-adjusted columns. A couple touch-adjusted ones at the bottom
    df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
    df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
    # df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
    df['Tkl+IntPer600OppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
    df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50
    df['CarriesPer50Touches'] = df['Carries'] / df['Touches'] * 50
    df['ProgCarriesPer50Touches'] = df['ProgCarries'] / df['Touches'] * 50
    df['ProgPassesPer50CmpPasses'] = df['ProgPasses'] / df['PassesCompleted'] * 50


    # Now we'll add the players' actual positions, from @jaseziv, into the file
    tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
    df = pd.merge(df, tm_pos, on ='Player', how ='left')

    for i in range(len(df)):
        if df.Pos[i] == 'GK':
            df['Main Position'][i] = 'Goalkeeper'
    df.to_csv("%s%s.csv" %(root, final_nongk), index=False, encoding='utf-8-sig')


    ##################################################################################
    ################ Make the final, complete, keepers data file #####################
    ##################################################################################

    df = df_final_gk.copy()
    teams = df_final_nongk_teams.copy()

    df['AvgTeamPoss'] = float(0.0)
    df['OppTouches'] = float(0.0)
    df['TeamMins'] = float(0.0)
    df['TeamTouches90'] = float(0.0)

    player_list = list(df['Player'])

    for i in range(len(player_list)):
        team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
        team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
        opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
        team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
        team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
        df.at[i, 'AvgTeamPoss'] = team_poss
        df.at[i, 'OppTouches'] = opp_touch
        df.at[i, 'TeamMins'] = team_mins
        df.at[i, 'TeamTouches90'] = team_touches

    df.iloc[:,9:] = df.iloc[:,9:].astype(float)
    # Same thing, makes pAdj stats for the GK file
    df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
    df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
    df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
    df['Tkl+IntPer600OppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
    df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50
    df['CarriesPer50Touches'] = df['Carries'] / df['Touches'] * 50
    df['ProgCarriesPer50Touches'] = df['ProgCarries'] / df['Touches'] * 50
    df['ProgPassesPer50CmpPasses'] = df['ProgPasses'] / df['PassesCompleted'] * 50


    # Just adding the main positions to the GK too, but of course, they will all be GK lol. Keeps other program variables clean
    tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
    df = pd.merge(df, tm_pos, on ='Player', how ='left')

    for i in range(len(df)):
        if df.Pos[i] == 'GK':
            df['Main Position'][i] = 'Goalkeeper'
    df.to_csv("%s%s.csv" %(root, final_gk), index=False, encoding='utf-8-sig')
    print(f'Done :) Files are located at  %s/Final FBRef {season}.csv' %root)


def scrape_fbref_next12_leagues_players(comps, seasons):
    def _get_table(soup):
        return soup.find_all('table')[0]

    def _get_opp_table(soup):
        return soup.find_all('table')[1]

    def _parse_row(row):
        cols = None
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        return cols

    def _parse_team_row(row):
        cols = None
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        return cols

    def get_players_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        comment = soup.find_all(text=lambda t: isinstance(t, Comment))
        c=0
        for i in range(len(comment)):
            if comment[i].find('\n\n<div class="table_container"') != -1:
                c = i
        a = comment[c]
        tbody = a.find('table')
        sp = BeautifulSoup(a[tbody:], 'html.parser')
        table = _get_table(sp)
        data = []
        headings=[]
        headtext = sp.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(4, 'Comp', [comp]*len(data))
        return data

    def get_team_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[0:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_team_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(1, 'Comp', [comp]*len(data))
        return data


    def get_opp_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_opp_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[0:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_team_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(1, 'Comp', [comp]*len(data))
        return data

    for k in range(len(comps)):
        season = seasons[k]
        comp = comps[k]
        print('Working on %s' %comp)

        raw_nongk = 'Raw FBRef %s - %s' %(season,comp)
        raw_gk = 'Raw FBRef GK %s - %s' %(season,comp)
        final_nongk = 'Final FBRef %s - %s' %(season,comp)
        final_gk = 'Final FBRef GK %s - %s' %(season,comp)

        if comp == 'Liga MX':
            lg_str = 'Liga-MX'
            lg_id = 31
        if comp == 'MLS':
            lg_str = 'Major-League-Soccer'
            lg_id = 22
        if comp == 'Brasileirão':
            lg_str = 'Serie-A'
            lg_id = 24
        if comp == 'Eredivisie':
            lg_str = 'Eredivisie'
            lg_id = 23
        if comp == 'Primeira Liga':
            lg_str = 'Primeira-Liga'
            lg_id = 32
        if comp == 'Championship':
            lg_str = 'Championship'
            lg_id = 10
        if comp == '2. Bundesliga':
            lg_str = '2-Bundesliga'
            lg_id = 33
        if comp == 'Ligue 2':
            lg_str = 'Ligue 2'
            lg_id = 60
        if comp == 'Serie B':
            lg_str = 'Serie-B'
            lg_id = 18
        if comp == 'La Liga 2':
            lg_str = 'Segunda-Division'
            lg_id = 17
        if comp == 'Belgian Pro League':
            lg_str = 'Belgian-Pro-League'
            lg_id = 37
        if comp == 'Argentine Primera División':
            lg_str = 'Primera-Division'
            lg_id = 21
        if comp == 'Copa de la Liga':
            lg_str = 'Copa-de-la-Liga-Profesional'
            lg_id = 905


        # this is the file path root, i.e. where this file is located
        root = str(Path(os.getcwd()).parents[0]).replace('\\','/')+'/'


        # this section gets the raw tables from FBRef.com

        standard = "https://fbref.com/en/comps/%i/stats/%s-Stats" %(lg_id, lg_str)
        shooting = "https://fbref.com/en/comps/%i/shooting/%s-Stats" %(lg_id, lg_str)
        passing = "https://fbref.com/en/comps/%i/passing/players/%s-Stats" %(lg_id, lg_str)
        pass_types = "https://fbref.com/en/comps/%i/passing_types/players/%s-Stats" %(lg_id, lg_str)
        gsca = "https://fbref.com/en/comps/%i/gca/players/%s-Stats" %(lg_id, lg_str)
        defense = "https://fbref.com/en/comps/%i/defense/players/%s-Stats" %(lg_id, lg_str)
        poss = "https://fbref.com/en/comps/%i/possession/players/%s-Stats" %(lg_id, lg_str)
        misc = "https://fbref.com/en/comps/%i/misc/players/%s-Stats" %(lg_id, lg_str)

        df_standard = get_players_df(standard)
        df_shooting = get_players_df(shooting)
        df_passing = get_players_df(passing)
        df_pass_types = get_players_df(pass_types)
        df_gsca = get_players_df(gsca)
        df_defense = get_players_df(defense)
        df_poss = get_players_df(poss)
        df_misc = get_players_df(misc)

        # this section sorts the raw tables then resets their indexes. Without this step, you will
        # run into issues with players who play minutes for 2 clubs in a season.

        df_standard.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_shooting.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_passing.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_pass_types.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_gsca.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_defense.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_poss.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_misc.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

        df_standard = df_standard.reset_index(drop=True)
        df_shooting = df_shooting.reset_index(drop=True)
        df_passing = df_passing.reset_index(drop=True)
        df_pass_types = df_pass_types.reset_index(drop=True)
        df_gsca = df_gsca.reset_index(drop=True)
        df_defense = df_defense.reset_index(drop=True)
        df_poss = df_poss.reset_index(drop=True)
        df_misc = df_misc.reset_index(drop=True)

        # Now the fun part... merging all raw tables into one.
        # Change any column name you want to change:
        # Example --   'Gls': 'Goals'  changes column "Gls" to be named "Goals", etc.
        ## Note that I inclide all columns but don't always change the names... this is useful to me when I need to update the columns, like when FBRef witched to Opta data haha. I got lucky as this made it easier on me!

        df = df_standard.iloc[:, 0:10]
        df = df.join(df_standard.iloc[:, 13])
        df = df.join(df_standard.iloc[:, 26])
        df = df.rename(columns={'G-PK': 'npGoals', 'Gls':'Glsxx'})
        df = df.join(df_shooting.iloc[:,8:25])
        df = df.rename(columns={'Gls': 'Goals', 'Sh': 'Shots', 'SoT': 'SoT', 'SoT%': 'SoT%', 'Sh/90': 'Sh/90', 'SoT/90': 'SoT/90', 'G/Sh': 'G/Sh', 'G/SoT': 'G/SoT', 'Dist': 'AvgShotDistance', 'FK': 'FKShots', 'PK': 'PK', 'PKatt': 'PKsAtt', 'xG': 'xG', 'npxG': 'npxG', 'npxG/Sh': 'npxG/Sh', 'G-xG': 'G-xG', 'np:G-xG': 'npG-xG'})

        df = df.join(df_passing.iloc[:,8:13])
        df = df.rename(columns={'Cmp': 'PassesCompleted', 'Att': 'PassesAttempted', 'Cmp%': 'TotCmp%', 'TotDist': 'TotalPassDist', 'PrgDist': 'ProgPassDist', })
        df = df.join(df_passing.iloc[:,13:16])
        df = df.rename(columns={'Cmp': 'ShortPassCmp', 'Att': 'ShortPassAtt', 'Cmp%': 'ShortPassCmp%', })
        df = df.join(df_passing.iloc[:,16:19])
        df = df.rename(columns={'Cmp': 'MedPassCmp', 'Att': 'MedPassAtt', 'Cmp%': 'MedPassCmp%', })
        df = df.join(df_passing.iloc[:,19:22])
        df = df.rename(columns={'Cmp': 'LongPassCmp', 'Att': 'LongPassAtt', 'Cmp%': 'LongPassCmp%', })
        df = df.join(df_passing.iloc[:,22:31])
        df = df.rename(columns={'Ast': 'Assists', 'xAG':'xAG', 'xA': 'xA', 'A-xAG': 'A-xAG', 'KP': 'KeyPasses', '1/3': 'Final1/3Cmp', 'PPA': 'PenAreaCmp', 'CrsPA': 'CrsPenAreaCmp', 'PrgP': 'ProgPasses', })

        df = df.join(df_pass_types.iloc[:, 9:23])
        df = df.rename(columns={'Live': 'LivePass', 'Dead': 'DeadPass', 'FK': 'FKPasses', 'TB': 'ThruBalls', 'Sw': 'Switches', 'Crs': 'Crs', 'CK': 'CK', 'In': 'InSwingCK', 'Out': 'OutSwingCK', 'Str': 'StrCK', 'TI': 'ThrowIn', 'Off': 'PassesToOff', 'Blocks':'PassesBlocked', 'Cmp':'Cmpxxx'})

        df = df.join(df_gsca.iloc[:, 8:16].rename(columns={'SCA': 'SCA', 'SCA90': 'SCA90', 'PassLive': 'SCAPassLive', 'PassDead': 'SCAPassDead', 'TO': 'SCADrib', 'Sh': 'SCASh', 'Fld': 'SCAFld', 'Def': 'SCADef'}))
        df = df.join(df_gsca.iloc[:, 16:24].rename(columns={'GCA': 'GCA', 'GCA90': 'GCA90', 'PassLive': 'GCAPassLive', 'PassDead': 'GCAPassDead', 'TO': 'GCADrib', 'Sh': 'GCASh', 'Fld': 'GCAFld', 'Def': 'GCADef'}))

        df = df.join(df_defense.iloc[:,8:13].rename(columns={'Tkl': 'Tkl', 'TklW': 'TklWinPoss', 'Def 3rd': 'Def3rdTkl', 'Mid 3rd': 'Mid3rdTkl', 'Att 3rd': 'Att3rdTkl'}))
        df = df.join(df_defense.iloc[:,13:24].rename(columns={'Tkl': 'DrbTkl', 'Att': 'DrbPastAtt', 'Tkl%': 'DrbTkl%', 'Lost': 'DrbPast', 'Blocks': 'Blocks', 'Sh': 'ShBlocks', 'Pass': 'PassBlocks', 'Int': 'Int', 'Tkl+Int': 'Tkl+Int', 'Clr': 'Clr', 'Err': 'Err'}))

        df = df.join(df_poss.iloc[:,8:30])
        df = df.rename(columns={'Touches': 'Touches', 'Def Pen': 'DefPenTouch', 'Def 3rd': 'Def3rdTouch', 'Mid 3rd': 'Mid3rdTouch', 'Att 3rd': 'Att3rdTouch', 'Att Pen': 'AttPenTouch', 'Live': 'LiveTouch', 'Succ': 'SuccDrb', 'Att': 'AttDrb', 'Succ%': 'DrbSucc%', 'Tkld':'TimesTackled', 'Tkld%':'TimesTackled%', 'Carries':'Carries', 'TotDist':'TotalCarryDistance', 'PrgDist':'ProgCarryDistance', 'PrgC':'ProgCarries', '1/3':'CarriesToFinalThird', 'CPA':'CarriesToPenArea', 'Mis': 'CarryMistakes', 'Dis': 'Disposesed', 'Rec': 'ReceivedPass', 'PrgR':'ProgPassesRec'})

        df = df.join(df_misc.iloc[:, 8:14])
        df = df.rename(columns={'CrdY': 'Yellows', 'CrdR': 'Reds', '2CrdY': 'Yellow2', 'Fls': 'Fls', 'Fld': 'Fld', 'Off': 'Off', })
        df = df.join(df_misc.iloc[:,17:24])
        df = df.rename(columns={'PKwon': 'PKwon', 'PKcon': 'PKcon', 'OG': 'OG', 'Recov': 'Recov', 'Won': 'AerialWins', 'Lost': 'AerialLoss', 'Won%': 'AerialWin%', })

        # Make sure to drop all blank rows (FBRef's tables have several)
        df.dropna(subset = ["Player"], inplace=True)

        # Turn the minutes columns to integers. So from '1,500' to '1500'. Otherwise it can't do calculations with minutes
        for i in range(0,len(df)):
            df.iloc[i][9] = df.iloc[i][9].replace(',','')
        df.iloc[:,9:] = df.iloc[:,9:].apply(pd.to_numeric)

        # Save the file to the root location
        df.to_csv("%s%s.csv" %(root, raw_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ############################## GK SECTION ########################################
        ##################################################################################

        gk = "https://fbref.com/en/comps/%i/keepers/players/%s-Stats" %(lg_id, lg_str)
        advgk = "https://fbref.com/en/comps/%i/keepersadv/players/%s-Stats" %(lg_id, lg_str)

        df_gk = get_players_df(gk)
        df_advgk = get_players_df(advgk)

        df_gk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_advgk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

        df_gk = df_gk.reset_index(drop=True)
        df_advgk = df_advgk.reset_index(drop=True)

        ###############################################################################

        df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
        df = df[df['Pos'].str.contains("GK")].reset_index().iloc[:,1:]
        df_gk['Pos'] = df_gk['Pos'].astype(str)
        df_gk = df_gk[df_gk['Pos'].str.contains('GK')]
        df_gk = df_gk.reset_index().iloc[:,1:]
        df_gk = df_gk.rename(columns={'PKatt':'PKsFaced'})

        df = df.join(df_gk.iloc[:, 11:26].astype(float), lsuffix='.1', rsuffix='.2')
        df = df.rename(columns={'GA': 'GA', 'GA90': 'GA90', 'SoTA': 'SoTA', 'Saves': 'Saves', 'Save%.1': 'Save%', 'W': 'W', 'D': 'D', 'L': 'L', 'CS': 'CS', 'CS%': 'CS%', 'PKsFaced': 'PKsFaced', 'PKA': 'PKA', 'PKsv': 'PKsv', 'PKm': 'PKm', 'Save%.2': 'PKSave%', })

        df_advgk['Pos'] = df_advgk['Pos'].astype(str)
        df_advgk = df_advgk[df_advgk['Pos'].str.contains('GK')]
        df_advgk = df_advgk.reset_index().iloc[:,1:]
        df = df.join(df_advgk.iloc[:,9:20].astype(float).rename(columns={'PKA': 'PKGA', 'FK': 'FKGA', 'CK': 'CKGA', 'OG': 'OGA', 'PSxG': 'PSxG', 'PSxG/SoT': 'PSxG/SoT', 'PSxG+/-': 'PSxG+/-', '/90': 'PSxG+/- /90', 'Cmp': 'LaunchCmp', 'Att': 'LaunchAtt', 'Cmp%': 'LaunchPassCmp%'}))
        df = df.join(df_advgk.iloc[:,20:24].astype(float).rename(columns={'Att': 'PassAtt', 'Thr': 'PassThr', 'Launch%': 'PassesLaunch%', 'AvgLen': 'AvgLenLaunch'}))
        df = df.join(df_advgk.iloc[:,24:33].astype(float).rename(columns={'Att': 'GoalKicksAtt', 'Launch%': 'GoalKicksLaunch%', 'AvgLen': 'AvgLen', 'Opp': 'OppCrs', 'Stp': 'StpCrs', 'Stp%': 'CrsStp%', '#OPA': '#OPA', '#OPA/90': '#OPA/90', 'AvgDist': 'AvgDistOPA'}))

        df.to_csv("%s%s.csv" %(root,raw_gk), index=False, encoding = 'utf-8-sig')

        ##################################################################################
        ##################### Final file for outfield data ###############################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
        df_90s = pd.read_csv("%s%s.csv" %(root, raw_nongk))
        df_90s['90s'] = df_90s['Min']/90
        for i in range(10,125):
            df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
        df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
        df_new = df.join(df_90s)

        if comp in ['Liga MX', 'Primeira Liga', 'Eredivisie', 'Championship']:
            for i in range(len(df_new)):
                df_new['Age'][i] = int(df_new['Age'][i][:2])

        df_new.to_csv("%s%s.csv" %(root, final_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ##################### Final file for keeper data #################################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, raw_gk))
        df_90s = pd.read_csv("%s%s.csv" %(root, raw_gk))
        df_90s['90s'] = df_90s['Min']/90
        for i in range(10,164):
            df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
        df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
        df_new = df.join(df_90s)

        if comp in ['Liga MX', 'Primeira Liga', 'Eredivisie', 'Championship']:
            for i in range(len(df_new)):
                df_new['Age'][i] = int(df_new['Age'][i][:2])

        df_new.to_csv("%s%s.csv" %(root, final_gk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ################ Download team data, for possession-adjusting ####################
        ##################################################################################

        standard = "https://fbref.com/en/comps/%i/stats/squads/%s-Stats" %(lg_id, lg_str)
        poss = "https://fbref.com/en/comps/%i/possession/squads/%s-Stats" %(lg_id, lg_str)

        df_standard = get_team_df(standard)
        df_poss = get_team_df(poss)

        df_standard = df_standard.reset_index(drop=True)
        df_poss = df_poss.reset_index(drop=True)

        ############################################

        df = df_standard.iloc[:, 0:30]

        # Gets the number of touches a team has per 90
        df['TeamTouches90'] = float(0.0)
        for i in range(len(df)):
            df.iloc[i,30] = float(df_poss.iloc[i,5]) / float(df_poss.iloc[i,4])

        # Take out the comma in minutes like above
        for j in range(0,len(df)):
            df.at[j,'Min'] = df.at[j,'Min'].replace(',','')
        df.iloc[:,7:] = df.iloc[:,7:].apply(pd.to_numeric)
        df.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ################ Download opposition data, for possession-adjusting ##############
        ##################################################################################

        opp_poss = "https://fbref.com/en/comps/%i/possession/squads/%s-Stats" %(lg_id, lg_str)

        df_opp_poss = get_opp_df(opp_poss)
        df_opp_poss = df_opp_poss.reset_index(drop=True)

        ############################################

        df = df_opp_poss.iloc[:, 0:15]
        df = df.rename(columns={'Touches':'Opp Touches'})
        df = df.reset_index()

        #############################################

        df1 = pd.read_csv("%s%s TEAMS.csv"%(root, final_nongk))

        df1['Opp Touches'] = 1
        for i in range(len(df1)):
            df1['Opp Touches'][i] = df['Opp Touches'][i]
        df1 = df1.rename(columns={'Min':'Team Min'})
        df1.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ################ Make the final, complete, outfield data file ####################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, final_nongk))
        teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

        df['AvgTeamPoss'] = float(0.0)
        df['OppTouches'] = int(1)
        df['TeamMins'] = int(1)
        df['TeamTouches90'] = float(0.0)

        player_list = list(df['Player'])

        for i in range(len(player_list)):
            team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
            team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
            opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
            team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
            team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
            df.at[i, 'AvgTeamPoss'] = team_poss
            df.at[i, 'OppTouches'] = opp_touch
            df.at[i, 'TeamMins'] = team_mins
            df.at[i, 'TeamTouches90'] = team_touches

        df.iloc[:,9:] = df.iloc[:,9:].astype(float)
        # All of these are the possession-adjusted columns. A couple touch-adjusted ones at the bottom
        df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
        df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
        # df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
        df['Tkl+IntPer600OppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
        df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50
        df['CarriesPer50Touches'] = df['Carries'] / df['Touches'] * 50
        df['ProgCarriesPer50Touches'] = df['ProgCarries'] / df['Touches'] * 50
        df['ProgPassesPer50CmpPasses'] = df['ProgPasses'] / df['PassesCompleted'] * 50


        # Now we'll add the players' actual positions, from @jaseziv, into the file
        tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
        df = pd.merge(df, tm_pos, on ='Player', how ='left')

        for i in range(len(df)):
            if df.Pos[i] == 'GK':
                df['Main Position'][i] = 'Goalkeeper'
        df.to_csv("%s%s.csv" %(root, final_nongk), index=False, encoding='utf-8-sig')


        ##################################################################################
        ################ Make the final, complete, keepers data file #####################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, final_gk))
        teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

        df['AvgTeamPoss'] = float(0.0)
        df['OppTouches'] = float(0.0)
        df['TeamMins'] = float(0.0)
        df['TeamTouches90'] = float(0.0)

        player_list = list(df['Player'])

        for i in range(len(player_list)):
            team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
            team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
            opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
            team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
            team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
            df.at[i, 'AvgTeamPoss'] = team_poss
            df.at[i, 'OppTouches'] = opp_touch
            df.at[i, 'TeamMins'] = team_mins
            df.at[i, 'TeamTouches90'] = team_touches

        df.iloc[:,9:] = df.iloc[:,9:].astype(float)
        # Same thing, makes pAdj stats for the GK file
        df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
        df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
        df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
        df['Tkl+IntPer600OppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
        df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50
        df['CarriesPer50Touches'] = df['Carries'] / df['Touches'] * 50
        df['ProgCarriesPer50Touches'] = df['ProgCarries'] / df['Touches'] * 50
        df['ProgPassesPer50CmpPasses'] = df['ProgPasses'] / df['PassesCompleted'] * 50


        # Just adding the main positions to the GK too, but of course, they will all be GK lol. Keeps other program variables clean
        tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
        df = pd.merge(df, tm_pos, on ='Player', how ='left')

        for i in range(len(df)):
            if df.Pos[i] == 'GK':
                df['Main Position'][i] = 'Goalkeeper'
        df.to_csv("%s%s.csv" %(root, final_gk), index=False, encoding='utf-8-sig')

        os.remove(f'{root}{raw_gk}.csv')
        os.remove(f'{root}{raw_nongk}.csv')
        os.remove(f'{root}{final_nongk} TEAMS.csv')

    ### combine all files
    df = pd.DataFrame()
    df_gk = pd.DataFrame()
    for k in range(len(comps)):
        season = seasons[k]
        comp = comps[k]
        
        final_nongk = 'Final FBRef %s - %s' %(season,comp)
        final_gk = 'Final FBRef GK %s - %s' %(season,comp)

        df1 = pd.read_csv(f'{root}{final_nongk}.csv')
        df1_gk = pd.read_csv(f'{root}{final_gk}.csv')

        df = pd.concat([df,df1])
        df_gk = pd.concat([df_gk,df1_gk])
        
        os.remove(f'{root}{final_gk}.csv')
        os.remove(f'{root}{final_nongk}.csv')

    df.to_csv(f'{root}Final FBRef Next 12 Leagues.csv', index=False, encoding='utf-8-sig')
    df_gk.to_csv(f'{root}Final FBRef Next 12 Leagues GK.csv', index=False, encoding='utf-8-sig')

    print('Done :) File named "Final FBRef Next 12 Leagues" is located at  %s' %root)



def combine_t5_next12_fbref(t5_season):
    root = str(Path(os.getcwd()).parents[0]).replace('\\','/')+'/'
    
    t5 = pd.read_csv(f'{root}Final FBRef {t5_season}.csv')
    n12 = pd.read_csv(f'{root}Final FBRef Next 12 Leagues.csv')
    
    df = pd.concat([t5,n12])
    df.to_csv(f'{root}Final FBRef {t5_season}.csv', encoding='utf_8_sig', index=False)
    




def fbref_scout_report(season, program, player_pos, playerPrompt, SquadPrompt, minutesPlayed, compP, saveinput, signature, data_date, fbref_file_path):
    # # Ask what file to use
    ssn = season
    if program == "gk":
        root = fbref_file_path
        final_gk = f'Final FBRef GK {season}' ####################################### INPUT FILE NAME HERE
        path = "%s%s.csv" %(root, final_gk)
    else:
        root = fbref_file_path
        final_nongk = f'Final FBRef {season}' ####################################### INPUT FILE NAME HERE
        path = "%s%s.csv" %(root, final_nongk)


    # Set the default style to white
    sns.set_style("white")

    # Data
    df = pd.read_csv(path)
    df["AerialWin%"] = (df["AerialWins"]/(df["AerialWins"]+df["AerialLoss"]))*100
    df["Dispossessed"] = df["Disposesed"]
    df["DispossessedPer90"] = df["DisposesedPer90"]
    df["PctCmpFinal1/3"] = (df["Final1/3Cmp"]/df["PassesCompleted"])*100
    df["Comp"] = df["Comp"].replace("eng Premier League","Premier League")
    df["Comp"] = df["Comp"].replace("fr Ligue 1","Ligue 1")
    df["Comp"] = df["Comp"].replace("de Bundesliga","Bundesliga")
    df["Comp"] = df["Comp"].replace("it Serie A","Serie A")
    df["Comp"] = df["Comp"].replace("es La Liga","La Liga")
    df['Main Position'].dropna()
    df = df.fillna(0)



    def strikers():
        ##### STRIKERS #####

        f, axes = plt.subplots(3, 4, figsize=(20,10))

        # Filter data
        player = df[df['Player']==playerPrompt]
        dfFilt = df[df['Min']>=minutesPlayed]
        dfFilt = dfFilt[dfFilt['Pos']==player_pos]
#         if ((player_pos == 'Goalkeeper') or
#             (player_pos == 'Centre-Back') or
#             (player_pos == 'Left-Back') or
#             (player_pos == 'Right-Back') or
#             (player_pos == 'Defensive Midfield') or
#             (player_pos == 'Central Midfield') or
#             (player_pos == 'Left Midfield') or
#             (player_pos == 'Right Midfield') or
#             (player_pos == 'Attacking Midfield') or
#             (player_pos == 'Left Winger') or
#             (player_pos == 'Right Winger') or
#             (player_pos == 'Second Striker') or
#             (player_pos == 'Centre-Forward')
#            ):
#             dfFilt = dfFilt[dfFilt['Main Position']==player_pos]
#         if player_pos == 'Fullback':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Left-Back') |
#                             (dfFilt['Main Position']=='Right-Back')]
#         if player_pos == 'Midfielder':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Defensive Midfield') |
#                             (dfFilt['Main Position']=='Central Midfield') |
#                             (dfFilt['Main Position']=='Attacking Midfield')]
#         if player_pos == 'Winger':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Right Midfield') |
#                             (dfFilt['Main Position']=='Left Midfield') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
#         if player_pos == 'Forward':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Centre-Forward') |
#                             (dfFilt['Main Position']=='Second Striker') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
            
        if SquadPrompt != "":
            player = player[player['Squad']==SquadPrompt]
        if compP == "n":
            dfFilt = dfFilt
        else:
            dfFilt = dfFilt[dfFilt['Comp']==compP]
#         if compP == "epl":
#             dfFilt = dfFilt[dfFilt['Comp']=="Premier League"]
#         if compP == "bundesliga":
#             dfFilt = dfFilt[dfFilt['Comp']=="Bundesliga"]
#         if compP == "la liga":
#             dfFilt = dfFilt[dfFilt['Comp']=="La Liga"]
#         if compP == "ligue 1":
#             dfFilt = dfFilt[dfFilt['Comp']=="Ligue 1"]
#         if compP == "serie a":
#             dfFilt = dfFilt[dfFilt['Comp']=="Serie A"]
        Comp = player['Comp'].values[0]

        # Variables to be plotted
        stat1 = "GlsxxPer90"
        stat2 = "npxGPer90"
        stat3 = "AssistsPer90"
        stat4 = "xAPer90"
        stat5 = "DrbSucc%"
        stat6 = "G/SoT"
        stat7 = "SCA90"
        stat8 = "GCA90"
        stat9 = "TouchCentrality"
        stat10 = "ProgPassesPer90"
        stat11 = "Tkl+IntPer90"
        stat12 = "AerialWin%"
        #Get the specific player's value (and name)
        x1 = player[stat1].values[0]
        x2 = player[stat2].values[0]
        x3 = player[stat3].values[0]
        x4 = player[stat4].values[0]
        x5 = player[stat5].values[0]
        x6 = player[stat6].values[0]
        x7 = player[stat7].values[0]
        x8 = player[stat8].values[0]
        x9 = player[stat9].values[0]
        x10 = player[stat10].values[0]
        x11 = player[stat11].values[0]
        x12 = player[stat12].values[0]
        playerName = player["Player"].values[0]
        teamName = player["Squad"].values[0]
        str_age = player["Age"][:2]
        age = str_age.values[0]
        minutes = player['Min'].values[0]

        # Calculate their percentile
        pct1 = stats.percentileofscore(dfFilt[stat1],x1)
        pct2 = stats.percentileofscore(dfFilt[stat2],x2)
        pct3 = stats.percentileofscore(dfFilt[stat3],x3)
        pct4 = stats.percentileofscore(dfFilt[stat4],x4)
        pct5 = stats.percentileofscore(dfFilt[stat5],x5)
        pct6 = stats.percentileofscore(dfFilt[stat6],x6)
        pct7 = stats.percentileofscore(dfFilt[stat7],x7)
        pct8 = stats.percentileofscore(dfFilt[stat8],x8)
        pct9 = stats.percentileofscore(dfFilt[stat9],x9)
        pct10 = stats.percentileofscore(dfFilt[stat10],x10)
        pct11 = stats.percentileofscore(dfFilt[stat11],x11)
        pct12 = stats.percentileofscore(dfFilt[stat12],x12)
        pctMins = stats.percentileofscore(dfFilt['Min'],minutes)

        if pct1 >= 90:
            col = "darkgreen"
        if 70 <= pct1 < 90:
            col = "yellowgreen"
        if 50 <= pct1 < 70:
            col = "darkgrey"
        if 30 <= pct1 < 50:
            col = "orange"
        if 0 <= pct1 < 30:
            col = "red"
        # The plot & player line
        ax1 = sns.kdeplot(dfFilt[stat1], color=col, fill=col, ax=axes[0,0])
        ax1.axvline(x1, 0, .95, lw=2.5, color=col)
        ## Percentile lines
        ax1.set_title("Non-Pen Goals: %.2f\n%i percentile" % (x1, pct1))
        # Clean graph
        ax1.set(xlabel=None)
        ax1.set(ylabel=None)
        ax1.set(yticks=[])

        if pct2 >= 90:
            col = "darkgreen"
        if 70 <= pct2 < 90:
            col = "yellowgreen"
        if 50 <= pct2 < 70:
            col = "darkgrey"
        if 30 <= pct2 < 50:
            col = "orange"
        if 0 <= pct2 < 30:
            col = "red"
        # The plot & player line
        ax2 = sns.kdeplot(dfFilt[stat2], color=col, fill=col, ax=axes[0,1])
        ax2.axvline(x2, 0, .95, lw=2.5, color=col)
        ax2.set_title("npxG: %.2f\n%i percentile" % (x2, pct2))
        # Clean graph
        ax2.set(xlabel=None)
        ax2.set(ylabel=None)
        ax2.set(yticks=[])

        if pct3 >= 90:
            col = "darkgreen"
        if 70 <= pct3 < 90:
            col = "yellowgreen"
        if 50 <= pct3 < 70:
            col = "darkgrey"
        if 30 <= pct3 < 50:
            col = "orange"
        if 0 <= pct3 < 30:
            col = "red"
        # The plot & player line
        ax3 = sns.kdeplot(dfFilt[stat3], color=col, fill=col, ax=axes[0,2])
        ax3.axvline(x3, 0, .95, lw=2.5, color=col)
        ax3.set_title("Assists: %.2f\n%i percentile" % (x3, pct3))
        # Clean graph
        ax3.set(xlabel=None)
        ax3.set(ylabel=None)
        ax3.set(yticks=[])

        if pct4 >= 90:
            col = "darkgreen"
        if 70 <= pct4 < 90:
            col = "yellowgreen"
        if 50 <= pct4 < 70:
            col = "darkgrey"
        if 30 <= pct4 < 50:
            col = "orange"
        if 0 <= pct4 < 30:
            col = "red"
        # The plot & player line
        ax4 = sns.kdeplot(dfFilt[stat4], color=col, fill=col, ax=axes[0,3])
        ax4.axvline(x4, 0, .95, lw=2.5, color=col)
        ax4.set_title("xA: %.2f\n%i percentile" % (x4, pct4))
        # Clean graph
        ax4.set(xlabel=None)
        ax4.set(ylabel=None)
        ax4.set(yticks=[])

        if pct5 >= 90:
            col = "darkgreen"
        if 70 <= pct5 < 90:
            col = "yellowgreen"
        if 50 <= pct5 < 70:
            col = "darkgrey"
        if 30 <= pct5 < 50:
            col = "orange"
        if 0 <= pct5 < 30:
            col = "red"
        # The plot & player line
        ax5 = sns.kdeplot(dfFilt[stat5], color=col, fill=col, ax=axes[1,0])
        ax5.axvline(x5, 0, .95, lw=2.5, color=col)
        ax5.set_title("Dribble Success Pct: %.1f\n%i percentile" % (x5, pct5))
        # Clean graph
        ax5.set(xlabel=None)
        ax5.set(ylabel=None)
        ax5.set(yticks=[])

        if pct6 >= 90:
            col = "darkgreen"
        if 70 <= pct6 < 90:
            col = "yellowgreen"
        if 50 <= pct6 < 70:
            col = "darkgrey"
        if 30 <= pct6 < 50:
            col = "orange"
        if 0 <= pct6 < 30:
            col = "red"
        # The plot & player line
        ax6 = sns.kdeplot(dfFilt[stat6], color=col, fill=col, ax=axes[1,1])
        ax6.axvline(x6, 0, .95, lw=2.5, color=col)
        ax6.set_title("Goals per Shot on Target: %.2f\n%i percentile" % (x6, pct6))
        # Clean graph
        ax6.set(xlabel=None)
        ax6.set(ylabel=None)
        ax6.set(yticks=[])

        if pct7 >= 90:
            col = "darkgreen"
        if 70 <= pct7 < 90:
            col = "yellowgreen"
        if 50 <= pct7 < 70:
            col = "darkgrey"
        if 30 <= pct7 < 50:
            col = "orange"
        if 0 <= pct7 < 30:
            col = "red"
        # The plot & player line
        ax7 = sns.kdeplot(dfFilt[stat7], color=col, fill=col, ax=axes[1,2])
        ax7.axvline(x7, 0, .95, lw=2.5, color=col)
        ax7.set_title("Shot-Creating Actions: %.2f\n%i percentile" % (x7, pct7))
        # Clean graph
        ax7.set(xlabel=None)
        ax7.set(ylabel=None)
        ax7.set(yticks=[])

        if pct8 >= 90:
            col = "darkgreen"
        if 70 <= pct8 < 90:
            col = "yellowgreen"
        if 50 <= pct8 < 70:
            col = "darkgrey"
        if 30 <= pct8 < 50:
            col = "orange"
        if 0 <= pct8 < 30:
            col = "red"
        # The plot & player line
        ax8 = sns.kdeplot(dfFilt[stat8], color=col, fill=col, ax=axes[1,3])
        ax8.axvline(x8, 0, .95, lw=2.5, color=col)
        ax8.set_title("Goal-Creating Actions: %.2f\n%i percentile" % (x8, pct8))
        # Clean graph
        ax8.set(xlabel=None)
        ax8.set(ylabel=None)
        ax8.set(yticks=[])

        if pct9 >= 90:
            col = "darkgreen"
        if 70 <= pct9 < 90:
            col = "yellowgreen"
        if 50 <= pct9 < 70:
            col = "darkgrey"
        if 30 <= pct9 < 50:
            col = "orange"
        if 0 <= pct9 < 30:
            col = "red"
        # The plot & player line
        ax9 = sns.kdeplot(dfFilt[stat9], color=col, fill=col, ax=axes[2,0])
        ax9.axvline(x9, 0, .95, lw=2.5, color=col)
        ax9.set_title("Centrality (pct of squad's touches/90): %.1f%s\n%i percentile" % (x9,'%', pct9))
        # Clean graph
        ax9.set(xlabel=None)
        ax9.set(ylabel=None)
        ax9.set(yticks=[])

        if pct10 >= 90:
            col = "darkgreen"
        if 70 <= pct10 < 90:
            col = "yellowgreen"
        if 50 <= pct10 < 70:
            col = "darkgrey"
        if 30 <= pct10 < 50:
            col = "orange"
        if 0 <= pct10 < 30:
            col = "red"
        # The plot & player line
        ax10 = sns.kdeplot(dfFilt[stat10], color=col, fill=col, ax=axes[2,1])
        ax10.axvline(x10, 0, .95, lw=2.5, color=col)
        ax10.set_title("Progressive Passes: %.1f\n%i percentile" % (x10, pct10))
        # Clean graph
        ax10.set(xlabel=None)
        ax10.set(ylabel=None)
        ax10.set(yticks=[])

        if pct11 >= 90:
            col = "darkgreen"
        if 70 <= pct11 < 90:
            col = "yellowgreen"
        if 50 <= pct11 < 70:
            col = "darkgrey"
        if 30 <= pct11 < 50:
            col = "orange"
        if 0 <= pct11 < 30:
            col = "red"
        # The plot & player line
        ax11 = sns.kdeplot(dfFilt[stat11], color=col, fill=col, ax=axes[2,2])
        ax11.axvline(x11, 0, .95, lw=2.5, color=col)
        ax11.set_title("Tackles & Interceptions: %.1f\n%i percentile" % (x11, pct11))
        # Clean graph
        ax11.set(xlabel=None)
        ax11.set(ylabel=None)
        ax11.set(yticks=[])

        if pct12 >= 90:
            col = "darkgreen"
        if 70 <= pct12 < 90:
            col = "yellowgreen"
        if 50 <= pct12 < 70:
            col = "darkgrey"
        if 30 <= pct12 < 50:
            col = "orange"
        if 0 <= pct12 < 30:
            col = "red"
        # The plot & player line
        ax12 = sns.kdeplot(dfFilt[stat12], color=col, fill=col, ax=axes[2,3])
        ax12.axvline(x12, 0, .95, lw=2.5, color=col)
        ax12.set_title("Aerial Wins Pct: %.1f\n%i percentile" % (x12, pct12))
        # Clean graph
        ax12.set(xlabel=None)
        ax12.set(ylabel=None)
        ax12.set(yticks=[])

        # Finish the graphs
        sns.despine(left=True)
        plt.subplots_adjust(hspace = 1)
#         plt.suptitle('%s (%i, %s, %s) - All values except percentages are per 90 minutes.\n Compared to %s %ss, %i+ minutes | Data from StatsBomb(FBRef) | %s | Code by @BeGriffis'
#                  % (playerName, int(age), teamName, ssn, Comp, player_pos, minutesPlayed, signature),
#                  fontsize=16,
#                 color="#4A2E19", fontweight="bold", fontname="DejaVu Sans")
        plt.style.use("default")
        
        fig = plt.gcf()
        
        fig.patch.set_facecolor('#fbf9f4')
        ax1.set_facecolor('#fbf9f4')
        ax2.set_facecolor('#fbf9f4')
        ax3.set_facecolor('#fbf9f4')
        ax4.set_facecolor('#fbf9f4')
        ax5.set_facecolor('#fbf9f4')
        ax6.set_facecolor('#fbf9f4')
        ax7.set_facecolor('#fbf9f4')
        ax8.set_facecolor('#fbf9f4')
        ax9.set_facecolor('#fbf9f4')
        ax10.set_facecolor('#fbf9f4')
        ax11.set_facecolor('#fbf9f4')
        ax12.set_facecolor('#fbf9f4')
        
        fig.text(0.11, .05,
                   'Red: Bottm 30%',
                   fontsize=10, color='red')
        fig.text(0.28, .05,
                   'Orange: 30th to 50th percentile',
                   fontsize=10, color='darkorange')
        fig.text(0.4625, .05,
                   'Grey: 50th to 70th percentile',
                   fontsize=10, color='darkgrey')
        fig.text(0.6575, .05,
                   'Light Green: 70th to 90th percentile',
                   fontsize=10, color='yellowgreen')
        fig.text(0.845, .05,
                   'Dark Green: Top 10%',
                   fontsize=10, color='darkgreen')
        
        fig.text(0.11,-.01,
                'All values except percentages are per 90 minutes\nCompared to %s %ss, %i+ minutes\nData from Opta via FBRef' %(Comp, player_pos, minutesPlayed),
                fontsize=14, color='#4A2E19', va='top', ha='left')
        fig.text(0.92,-.01,
                '%s\n\nCreated: %s | Code by @BeGriffis' %(data_date, signature),
                fontsize=14, color='#4A2E19', va='top', ha='right')
        
        fig.text(.5,1.0,
                '%s (%i, %s, %s)' %(playerName, int(age), teamName, ssn),
                fontsize=25, color="#4A2E19", fontweight="bold", va='center', ha='center')

        
        fig.set_size_inches(20, 10) #length, height
        if saveinput == "y":
            fig.savefig("%s%s %s fw.png" %(root, playerName, ssn), dpi=220, bbox_inches='tight')
        print("Minutes: %i — %i percentile" %(minutes,pctMins))
        fig = plt.gcf()
        fig.set_size_inches(20, 10) #length, height
        fig

    def midfielders():
        ##### MIDFIELDERS #####

        f, axes = plt.subplots(3, 4, figsize=(30,10))

        # Filter data
        player = df[df['Player']==playerPrompt]
        dfFilt = df[df['Min']>=minutesPlayed]
        dfFilt = dfFilt[dfFilt['Pos'].str.contains(player_pos)]
#         if ((player_pos == 'Goalkeeper') or
#             (player_pos == 'Centre-Back') or
#             (player_pos == 'Left-Back') or
#             (player_pos == 'Right-Back') or
#             (player_pos == 'Defensive Midfield') or
#             (player_pos == 'Central Midfield') or
#             (player_pos == 'Left Midfield') or
#             (player_pos == 'Right Midfield') or
#             (player_pos == 'Attacking Midfield') or
#             (player_pos == 'Left Winger') or
#             (player_pos == 'Right Winger') or
#             (player_pos == 'Second Striker') or
#             (player_pos == 'Centre-Forward')
#            ):
#             dfFilt = dfFilt[dfFilt['Main Position']==player_pos]
#         if player_pos == 'Fullback':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Left-Back') |
#                             (dfFilt['Main Position']=='Right-Back')]
#         if player_pos == 'Midfielder':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Defensive Midfield') |
#                             (dfFilt['Main Position']=='Central Midfield') |
#                             (dfFilt['Main Position']=='Attacking Midfield')]
#         if player_pos == 'Winger':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Right Midfield') |
#                             (dfFilt['Main Position']=='Left Midfield') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
#         if player_pos == 'Forward':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Centre-Forward') |
#                             (dfFilt['Main Position']=='Second Striker') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
            
        if SquadPrompt != "":
            player = player[player['Squad']==SquadPrompt]
        if compP == "n":
            dfFilt = dfFilt
        if compP != "n":
            dfFilt = dfFilt[dfFilt['Comp']==compP]
#         if compP == "epl":
#             dfFilt = dfFilt[dfFilt['Comp']=="Premier League"]
#         if compP == "bundesliga":
#             dfFilt = dfFilt[dfFilt['Comp']=="Bundesliga"]
#         if compP == "la liga":
#             dfFilt = dfFilt[dfFilt['Comp']=="La Liga"]
#         if compP == "ligue 1":
#             dfFilt = dfFilt[dfFilt['Comp']=="Ligue 1"]
#         if compP == "serie a":
#             dfFilt = dfFilt[dfFilt['Comp']=="Serie A"]
        Comp = player['Comp'].values[0]

        # Variables to be plotted
        stat1 = "ShortPassCmp%"
        stat2 = "MedPassCmp%"
        stat3 = "LongPassCmp%"
        stat4 = "KeyPassesPer90"
        stat5 = "xAPer90"
        stat6 = "AssistsPer90"
        stat7 = "SCA90"
        stat8 = "GCA90"
        stat9 = "ProgPassesPer90"
        stat10 = "pAdjIntPer90"
        stat11 = "pAdjDrbTklPer90"
        stat12 = "TouchCentrality"
        
        #Get the specific player's value (and name)
        x1 = player[stat1].values[0]
        x2 = player[stat2].values[0]
        x3 = player[stat3].values[0]
        x4 = player[stat4].values[0]
        x5 = player[stat5].values[0]
        x6 = player[stat6].values[0]
        x7 = player[stat7].values[0]
        x8 = player[stat8].values[0]
        x9 = player[stat9].values[0]
        x10 = player[stat10].values[0]
        x11 = player[stat11].values[0]
        x12 = player[stat12].values[0]
        playerName = player["Player"].values[0]
        teamName = player["Squad"].values[0]
        str_age = player["Age"][:2]
        age = str_age.values[0]
        minutes = player['Min'].values[0]

        # Calculate their percentile
        pct1 = stats.percentileofscore(dfFilt[stat1],x1)
        pct2 = stats.percentileofscore(dfFilt[stat2],x2)
        pct3 = stats.percentileofscore(dfFilt[stat3],x3)
        pct4 = stats.percentileofscore(dfFilt[stat4],x4)
        pct5 = stats.percentileofscore(dfFilt[stat5],x5)
        pct6 = stats.percentileofscore(dfFilt[stat6],x6)
        pct7 = stats.percentileofscore(dfFilt[stat7],x7)
        pct8 = stats.percentileofscore(dfFilt[stat8],x8)
        pct9 = stats.percentileofscore(dfFilt[stat9],x9)
        pct10 = stats.percentileofscore(dfFilt[stat10],x10)
        pct11 = stats.percentileofscore(dfFilt[stat11],x11)
        pct12 = stats.percentileofscore(dfFilt[stat12],x12)
        pctMins = stats.percentileofscore(dfFilt['Min'],minutes)

        if pct1 >= 90:
            col = "darkgreen"
        if 70 <= pct1 < 90:
            col = "yellowgreen"
        if 50 <= pct1 < 70:
            col = "darkgrey"
        if 30 <= pct1 < 50:
            col = "orange"
        if 0 <= pct1 < 30:
            col = "red"
        # The plot & player line
        ax1 = sns.kdeplot(dfFilt[stat1], color=col, fill=col, ax=axes[0,0])
        ax1.axvline(x1, 0, .95, lw=2.5, color=col)
        ## Percentile lines
        ax1.set_title("Short Pass Completion Pct: %.1f\n%i percentile" % (x1, pct1))
        # Clean graph
        ax1.set(xlabel=None)
        ax1.set(ylabel=None)
        ax1.set(yticks=[])

        if pct2 >= 90:
            col = "darkgreen"
        if 70 <= pct2 < 90:
            col = "yellowgreen"
        if 50 <= pct2 < 70:
            col = "darkgrey"
        if 30 <= pct2 < 50:
            col = "orange"
        if 0 <= pct2 < 30:
            col = "red"
        # The plot & player line
        ax2 = sns.kdeplot(dfFilt[stat2], color=col, fill=col, ax=axes[0,1])
        ax2.axvline(x2, 0, .95, lw=2.5, color=col)
        ax2.set_title("Medium Pass Completion Pct: %.1f\n%i percentile" % (x2, pct2))
        # Clean graph
        ax2.set(xlabel=None)
        ax2.set(ylabel=None)
        ax2.set(yticks=[])

        if pct3 >= 90:
            col = "darkgreen"
        if 70 <= pct3 < 90:
            col = "yellowgreen"
        if 50 <= pct3 < 70:
            col = "darkgrey"
        if 30 <= pct3 < 50:
            col = "orange"
        if 0 <= pct3 < 30:
            col = "red"
        # The plot & player line
        ax3 = sns.kdeplot(dfFilt[stat3], color=col, fill=col, ax=axes[0,2])
        ax3.axvline(x3, 0, .95, lw=2.5, color=col)
        ax3.set_title("Long Pass Completion Pct: %.1f\n%i percentile" % (x3, pct3))
        # Clean graph
        ax3.set(xlabel=None)
        ax3.set(ylabel=None)
        ax3.set(yticks=[])

        if pct4 >= 90:
            col = "darkgreen"
        if 70 <= pct4 < 90:
            col = "yellowgreen"
        if 50 <= pct4 < 70:
            col = "darkgrey"
        if 30 <= pct4 < 50:
            col = "orange"
        if 0 <= pct4 < 30:
            col = "red"
        # The plot & player line
        ax4 = sns.kdeplot(dfFilt[stat4], color=col, fill=col, ax=axes[0,3])
        ax4.axvline(x4, 0, .95, lw=2.5, color=col)
        ax4.set_title("Key Passes: %.1f\n%i percentile" % (x4, pct4))
        # Clean graph
        ax4.set(xlabel=None)
        ax4.set(ylabel=None)
        ax4.set(yticks=[])

        if pct5 >= 90:
            col = "darkgreen"
        if 70 <= pct5 < 90:
            col = "yellowgreen"
        if 50 <= pct5 < 70:
            col = "darkgrey"
        if 30 <= pct5 < 50:
            col = "orange"
        if 0 <= pct5 < 30:
            col = "red"
        # The plot & player line
        ax5 = sns.kdeplot(dfFilt[stat5], color=col, fill=col, ax=axes[1,0])
        ax5.axvline(x5, 0, .95, lw=2.5, color=col)
        ax5.set_title("xA: %.2f\n%i percentile" % (x5, pct5))
        # Clean graph
        ax5.set(xlabel=None)
        ax5.set(ylabel=None)
        ax5.set(yticks=[])

        if pct6 >= 90:
            col = "darkgreen"
        if 70 <= pct6 < 90:
            col = "yellowgreen"
        if 50 <= pct6 < 70:
            col = "darkgrey"
        if 30 <= pct6 < 50:
            col = "orange"
        if 0 <= pct6 < 30:
            col = "red"
        # The plot & player line
        ax6 = sns.kdeplot(dfFilt[stat6], color=col, fill=col, ax=axes[1,1])
        ax6.axvline(x6, 0, .95, lw=2.5, color=col)
        ax6.set_title("Assists: %.1f\n%i percentile" % (x6, pct6))
        # Clean graph
        ax6.set(xlabel=None)
        ax6.set(ylabel=None)
        ax6.set(yticks=[])

        if pct7 >= 90:
            col = "darkgreen"
        if 70 <= pct7 < 90:
            col = "yellowgreen"
        if 50 <= pct7 < 70:
            col = "darkgrey"
        if 30 <= pct7 < 50:
            col = "orange"
        if 0 <= pct7 < 30:
            col = "red"
        # The plot & player line
        ax7 = sns.kdeplot(dfFilt[stat7], color=col, fill=col, ax=axes[1,2])
        ax7.axvline(x7, 0, .95, lw=2.5, color=col)
        ax7.set_title("Shot-Creating Actions: %.1f\n%i percentile" % (x7, pct7))
        # Clean graph
        ax7.set(xlabel=None)
        ax7.set(ylabel=None)
        ax7.set(yticks=[])

        if pct8 >= 90:
            col = "darkgreen"
        if 70 <= pct8 < 90:
            col = "yellowgreen"
        if 50 <= pct8 < 70:
            col = "darkgrey"
        if 30 <= pct8 < 50:
            col = "orange"
        if 0 <= pct8 < 30:
            col = "red"
        # The plot & player line
        ax8 = sns.kdeplot(dfFilt[stat8], color=col, fill=col, ax=axes[1,3])
        ax8.axvline(x8, 0, .95, lw=2.5, color=col)
        ax8.set_title("Goal-Creating Actions: %.1f\n%i percentile" % (x8, pct8))
        # Clean graph
        ax8.set(xlabel=None)
        ax8.set(ylabel=None)
        ax8.set(yticks=[])

        if pct9 >= 90:
            col = "darkgreen"
        if 70 <= pct9 < 90:
            col = "yellowgreen"
        if 50 <= pct9 < 70:
            col = "darkgrey"
        if 30 <= pct9 < 50:
            col = "orange"
        if 0 <= pct9 < 30:
            col = "red"
        # The plot & player line
        ax9 = sns.kdeplot(dfFilt[stat9], color=col, fill=col, ax=axes[2,0])
        ax9.axvline(x9, 0, .95, lw=2.5, color=col)
        ax9.set_title("Progressive Passes: %.1f\n%i percentile" % (x9, pct9))
        # Clean graph
        ax9.set(xlabel=None)
        ax9.set(ylabel=None)
        ax9.set(yticks=[])

        if pct10 >= 90:
            col = "darkgreen"
        if 70 <= pct10 < 90:
            col = "yellowgreen"
        if 50 <= pct10 < 70:
            col = "darkgrey"
        if 30 <= pct10 < 50:
            col = "orange"
        if 0 <= pct10 < 30:
            col = "red"
        # The plot & player line
        ax10 = sns.kdeplot(dfFilt[stat10], color=col, fill=col, ax=axes[2,1])
        ax10.axvline(x10, 0, .95, lw=2.5, color=col)
        ax10.set_title("Interceptions (pAdj.): %.1f\n%i percentile" % (x10, pct10))
        # Clean graph
        ax10.set(xlabel=None)
        ax10.set(ylabel=None)
        ax10.set(yticks=[])

        if pct11 >= 90:
            col = "darkgreen"
        if 70 <= pct11 < 90:
            col = "yellowgreen"
        if 50 <= pct11 < 70:
            col = "darkgrey"
        if 30 <= pct11 < 50:
            col = "orange"
        if 0 <= pct11 < 30:
            col = "red"
        # The plot & player line
        ax11 = sns.kdeplot(dfFilt[stat11], color=col, fill=col, ax=axes[2,2])
        ax11.axvline(x11, 0, .95, lw=2.5, color=col)
        ax11.set_title("Tackles (pAdj.): %.1f\n%i percentile" % (x11, pct11))
        # Clean graph
        ax11.set(xlabel=None)
        ax11.set(ylabel=None)
        ax11.set(yticks=[])

        if pct12 >= 90:
            col = "darkgreen"
        if 70 <= pct12 < 90:
            col = "yellowgreen"
        if 50 <= pct12 < 70:
            col = "darkgrey"
        if 30 <= pct12 < 50:
            col = "orange"
        if 0 <= pct12 < 30:
            col = "red"
        # The plot & player line
        ax12 = sns.kdeplot(dfFilt[stat12], color=col, fill=col, ax=axes[2,3])
        ax12.axvline(x12, 0, .95, lw=2.5, color=col)
        ax12.set_title("Centrality (pct of squad's touches/90): %.1f%s\n%i percentile" % (x12, '%',pct12))
        # Clean graph
        ax12.set(xlabel=None)
        ax12.set(ylabel=None)
        ax12.set(yticks=[])

        # Finish the graphs
        sns.despine(left=True)
        plt.subplots_adjust(hspace = 1)
#         plt.suptitle('%s (%i, %s, %s) - All values except percentages are per 90 minutes. pAdj = Possession-Adjusted\n Compared to %s %ss, %i+ minutes | Data from StatsBomb(FBRef) | %s | Code by @BeGriffis'
#                      % (playerName, int(age), teamName, ssn, Comp, player_pos, minutesPlayed, signature),
#                      fontsize=16,
#                     color="#4A2E19", fontweight="bold", fontname="DejaVu Sans")
        plt.style.use("default")
        #f.style.use("Solarize_Light2")

        fig = plt.gcf()
        
        fig.patch.set_facecolor('#fbf9f4')
        ax1.set_facecolor('#fbf9f4')
        ax2.set_facecolor('#fbf9f4')
        ax3.set_facecolor('#fbf9f4')
        ax4.set_facecolor('#fbf9f4')
        ax5.set_facecolor('#fbf9f4')
        ax6.set_facecolor('#fbf9f4')
        ax7.set_facecolor('#fbf9f4')
        ax8.set_facecolor('#fbf9f4')
        ax9.set_facecolor('#fbf9f4')
        ax10.set_facecolor('#fbf9f4')
        ax11.set_facecolor('#fbf9f4')
        ax12.set_facecolor('#fbf9f4')
        
        fig.text(0.11, .05,
                   'Red: Bottm 30%',
                   fontsize=10, color='red')
        fig.text(0.28, .05,
                   'Orange: 30th to 50th percentile',
                   fontsize=10, color='orange')
        fig.text(0.4625, .05,
                   'Grey: 50th to 70th percentile',
                   fontsize=10, color='darkgrey')
        fig.text(0.6575, .05,
                   'Light Green: 70th to 90th percentile',
                   fontsize=10, color='yellowgreen')
        fig.text(0.845, .05,
                   'Dark Green: Top 10%',
                   fontsize=10, color='darkgreen')
        
        fig.text(0.11,-.01,
                'All values except percentages are per 90 minutes\nCompared to %s %ss, %i+ minutes\nData from Opta via FBRef' %(Comp, player_pos, minutesPlayed),
                fontsize=14, color='#4A2E19', va='top', ha='left')
        fig.text(0.92,-.01,
                '%s\n\nCreated: %s | Code by @BeGriffis' %(data_date, signature),
                fontsize=14, color='#4A2E19', va='top', ha='right')
        
        fig.text(.5,1.0,
                '%s (%i, %s, %s)' %(playerName, int(age), teamName, ssn),
                fontsize=25, color="#4A2E19", fontweight="bold", va='center', ha='center')


        fig.set_size_inches(20, 10) #length, height
#         saveinput = input("Save figure? y/n ")
        if saveinput == "y":
            fig.savefig("%s%s %s mf.png" %(root, playerName, ssn), dpi=220, bbox_inches='tight')
        print("Minutes: %i — %i percentile" %(minutes,pctMins))
        fig = plt.gcf()
        fig.set_size_inches(20, 10) #length, height
        fig

    def defenders():
        ##### DEFENDERS #####

        f, axes = plt.subplots(3, 4, figsize=(30,10))

        # Variables to be plotted
        stat1 = "pAdjDrbTklPer90"
        stat2 = "pAdjTklWinPossPer90"
        stat3 = "DrbTkl%"
        stat4 = "Tkl+IntPer600OppTouch"
        stat5 = "pAdjClrPer90"
        stat6 = "pAdjShBlocksPer90"
        stat7 = "pAdjIntPer90"
        stat8 = "AerialWin%"
        stat9 = "LongPassCmp%"
        stat10 = "SCA90"
        stat11 = "ProgPassesPer90"
        stat12 = "TouchCentrality"
        # Filter data
        player = df[df['Player']==playerPrompt]
        dfFilt = df[df['Min']>=minutesPlayed]
        dfFilt = dfFilt[dfFilt['Pos']==player_pos]
#         if ((player_pos == 'Goalkeeper') or
#             (player_pos == 'Centre-Back') or
#             (player_pos == 'Left-Back') or
#             (player_pos == 'Right-Back') or
#             (player_pos == 'Defensive Midfield') or
#             (player_pos == 'Central Midfield') or
#             (player_pos == 'Left Midfield') or
#             (player_pos == 'Right Midfield') or
#             (player_pos == 'Attacking Midfield') or
#             (player_pos == 'Left Winger') or
#             (player_pos == 'Right Winger') or
#             (player_pos == 'Second Striker') or
#             (player_pos == 'Centre-Forward')
#            ):
#             dfFilt = dfFilt[dfFilt['Main Position']==player_pos]
#         if player_pos == 'Fullback':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Left-Back') |
#                             (dfFilt['Main Position']=='Right-Back')]
#         if player_pos == 'Midfielder':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Defensive Midfield') |
#                             (dfFilt['Main Position']=='Central Midfield') |
#                             (dfFilt['Main Position']=='Attacking Midfield')]
#         if player_pos == 'Winger':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Right Midfield') |
#                             (dfFilt['Main Position']=='Left Midfield') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
#         if player_pos == 'Forward':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Centre-Forward') |
#                             (dfFilt['Main Position']=='Second Striker') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
            
        if SquadPrompt != "":
            player = player[player['Squad']==SquadPrompt]
        if compP == "n":
            dfFilt = dfFilt
        else:
            dfFilt = dfFilt[dfFilt['Comp']==compP]
#         if compP == "epl":
#             dfFilt = dfFilt[dfFilt['Comp']=="Premier League"]
#         if compP == "bundesliga":
#             dfFilt = dfFilt[dfFilt['Comp']=="Bundesliga"]
#         if compP == "la liga":
#             dfFilt = dfFilt[dfFilt['Comp']=="La Liga"]
#         if compP == "ligue 1":
#             dfFilt = dfFilt[dfFilt['Comp']=="Ligue 1"]
#         if compP == "serie a":
#             dfFilt = dfFilt[dfFilt['Comp']=="Serie A"]
        Comp = player['Comp'].values[0]

        #Get the specific player's value (and name)
        x1 = player[stat1].values[0]
        x2 = player[stat2].values[0]
        x3 = player[stat3].values[0]
        x4 = player[stat4].values[0]
        x5 = player[stat5].values[0]
        x6 = player[stat6].values[0]
        x7 = player[stat7].values[0]
        x8 = player[stat8].values[0]
        x9 = player[stat9].values[0]
        x10 = player[stat10].values[0]
        x11 = player[stat11].values[0]
        x12 = player[stat12].values[0]
        playerName = player["Player"].values[0]
        teamName = player["Squad"].values[0]
        str_age = player["Age"][:2]
        age = str_age.values[0]
        minutes = player['Min'].values[0]

        # Calculate their percentile
        pct1 = stats.percentileofscore(dfFilt[stat1],x1)
        pct2 = stats.percentileofscore(dfFilt[stat2],x2)
        pct3 = stats.percentileofscore(dfFilt[stat3],x3)
        pct4 = stats.percentileofscore(dfFilt[stat4],x4)
        pct5 = stats.percentileofscore(dfFilt[stat5],x5)
        pct6 = stats.percentileofscore(dfFilt[stat6],x6)
        pct7 = stats.percentileofscore(dfFilt[stat7],x7)
        pct8 = stats.percentileofscore(dfFilt[stat8],x8)
        pct9 = stats.percentileofscore(dfFilt[stat9],x9)
        pct10 = stats.percentileofscore(dfFilt[stat10],x10)
        pct11 = stats.percentileofscore(dfFilt[stat11],x11)
        pct12 = stats.percentileofscore(dfFilt[stat12],x12)
        pctMins = stats.percentileofscore(dfFilt['Min'],minutes)
        

        if pct1 >= 90:
            col = "darkgreen"
        if 70 <= pct1 < 90:
            col = "yellowgreen"
        if 50 <= pct1 < 70:
            col = "darkgrey"
        if 30 <= pct1 < 50:
            col = "orange"
        if 0 <= pct1 < 30:
            col = "red"
        # The plot & player line
        ax1 = sns.kdeplot(dfFilt[stat1], color=col, fill=col, ax=axes[0,0])
        ax1.axvline(x1, 0, .95, lw=2.5, color=col)
        ## Percentile lines
        ax1.set_title("Tackles Won (pAdj.): %.1f\n%i percentile" % (x1, pct1))
        # Clean graph
        ax1.set(xlabel=None)
        ax1.set(ylabel=None)
        ax1.set(yticks=[])

        if pct2 >= 90:
            col = "darkgreen"
        if 70 <= pct2 < 90:
            col = "yellowgreen"
        if 50 <= pct2 < 70:
            col = "darkgrey"
        if 30 <= pct2 < 50:
            col = "orange"
        if 0 <= pct2 < 30:
            col = "red"
        # The plot & player line
        ax2 = sns.kdeplot(dfFilt[stat2], color=col, fill=col, ax=axes[0,1])
        ax2.axvline(x2, 0, .95, lw=2.5, color=col)
        ax2.set_title("Tackles Winning Possession (pAdj.): %.1f\n%i percentile" % (x2, pct2))
        # Clean graph
        ax2.set(xlabel=None)
        ax2.set(ylabel=None)
        ax2.set(yticks=[])

        if pct3 >= 90:
            col = "darkgreen"
        if 70 <= pct3 < 90:
            col = "yellowgreen"
        if 50 <= pct3 < 70:
            col = "darkgrey"
        if 30 <= pct3 < 50:
            col = "orange"
        if 0 <= pct3 < 30:
            col = "red"
        # The plot & player line
        ax3 = sns.kdeplot(dfFilt[stat3], color=col, fill=col, ax=axes[0,2])
        ax3.axvline(x3, 0, .95, lw=2.5, color=col)
        ax3.set_title("Tackle Win Pct: %.1f\n%i percentile" % (x3, pct3))
        # Clean graph
        ax3.set(xlabel=None)
        ax3.set(ylabel=None)
        ax3.set(yticks=[])

        if pct4 >= 90:
            col = "darkgreen"
        if 70 <= pct4 < 90:
            col = "yellowgreen"
        if 50 <= pct4 < 70:
            col = "darkgrey"
        if 30 <= pct4 < 50:
            col = "orange"
        if 0 <= pct4 < 30:
            col = "red"
        # The plot & player line
        ax4 = sns.kdeplot(dfFilt[stat4], color=col, fill=col, ax=axes[0,3])
        ax4.axvline(x4, 0, .95, lw=2.5, color=col)
        ax4.set_title("Tkls & Ints per 600 Opp. Touches: %.1f\n%i percentile" % (x4, pct4))
        # Clean graph
        ax4.set(xlabel=None)
        ax4.set(ylabel=None)
        ax4.set(yticks=[])

        if pct5 >= 90:
            col = "darkgreen"
        if 70 <= pct5 < 90:
            col = "yellowgreen"
        if 50 <= pct5 < 70:
            col = "darkgrey"
        if 30 <= pct5 < 50:
            col = "orange"
        if 0 <= pct5 < 30:
            col = "red"
        # The plot & player line
        ax5 = sns.kdeplot(dfFilt[stat5], color=col, fill=col, ax=axes[1,0])
        ax5.axvline(x5, 0, .95, lw=2.5, color=col)
        ax5.set_title("Clearances (pAdj.): %.1f\n%i percentile" % (x5, pct5))
        # Clean graph
        ax5.set(xlabel=None)
        ax5.set(ylabel=None)
        ax5.set(yticks=[])

        if pct6 >= 90:
            col = "darkgreen"
        if 70 <= pct6 < 90:
            col = "yellowgreen"
        if 50 <= pct6 < 70:
            col = "darkgrey"
        if 30 <= pct6 < 50:
            col = "orange"
        if 0 <= pct6 < 30:
            col = "red"
        # The plot & player line
        ax6 = sns.kdeplot(dfFilt[stat6], color=col, fill=col, ax=axes[1,1])
        ax6.axvline(x6, 0, .95, lw=2.5, color=col)
        ax6.set_title("Shot Blocks (pAdj.): %.1f\n%i percentile" % (x6, pct6))
        # Clean graph
        ax6.set(xlabel=None)
        ax6.set(ylabel=None)
        ax6.set(yticks=[])

        if pct7 >= 90:
            col = "darkgreen"
        if 70 <= pct7 < 90:
            col = "yellowgreen"
        if 50 <= pct7 < 70:
            col = "darkgrey"
        if 30 <= pct7 < 50:
            col = "orange"
        if 0 <= pct7 < 30:
            col = "red"
        # The plot & player line
        ax7 = sns.kdeplot(dfFilt[stat7], color=col, fill=col, ax=axes[1,2])
        ax7.axvline(x7, 0, .95, lw=2.5, color=col)
        ax7.set_title("Interceptions (pAdj.): %.1f\n%i percentile" % (x7, pct7))
        # Clean graph
        ax7.set(xlabel=None)
        ax7.set(ylabel=None)
        ax7.set(yticks=[])

        if pct8 >= 90:
            col = "darkgreen"
        if 70 <= pct8 < 90:
            col = "yellowgreen"
        if 50 <= pct8 < 70:
            col = "darkgrey"
        if 30 <= pct8 < 50:
            col = "orange"
        if 0 <= pct8 < 30:
            col = "red"
        # The plot & player line
        ax8 = sns.kdeplot(dfFilt[stat8], color=col, fill=col, ax=axes[1,3])
        ax8.axvline(x8, 0, .95, lw=2.5, color=col)
        ax8.set_title("Aerial Win Pct: %.1f\n%i percentile" % (x8, pct8))
        # Clean graph
        ax8.set(xlabel=None)
        ax8.set(ylabel=None)
        ax8.set(yticks=[])

        if pct9 >= 90:
            col = "darkgreen"
        if 70 <= pct9 < 90:
            col = "yellowgreen"
        if 50 <= pct9 < 70:
            col = "darkgrey"
        if 30 <= pct9 < 50:
            col = "orange"
        if 0 <= pct9 < 30:
            col = "red"
        # The plot & player line
        ax9 = sns.kdeplot(dfFilt[stat9], color=col, fill=col, ax=axes[2,0])
        ax9.axvline(x9, 0, .95, lw=2.5, color=col)
        ax9.set_title("Long Pass Completion Pct: %.1f\n%i percentile" % (x9, pct9))
        # Clean graph
        ax9.set(xlabel=None)
        ax9.set(ylabel=None)
        ax9.set(yticks=[])

        if pct10 >= 90:
            col = "darkgreen"
        if 70 <= pct10 < 90:
            col = "yellowgreen"
        if 50 <= pct10 < 70:
            col = "darkgrey"
        if 30 <= pct10 < 50:
            col = "orange"
        if 0 <= pct10 < 30:
            col = "red"
        # The plot & player line
        ax10 = sns.kdeplot(dfFilt[stat10], color=col, fill=col, ax=axes[2,1])
        ax10.axvline(x10, 0, .95, lw=2.5, color=col)
        ax10.set_title("Shot-Creating Actions: %.1f\n%i percentile" % (x10, pct10))
        # Clean graph
        ax10.set(xlabel=None)
        ax10.set(ylabel=None)
        ax10.set(yticks=[])

        if pct11 >= 90:
            col = "darkgreen"
        if 70 <= pct11 < 90:
            col = "yellowgreen"
        if 50 <= pct11 < 70:
            col = "darkgrey"
        if 30 <= pct11 < 50:
            col = "orange"
        if 0 <= pct11 < 30:
            col = "red"
        # The plot & player line
        ax11 = sns.kdeplot(dfFilt[stat11], color=col, fill=col, ax=axes[2,2])
        ax11.axvline(x11, 0, .95, lw=2.5, color=col)
        ax11.set_title("Progressive Passes: %.1f\n%i percentile" % (x11, pct11))
        # Clean graph
        ax11.set(xlabel=None)
        ax11.set(ylabel=None)
        ax11.set(yticks=[])

        if pct12 >= 90:
            col = "darkgreen"
        if 70 <= pct12 < 90:
            col = "yellowgreen"
        if 50 <= pct12 < 70:
            col = "darkgrey"
        if 30 <= pct12 < 50:
            col = "orange"
        if 0 <= pct12 < 30:
            col = "red"
        # The plot & player line
        ax12 = sns.kdeplot(dfFilt[stat12], color=col, fill=col, ax=axes[2,3])
        ax12.axvline(x12, 0, .95, lw=2.5, color=col)
        ax12.set_title("Centrality (pct of squad's touches/90): %.1f%s\n%i percentile" % (x12,'%', pct12))
        # Clean graph
        ax12.set(xlabel=None)
        ax12.set(ylabel=None)
        ax12.set(yticks=[])

        # Finish the graphs
        sns.despine(left=True)
        plt.subplots_adjust(hspace = 1)
#         plt.suptitle('%s (%i, %s, %s) - All values except percentages are per 90 minutes. pAdj = Possession-Adjusted\n Compared to %s %ss, %i+ minutes | Data from StatsBomb(FBRef) | Code by @BeGriffis | Created: %s'
#                      % (playerName, int(age), teamName, ssn, Comp, player_pos, minutesPlayed, signature),
#                      fontsize=16,
#                     color="#4A2E19", fontweight="bold", fontname="DejaVu Sans")
        plt.style.use("default")

        fig = plt.gcf()
        
        fig.patch.set_facecolor('#fbf9f4')
        ax1.set_facecolor('#fbf9f4')
        ax2.set_facecolor('#fbf9f4')
        ax3.set_facecolor('#fbf9f4')
        ax4.set_facecolor('#fbf9f4')
        ax5.set_facecolor('#fbf9f4')
        ax6.set_facecolor('#fbf9f4')
        ax7.set_facecolor('#fbf9f4')
        ax8.set_facecolor('#fbf9f4')
        ax9.set_facecolor('#fbf9f4')
        ax10.set_facecolor('#fbf9f4')
        ax11.set_facecolor('#fbf9f4')
        ax12.set_facecolor('#fbf9f4')
        
        fig.text(0.11, .05,
                   'Red: Bottm 30%',
                   fontsize=10, color='red')
        fig.text(0.28, .05,
                   'Orange: 30th to 50th percentile',
                   fontsize=10, color='orange')
        fig.text(0.4625, .05,
                   'Grey: 50th to 70th percentile',
                   fontsize=10, color='darkgrey')
        fig.text(0.6575, .05,
                   'Light Green: 70th to 90th percentile',
                   fontsize=10, color='yellowgreen')
        fig.text(0.845, .05,
                   'Dark Green: Top 10%',
                   fontsize=10, color='darkgreen')
        
        fig.text(0.11,-.01,
                'All values except percentages are per 90 minutes\nCompared to %s %ss, %i+ minutes\nData from Opta via FBRef' %(Comp, player_pos, minutesPlayed),
                fontsize=14, color='#4A2E19', va='top', ha='left')
        fig.text(0.92,-.01,
                '%s\n\nCreated: %s | Code by @BeGriffis' %(data_date, signature),
                fontsize=14, color='#4A2E19', va='top', ha='right')
        
        fig.text(.5,1.0,
                '%s (%i, %s, %s)' %(playerName, int(age), teamName, ssn),
                fontsize=25, color="#4A2E19", fontweight="bold", va='center', ha='center')
        
        fig.set_size_inches(20, 10) #length, height
#         saveinput = input("Save figure? y/n ")
        if saveinput == "y":
            fig.savefig("%s%s %s df.png" %(root, playerName, ssn), dpi=220, bbox_inches='tight')
        print("Minutes: %i — %i percentile" %(minutes,pctMins))
        fig = plt.gcf()
        fig.set_size_inches(20, 10) #length, height
        fig

    def goalkeepers():
        ##### GOALKEEPERS #####

        f, axes = plt.subplots(3, 4, figsize=(30,10))

        # Variables to be plotted
        stat1 = "GAPer90"
        stat2 = "PSxG+/-"
        stat3 = "PSxG/SoT"
        stat4 = "Save%"
        stat5 = "CS%"
        stat6 = "RecovPer90"
        stat7 = "CrsStp%"
        stat8 = "PassAtt"
        stat9 = "LaunchPassCmp%"
        stat10 = "AvgLen"
        stat11 = "#OPA/90"
        stat12 = "AvgDistOPA"
        # Filter data
        player = df[df['Player']==playerPrompt]
        dfFilt = df[df['Min']>=minutesPlayed]
        dfFilt = dfFilt[dfFilt['Pos']==player_pos]
#         if ((player_pos == 'Goalkeeper') or
#             (player_pos == 'Centre-Back') or
#             (player_pos == 'Left-Back') or
#             (player_pos == 'Right-Back') or
#             (player_pos == 'Defensive Midfield') or
#             (player_pos == 'Central Midfield') or
#             (player_pos == 'Left Midfield') or
#             (player_pos == 'Right Midfield') or
#             (player_pos == 'Attacking Midfield') or
#             (player_pos == 'Left Winger') or
#             (player_pos == 'Right Winger') or
#             (player_pos == 'Second Striker') or
#             (player_pos == 'Centre-Forward')
#            ):
#             dfFilt = dfFilt[dfFilt['Main Position']==player_pos]
#         if player_pos == 'Fullback':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Left-Back') |
#                             (dfFilt['Main Position']=='Right-Back')]
#         if player_pos == 'Midfielder':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Defensive Midfield') |
#                             (dfFilt['Main Position']=='Central Midfield') |
#                             (dfFilt['Main Position']=='Attacking Midfield')]
#         if player_pos == 'Winger':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Right Midfield') |
#                             (dfFilt['Main Position']=='Left Midfield') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
#         if player_pos == 'Forward':
#             dfFilt = dfFilt[(dfFilt['Main Position']=='Centre-Forward') |
#                             (dfFilt['Main Position']=='Second Striker') |
#                             (dfFilt['Main Position']=='Left Winger') |
#                             (dfFilt['Main Position']=='Right Winger')]
            
        if SquadPrompt != "":
            player = player[player['Squad']==SquadPrompt]
        if compP == "n":
            dfFilt = dfFilt
        else:
            dfFilt = dfFilt[dfFilt['Comp']==compP]
#         if compP == "epl":
#             dfFilt = dfFilt[dfFilt['Comp']=="Premier League"]
#         if compP == "bundesliga":
#             dfFilt = dfFilt[dfFilt['Comp']=="Bundesliga"]
#         if compP == "la liga":
#             dfFilt = dfFilt[dfFilt['Comp']=="La Liga"]
#         if compP == "ligue 1":
#             dfFilt = dfFilt[dfFilt['Comp']=="Ligue 1"]
#         if compP == "serie a":
#             dfFilt = dfFilt[dfFilt['Comp']=="Serie A"]
        Comp = player['Comp'].values[0]

        #Get the specific player's value (and name)
        x1 = player[stat1].values[0]
        x2 = player[stat2].values[0]
        x3 = player[stat3].values[0]
        x4 = player[stat4].values[0]
        x5 = player[stat5].values[0]
        x6 = player[stat6].values[0]
        x7 = player[stat7].values[0]
        x8 = player[stat8].values[0]
        x9 = player[stat9].values[0]
        x10 = player[stat10].values[0]
        x11 = player[stat11].values[0]
        x12 = player[stat12].values[0]
        playerName = player["Player"].values[0]
        teamName = player["Squad"].values[0]
        str_age = player["Age"][:2]
        age = str_age.values[0]
        minutes = player['Min'].values[0]

        # Calculate their percentile
        pct1 = 100-stats.percentileofscore(dfFilt[stat1],x1)
        pct2 = stats.percentileofscore(dfFilt[stat2],x2)
        pct3 = stats.percentileofscore(dfFilt[stat3],x3)
        pct4 = stats.percentileofscore(dfFilt[stat4],x4)
        pct5 = stats.percentileofscore(dfFilt[stat5],x5)
        pct6 = stats.percentileofscore(dfFilt[stat6],x6)
        pct7 = stats.percentileofscore(dfFilt[stat7],x7)
        pct8 = stats.percentileofscore(dfFilt[stat8],x8)
        pct9 = stats.percentileofscore(dfFilt[stat9],x9)
        pct10 = stats.percentileofscore(dfFilt[stat10],x10)
        pct11 = stats.percentileofscore(dfFilt[stat11],x11)
        pct12 = stats.percentileofscore(dfFilt[stat12],x12)

        if pct1 >= 90:
            col = "darkgreen"
        if 70 <= pct1 < 90:
            col = "yellowgreen"
        if 50 <= pct1 < 70:
            col = "darkgrey"
        if 30 <= pct1 < 50:
            col = "orange"
        if 0 <= pct1 < 30:
            col = "red"
        # The plot & player line
        ax1 = sns.kdeplot(dfFilt[stat1], color=col, fill=col, ax=axes[0,0])
        ax1.axvline(x1, 0, .95, lw=2.5, color=col)
        ax1.set_title("Goals Against: %.1f\n%i percentile" % (x1, pct1))
        # Clean graph
        ax1.set(xlabel=None)
        ax1.set(ylabel=None)
        ax1.set(yticks=[])

        if pct2 >= 90:
            col = "darkgreen"
        if 70 <= pct2 < 90:
            col = "yellowgreen"
        if 50 <= pct2 < 70:
            col = "darkgrey"
        if 30 <= pct2 < 50:
            col = "orange"
        if 0 <= pct2 < 30:
            col = "red"
        # The plot & player line
        ax2 = sns.kdeplot(dfFilt[stat2], color=col, fill=col, ax=axes[0,1])
        ax2.axvline(x2, 0, .95, lw=2.5, color=col)
        ax2.set_title("Post-Shot xG - Goals (not per90): %.2f\n%i percentile" % (x2, pct2))
        # Clean graph
        ax2.set(xlabel=None)
        ax2.set(ylabel=None)
        ax2.set(yticks=[])

        if pct3 >= 90:
            col = "darkgreen"
        if 70 <= pct3 < 90:
            col = "yellowgreen"
        if 50 <= pct3 < 70:
            col = "darkgrey"
        if 30 <= pct3 < 50:
            col = "orange"
        if 0 <= pct3 < 30:
            col = "red"
        # The plot & player line
        ax3 = sns.kdeplot(dfFilt[stat3], color=col, fill=col, ax=axes[0,2])
        ax3.axvline(x3, 0, .95, lw=2.5, color=col)
        ax3.set_title("Post-Shot xG/SoT Faced: %.1f\n%i percentile" % (x3, pct3))
        # Clean graph
        ax3.set(xlabel=None)
        ax3.set(ylabel=None)
        ax3.set(yticks=[])

        if pct4 >= 90:
            col = "darkgreen"
        if 70 <= pct4 < 90:
            col = "yellowgreen"
        if 50 <= pct4 < 70:
            col = "darkgrey"
        if 30 <= pct4 < 50:
            col = "orange"
        if 0 <= pct4 < 30:
            col = "red"
        # The plot & player line
        ax4 = sns.kdeplot(dfFilt[stat4], color=col, fill=col, ax=axes[0,3])
        ax4.axvline(x4, 0, .95, lw=2.5, color=col)
        ax4.set_title("Save Pct: %.1f\n%i percentile" % (x4, pct4))
        # Clean graph
        ax4.set(xlabel=None)
        ax4.set(ylabel=None)
        ax4.set(yticks=[])

        if pct5 >= 90:
            col = "darkgreen"
        if 70 <= pct5 < 90:
            col = "yellowgreen"
        if 50 <= pct5 < 70:
            col = "darkgrey"
        if 30 <= pct5 < 50:
            col = "orange"
        if 0 <= pct5 < 30:
            col = "red"
        # The plot & player line
        ax5 = sns.kdeplot(dfFilt[stat5], color=col, fill=col, ax=axes[1,0])
        ax5.axvline(x5, 0, .95, lw=2.5, color=col)
        ax5.set_title("Clean Sheet Pct: %.1f\n%i percentile" % (x5, pct5))
        # Clean graph
        ax5.set(xlabel=None)
        ax5.set(ylabel=None)
        ax5.set(yticks=[])

        if pct6 >= 90:
            col = "darkgreen"
        if 70 <= pct6 < 90:
            col = "yellowgreen"
        if 50 <= pct6 < 70:
            col = "darkgrey"
        if 30 <= pct6 < 50:
            col = "orange"
        if 0 <= pct6 < 30:
            col = "red"
        # The plot & player line
        ax6 = sns.kdeplot(dfFilt[stat6], color=col, fill=col, ax=axes[1,1])
        ax6.axvline(x6, 0, .95, lw=2.5, color=col)
        ax6.set_title("Loose Ball Recoveries: %.1f\n%i percentile" % (x6, pct6))
        # Clean graph
        ax6.set(xlabel=None)
        ax6.set(ylabel=None)
        ax6.set(yticks=[])

        if pct7 >= 90:
            col = "darkgreen"
        if 70 <= pct7 < 90:
            col = "yellowgreen"
        if 50 <= pct7 < 70:
            col = "darkgrey"
        if 30 <= pct7 < 50:
            col = "orange"
        if 0 <= pct7 < 30:
            col = "red"
        # The plot & player line
        ax7 = sns.kdeplot(dfFilt[stat7], color=col, fill=col, ax=axes[1,2])
        ax7.axvline(x7, 0, .95, lw=2.5, color=col)
        ax7.set_title("Crosses Stopped Pct: %.1f\n%i percentile" % (x7, pct7))
        # Clean graph
        ax7.set(xlabel=None)
        ax7.set(ylabel=None)
        ax7.set(yticks=[])

        if pct8 >= 90:
            col = "darkgreen"
        if 70 <= pct8 < 90:
            col = "yellowgreen"
        if 50 <= pct8 < 70:
            col = "darkgrey"
        if 30 <= pct8 < 50:
            col = "orange"
        if 0 <= pct8 < 30:
            col = "red"
        # The plot & player line
        ax8 = sns.kdeplot(dfFilt[stat8], color=col, fill=col, ax=axes[1,3])
        ax8.axvline(x8, 0, .95, lw=2.5, color=col)
        ax8.set_title("Passes Attempted: %.1f\n%i percentile" % (x8, pct8))
        # Clean graph
        ax8.set(xlabel=None)
        ax8.set(ylabel=None)
        ax8.set(yticks=[])

        if pct9 >= 90:
            col = "darkgreen"
        if 70 <= pct9 < 90:
            col = "yellowgreen"
        if 50 <= pct9 < 70:
            col = "darkgrey"
        if 30 <= pct9 < 50:
            col = "orange"
        if 0 <= pct9 < 30:
            col = "red"
        # The plot & player line
        ax9 = sns.kdeplot(dfFilt[stat9], color=col, fill=col, ax=axes[2,0])
        ax9.axvline(x9, 0, .95, lw=2.5, color=col)
        ax9.set_title("Launched Pass Completion Pct: %.1f\n%i percentile" % (x9, pct9))
        # Clean graph
        ax9.set(xlabel=None)
        ax9.set(ylabel=None)
        ax9.set(yticks=[])

        if pct10 >= 90:
            col = "darkgreen"
        if 70 <= pct10 < 90:
            col = "yellowgreen"
        if 50 <= pct10 < 70:
            col = "darkgrey"
        if 30 <= pct10 < 50:
            col = "orange"
        if 0 <= pct10 < 30:
            col = "red"
        # The plot & player line
        ax10 = sns.kdeplot(dfFilt[stat10], color=col, fill=col, ax=axes[2,1])
        ax10.axvline(x10, 0, .95, lw=2.5, color=col)
        ax10.set_title("Avg Length of Goal Kicks (yds): %.1f\n%i percentile" % (x10, pct10))
        # Clean graph
        ax10.set(xlabel=None)
        ax10.set(ylabel=None)
        ax10.set(yticks=[])

        if pct11 >= 90:
            col = "darkgreen"
        if 70 <= pct11 < 90:
            col = "yellowgreen"
        if 50 <= pct11 < 70:
            col = "darkgrey"
        if 30 <= pct11 < 50:
            col = "orange"
        if 0 <= pct11 < 30:
            col = "red"
        # The plot & player line
        ax11 = sns.kdeplot(dfFilt[stat11], color=col, fill=col, ax=axes[2,2])
        ax11.axvline(x11, 0, .95, lw=2.5, color=col)
        ax11.set_title("Defensive Actions Outside Box: %.2f\n%i percentile" % (x11, pct11))
        # Clean graph
        ax11.set(xlabel=None)
        ax11.set(ylabel=None)
        ax11.set(yticks=[])

        if pct12 >= 90:
            col = "darkgreen"
        if 70 <= pct12 < 90:
            col = "yellowgreen"
        if 50 <= pct12 < 70:
            col = "darkgrey"
        if 30 <= pct12 < 50:
            col = "orange"
        if 0 <= pct12 < 30:
            col = "red"
        # The plot & player line
        ax12 = sns.kdeplot(dfFilt[stat12], color=col, fill=col, ax=axes[2,3])
        ax12.axvline(x12, 0, .95, lw=2.5, color=col)
        ax12.set_title("Avg Dist. of Def. Actions Outside Box (yds): %.1f\n%i percentile" % (x12, pct12))
        # Clean graph
        ax12.set(xlabel=None)
        ax12.set(ylabel=None)
        ax12.set(yticks=[])

        # Finish the graphs
        sns.despine(left=True)
        plt.subplots_adjust(hspace = 1)
#         plt.suptitle('%s (%i, %s, %s) - All values except percentages & distance are per 90 minutes.\n Compared to %s %ss, %i+ minutes | Data from StatsBomb(FBRef) | %s | Code by @BeGriffis'
#                      % (playerName, int(age), teamName, ssn, Comp, player_pos, minutesPlayed, signature),
#                      fontsize=18,
#                     color="#4A2E19", fontweight="bold", fontname="DejaVu Sans")
        plt.style.use("default")

        fig = plt.gcf()
        
        fig.patch.set_facecolor('#fbf9f4')
        ax1.set_facecolor('#fbf9f4')
        ax2.set_facecolor('#fbf9f4')
        ax3.set_facecolor('#fbf9f4')
        ax4.set_facecolor('#fbf9f4')
        ax5.set_facecolor('#fbf9f4')
        ax6.set_facecolor('#fbf9f4')
        ax7.set_facecolor('#fbf9f4')
        ax8.set_facecolor('#fbf9f4')
        ax9.set_facecolor('#fbf9f4')
        ax10.set_facecolor('#fbf9f4')
        ax11.set_facecolor('#fbf9f4')
        ax12.set_facecolor('#fbf9f4')
        
        fig.text(0.11, .05,
                   'Red: Bottm 30%',
                   fontsize=10, color='red')
        fig.text(0.28, .05,
                   'Orange: 30th to 50th percentile',
                   fontsize=10, color='orange')
        fig.text(0.4625, .05,
                   'Grey: 50th to 70th percentile',
                   fontsize=10, color='darkgrey')
        fig.text(0.6575, .05,
                   'Light Green: 70th to 90th percentile',
                   fontsize=10, color='yellowgreen')
        fig.text(0.845, .05,
                   'Dark Green: Top 10%',
                   fontsize=10, color='darkgreen')
        
        fig.text(0.11,-.01,
                'All values except percentages & distance are per 90 minutes\nCompared to %s %ss, %i+ minutes\nData from Opta via FBRef' %(Comp, player_pos, minutesPlayed),
                fontsize=14, color='#4A2E19', va='top', ha='left')
        fig.text(0.92,-.01,
                '%s\n\nCreated: %s | Code by @BeGriffis' %(data_date, signature),
                fontsize=14, color='#4A2E19', va='top', ha='right')
        
        fig.text(.5,1.0,
                '%s (%i, %s, %s)' %(playerName, int(age), teamName, ssn),
                fontsize=25, color="#4A2E19", fontweight="bold", va='center', ha='center')
        
        fig.set_size_inches(20, 10) #length, height
#         saveinput = input("Save figure? y/n ")
        if saveinput == "y":
            fig.savefig("%s%s %s gk.png" %(root, playerName, ssn), dpi=220, bbox_inches='tight')
        print("Minutes: %i" %minutes)
        fig = plt.gcf()
        fig.set_size_inches(20, 10) #length, height
        fig

    def main():
#         qq = input("What program? fw/mf/df/gk ")
        if program == "fw":
            strikers()
        if program == "mf":
            midfielders()
        if program == "df":
            defenders()
        if program == "gk":
            goalkeepers()
    main()
