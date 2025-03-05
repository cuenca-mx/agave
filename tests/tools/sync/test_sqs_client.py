import json

from agave.tools.sync.sqs_client import SqsClient

CORE_QUEUE_REGION = 'us-east-1'


async def test_send_message(sqs_client) -> None:
    data1 = dict(hola='mundo')
    data2 = dict(foo='bar')

    client = SqsClient(sqs_client.queue_url, CORE_QUEUE_REGION)
    client.send_message(data1)
    client.send_message(data2, message_group_id='12345')

    sqs_message = await sqs_client.receive_message()
    message_body = json.loads(sqs_message['Messages'][0]['Body'])
    assert message_body == data1

    sqs_message = await sqs_client.receive_message()
    message = json.loads(sqs_message['Messages'][0]['Body'])
    assert message == data2
