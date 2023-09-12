import requests
from bs4 import BeautifulSoup

def fetch(url: str):
    print('start fetching...')
    fetch_results = requests.get(url)
    content = fetch_results.text
    soup = BeautifulSoup(content, 'html.parser')
    processed_results = soup.select('#what-is-qweather-develop-service + p')[0].get_text()
    return processed_results



if __name__ == "__main__":
    fetch("https://dev.qweather.com/en/help")