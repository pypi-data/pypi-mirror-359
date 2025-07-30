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


class SetCommand(CommandBase):
    """
    Handles the SET command in VertexCache.

    Stores a value in the cache under the specified key, optionally assigning
    secondary (idx1) and tertiary (idx2) indexes for lookup. Existing keys will
    be overwritten. Supports expiration and format validation if configured.

    Requires the client to have WRITE or ADMIN access.
    """

    def __init__(self, primary_key: str, value: str, secondary_key: str = None, tertiary_key: str = None):
        super().__init__()

        if primary_key is None or primary_key.strip() == "":
            raise VertexCacheSdkException("Missing Primary Key")

        if value is None or value.strip() == "":
            raise VertexCacheSdkException("Missing Value")

        if secondary_key is not None and secondary_key.strip() == "":
            raise VertexCacheSdkException("Secondary key can't be empty when used")

        if secondary_key and secondary_key.strip() != "" and tertiary_key is not None and tertiary_key.strip() == "":
            raise VertexCacheSdkException("Tertiary key can't be empty when used")

        self.primary_key = primary_key
        self.value = value
        self.secondary_key = secondary_key
        self.tertiary_key = tertiary_key

    def build_command(self) -> str:
        parts = [CommandType.SET.keyword(), self.primary_key, self.value]

        if self.secondary_key and self.secondary_key.strip() != "":
            parts += [CommandType.IDX1.keyword(), self.secondary_key]

        if self.tertiary_key and self.tertiary_key.strip() != "":
            parts += [CommandType.IDX2.keyword(), self.tertiary_key]

        return " ".join(parts)

    def parse_response(self, response_body: str):
        if response_body.strip().lower() != "ok":
            self.set_failure("OK Not received")
        else:
            self.set_success()
