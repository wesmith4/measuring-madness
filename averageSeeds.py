# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# <a href="https://colab.research.google.com/github/wesmith4/mat210/blob/main/sports/round2seeds.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %%
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
st.set_page_config(layout="wide")
import streamlit.components.v1 as components

roundIndices = {
    "Round of 32": 1,
    "Sweet 16": 2,
    "Elite 8": 3,
    "Final Four": 4
}

pageContainer = st.beta_container()
with pageContainer:
    left_col, right_col = st.beta_columns(2)

with left_col:
    main = st.beta_container()
 
    main.title('Measuring the Madness')
    main.write("Looking at the average seeds of remaining teams in the March Madness tournament.")
    main.markdown("*Note: Data for Elite 8, and Final Four not yet available for 2021.*")

    round = main.radio('Tournament Round', list(roundIndices.keys()),index=0)

# %%
def getWinners(round):
    games = round.findChildren('div', recursive=False)
    
    seeds = []
    for game in games:
        teams = game.findChildren('div', recursive=False)
        for team in teams:
            try:
                seeds.append(int(team.find('span').string))
            except:
                print(team.find('span').string)
    return seeds

def getBrackets(year):
    pageaddress = 'https://www.sports-reference.com/cbb/postseason/{}-ncaa.html'.format(year)
    soup = BeautifulSoup(urlopen(pageaddress), "html.parser")
    bracketDiv = soup.find_all('div', {'id': 'brackets'})[0]

    regions = bracketDiv.findChildren('div',recursive=False)[0:5]
    regionBrackets = {}
    for region in regions:
        regionBrackets[region.get('id')] = region.find_all('div', {'id': 'bracket'})[0]
    return regionBrackets

@st.cache
# %%
def getRoundSeeds(year):
    pageaddress = "https://www.sports-reference.com/cbb/postseason/{}-ncaa.html".format(year)
    soup = BeautifulSoup(urlopen(pageaddress), "html.parser")
    bracketDiv = soup.find_all('div', {'id': 'brackets'})[0]
    print('Finding teams from {}'.format(year))
       
    round32 = []
    for region in range(4):
        bracket = bracketDiv.findChildren('div',recursive=False)[region].find_all('div', {'class': 'round'})[1]
        round32.extend(getWinners(bracket))
    round32 = np.array(round32)

    sweet16 = []
    for region in range(4):
        bracket = bracketDiv.findChildren('div',recursive=False)[region].find_all('div', {'class': 'round'})[2]
        sweet16.extend(getWinners(bracket))
    sweet16 = np.array(sweet16)
    

    elite8 = []
    if year < 2020:
        for region in range(4):
            bracket = bracketDiv.findChildren('div',recursive=False)[region].find_all('div', {'class': 'round'})[3]
            elite8.extend(getWinners(bracket))
        elite8 = np.array(elite8)

    final4 = []
    if year < 2020:
        for region in range(4):
            bracket = bracketDiv.findChildren('div',recursive=False)[region].find_all('div', {'class': 'round'})[4]
            final4.extend(getWinners(bracket))
        final4 = np.array(final4)

    return round32,sweet16,elite8,final4

# %%
roundInd = roundIndices[round]
counter = 0
if round == "Round of 32":
    roundSeeds = np.zeros((32,32))
elif round == "Sweet 16":
    roundSeeds = np.zeros((32,16))
elif round == "Elite 8":
    roundSeeds = np.zeros((32,8))
elif round == "Final Four":
    roundSeeds = np.zeros((32,4))
for year in range(1990,2022):
    if not year == 2020:
        round32,sweet16,elite8,final4 = getRoundSeeds(year)
        if round == "Round of 32":
            roundSeeds[counter] = round32
        elif round == "Sweet 16":
            roundSeeds[counter] = sweet16
        elif round == "Elite 8" and year < 2020:
            roundSeeds[counter] = elite8
        elif round == "Final Four" and year < 2020:
            roundSeeds[counter] = final4
    counter += 1
roundSeeds = roundSeeds.astype(int)


# %%
df = pd.DataFrame(roundSeeds)
means = np.mean(df, axis=1)
variances = np.var(df,axis=1)


# %%
stats = pd.DataFrame(range(1990,2022),columns=['year'])
stats['avg_seed'] = means
stats['variance'] = variances
stats = stats.set_index('year')
stats = stats.drop([2020])

if not (round == 'Round of 32' or round == "Sweet 16"):
    stats = stats.drop([2021])



fig2 = px.scatter(x=stats.index,y=stats.avg_seed,trendline='ols', labels={'x':'Year','y':'Average Seed'})
right_col.write(fig2)
# %%
sortByMean = stats.sort_values(by='avg_seed',ascending=False).head()


# %%
sortByVar = stats.sort_values(by='variance',ascending=False).head()


# %%
with main:
    sideContainer = st.beta_container()
    sideContainer.dataframe(stats)

# sortByMean
# sortByVar

st.markdown('# Bracket Viewer')
spacer,col1,spacer2 = st.beta_columns([1,3,1])
year = col1.slider('Year', min_value=1990, max_value=2021,value=2021,step=1)
regions = getBrackets(year)
if not year == 2021:
    regions['final four'] = regions.pop('national')

region  = col1.radio('Region', list(regions.keys()))

selectedBracket = regions[region]


st.markdown('## {} - {} bracket'.format(year,region))
components.html(selectedBracket.encode('utf-8') + """
    <style>
        body {
            position: relative;
            z-index: 0;
            -webkit-text-size-adjust: none;
            -moz-text-size-adjust: none;
            -ms-text-size-adjust: none;
        }

        .switcher_content>div.current {
            display: block;
        }

        #bracket {
            background-color: #fff;
            padding: 10px;
            width: 98%;
            width: calc(100% - 20px);
            display: flex;
            height: 600px;
            overflow-y: auto;
        }

        #bracket.team4 {
            height: 150px;
        }

        #bracket.team4 .round:nth-child(3) {
            margin-top: 91px;
        }

        #bracket .round {
            display: flex;
            flex-wrap: wrap;
            width: 19%;
            min-width: 220px;
            justify-content: space-between;
        }

        #bracket .round>div {
            width: 100%;
            position: relative;
        }

        #bracket .round>div>div {
            position: absolute;
            bottom: 0;
            padding-bottom: 2px;
            border-right: 1px solid #000;
            border-bottom: 1px solid #000;
            width: 100%;
            height: calc(50% - 2px);
            display: flex;
            align-items: flex-end;
        }

        #bracket .round>div>div:first-child {
            bottom: 50%;
            border-right: 0;
        }

        #bracket .round:nth-child(2) {
            margin-bottom: 19px;
            margin-top: -19px;
        }

        #bracket .round:nth-child(3) {
            margin-bottom: 57px;
            margin-top: -57px;
        }

        #bracket .round:nth-child(4) {
            margin-bottom: 131px;
            margin-top: -131px;
        }

        #bracket .round:nth-child(5) {
            margin-top: 3%;
        }

        #bracket .round>div>div>span {
            width: 20px;
            text-align: right;
            font-weight: bold;
        }

        #bracket .round>div>div>* {
            display: inline-block;
            margin-right: 5px;
            white-space: nowrap;
        }

        #bracket .round>div>div>a+a {
            margin: 0 10px 0 auto;
        }

        #bracket .round>div>span {
            position: absolute;
            color: #555;
            font-size: .785714286em;
            right: 10px;
            bottom: 28%;
        }

        html:not(.backstop) div, html:not(.backstop) span {
            scroll-margin: 2.5em 0 0 0;
            scroll-snap-margin: 2.5em 0 0 0;
        }

    </style>



""".encode('utf-8'), height=1000,width=1200)
