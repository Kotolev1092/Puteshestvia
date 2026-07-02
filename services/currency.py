import requests

def get_currency_rates():
    """Возвращает курсы USD и EUR к RUB"""
    try:
        resp = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            usd_to_rub = data['rates'].get('RUB')
        else:
            usd_to_rub = None

        resp_eur = requests.get('https://api.exchangerate-api.com/v4/latest/EUR', timeout=10)
        if resp_eur.status_code == 200:
            eur_to_rub = resp_eur.json()['rates'].get('RUB')
        else:
            eur_to_rub = None

        return {'USD': usd_to_rub, 'EUR': eur_to_rub}
    except Exception as e:
        print(f"Ошибка курсов валют: {e}")
        return None