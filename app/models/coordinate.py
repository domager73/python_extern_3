class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    @classmethod
    def from_json(cls, json_data):
        latitude = json_data['results'][0]['latitude']
        longitude = json_data['results'][0]['longitude']
        return cls(latitude, longitude)
