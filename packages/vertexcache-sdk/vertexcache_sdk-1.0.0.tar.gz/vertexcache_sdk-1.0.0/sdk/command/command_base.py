# ------------------------------------------------------------------------------
# Copyright 2025 to Present, Jason Lam - VertexCache (https://github.com/vertexcache/vertexcache)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# ------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from sdk.command.command_interface import CommandInterface
from sdk.comm.client_connector import ClientConnector
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException


class CommandBase(CommandInterface, ABC):
    """
    BaseCommand defines the foundational structure for all client-issued commands
    in the VertexCache SDK. It handles execution logic and shared response parsing.

    Subclasses must implement the `build_command` method and optionally override
    `parse_response` if custom response parsing is needed.
    """

    RESPONSE_OK = "OK"
    COMMAND_SPACER = " "

    def __init__(self):
        self._success = False
        self._response = None
        self._error = None

    def execute(self, client: ClientConnector) -> "CommandBase":
        try:
            raw = client.send(self.build_command()).strip()

            if raw.startswith("+"):
                self._response = raw[1:]
                self.parse_response(self._response)
                if self._error is None:
                    self._success = True
            elif raw.startswith("-"):
                self._success = False
                self._error = raw[1:]
            else:
                self._success = False
                self._error = f"Unexpected response: {raw}"

        except VertexCacheSdkException as e:
            self._success = False
            self._error = str(e)

        return self

    @abstractmethod
    def build_command(self) -> str:
        pass

    def parse_response(self, response_body: str):
        # Default implementation does nothing; override if needed
        pass

    def set_failure(self, response: str):
        self._success = False
        self._error = response

    def set_success(self):
        self._success = True
        self._response = self.RESPONSE_OK
        self._error = None

    def set_success_with_response(self, response: str):
        self._success = True
        self._response = response
        self._error = None

    def is_success(self) -> bool:
        return self._success

    def get_response(self) -> str:
        return self._response

    def get_error(self) -> str:
        return self._error

    def get_status_message(self) -> str:
        return self.get_response() if self.is_success() else self.get_error()
