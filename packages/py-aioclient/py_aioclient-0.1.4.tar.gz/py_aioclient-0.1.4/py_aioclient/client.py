import aiohttp
import asyncio

from types import TracebackType
from typing import Any, Self, Type, TypeVar, Awaitable

# Type variable for linking input task types to the limiter's output type.
T = TypeVar('T')

class PyAioClient:
    """
    An asynchronous wrapper for aiohttp.ClientSession to simplify
    concurrent HTTP requests with context management, rate limiting,
    and flexible response handling.
    """

    # --- Class Constants ---

    RETURN_TYPES: list[str] = [
        'text', 'read', 'json', 'status', 'reason', 'response'
    ]

    METHOD_TYPES: list[str] = [
        'get', 'post', 'put', 'delete', 'head', 'options', 'patch'
    ]

    _COMPARATIVE_LIST: list[str] = METHOD_TYPES + RETURN_TYPES


    INVALID_PARAMETER: str = 'Parâmetro "{value}" não reconhecido.'

    # --- Dunder Methods ---

    def __init__(
        self,
        limit_connector: int = 0,
        cookies: dict[str, Any] | None = None
    ) -> None:
        """Initializes the asynchronous request client.

        This method sets up the session parameters. The session itself is
        created asynchronously upon entering the `async with` context manager.

        Args:
            limit_connector: Maximum number of simultaneous TCP connections.
                A value of 0 means no limit (default).
            cookies: A dictionary of cookies to be sent with all requests.
                Defaults to None.

        Attributes:
            limit_connector: The configured connection limit.
            cookies: The dictionary of cookies in use. Will be an empty
                dict if none are provided.
            connector: The TCP connector for the session. Initialized as
                `None` and created by the `async with` context manager.
            session: The aiohttp ClientSession. Initialized as `None` and
                created by the `async with` context manager.
        """

        # --- Atributos configuráveis ---
        self.limit_connector = limit_connector
        self.cookies = cookies or {}

        # --- Atributos de estado ---
        self.connector: aiohttp.TCPConnector | None = None
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        """Prepares and initializes the session for asynchronous requests.

        This magic method is the entry point for the asynchronous context
        manager (`async with`). Its responsibility is to create I/O-bound
        resources like the TCPConnector and the aiohttp.ClientSession, which
        require an active event loop.

        Returns:
            The instance of the object, now ready to perform requests
            with an active session.
        """

        self.connector = aiohttp.TCPConnector(limit=self.limit_connector)
        parameters: dict[str, Any] = {'connector': self.connector}

        if self.cookies:
            parameters['cookies'] = self.cookies

        self.session = aiohttp.ClientSession(**parameters)

        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None
    ) -> None:
        """Closes the session and cleans up connection resources.

        This magic method is the exit point for the `async with` context
        manager, ensuring the aiohttp session is always safely closed,
        even if exceptions occur within the block.
        """

        if self.session and not self.session.closed:
            await self.session.close()

    # --- Public Methods ---

    async def limiter(
        self,
        limit: int,
        tasks: list[Awaitable[T]]
    ) -> list[Awaitable[T]]:
        """Executes a list of awaitable tasks with a concurrency limit.

        This method uses an `asyncio.Semaphore` to ensure that no more
        than `limit` tasks are running simultaneously. It is ideal for
        controlling access to limited resources, such as APIs or databases,
        to prevent overloading and rate limiting.

        If the limit is zero or negative, all tasks will be scheduled
        for concurrent execution without any limitation.

        Args:
            limit: The maximum number of tasks that can run at the same time.
            tasks: A list of awaitable objects (e.g., coroutines) to execute.

        Returns:
            A list containing the results of each task, preserving the
            original order of the input list.
        """

        if limit <= 0:
            return await asyncio.gather(*tasks)

        semaphore = asyncio.Semaphore(limit)

        async def _internal(task: Awaitable[T]) -> T:

            async with semaphore:
                return await task

        return await asyncio.gather(*[_internal(task) for task in tasks])

    async def client(
        self,
        method: str = 'get',
        return_attrs: list[str] | None = None,
        content_type: str | None = None,
        timeout: int | None = None,
        **kwargs: Any
    ) -> list[Any] | Any:
        """Executes a single asynchronous HTTP request.

        This is the main method for making HTTP calls. It uses the session
        created by the context manager.

        Args:
            method: The HTTP method to use (e.g., 'get', 'post').
            return_attrs: A list of response attributes to return.
                Ex: ['status', 'json']. Defaults to ['status'].
            content_type: Used when decoding a JSON response.
            timeout: Timeout in seconds for the request.
            **kwargs: Keyword arguments passed directly to aiohttp, such as
                `url`, `params`, `headers`, `json`, `data`.

        Returns:
            A single value or a list of values, depending on the length
            of `return_attrs`. In case of a timeout, returns a list
            of TimeoutError objects.

        Raises:
            RuntimeError: If the method is called outside an `async with` block.
            AttributeError: If an invalid method or return attribute is provided.
        """

        assert self.session is not None, (
            "Session not initialized. Use this class with 'async with'."
        )

        if return_attrs is None:
            return_attrs = ['status']

        self._parameter_validation(return_attrs + [method])

        if timeout:
            kwargs['timeout'] = aiohttp.ClientTimeout(total=timeout)

        try:
            async with getattr(self.session, method)(**kwargs) as response:

                return_list: list[Any] = []
                for attr_name in return_attrs:

                    item = (
                        response if attr_name == 'response'
                        else getattr(response, attr_name)
                    )

                    if callable(item):
                        if attr_name == 'json':
                            return_list.append(
                                await item(content_type=content_type)
                            )
                        else:
                            return_list.append(await item())

                    else:
                        return_list.append(item)

        except asyncio.TimeoutError as error:
            return [error for _ in return_attrs]

        return return_list[0] if len(return_list) == 1 else return_list

    # --- Internal Methods ---

    def _parameter_validation(self, parameters: list[str]) -> None:
        """Internally validates if the provided parameters are recognized.

        This is an internal helper method to ensure that method and return
        values passed to the `client` method are valid by checking them
        against `self._COMPARATIVE_LIST`.

        Args:
            parameters: The list of strings to be validated.

        Raises:
            AttributeError: If any of the parameters in the list is not
                recognized, indicating an invalid value.
        """

        for value in parameters:
            if value not in self._COMPARATIVE_LIST:
                raise AttributeError(self.INVALID_PARAMETER.format(value=value))
