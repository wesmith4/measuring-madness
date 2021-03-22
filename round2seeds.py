# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# <a href="https://colab.research.google.com/github/wesmith4/mat210/blob/main/sports/round2seeds.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %%
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import streamlit as st
import streamlit.components.v1 as components

pageContainer = st.beta_container()
with pageContainer:
    left_col, right_col = st.beta_columns(2)

with left_col:
    main = st.beta_container()
    main.title('Measuring the Madness')
    main.write("Looking at the average seeds of teams that have made the second round.")

# %%
def getWinners(round):
    games = round.findChildren('div', recursive=False)
    
    seeds = []
    for game in games:
        teams = game.findChildren('div', recursive=False)
        for team in teams:
            seeds.append(int(team.find('span').string))
    return seeds

def getBrackets(year):
    pageaddress = 'https://www.sports-reference.com/cbb/postseason/{}-ncaa.html'.format(year)
    soup = BeautifulSoup(urlopen(pageaddress), "html.parser")
    bracketDiv = soup.find_all('div', {'id': 'brackets'})[0]

    regions = bracketDiv.findChildren('div',recursive=False)[0:4]
    regionBrackets = {}
    for region in regions:
        regionBrackets[region.get('id')] = region.find_all('div', {'id': 'bracket'})[0]
    return regionBrackets

@st.cache
# %%
def getRound2Seeds(year):
    pageaddress = "https://www.sports-reference.com/cbb/postseason/{}-ncaa.html".format(year)
    soup = BeautifulSoup(urlopen(pageaddress), "html.parser")
    bracketDiv = soup.find_all('div', {'id': 'brackets'})[0]
    print('Finding teams from {}'.format(year))
       
    allWinners = []
    for region in range(4):
        bracket = bracketDiv.findChildren('div',recursive=False)[region].find_all('div', {'class': 'round'})[1]
        allWinners.extend(getWinners(bracket))
    allWinners = np.array(allWinners)
    
    return allWinners
    


# %%
allRound2Seeds = np.zeros((len(range(1990,2022)),32))
counter = 0
for year in range(1990,2022):
    if not year == 2020:
        allRound2Seeds[counter] = getRound2Seeds(year)
    counter += 1
allRound2Seeds = allRound2Seeds.astype(int)


# %%
df = pd.DataFrame(allRound2Seeds)
means = np.mean(df, axis=1)
variances = np.var(df,axis=1)


# %%
stats = pd.DataFrame(range(1990,2022),columns=['year'])
stats['avg_seed'] = means
stats['variance'] = variances
stats = stats.set_index('year')
stats = stats.drop([2020])


# %%
fig, ax = plt.subplots()
ax.scatter(stats.index, stats.avg_seed)

z = np.polyfit(stats.index, stats.avg_seed, 1)
p = np.poly1d(z)
ax.plot(stats.index,p(stats.index),"r--")
plt.title('Average Seed of 2nd Round Teams')

main.pyplot(fig)

# %%
sortByMean = stats.sort_values(by='avg_seed',ascending=False).head()


# %%
sortByVar = stats.sort_values(by='variance',ascending=False).head()


# %%
with right_col:
    sideContainer = st.beta_container()
    sideContainer.dataframe(stats)

# sortByMean
# sortByVar

st.markdown('# Bracket Viewer')
year = st.slider('Year', min_value=1990, max_value=2021,value=2021,step=1)

regions = getBrackets(year)

region  = st.selectbox('Region', list(regions.keys()))

selectedBracket = regions[region]


st.markdown('## {} - {} bracket'.format(year,region))
components.html(selectedBracket.encode('utf-8') + """
    <style>
        body {
            position: relative;
            background: #c9cbcd;
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
