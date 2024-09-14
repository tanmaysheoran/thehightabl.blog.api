import googlemaps
import os


class Maps:
    __client = None
    __api_key = os.environ.get("GOOGLE_MAPS_KEY")

    def __new__(cls):
        if not cls.__client:
            cls.__client = googlemaps.Client(cls.__api_key)
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        self.client = self.__client

    def autocomplete(self, input_text):
        # Perform autocomplete request
        autocomplete_result = self.client.places_autocomplete(
            input_text, types=['(cities)', '(regions)', '(countries)'])

        # Extract predictions from the result
        predictions = [prediction['description']
                       for prediction in autocomplete_result]

        return predictions