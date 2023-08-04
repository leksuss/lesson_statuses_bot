import requests
import time

from environs import Env


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')
    devman_token = env('DEVMAN_TOKEN')

    headers = {
        'Authorization': f'Token {devman_token}',
    }
    timestamp = time.time()
    url = 'https://dvmn.org/api/long_polling/'

    while True:
        params = {
            'timestamp': timestamp,
        }
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=5,
            )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue

        response.raise_for_status()

        response = response.json()
        if response['status'] == 'found':
            timestamp = response['last_attempt_timestamp']
            print(response['new_attempts'])
