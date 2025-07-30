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
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from sdk.comm.client_connector import ClientConnector
from sdk.command.impl.ping_command import PingCommand
from sdk.command.impl.set_command import SetCommand
from sdk.command.impl.del_command import DelCommand
from sdk.command.impl.get_command import GetCommand
from sdk.command.impl.get_secondary_idx_one_command import GetSecondaryIdxOneCommand
from sdk.command.impl.get_secondary_idx_two_command import GetSecondaryIdxTwoCommand
from sdk.model.command_result import CommandResult
from sdk.model.get_result import GetResult


class VertexCacheSDK:
    """
    VertexCacheSDK serves as the main entry point for interacting with the VertexCache server.

    It provides methods to perform cache operations such as GET, SET, and DEL, and abstracts away
    the underlying TCP transport details including encryption, authentication, and framing.
    """

    def __init__(self, client_option):
        self.client_connector = ClientConnector(client_option)

    def open_connection(self):
        self.client_connector.connect()

    def ping(self) -> CommandResult:
        cmd = PingCommand().execute(self.client_connector)
        return CommandResult(cmd.is_success(), cmd.get_status_message())

    def set(self, key: str, value: str, idx1: str = None, idx2: str = None) -> CommandResult:
        cmd = SetCommand(key, value, idx1, idx2).execute(self.client_connector)
        return CommandResult(cmd.is_success(), cmd.get_status_message())

    def delete(self, key: str) -> CommandResult:
        cmd = DelCommand(key).execute(self.client_connector)
        return CommandResult(cmd.is_success(), cmd.get_status_message())

    def get(self, key: str) -> GetResult:
        cmd = GetCommand(key).execute(self.client_connector)
        return GetResult(cmd.is_success(), cmd.get_status_message(), cmd.get_value())

    def get_by_secondary_index(self, key: str) -> GetResult:
        cmd = GetSecondaryIdxOneCommand(key).execute(self.client_connector)
        return GetResult(cmd.is_success(), cmd.get_status_message(), cmd.get_value())

    def get_by_tertiary_index(self, key: str) -> GetResult:
        cmd = GetSecondaryIdxTwoCommand(key).execute(self.client_connector)
        return GetResult(cmd.is_success(), cmd.get_status_message(), cmd.get_value())

    def is_connected(self) -> bool:
        return self.client_connector.is_connected()

    def close(self):
        self.client_connector.close()
