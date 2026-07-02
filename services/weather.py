import os
import requests
from collections import defaultdict
from datetime import datetime, timedelta

def get_weather(city_name, days=7):
    # сначала Open-Meteo
    weather = _get_weather_open_meteo(city_name, days)
    if weather:
        return weather
    # если не вышло – OpenWeatherMap
    return _get_weather_openweathermap(city_name, days)

def _get_weather_open_meteo(city_name, days):
    try:
        geo_url = 'https://geocoding-api.open-meteo.com/v1/search'
        geo_params = {'name': city_name, 'count': 1, 'language': 'ru', 'format': 'json'}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        if geo_resp.status_code != 200 or 'results' not in geo_resp.json():
            return None
        results = geo_resp.json()['results']
        if not results:
            return None
        lat = results[0]['latitude']
        lon = results[0]['longitude']

        weather_url = 'https://api.open-meteo.com/v1/forecast'
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'daily': ['temperature_2m_max', 'weathercode'],
            'timezone': 'auto',
            'forecast_days': days
        }
        w_resp = requests.get(weather_url, params=weather_params, timeout=10)
        if w_resp.status_code != 200:
            return None
        w_data = w_resp.json()
        daily = w_data['daily']
        dates = daily['time']
        temps = daily['temperature_2m_max']
        codes = daily['weathercode']

        def code_to_info(code):
            if code in (0,): return 'ясно', '01d'
            elif code in (1,2,3): return 'переменная облачность', '03d'
            elif code in (45,48): return 'туман', '50d'
            elif code in (51,53,55): return 'морось', '09d'
            elif code in (61,63,65): return 'дождь', '10d'
            elif code in (71,73,75): return 'снег', '13d'
            elif code in (80,81,82): return 'ливень', '09d'
            elif code in (95,96,99): return 'гроза', '11d'
            else: return 'облачно', '04d'

        forecast = []
        for i in range(len(dates)):
            dt = datetime.strptime(dates[i], '%Y-%m-%d')
            rus_date = dt.strftime('%d.%m.%Y')
            desc, icon = code_to_info(codes[i])
            forecast.append({
                'date': rus_date,
                'temp': round(temps[i], 1),
                'description': desc,
                'icon': icon
            })
        return forecast
    except Exception as e:
        print(f"Open-Meteo error: {e}")
        return None

def _get_weather_openweathermap(city_name, days):
    API_KEY = os.getenv('WEATHER_API_KEY')
    BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        forecast_by_day = defaultdict(list)
        for entry in data['list']:
            date_str = entry['dt_txt'].split(' ')[0]
            forecast_by_day[date_str].append({
                'time': entry['dt_txt'],
                'temp': entry['main']['temp'],
                'description': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon']
            })
        daily_forecast = []
        for date, entries in forecast_by_day.items():
            midday = next((e for e in entries if '12:00:00' in e['time']), entries[0])
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            rus_date = date_obj.strftime('%d.%m.%Y')
            daily_forecast.append({
                'date': rus_date,
                'temp': round(midday['temp'], 1),
                'description': midday['description'],
                'icon': midday['icon']
            })
        return daily_forecast[:days]
    except Exception as e:
        print(f"OpenWeatherMap error: {e}")
        return None