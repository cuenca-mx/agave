import json

from agave.tools.asyncio.sqs_client import SqsClient

CORE_QUEUE_REGION = 'us-east-1'


async def test_send_message(sqs_client) -> None:
    data1 = dict(hola='mundo')
    data2 = dict(foo='bar')

    async with SqsClient(sqs_client.queue_url, CORE_QUEUE_REGION) as sqs:
        await sqs.send_message(data1)
        await sqs.send_message(data2, message_group_id='12345')

    sqs_message = await sqs_client.receive_message()
    message = json.loads(sqs_message['Messages'][0]['Body'])
    assert message == data1

    sqs_message = await sqs_client.receive_message()
    message = json.loads(sqs_message['Messages'][0]['Body'])
    assert message == data2


async def test_send_message_async(sqs_client) -> None:
    data1 = dict(hola='mundo')

    async with SqsClient(sqs_client.queue_url, CORE_QUEUE_REGION) as sqs:
        task = sqs.send_message_async(data1)
        await task

    sqs_message = await sqs_client.receive_message()
    message = json.loads(sqs_message['Messages'][0]['Body'])

    assert message == data1
