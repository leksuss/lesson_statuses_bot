import argparse
import logging
import requests
import telegram
import time
from environs import Env


LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'
RETRY_TIMEOUT = 5  # in seconds
MAX_COUNT_EXCEPTIONS = 3

logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


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


def run_long_polling(chat_id, bot, devman_token, logger):
    timestamp = time.time()
    headers = {
        'Authorization': f"Token {devman_token}",
    }
    count_exceptions = 0
    while True:
        if count_exceptions >= MAX_COUNT_EXCEPTIONS:
            break
        params = {
            'timestamp': timestamp,
        }
        try:
            response = requests.get(
                LONG_POLLING_URL,
                headers=headers,
                params=params,
            )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logger.warning(
                f'Проблемы с сетью, пробуем через {RETRY_TIMEOUT} секунд'
            )
            time.sleep(RETRY_TIMEOUT)
            continue
        except Exception as e:
            logger.exception(e)
            count_exceptions += 1
            continue

        response.raise_for_status()

        user_reviews = response.json()
        if user_reviews['status'] == 'found':
            timestamp = user_reviews['last_attempt_timestamp']
            for attempt in user_reviews['new_attempts']:
                message = f'У вас проверили работу «{attempt["lesson_title"]}»\n\n'
                if attempt['is_negative']:
                    message += f'К сожалению, в работе [нашлись ошибки]({attempt["lesson_url"]})'
                else:
                    message += 'Преподавателю всё понравилось, можно приступать к следующему уроку\!'
                bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='MarkdownV2',
                )


def main():
    env = Env()
    env.read_env()
    devman_token = env('DEVMAN_TOKEN')
    tg_token = env('TG_TOKEN')

    bot = telegram.Bot(token=tg_token)
    args = read_args()

    handler = TelegramLogsHandler(bot, args.chat_id)
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('Бот стартовал')

    run_long_polling(
        args.chat_id,
        bot,
        devman_token,
        logger,
    )

if __name__ == '__main__':
    main()
