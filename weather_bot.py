import wemo
import argparse
from darksky import forecast
from datetime import date, timedelta
from credentials import darksky_key
from location_data import get_location
from time import sleep

active_alerts = 0
CAUTION_TYPES = ('Tornado Warning', 'Tornado Watch', 'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch')
ALERT_TYPES = ('Tornado Warning',)

# CONFIGURATION #
home_location = 'home'
sleep_clear = 60
sleep_stormy = 10
debug = False


def activate_warning():
    if args.debug is True:
        print('### TORNADO DETECTED ###')


def monitor_alerts(alerts):
    global active_alerts

    active_alerts = 0
    for alert in alerts:
        if alert['title'] in CAUTION_TYPES:
            active_alerts += 1
            if args.debug is True:
                print('Alert ' + str(active_alerts) + ':  ' + alert['title'])
            if alert['title'] in ALERT_TYPES:
                activate_warning()
        print(alert['title'])
        print(alert['description'])
        print('##############################')


def check_weather(lat, lon, location):
    global active_alerts

    weekday = date.today()

    #with forecast(darksky_key, lat, lon) as current_forecast:
    try:
        current_forecast = forecast(darksky_key, lat, lon)
    except:
        print('Unable to retrieve weather data.')
        return

    if args.all is True:
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
        active_alerts = len(current_forecast['alerts'])
        monitor_alerts(current_forecast['alerts'])
    except KeyError:
        return


if __name__ == '__main__':
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--once', help='Only run once', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-l', '--location', type=str, default='home')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.debug is True:
        poll_count = 0

    current_lat, current_lon, current_name = get_location(args.location)
    while True:
        check_weather(current_lat, current_lon, current_name)

        if args.debug is True:
            poll_count += 1
            print('Poll count: ' + str(poll_count))

        if args.once is True:
            break
        if active_alerts > 0:
            sleep(sleep_stormy)
        else:
            sleep(sleep_clear)


