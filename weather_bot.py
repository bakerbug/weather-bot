import pywemo as wemo
import argparse
from darksky import forecast
from datetime import date, timedelta
from credentials import darksky_key as api_key
from location_data import get_location
from time import time, localtime, sleep, asctime

caution_count = 0
lights = []
alert_hash_list = []
CAUTION_TYPES = ('Tornado Warning', 'Tornado Watch', 'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch')
ALERT_TYPES = ('Tornado Warning',)
LIGHTS_CONTROLLED = ('Sofa Lamp', 'Entry Lamp', 'Bedroom Lamp', 'Sink Light')

# CONFIGURATION #
# Sleep time between polls
SLEEP_CLEAR = (60 * 15)  # Every 15 minutes
SLEEP_STORMY = 60  # Once a minute

def prepare_lights():
    """ Discovers all Wemo lights, and stores data for those to be controlled."""
    global lights

    # Lights are already prepared, don't waste time doing it again.
    if len(lights) >= len(LIGHTS_CONTROLLED):
        return

    discovered_lights = wemo.discover_devices()

    if DEBUG:
        for light in discovered_lights:
            print('Discovered %s' % light.name)

    for light in discovered_lights:
        if light.name in LIGHTS_CONTROLLED and light.name not in lights:
            lights.append(light)

    if DEBUG:
        print('Searching for %i lights.  Found %i' % (len(LIGHTS_CONTROLLED), len(lights)))

def stand_down():
    """Clears discovered information so that the data doesn't become stale."""
    global lights, alert_hash_list
    del lights
    del alert_hash_list


def activate_warning():
    if DEBUG is True:
        print('### TORNADO DETECTED ###')
    for light in lights:
        light.on()
        if DEBUG:
            print('Enabled %s' % light.name)


def check_alerts(alerts):
    """ Inspects weather data for alerts and takes action for certain conditions. """
    global caution_count, alert_hash_list

    new_caution_count = 0
    for alert in alerts:
        if alert['title'] in CAUTION_TYPES:
            new_caution_count += 1
            prepare_lights()
            if DEBUG is True:
                print('Caution Statement %i:  %s' % (new_caution_count, alert['title']))
            if alert['title'] in ALERT_TYPES:
                alert_hash = hash(alert['description'])
                if DEBUG:
                    print('Alert hash: %s' % alert_hash)
                if alert_hash not in alert_hash_list:
                    activate_warning()
                    alert_hash_list.append(alert_hash)
        
        if ALL_OUTPUT is True:
            print(alert['title'])
            print(alert['description'])
            print('##############################')

    if caution_count > 0 and new_caution_count == 0:
        stand_down()
    caution_count = new_caution_count

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
            current_forecast = forecast(api_key, lat, lon, exclude='minutely,hourly')
        else:
            current_forecast = forecast(api_key, lat, lon, exclude='currently,minutely,hourly,daily')
    except:
        print('Unable to retrieve weather data.')
        return None

    if ALL_OUTPUT is True:
        print('Report for: %s' % location)
        temp = str(current_forecast['currently']['temperature']) + u'\N{DEGREE SIGN}' + 'F'
        humidity = str(int(current_forecast['currently']['humidity'] * 100))
        summary = current_forecast['currently']['summary']
        print('Current conditions: %s, %s with %s%% humidity.' % (summary, temp, humidity) )
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
            print('Poll: %i  Cautions: %i at %s.' % (poll_count, caution_count, asctime(now)))

        if RUN_ONCE is True:
            break
        if caution_count > 0:
            sleep(SLEEP_STORMY)
        else:
            sleep(SLEEP_CLEAR)


