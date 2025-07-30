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

class CommandResult:
    """
    Represents the result of executing a cache command in the VertexCache SDK.

    This class encapsulates the response status, message, and optional payload
    returned from the server after executing a command such as GET, SET, or DEL.

    It is used by SDK consumers to inspect whether the command succeeded and to retrieve
    associated values or error details. Utility methods like `success` and `message`
    help simplify response handling in client logic.
    """

    def __init__(self, success: bool, message: str):
        self._success = success
        self._message = message

    @property
    def success(self) -> bool:
        return self._success

    @property
    def message(self) -> str:
        return self._message
