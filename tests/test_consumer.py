import pytest
from collections import namedtuple


async def test_authorized_consumer_connect(
    authorized_consumer,
    accept_consumer_mocker,
    close_consumer_mocker,
):
    await authorized_consumer.connect()
    accept_consumer_mocker.assert_called_once()
    close_consumer_mocker.assert_not_called()


async def test_unauthorized_consumer_connect(
    unauthorized_consumer,
    accept_consumer_mocker,
    close_consumer_mocker,
):
    await unauthorized_consumer.connect()
    accept_consumer_mocker.assert_not_called()
    close_consumer_mocker.assert_called_once()


@pytest.mark.parametrize(
    "consumer_slug, geodata_result, geodata_status, json_request, response",
    [
        (
            "USER1",
            None,
            "PROGRESS",
            {"task_id": "TASK1"},
            {"status": "PROGRESS", "response": {"data": "None"}},
        ),
        (
            "USER2",
            None,
            "PROGRESS",
            {"task_id": "TASK1"},
            {"status": "PENDING", "response": {"data": "None"}},
        ),
        (
            "USER1",
            None,
            "PROGRESS",
            {"bad_field": "TASK2"},
            {
                "status": "REQUEST_ERROR",
                "response": {
                    "task_id": [
                        "This field is required.",
                    ]
                },
            },
        ),
    ],
)
async def test_consumer_response(
    authorized_consumer,
    send_consumer_mocker,
    accept_consumer_mocker,
    geodata_result_mocker,
    consumer_slug,
    geodata_result,
    geodata_status,
    json_request,
    response,
):
    AsyncResult = namedtuple("AsyncResult", ["args", "status", "result"])
    geodata_result_mocker.return_value = AsyncResult(
        [None, consumer_slug], geodata_status, geodata_result
    )

    await authorized_consumer.connect()
    await authorized_consumer.receive_json(json_request)

    assert send_consumer_mocker.called
    assert send_consumer_mocker.call_args[0][0] == response
