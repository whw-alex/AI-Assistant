import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

def search(content: str):
    print('start searching...')
    params = {
        'engine': 'bing',
        'q': content,
        'cc': 'US',
        "api_key": "43507bd66a1b56244085de4bb3dd93b80082484b55c53dd2b8e65ab579529178"
    }
    search = GoogleSearch(params)
    if search.get_dict()['organic_results'] and len(search.get_dict()['organic_results'])>0 and search.get_dict()['organic_results'][0]['snippet']:
        results = search.get_dict()['organic_results'][0]['snippet']
    else:
        results='nothing'
    print(results)
    return results


if __name__ == "__main__":
    search("what is chatgpt?")