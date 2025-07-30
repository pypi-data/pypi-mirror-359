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


class GetCommand(CommandBase):
    """
    Handles the GET command in VertexCache.

    Retrieves the value for a given key from the cache.
    Returns an error if the key is missing or expired.

    Requires the client to have READ, READ_WRITE, or ADMIN access.
    This command supports primary key lookups only.
    """

    def __init__(self, key: str):
        super().__init__()
        if key is None or key.strip() == "":
            raise VertexCacheSdkException("GET command requires a non-empty key")
        self.key = key
        self.value = None

    def build_command(self) -> str:
        return f"GET {self.key}"

    def parse_response(self, response_body: str):
        if response_body.strip().lower() == "(nil)":
            self.set_success_with_response("No matching key found, +(nil)")
        elif response_body.startswith("ERR"):
            self.set_failure(f"GET failed: {response_body}")
        else:
            self.value = response_body

    def get_value(self) -> str:
        return self.value
