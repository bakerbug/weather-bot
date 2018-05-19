def get_location(place='home'):
    locations = {
        'home': {'lat': 34.718553, 'lon': -86.778150, 'label': 'Madison, AL'},
        'mom': {'lat': 34.807048, 'lon': -92.282116, 'label': 'North Little Rock, AR'},
        'test': {'lat': 35.745894, 'lon': -89.531717, 'label': 'Some random place with interesting weather'},
    }

    try:
        lat = locations[place]['lat']
        lon = locations[place]['lon']
        label = locations[place]['label']
    except KeyError:
        print('*** Location not recognized. ***')
        exit()

    return lat, lon, label
