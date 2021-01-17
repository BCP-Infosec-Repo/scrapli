"""scrapli.driver.base.async_driver"""
from types import TracebackType
from typing import Any, Optional, Type

from scrapli.channel import AsyncChannel
from scrapli.driver.base.base_driver import BaseDriver
from scrapli.exceptions import ScrapliValueError
from scrapli.transport import ASYNCIO_TRANSPORTS


class AsyncDriver(BaseDriver):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        if self.transport_name not in ASYNCIO_TRANSPORTS:
            raise ScrapliValueError

        self.channel = AsyncChannel(
            transport=self.transport,
            base_channel_args=self._base_channel_args,
        )

    async def __aenter__(self) -> "AsyncDriver":
        """
        Enter method for context manager

        Args:
            N/A

        Returns:
            AsyncDriver: opened AsyncDriver object

        Raises:
            N/A

        """
        await self.open()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Exit method to cleanup for context manager

        Args:
            exception_type: exception type being raised
            exception_value: message from exception being raised
            traceback: traceback from exception being raised

        Returns:
            None

        Raises:
            N/A

        """
        await self.close()

    async def open(self) -> None:
        """
        Open the scrapli connection

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self._pre_open_closing_log(closing=False)

        await self.transport.open()

        if (
            self.transport_name
            in (
                "telnet",
                "asynctelnet",
            )
            and not self.auth_bypass
        ):
            await self.channel.channel_authenticate_telnet(
                auth_username=self.auth_username, auth_password=self.auth_password
            )

        if self.on_open:
            await self.on_open(self)

        self._post_open_closing_log(closing=False)

    async def close(self) -> None:
        """
        Close the scrapli connection

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self._post_open_closing_log(closing=True)

        if self.on_close:
            await self.on_close(self)

        if self.channel.channel_log:
            self.channel.channel_log.close()

        self.transport.close()

        self._post_open_closing_log(closing=True)
