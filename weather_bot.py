import wemo
from darksky import forecast
from datetime import date, timedelta
from credentials import darksky_key
from location_data import get_location

home_location = 'home'


def tornado_warning():
    print('### TORNADO DETECTED ###')


def check_weather(lat, lon, location):
    weekday = date.today()

    with forecast(darksky_key, lat, lon) as current_forecast:
        print('Report for: ' + location)
        print(current_forecast.daily.summary, end='\n---\n')

        for day in current_forecast.daily:
            day = dict(day=date.strftime(weekday, '%a'),
                       sum=day.summary,
                       tempMin=day.temperatureMin,
                       tempMax=day.temperatureMax
                       )
            print('{day}: {sum} Temp range: {tempMin} - {tempMax}'.format(**day))
            weekday += timedelta(days=1)
        print('---')

        try:
            for alert in current_forecast['alerts']:
                if alert['title'] == 'Tornado Warning':
                    tornado_warning()
                print(alert['title'])
                print(alert['description'])
                print('---')
        except KeyError:
            print('No active weather alerts.')


if __name__ == '__main__':
    current_lat, current_lon, current_name = get_location(home_location)
    check_weather(current_lat, current_lon, current_name)

