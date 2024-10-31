class VariablesByTimes:
    def __init__(self, variable, times):
        self.variable = variable
        self.times = times

    @classmethod
    def from_json(cls, json, weather_parameter):
        variable = json['hourly'][weather_parameter]
        times = json['hourly']['time']

        return cls(variable, times)
