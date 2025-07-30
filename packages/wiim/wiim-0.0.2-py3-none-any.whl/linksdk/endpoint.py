import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict

from aiohttp import ClientSession, ClientTimeout, ClientError

from .consts import (
    API_ENDPOINT,
    API_TIMEOUT,
    SDK_LOGGER,
    WiimHttpCommand,
)  # Use SDK logger
from .exceptions import WiimRequestException, WiimInvalidDataException  # Renamed


class WiimBaseEndpoint(ABC):  # New base class
    """Represents an abstract WiiM endpoint."""

    logger = SDK_LOGGER

    @abstractmethod
    async def request(self, command: str) -> None:
        """Performs a request on the given command and verifies the result (e.g., expects 'OK')."""

    @abstractmethod
    async def json_request(self, command: str) -> Dict[str, Any]:  # Return type changed
        """Performs a request on the given command and returns the result as a JSON object."""

    @abstractmethod
    def to_dict(self) -> dict[str, str]:
        """Return the state of the WiimBaseEndpoint"""

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the endpoint."""


class WiimApiEndpoint(WiimBaseEndpoint):  # Renamed from LinkPlayApiEndpoint
    """Represents a WiiM HTTP API endpoint."""

    def __init__(
        self, *, protocol: str, port: int, endpoint: str, session: ClientSession
    ):
        assert protocol in [
            "http",
            "https",
        ], "Protocol must be either 'http' or 'https'"

        # Determine if port should be included in the URL
        include_port = (protocol == "http" and port != 80) or (
            protocol == "https" and port != 443
        )
        port_suffix = f":{port}" if include_port else ""
        self._base_url: str = f"{protocol}://{endpoint}{port_suffix}"
        self._session: ClientSession = session
        self.logger.debug("WiimApiEndpoint initialized for %s", self._base_url)

    def to_dict(self) -> dict[str, str]:
        """Return the state of the WiimApiEndpoint"""
        return {"base_url": self._base_url}

    async def request(self, command: str) -> None:
        """
        Performs a GET request on the given command and verifies the result.
        Expects the response text to be "OK".
        """
        url = API_ENDPOINT.format(self._base_url, command)
        self.logger.debug(f"Requesting (expect OK): {url}")
        try:
            async with self._session.get(
                url, timeout=ClientTimeout(total=API_TIMEOUT)
            ) as response:
                response_text = await response.text()
                self.logger.debug(
                    f"Response from {url}: {response.status} {response_text[:100]}"
                )  # Log snippet
                if response.status != 200:
                    raise WiimRequestException(
                        f"Request to {url} failed with status {response.status}: {response_text}"
                    )
                # if response_text.strip().upper() != "OK":
                txt = response_text.strip().upper()
                if "OK" not in txt:
                    raise WiimInvalidDataException(
                        f"Request to {url} did not return 'OK'. Got: '{response_text}'"
                    )
        except ClientError as err:
            self.logger.warning(f"ClientError for {url}: {err}")
            raise WiimRequestException(f"Network error for {url}: {err}") from err
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout for {url}")
            raise WiimRequestException(f"Timeout for {url}") from asyncio.TimeoutError

    async def json_request(self, command: str) -> Dict[str, Any]:
        """
        Performs a GET request on the given command and returns the result as a JSON object.
        """
        url = API_ENDPOINT.format(self._base_url, command)
        self.logger.debug(f"Requesting (expect JSON): {url}")
        try:
            async with self._session.get(
                url, timeout=ClientTimeout(total=API_TIMEOUT)
            ) as response:
                # WiiM devices might return JSON with text/plain content type
                response_text = (
                    await response.text()
                )  # Get text first for better error reporting
                self.logger.debug(
                    f"Response from {url}: {response.status} {response_text[:200]}"
                )  # Log snippet
                if response.status != 200:
                    raise WiimRequestException(
                        f"Request to {url} failed with status {response.status}: {response_text}"
                    )
                try:
                    # We need to parse this into a dict.
                    if (
                        command == WiimHttpCommand.DEVICE_STATUS
                        or command == WiimHttpCommand.PLAYER_STATUS
                        or command == WiimHttpCommand.AUDIO_OUTPUT_HW_MODE
                        or command == WiimHttpCommand.MULTIROOM_LIST
                    ):  # These return key=value or JSON
                        if response_text.strip().startswith(
                            "{"
                        ) and response_text.strip().endswith("}"):
                            # Looks like JSON
                            return await response.json(
                                content_type=None
                            )  # Allow any content type for JSON

                        # Parse key=value pairs
                        data: Dict[str, Any] = {}
                        for line in response_text.strip().split("\n"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                data[key.strip()] = value.strip()
                            elif (
                                line.strip()
                            ):  # Handle cases where a line might not be key=value
                                data[line.strip()] = True  # Or some other indicator
                        if (
                            not data and response_text.strip()
                        ):  # If no '=' but text exists
                            # Could be a single value response, or an error message not caught by status
                            if (
                                response_text.strip().upper() == "FAILED"
                            ):  # Common error string
                                raise WiimInvalidDataException(
                                    f"Command {command} returned 'Failed'",
                                    data=response_text,
                                )
                            # If it's not "Failed" but also not key-value, it's unusual for status commands
                            self.logger.warning(
                                "Unexpected format for %s, treating as simple string: %s",
                                command,
                                response_text,
                            )
                            return {"response": response_text.strip()}
                        return data
                    else:
                        # For other commands, if JSON is expected, try to parse as JSON directly
                        # This part might need adjustment based on what other commands return
                        return await response.json(content_type=None)

                except ValueError as err:  # Includes JSONDecodeError
                    self.logger.warning(
                        f"Failed to parse JSON/Key-Value from {url}: {err}. Response text: {response_text[:200]}"
                    )
                    raise WiimInvalidDataException(
                        f"Invalid JSON or Key-Value response from {url}: {response_text}",
                        data=response_text,
                    ) from err
        except ClientError as err:
            self.logger.warning(f"ClientError for {url}: {err}")
            raise WiimRequestException(f"Network error for {url}: {err}") from err
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout for {url}")
            raise WiimRequestException(f"Timeout for {url}") from asyncio.TimeoutError

    def __str__(self) -> str:
        return self._base_url
