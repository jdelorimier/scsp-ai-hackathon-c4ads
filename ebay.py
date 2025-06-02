import requests
import os
import time
import json
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import urllib.parse

# Load the .env file
load_dotenv()

# "PROD" OR "SANDBOX"
ENV = "PROD"

if ENV == "SANDBOX":
    EBAY_CLIENT_ID = os.getenv('EBAY_CLIENT_ID_SANDBOX')
    EBAY_CLIENT_SECRET = os.getenv('EBAY_CLIENT_SECRET_SANDBOX')
    TOKEN_CACHE_FILE = os.getenv('TOKEN_CACHE_FILE_SANDBOX')
    ENDPOINT = os.getenv('ENDPOINT_SANDBOX')
else:
    EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
    EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
    TOKEN_CACHE_FILE = os.getenv("TOKEN_CACHE_FILE")
    ENDPOINT = os.getenv("ENDPOINT")


def get_cached_token():
    if not os.path.exists(TOKEN_CACHE_FILE):
        return None

    with open(TOKEN_CACHE_FILE, 'r') as f:
        data = json.load(f)
        if time.time() < data['expires_at']:
            print("loading cached token")
            return data['access_token']
    return None

def cache_token(token, expires_in):
    data = {
        'access_token': token,
        'expires_at': time.time() + expires_in - 60  # subtract 1 min buffer
    }
    with open(TOKEN_CACHE_FILE, 'w') as f:
        json.dump(data, f)

def get_access_token():
    token = get_cached_token()
    if token:
        return token

    print("Fetching new token...")
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }
    response = requests.post(
        ENDPOINT + "/identity/v1/oauth2/token",
        auth=HTTPBasicAuth(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET),
        headers=headers,
        data=data
    )
    response.raise_for_status()
    json_resp = response.json()
    cache_token(json_resp['access_token'], json_resp['expires_in'])
    return json_resp['access_token']

def search_ebay_products(
        access_token,
        query,
        limit=5,
        filter_list = None,
        sort = None,
        offset = None,
        ):
    """
    Basic Search with filters. See full params in link below
    ref: https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search

    Params
    query (str): string query
    limit (int): number of results to return
    filter_list (str): price:[10..50],priceCurrency:USD (between 10 and 50) or price:[..500] (below 500) or [100] (at or above 100)
    sort (str): Can be any sort field -see docs. e.g. "-price" {highest to lowest} "price" lowest to highest
    offset (int): number of items to offset in list (for pagination?)
    """
    endpoint = f'{ENDPOINT}/buy/browse/v1/item_summary/search'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'  # Adjust for your marketplace
    }
    params = {
        'q': query,
        'limit': limit,
        'filter': filter_list,
        'sort': sort,
    }
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_ebay_item(
        access_token,
        item_id
        ):
    """
    API ref: https://developer.ebay.com/api-docs/buy/browse/resources/item/methods/getItem
    """
    encoded_item_id = urllib.parse.quote(item_id, safe='')
    endpoint = f'{ENDPOINT}/buy/browse/v1/item/{encoded_item_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'  # Adjust for your marketplace
    }

    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()
