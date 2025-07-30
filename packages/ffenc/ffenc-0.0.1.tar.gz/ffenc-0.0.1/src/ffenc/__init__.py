# SPDX-FileCopyrightText: 2025-present Hao Wu <haowu@dataset.sh>
#
# SPDX-License-Identifier: MIT

"""FFenc - File encryption and decryption tool."""

from .crypto import encrypt, decrypt

__all__ = ['encrypt', 'decrypt']
