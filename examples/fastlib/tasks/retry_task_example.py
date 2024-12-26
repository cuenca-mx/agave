import random
from fast_agave.tasks.sqs_tasks import task
from fast_agave.exc import RetryTask


# Esta URL es solo un mock de la queue.
# Debes reemplazarla con la URL de tu queue
QUEUE_URL = 'http://127.0.0.1:4000/123456789012/core.fifo'


class YouCanTryAgain(Exception):
    ...


def test_your_luck(message):
    value = random.uniform(100)
    if 0 < value <= 33:
        print('you are lucky!', message)
    elif 33 < value <= 66:
        raise YouCanTryAgain
    else:
        raise Exception('game over! :(')


@task(queue_url=QUEUE_URL, region_name='us-east-1', max_retries=2)
async def dummy_retry_task(message) -> None:
    try:
        test_your_luck(message)
    except YouCanTryAgain:
        raise RetryTask
