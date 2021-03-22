from bs4 import BeautifulSoup
from urllib.request import urlopen

def getBrackets(year):
    pageaddress = 'https://www.sports-reference.com/cbb/postseason/{}-ncaa.html'.format(year)
    soup = BeautifulSoup(urlopen(pageaddress), "html.parser")
    bracketDiv = soup.find_all('div', {'id': 'brackets'})[0]

    regions = bracketDiv.findChildren('div',recursive=False)[0:4]
    regionBrackets = {}
    for region in regions:
        regionBrackets[region.get('id')] = region.find_all('div', {'id': 'bracket'})[0]
    return regionBrackets

brackets2019 = getBrackets(2019)

print(list(brackets2019.keys()))