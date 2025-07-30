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
from sdk.comm.client_connector import ClientConnector

class CommandInterface(ABC):
    """
    CommandInterface represents a generic base class for all command types that can be executed
    by the VertexCache SDK.

    Subclasses must define how a command is executed using the ClientConnector and expose its
    result, error, and status fields.
    """

    @abstractmethod
    def execute(self, client: ClientConnector) -> "CommandInterface":
        pass

    @abstractmethod
    def is_success(self) -> bool:
        pass

    @abstractmethod
    def get_response(self) -> str:
        pass

    @abstractmethod
    def get_error(self) -> str:
        pass

    @abstractmethod
    def get_status_message(self) -> str:
        pass
