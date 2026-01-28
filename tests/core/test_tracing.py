import asyncio
import json
from typing import Optional
from unittest.mock import patch

from agave.core.tracing import (
    _add_attributes,
    _get_nested_value,
    accept_trace_from_queue,
    accept_trace_headers,
    add_custom_attribute,
    background_task,
    get_trace_headers,
    inject_trace_headers,
    trace_attributes,
)
from agave.tasks.sqs_tasks import task

from ..utils import CORE_QUEUE_REGION


def test_get_trace_headers_returns_dict_with_headers():
    with patch("newrelic.agent") as mock_agent:
        mock_agent.insert_distributed_trace_headers.side_effect = (
            lambda h: h.extend([("traceparent", "abc"), ("tracestate", "xyz")])
        )
        result = get_trace_headers()
        assert result == {"traceparent": "abc", "tracestate": "xyz"}


def test_accept_trace_headers_accepts_headers():
    with patch("newrelic.agent") as mock_agent:
        headers = {"traceparent": "abc"}
        accept_trace_headers(headers, transport_type="Queue")
        mock_fn = mock_agent.accept_distributed_trace_headers
        mock_fn.assert_called_once_with(headers, transport_type="Queue")


def test_accept_trace_headers_does_nothing_when_no_headers():
    with patch("newrelic.agent") as mock_agent:
        accept_trace_headers({})
        mock_agent.accept_distributed_trace_headers.assert_not_called()


def test_accept_trace_headers_does_nothing_when_headers_none():
    with patch("newrelic.agent") as mock_agent:
        accept_trace_headers(None)
        mock_agent.accept_distributed_trace_headers.assert_not_called()


def test_add_custom_attribute_adds_attribute():
    with patch("newrelic.agent") as mock_agent:
        add_custom_attribute("key", "value")
        mock_agent.add_custom_attribute.assert_called_once_with("key", "value")


def test_add_custom_attribute_does_nothing_when_value_none():
    with patch("newrelic.agent") as mock_agent:
        add_custom_attribute("key", None)
        mock_agent.add_custom_attribute.assert_not_called()


def test_add_custom_attribute_preserves_native_types():
    with patch("newrelic.agent") as mock_agent:
        add_custom_attribute("key", 12345)
        mock_agent.add_custom_attribute.assert_called_once_with("key", 12345)


def test_accept_trace_from_queue_accepts_headers():
    @accept_trace_from_queue
    def my_task(data: dict):
        return data

    with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
        result = my_task(
            {"value": 1}, _nr_trace_headers={"traceparent": "abc"}
        )
        assert result == {"value": 1}
        mock_accept.assert_called_once_with(
            {"traceparent": "abc"}, transport_type="Queue"
        )


def test_accept_trace_from_queue_removes_headers_from_kwargs():
    @accept_trace_from_queue
    def my_task(**kwargs):
        return kwargs

    with patch("agave.core.tracing.accept_trace_headers"):
        result = my_task(
            data={"value": 1}, _nr_trace_headers={"traceparent": "abc"}
        )
        # _nr_trace_headers should be removed
        assert "_nr_trace_headers" not in result
        assert result == {"data": {"value": 1}}


def test_accept_trace_from_queue_works_without_headers():
    @accept_trace_from_queue
    def my_task(data: dict):
        return data

    with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
        result = my_task({"value": 1})
        assert result == {"value": 1}
        mock_accept.assert_not_called()


def test_accept_trace_from_queue_async_accepts_headers():
    @accept_trace_from_queue
    async def my_task(data: dict):
        return data

    with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
        result = asyncio.run(
            my_task({"value": 1}, _nr_trace_headers={"traceparent": "abc"})
        )
        assert result == {"value": 1}
        mock_accept.assert_called_once_with(
            {"traceparent": "abc"}, transport_type="Queue"
        )


def test_accept_trace_from_queue_async_works_without_headers():
    @accept_trace_from_queue
    async def my_task(data: dict):
        return data

    with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
        result = asyncio.run(my_task({"value": 1}))
        assert result == {"value": 1}
        mock_accept.assert_not_called()


def test_inject_trace_headers_async_keyword_arg():
    @inject_trace_headers()
    async def my_func(_url: str, trace_headers: Optional[dict] = None):
        return trace_headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        result = asyncio.run(my_func("http://example.com"))
        assert result == {"traceparent": "abc"}


def test_inject_trace_headers_merges_existing_headers_async():
    @inject_trace_headers()
    async def my_func(_url: str, trace_headers: Optional[dict] = None):
        return trace_headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        result = asyncio.run(
            my_func("http://example.com", trace_headers={"custom": "header"})
        )
        assert result == {"custom": "header", "traceparent": "abc"}


def test_inject_trace_headers_handles_positional_headers_async():
    """Test that positional args don't cause 'multiple values' error."""

    @inject_trace_headers("headers")
    async def my_func(_url: str, headers: Optional[dict] = None):
        return headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        # Pass headers as positional argument
        result = asyncio.run(
            my_func("http://example.com", {"custom": "header"})
        )
        assert result == {"custom": "header", "traceparent": "abc"}


def test_inject_trace_headers_sync_keyword_arg():
    @inject_trace_headers()
    def my_func(_url: str, trace_headers: Optional[dict] = None):
        return trace_headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        result = my_func("http://example.com")
        assert result == {"traceparent": "abc"}


def test_inject_trace_headers_merges_existing_headers_sync():
    @inject_trace_headers()
    def my_func(_url: str, trace_headers: Optional[dict] = None):
        return trace_headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        result = my_func(
            "http://example.com", trace_headers={"custom": "header"}
        )
        assert result == {"custom": "header", "traceparent": "abc"}


def test_inject_trace_headers_handles_positional_headers_sync():
    """Test that positional args don't cause 'multiple values' error."""

    @inject_trace_headers("headers")
    def my_func(_url: str, headers: Optional[dict] = None):
        return headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        # Pass headers as positional argument
        result = my_func("http://example.com", {"custom": "header"})
        assert result == {"custom": "header", "traceparent": "abc"}


def test_inject_trace_headers_custom_param_name():
    @inject_trace_headers("custom_headers")
    def my_func(_url: str, custom_headers: Optional[dict] = None):
        return custom_headers

    with patch(
        "agave.core.tracing.get_trace_headers",
        return_value={"traceparent": "abc"},
    ):
        result = my_func("http://example.com")
        assert result == {"traceparent": "abc"}


def test_trace_attributes_extracts_simple_kwarg_async():
    @trace_attributes(my_attr="value")
    async def my_func(value: str):
        return value

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = asyncio.run(my_func("test_value"))
        assert result == "test_value"
        mock_add.assert_called_once_with("my_attr", "test_value")


def test_trace_attributes_extracts_nested_attr_async():
    class Order:
        def __init__(self):
            self.clave_emisor = "12345"

    @trace_attributes(emisor="order.clave_emisor")
    async def my_func(order: Order):
        return order.clave_emisor

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = asyncio.run(my_func(Order()))
        assert result == "12345"
        mock_add.assert_called_once_with("emisor", "12345")


def test_trace_attributes_extracts_with_callable_async():
    @trace_attributes(total=lambda kw: kw["a"] + kw["b"])
    async def my_func(a: int, b: int):
        return a + b

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = asyncio.run(my_func(1, 2))
        assert result == 3
        mock_add.assert_called_once_with("total", 3)


def test_trace_attributes_extracts_simple_kwarg_sync():
    @trace_attributes(my_attr="value")
    def my_func(value: str):
        return value

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = my_func("test_value")
        assert result == "test_value"
        mock_add.assert_called_once_with("my_attr", "test_value")


def test_trace_attributes_extracts_nested_attr_sync():
    class Order:
        def __init__(self):
            self.clave_emisor = "12345"

    @trace_attributes(emisor="order.clave_emisor")
    def my_func(order: Order):
        return order.clave_emisor

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = my_func(Order())
        assert result == "12345"
        mock_add.assert_called_once_with("emisor", "12345")


def test_trace_attributes_extracts_with_callable_sync():
    @trace_attributes(total=lambda kw: kw["a"] + kw["b"])
    def my_func(a: int, b: int):
        return a + b

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = my_func(1, 2)
        assert result == 3
        mock_add.assert_called_once_with("total", 3)


def test_trace_attributes_handles_positional_args():
    """Test that positional args are properly bound to param names."""

    @trace_attributes(x_val="x", y_val="y")
    def my_func(x: int, y: int):
        return x + y

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        result = my_func(10, 20)  # Both as positional
        assert result == 30
        assert mock_add.call_count == 2


def test_trace_attributes_handles_extraction_error_gracefully():
    @trace_attributes(missing="nonexistent.path.deep")
    def my_func(value: str):
        return value

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        # Should not raise, just silently fail the attribute
        result = my_func("test")
        assert result == "test"
        mock_add.assert_called_once_with("missing", None)


def test_get_nested_value_from_dict():
    obj = {"transaction": {"clave_rastreo": "ABC123"}}
    result = _get_nested_value(obj, "transaction.clave_rastreo")
    assert result == "ABC123"


def test_get_nested_value_from_object():
    class Transaction:
        clave_rastreo = "ABC123"

    class Data:
        transaction = Transaction()

    result = _get_nested_value(Data(), "transaction.clave_rastreo")
    assert result == "ABC123"


def test_get_nested_value_returns_none_for_missing_path():
    obj = {"transaction": {}}
    result = _get_nested_value(obj, "transaction.missing.deep")
    assert result is None


def test_get_nested_value_simple_key():
    obj = {"name": "test"}
    result = _get_nested_value(obj, "name")
    assert result == "test"


def test_get_nested_value_mixed_dict_and_object():
    class Inner:
        value = "nested"

    obj = {"outer": Inner()}
    result = _get_nested_value(obj, "outer.value")
    assert result == "nested"


def test_add_attributes_with_callable_extractor():
    kwargs = {"a": 1, "b": 2}
    extractors = {"sum": lambda kw: kw["a"] + kw["b"]}

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        _add_attributes(kwargs, extractors)
        mock_add.assert_called_once_with("sum", 3)


def test_add_attributes_with_string_extractor():
    kwargs = {"name": "test"}
    extractors = {"result": "name"}

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        _add_attributes(kwargs, extractors)
        mock_add.assert_called_once_with("result", "test")


def test_add_attributes_with_dotted_path_extractor():
    class Obj:
        value = "nested"

    kwargs = {"obj": Obj()}
    extractors = {"result": "obj.value"}

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        _add_attributes(kwargs, extractors)
        mock_add.assert_called_once_with("result", "nested")


def test_add_attributes_handles_exception_gracefully():
    kwargs = {}
    extractors = {"broken": lambda kw: kw["missing"]}

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        # Should not raise
        _add_attributes(kwargs, extractors)
        mock_add.assert_not_called()


def test_add_attributes_with_non_callable_non_string_extractor():
    """Test that non-callable non-string extractors result in None."""
    kwargs = {"name": "test"}
    extractors = {"result": 12345}  # Not a callable, not a string

    with patch("agave.core.tracing.add_custom_attribute") as mock_add:
        _add_attributes(kwargs, extractors)
        mock_add.assert_called_once_with("result", None)


def test_background_task_creates_transaction():
    """Test that background_task creates a New Relic BackgroundTask."""
    with patch("agave.core.tracing.newrelic.agent") as mock_agent:
        mock_agent.application.return_value = "test_app"
        mock_agent.BackgroundTask.return_value.__enter__ = lambda s: None
        mock_agent.BackgroundTask.return_value.__exit__ = lambda s, *a: None

        with background_task("my_task", "Redis/Queue"):
            pass

        mock_agent.BackgroundTask.assert_called_once_with(
            application="test_app",
            name="my_task",
            group="Redis/Queue",
        )


def test_background_task_accepts_trace_headers():
    """Test that background_task accepts trace headers inside transaction."""
    with patch("agave.core.tracing.newrelic.agent") as mock_agent:
        mock_agent.application.return_value = "test_app"
        mock_agent.BackgroundTask.return_value.__enter__ = lambda s: None
        mock_agent.BackgroundTask.return_value.__exit__ = lambda s, *a: None

        with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
            headers = {"traceparent": "abc"}
            with background_task("my_task", "SQS/Queue", headers):
                pass

            mock_accept.assert_called_once_with(
                headers, transport_type="Queue"
            )


def test_background_task_does_not_accept_when_no_headers():
    """Test that background_task skips accept when no trace headers."""
    with patch("agave.core.tracing.newrelic.agent") as mock_agent:
        mock_agent.application.return_value = "test_app"
        mock_agent.BackgroundTask.return_value.__enter__ = lambda s: None
        mock_agent.BackgroundTask.return_value.__exit__ = lambda s, *a: None

        with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
            with background_task("my_task", "Task"):
                pass

            mock_accept.assert_not_called()


async def test_accept_trace_from_queue_with_sqs_task(sqs_client):
    @task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )
    @accept_trace_from_queue
    async def my_task(data: dict):
        return data

    message = {"value": 1, "_nr_trace_headers": {"traceparent": "abc123"}}
    await sqs_client.send_message(
        MessageBody=json.dumps(message),
        MessageGroupId="1234",
    )

    with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
        await my_task()
        mock_accept.assert_called_once_with(
            {"traceparent": "abc123"}, transport_type="Queue"
        )


async def test_trace_headers_propagation_through_queue(sqs_client):
    received_data = {}

    @task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )
    @accept_trace_from_queue
    async def consumer_task(data: dict):
        received_data.update(data)

    trace_headers = {
        "traceparent": "00-abc123-def456-01",
        "tracestate": "nr=xyz",
    }
    message = {
        "order_id": "ORD001",
        "_nr_trace_headers": trace_headers,
    }

    await sqs_client.send_message(
        MessageBody=json.dumps(message),
        MessageGroupId="propagation-test",
    )

    with patch("agave.core.tracing.accept_trace_headers") as mock_accept:
        await consumer_task()
        mock_accept.assert_called_once_with(
            trace_headers, transport_type="Queue"
        )

    assert received_data == {"order_id": "ORD001"}
    assert "_nr_trace_headers" not in received_data
