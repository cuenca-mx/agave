import base64
import json

from agave.tools.asyncio.sqs_celery_client import SqsCeleryClient

CORE_QUEUE_REGION = 'us-east-1'


async def test_send_task(sqs_client) -> None:
    args = [10, 'foo']
    kwargs = dict(hola='mundo')
    queue = SqsCeleryClient(sqs_client.queue_url, CORE_QUEUE_REGION)
    await queue.start()

    await queue.send_task('some.task', args=args, kwargs=kwargs)
    sqs_message = await sqs_client.receive_message()
    encoded_body = sqs_message['Messages'][0]['Body']
    message = json.loads(
        base64.b64decode(encoded_body.encode('utf-8')).decode()
    )
    body_json = json.loads(
        base64.b64decode(message['body'].encode('utf-8')).decode()
    )

    assert body_json[0] == args
    assert body_json[1] == kwargs
    assert message['headers']['lang'] == 'py'
    assert message['headers']['task'] == 'some.task'
    await queue.close()


async def test_send_background_task(sqs_client) -> None:
    args = [10, 'foo']
    kwargs = dict(hola='mundo')
    queue = SqsCeleryClient(sqs_client.queue_url, CORE_QUEUE_REGION)
    await queue.start()

    assert len(queue.background_tasks) == 0

    task = queue.send_background_task('some.task', args=args, kwargs=kwargs)
    await task
    sqs_message = await sqs_client.receive_message()
    encoded_body = sqs_message['Messages'][0]['Body']
    message = json.loads(
        base64.b64decode(encoded_body.encode('utf-8')).decode()
    )
    body_json = json.loads(
        base64.b64decode(message['body'].encode('utf-8')).decode()
    )

    assert body_json[0] == args
    assert body_json[1] == kwargs
    assert message['headers']['lang'] == 'py'
    assert message['headers']['task'] == 'some.task'
    await queue.close()
    assert len(queue.background_tasks) == 0
