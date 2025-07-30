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

import struct

MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB
PROTOCOL_VERSION_RSA_PKCS1 = 0x00000101
PROTOCOL_VERSION_AES_GCM   = 0x00000181

# Mutable module-level state
_protocol_version = PROTOCOL_VERSION_RSA_PKCS1

def switch_to_symmetric():
    global _protocol_version
    _protocol_version = PROTOCOL_VERSION_AES_GCM


def switch_to_asymmetric():
    global _protocol_version
    _protocol_version = PROTOCOL_VERSION_RSA_PKCS1

def get_protocol_version():
    return _protocol_version

def write_framed_message(payload: bytes) -> bytes:
    """
    Writes a framed message using the VertexCache protocol format.

    Format:
    - 4 bytes big-endian payload length
    - 4 bytes big-endian protocol version
    - N bytes payload

    Returns:
        bytes: The framed binary message.
    """
    if not isinstance(payload, bytes):
        raise TypeError("Payload must be bytes")

    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message too large: {len(payload)}")

    length_bytes = struct.pack(">I", len(payload))
    version_bytes = struct.pack(">I", get_protocol_version())
    return length_bytes + version_bytes + payload


def read_framed_message(buffer: bytes):
    """
    Reads a framed message from a byte buffer.

    Returns:
        tuple[bytes, bytes] | None:
            - (payload, remaining) if complete and valid
            - None if buffer too short

    Raises:
        ValueError: If the version is unsupported or length is invalid
    """
    if len(buffer) < 8:
        return None

    length, version = struct.unpack(">II", buffer[:8])

    if version not in (PROTOCOL_VERSION_RSA_PKCS1, PROTOCOL_VERSION_AES_GCM):
        raise ValueError(f"Unsupported protocol version: 0x{version:08X}")

    if length <= 0 or length > MAX_MESSAGE_SIZE:
        raise ValueError(f"Invalid message length: {length}")

    if len(buffer) < 8 + length:
        return None

    payload = buffer[8:8 + length]
    remaining = buffer[8 + length:]
    return payload, remaining