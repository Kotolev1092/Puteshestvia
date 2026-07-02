import os
import requests
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CREDENTIALS_BASE64 = os.getenv('GIGACHAT_API_KEY')
AUTH_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
API_URL = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'

_cached_token = None


def _get_access_token():
    global _cached_token
    if _cached_token:
        return _cached_token

    headers = {
        'Authorization': f'Basic {CREDENTIALS_BASE64}',
        'RqUID': '6f0b1291-c306-4b0f-b2a3-7c1f1e9e6a9d',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {'scope': 'GIGACHAT_API_PERS'}
    try:
        resp = requests.post(AUTH_URL, headers=headers, data=payload, verify=False)
        if resp.status_code == 200:
            _cached_token = resp.json()['access_token']
            return _cached_token
        else:
            raise Exception(f"Ошибка авторизации: {resp.status_code} {resp.text}")
    except Exception as e:
        raise Exception(f"Не удалось получить токен: {str(e)}")

def ask_gigachat(prompt, retry_on_auth_error=True):
    token = _get_access_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    resp = requests.post(API_URL, headers=headers, json=payload, verify=False)
    if resp.status_code == 200:
        return resp.json()['choices'][0]['message']['content']
    elif resp.status_code == 401 and retry_on_auth_error:
        # Токен истёк – сбрасываем кэш и пробуем ещё раз
        global _cached_token
        _cached_token = None
        return ask_gigachat(prompt, retry_on_auth_error=False)
    else:
        return f"Ошибка нейросети: {resp.status_code} {resp.text}"