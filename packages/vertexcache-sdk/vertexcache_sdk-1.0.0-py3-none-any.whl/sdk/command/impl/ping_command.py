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

from sdk.command.command_base import CommandBase


class PingCommand(CommandBase):
    """
    Handles the PING command in VertexCache.

    This command is used to check server availability and latency.
    It returns a basic "PONG" response and can be used by clients to verify liveness.

    PING is always allowed regardless of authentication state or client role.
    It does not require access validation or key arguments.
    """

    def build_command(self) -> str:
        return "PING"

    def parse_response(self, response_body: str):
        if response_body is None or response_body.strip() == "" or response_body.strip().lower() != "pong":
            self.set_failure("PONG not received")
