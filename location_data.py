def get_location(place):
    locations = {
        'home': {'lat': 34.718553, 'lon': -86.778150, 'label': 'Madison, AL'},
        'mom': {'lat': 34.807048, 'lon': -92.282116, 'label': 'North Little Rock, AR'},
        'test': {'lat': 35.170850, 'lon': -88.594317, 'label': 'McNairy County in southwestern Tennessee'},
    }

    return locations[place]['lat'], locations[place]['lon'], locations[place]['label']
