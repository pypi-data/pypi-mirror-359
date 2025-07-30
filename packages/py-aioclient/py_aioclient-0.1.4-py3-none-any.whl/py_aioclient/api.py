from .client import PyAioClient
from typing import Any, Awaitable


async def request(
    url: str,
    method: str = 'get',
    return_attrs: list[str] | None = None,
    **kwargs: Any
) -> Any:
    """Executes a single asynchronous HTTP request.

    This high-level function is a convenient wrapper around the
    PyAioClient class. It automatically handles the setup and teardown
    of the client session, making it ideal for simple, one-off requests.

    Args:
        method: The HTTP method to use (e.g., 'get', 'post').
        url: The target URL for the request.
        return_attrs: A list of response attributes to return.
            Defaults to ['status'].
        **kwargs: Additional keyword arguments passed directly to the
            underlying client method, such as `params`, `json`,
            `headers`, or `timeout`.

    Returns:
        The result of the request, which can be a single value or a list
        of values depending on `return_attrs`.
    """

    async with PyAioClient() as client:
        return await client.client(
            method=method,
            url=url,
            return_attrs=return_attrs,
            **kwargs
        )


async def batch_requests(
    requests_params: list[dict[str, Any]],
    limit: int = 10,
    common_return_attrs: list[str] | None = None
) -> list[Any]:
    """Executes multiple asynchronous requests in a concurrent batch.

    This function is designed for high-throughput scenarios, running
    many requests concurrently while respecting a concurrency limit to
    avoid overwhelming a server.

    Args:
        requests_params: A list of dictionaries, where each dict
            contains the parameters for a single request call (e.g.,
            {'method': 'get', 'url': '...', 'json': {...}}).
        limit: The maximum number of requests to run concurrently.
        common_return_attrs: A default list of return attributes to apply
            to all requests in the batch. This can be overridden by
            a 'return_attrs' key in an individual request's dictionary.

    Returns:
        A list containing the results of each request, preserving the
        original order of the input `requests_params`.
    """

    async with PyAioClient() as client:

        tasks: list[Awaitable[Any]] = []
        for params in requests_params:
            # Set the return attributes for the task, using the common
            # one as a fallback.
            params['return_attrs'] = params.get(
                'return_attrs', common_return_attrs
            )
            tasks.append(client.client(**params))

        return await client.limiter(limit=limit, tasks=tasks)
