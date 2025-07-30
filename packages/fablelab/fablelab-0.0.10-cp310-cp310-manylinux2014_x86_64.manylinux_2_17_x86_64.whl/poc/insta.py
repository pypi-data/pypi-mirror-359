import requests
import json
from .rest import fetch_with_retry

def hashtag_search(user_id, hashtag, token):
    url = f'https://graph.facebook.com/v22.0/ig_hashtag_search'
    params = {
        'user_id': user_id,
        'q': hashtag,
        'access_token': token
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return [response.json().get('data')[0].get('id'), hashtag]
    except requests.exceptions.RequestException as e:
        print(e)
        return []

def hashtag(hashtag_id, edge, user_id, token):
    url = f'https://graph.facebook.com/v22.0/{hashtag_id}/{edge}'
    params = {
        'user_id': user_id,
        'fields': 'caption,comments_count,id,like_count,media_product_type,media_type,permalink,timestamp',
        'access_token': token
    }
    
    data = fetch_with_retry(url, params=params)
    if data:
        return [[hashtag_id, edge, json.dumps(item)] for item in data.get('data')]
    return []