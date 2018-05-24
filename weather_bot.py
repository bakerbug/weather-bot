import pywemo as wemo
import argparse
from darksky import forecast
from datetime import date, timedelta
from credentials import darksky_key as api_key
from location_data import get_location
from time import time, localtime, sleep, asctime

active_alerts = 0
lights = []
CAUTION_TYPES = ('Tornado Warning', 'Tornado Watch', 'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch', 'Wind Advisory')
ALERT_TYPES = ('Tornado Warning',)
LIGHTS_CONTROLLED = ('Sofa Lamp', 'Entry Lamp', 'Bedroom Lamp')

# CONFIGURATION #
# Sleep time between polls
SLEEP_CLEAR = (60 * 15)  # Every 15 minutes
SLEEP_STORMY = 60  # Once a minute

def prepare_lights():
    """ Discovers all Wemo lights, and stores data for those to be controlled."""
    global lights

    # Lights are already prepared, don't waste time doing it again.
    if len(lights) > 0:
        return

    discovered_lights = wemo.discover_devices()

    if DEBUG:
        for light in discovered_lights:
            print('Discovered ' + light.name)

    for light in discovered_lights:
        if light.name in LIGHTS_CONTROLLED:
            lights.append(light)

def forget_lights():
    """Clears discovered lights so that the data doesn't become stale."""
    global lights
    del lights


def activate_warning():
    if DEBUG is True:
        print('### TORNADO DETECTED ###')
    for light in lights:
        light.on()
        if DEBUG:
            print('Enabled ' + light.name)


def check_alerts(alerts):
    """ Inspects weather data for alerts and takes action for certain conditions. """
    global active_alerts

    active_alerts = 0
    for alert in alerts:
        if alert['title'] in CAUTION_TYPES:
            active_alerts += 1
            prepare_lights()
            if DEBUG is True:
                print('Alert ' + str(active_alerts) + ':  ' + alert['title'])
            if alert['title'] in ALERT_TYPES:
                activate_warning()
        
        if ALL_OUTPUT is True:
            print(alert['title'])
            print(alert['description'])
            print('##############################')


def get_weather_statements(lat, lon, location):
    """ Fetches the weather data.
    lat:  Latitude coordinates
    lon:  Longitude coordinates
    location:  A description of the location"
    """
    weekday = date.today()

    #with forecast(darksky_key, lat, lon) as current_forecast:
    try:
        if ALL_OUTPUT is True:
            current_forecast = forecast(api_key, lat, lon)
        else:
            current_forecast = forecast(api_key, lat, lon, exclude='currently,minutely,hourly,daily')
    except:
        print('Unable to retrieve weather data.')
        return None

    if ALL_OUTPUT is True:
        print('Report for: ' + location)
        print(current_forecast.daily.summary, end='\n---\n')

        for day in current_forecast.daily:
            day = dict(day=date.strftime(weekday, '%a'),
                       sum=day.summary,
                       tempMin=day.temperatureMin,
                       tempMax=day.temperatureMax
                       )
            print('{day}: {sum} Temp range: {tempMax} - {tempMin}'.format(**day))
            weekday += timedelta(days=1)
        print('---')

    try:
        len(current_forecast['alerts'])
        return current_forecast['alerts']
    except KeyError:
        return None


def arg_parser():
    """ Sets command line arguments as global variables. """
    global DEBUG, RUN_ONCE, ALL_OUTPUT, LOCATION
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--once', help='Only run once', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-l', '--location', type=str, default='home')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    DEBUG = args.debug
    RUN_ONCE = args.once
    ALL_OUTPUT = args.all
    LOCATION = args.location


if __name__ == '__main__':
    poll_count = 0
    arg_parser()

    current_lat, current_lon, current_name = get_location(LOCATION)
    while True:
        weather_statements = get_weather_statements(current_lat, current_lon, current_name)

        if weather_statements is not None:
            check_alerts(weather_statements)

        if DEBUG is True:
            now = localtime(time())
            poll_count += 1
            print('Poll: ' + str(poll_count) + ' Alerts: ' + str(active_alerts) + ' at ' + asctime(now))

        if RUN_ONCE is True:
            break
        if active_alerts > 0:
            sleep(SLEEP_STORMY)
        else:
            sleep(SLEEP_CLEAR)


