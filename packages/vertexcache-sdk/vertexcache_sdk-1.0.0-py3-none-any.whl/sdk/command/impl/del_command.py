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
from sdk.command.command_type import CommandType
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException

class DelCommand(CommandBase):
    """
    Handles the DEL command in VertexCache.

    Deletes a key and its associated value from the cache.
    If the system is configured to allow idempotent deletes,
    then attempting to delete a non-existent key will still
    return a success response ("OK DEL (noop)").

    Requires the client to have WRITE or ADMIN access.
    """

    def __init__(self, key: str):
        super().__init__()
        if key is None or key.strip() == "":
            raise VertexCacheSdkException(f"{CommandType.DEL} command requires a non-empty key")
        self.key = key

    def build_command(self) -> str:
        return f"{CommandType.DEL.keyword()} {self.key}"

    def parse_response(self, response_body: str):
        if response_body.strip().lower() != "ok":
            self.set_failure(f"DEL failed: {response_body}")
