import requests
import time
import telegram

from environs import Env


def send_message(chat_id, text):

    bot.send_message(chat_id=chat_id, text=text)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    bot = telegram.Bot(token=env('TG_TOKEN'))

    headers = {
        'Authorization': f"Token {env('DEVMAN_TOKEN')}",
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
            send_message('Преподаватель проверил работу!')
            # print(response['new_attempts'])
