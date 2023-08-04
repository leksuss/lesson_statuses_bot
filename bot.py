import argparse
import logging
import requests
import telegram
import time
from environs import Env


LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'
RETRY_TIMEOUT = 5  # in seconds


logger = logging.getLogger(__file__)


def read_args():
    parser = argparse.ArgumentParser(
        description='''
            Telegram Bot for notify user about checked lessons on devman.org
        '''
    )
    parser.add_argument(
        '--chat_id',
        required=True,
        type=int,
        help='Telegram User ID'
    )

    args = parser.parse_args()
    return args


def send_message(bot, chat_id, text):
    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode='MarkdownV2',
    )


def run_long_polling(chat_id, bot, devman_token, url, retry_timeout, logger):
    timestamp = time.time()
    headers = {
        'Authorization': f"Token {devman_token}",
    }
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
            logger.warning(
                f'Проблемы с сетью, пробуем через {retry_timeout} секунд'
            )
            time.sleep(retry_timeout)
            continue

        response.raise_for_status()

        response = response.json()
        if response['status'] == 'found':
            timestamp = response['last_attempt_timestamp']
            for attempt in response['new_attempts']:
                message = f'У вас проверили работу «{attempt["lesson_title"]}»\n\n'
                if attempt['is_negative']:
                    message += f'К сожалению, в работе [нашлись ошибки]({attempt["lesson_url"]})'
                    logger.info(f'Работа «{attempt["lesson_title"]}» проверена, есть ошибки')
                else:
                    message += 'Преподавателю всё понравилось, можно приступать к следующему уроку!'
                    logger.info(f'Работа «{attempt["lesson_title"]}» проверена, ошибок нет')
                send_message(bot, chat_id, message)


def main():
    env = Env()
    env.read_env()
    devman_token = env('DEVMAN_TOKEN')
    tg_token = env('TG_TOKEN')

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(message)s'))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    args = read_args()

    bot = telegram.Bot(token=tg_token)

    run_long_polling(
        args.chat_id,
        bot,
        devman_token,
        LONG_POLLING_URL,
        RETRY_TIMEOUT,
        logger,
    )


if __name__ == '__main__':
    main()
