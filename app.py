from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

regex = r'^([A-Z]{1,3})\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$'

base_url = 'https://www.google.com'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
}

def mount_url(product, min_price, max_price):
    return f"{base_url}/search?igu=1&hl=en&tbm=shop&psb=1&q={product}&tbs=mr:1,price:1,ppr_min:{min_price},ppr_max:{max_price}"


def get_currency_and_amount(text):
    matches = re.match(regex, text)

    if matches:
        return float(matches.group(2).replace(',', ''))

    return 0


def recursive_scrape(url):
    result = []

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    elements = soup.find_all(class_='HRLxBb')

    if len(elements) == 0:
        print(soup.prettify())
        return result

    next_link = soup.find(class_='lYtaR').get_attribute_list('href')[0]

    for element in soup.find_all(class_='HRLxBb'):
        value = get_currency_and_amount(element.get_text())
        result.append(value)

    # Recursive call to continue scraping next pages
    if next_link:
        result += recursive_scrape(f'{base_url}{next_link}')

    return result


@app.route("/search")
def search():
    product = request.args.get('product')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    url = mount_url(product, min_price, max_price)

    result = recursive_scrape(url)

    if len(result) == 0:
        return { 'message': 'No results found', 'url': url }

    return {'url': url, 'result': result, 'next': f'{base_url}{next}'}
