# instructions...
# run: 
#   $ python3.10 _search_cache_filter
# input: # input example...
#   site:twitter.com ("@" OR "cryptocurrency" OR "DeFi" OR "blockchain" OR "NFT" OR "Ethereum" OR "Bitcoin" OR "altcoins") ("founder" OR "investor" OR "trader" OR "meme" OR "pulsechain") -filter:replies

import requests
from bs4 import BeautifulSoup

def search_duckduckgo(query):
    url = 'https://duckduckgo.com/html/'
    params = {
        'q': query
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, params=params, headers=headers)
    # if response.status_code == 200 or response.status_code == 202:
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('a', class_='result__a')
        for result in results:
            # print(result.get_text(), result['href'])
            txt = result.get_text(), result['href']
            for c in txt:
                print(c, flush=False)
                # print(c)
        # for result in results:
        #     title = result.find('a', class_='result__a').get_text()
        #     url = result.find('a', class_='result__a')['href']
        #     snippet = result.find('a', class_='result__snippet').get_text() if result.find('a', class_='result__snippet') else 'No snippet available'
        #     print(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    query = input("Enter search query: ")
    search_duckduckgo(query)

