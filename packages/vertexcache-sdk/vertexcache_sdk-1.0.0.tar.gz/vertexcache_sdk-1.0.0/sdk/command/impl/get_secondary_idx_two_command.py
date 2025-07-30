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
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException


class GetSecondaryIdxTwoCommand(CommandBase):
    """
    Handles the GET Secondary Idx (idx2) command in VertexCache.

    Retrieves the value for a given tertiary index key (idx2) from the cache.
    Returns an error if the key is missing or expired.

    Requires the client to have READ, READ_WRITE, or ADMIN access.
    """

    def __init__(self, key: str):
        super().__init__()
        if key is None or key.strip() == "":
            raise VertexCacheSdkException("GET By Secondary Index (idx2) command requires a non-empty key")
        self.key = key
        self.value = None

    def build_command(self) -> str:
        return f"GETIDX2 {self.key}"

    def parse_response(self, response_body: str):
        if response_body.strip().lower() == "(nil)":
            self.set_success_with_response("No matching key found, +(nil)")
        elif response_body.startswith("ERR"):
            self.set_failure(f"GETIDX2 failed: {response_body}")
        else:
            self.value = response_body

    def get_value(self) -> str:
        return self.value
