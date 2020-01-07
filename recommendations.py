import requests
from collections import OrderedDict
import copy
from datetime import datetime

ENDPOINT_BASE = 'https://listening.api.npr.org'


class Recommendations:
    def __init__(self, access_token):
        self.headers = {'Authorization': 'Bearer ' + access_token}
        self.reset()

    def reset(self):
        # Create a list to queue rating objects to send in a batch
        self.ratings = []
        # Cache the upcoming recommended items in a dict
        # Each item's first audio url is the unique id for the item
        # OrderedDict preserves the order of insertion
        self.items = OrderedDict()
        # Get the initial set of recommendations
        r = requests.get(ENDPOINT_BASE + '/v2/recommendations', headers=self.headers)
        # Raise an exception if the GET request was not successful
        r.raise_for_status()
        data = r.json()
        for item_data in data['items']:
            self.items[item_data['links']['audio'][0]['href']] = Item(item_data)

    def get_next_item(self):
        _, item = self.items.popitem(last=False)
        return item

    def rate_item(self, item, event, *args):
        rating = copy.deepcopy(item.data['attributes']['rating'])
        # TODO: Include timezone info at the end of timstamp string
        rating['timestamp'] = str(datetime.now().isoformat(timespec='milliseconds'))
        rating['rating'] = event
        if event == 'START':
            print('Rating is START, elapsed time:', args[0])
            rating['elapsed'] = args[0]
        elif event == 'COMPLETED':
            print('Rating is COMPLETED')
            rating['elapsed'] = rating['duration']

        print('Adding rating object:', rating)
        self.ratings.append(rating)

        if event == 'START':
            # Send all ratings in the ratings queue
            print('POSTing ratings')
            print('Ratings:', self.ratings)
            ratings_endpoint = item.data['links']['recommendations'][0]['href']
            if args[0] > 0:
                ratings_endpoint = item.data['links']['ratings'][0]['href']
            print('Ratings endpoint:', ratings_endpoint)
            r = requests.post(ratings_endpoint, headers=self.headers, json=self.ratings)
            if r.status_code == 200:
                # Ratings POST was successful
                self.ratings = []
                data = r.json()
                if 'items' in data:
                    # Add new items in the recommendations that were not added before
                    for item_data in data['items']:
                        item_url = item_data['links']['audio'][0]['href']
                        if item_url not in self.items:
                            self.items[item_url] = Item(item_data)
            else:
                # Don't empty ratings if POST didn't go through
                print('POST ratings was not successful; keeping ratings list')


class Item:
    def __init__(self, data):
        self.data = data

    def get_audio_uri(self):
        return self.data['links']['audio'][0]['href']
