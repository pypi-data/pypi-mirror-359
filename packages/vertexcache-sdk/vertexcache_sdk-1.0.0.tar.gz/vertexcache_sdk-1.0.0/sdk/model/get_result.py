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

from sdk.model.command_result import CommandResult

class GetResult(CommandResult):
    """
    Specialized result class for handling GET command responses from VertexCache.

    Extends CommandResult by adding a `value` field which contains the actual
    cached value associated with the requested key, if present.

    This class is typically used when calling `sdk.get(key)` to retrieve a value
    from the cache and determine its presence and contents.
    """

    def __init__(self, success: bool, message: str, value: str):
        super().__init__(success, message)
        self._value = value

    @property
    def value(self) -> str:
        return self._value
