def get_location(place='home'):
    locations = {
        'home': {'lat': 34.718553, 'lon': -86.778150, 'label': 'Madison, AL'},
        'mom': {'lat': 34.807048, 'lon': -92.282116, 'label': 'North Little Rock, AR'},
        'test': {'lat': 31.097370, 'lon': -87.872430, 'label': 'Some random place with interesting weather'},
    }

    lat = locations[place]['lat']
    lon = locations[place]['lon']
    label = locations[place]['label']

    return lat, lon, label
