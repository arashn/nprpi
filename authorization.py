import requests
from time import sleep
from pathlib import Path
import logging

ENDPOINT_BASE = 'https://authorization.api.npr.org'

logger = logging.Logger('nprpi')


class Authorization:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self):
        p = Path('/tmp/nprpi_access_token')
        if p.is_file():
            with open(p) as f:
                return f.readline().strip()
        else:
            token = self.get_new_token()
            if token is not None:
                with open(p, 'w') as f:
                    f.write(token['access_token'])
                return token['access_token']
            raise Exception('Failed to get new token')

    def get_new_token(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'identity.readonly identity.write listening.readonly listening.write'
        }
        r = requests.post(ENDPOINT_BASE + '/v2/device', params)
        r.raise_for_status()
        data = r.json()
        logger.debug('URL: {}, code: {}'.format(data['verification_uri'], data['user_code']))
        while True:
            sleep(data['interval'])
            params = {
                'grant_type': 'device_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': data['device_code'],
                'scope': 'identity.readonly identity.write listening.readonly listening.write',
                'token_type_hint': 'access_token'
            }

            res = requests.post(ENDPOINT_BASE + '/v2/token', params)
            token = res.json()
            if 'error' in token:
                if token['error'] != 'authorization_pending':
                    return None
                logger.debug('Waiting for user authorization')
            else:
                if 'access_token' not in token:
                    raise Exception('Access token does not exist in response')
                logger.debug('Got user authorization')
                return token
