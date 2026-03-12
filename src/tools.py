"""
MCP Tools Module

This module manages the global GMA2 telnet client instance used by
the MCP server tools defined in server.py, and shared by resources.py
and prompts.py.
"""

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv

from src.telnet_client import GMA2TelnetClient

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration (read once at import time)
GMA_HOST = os.getenv("GMA_HOST", "127.0.0.1")
GMA_PORT = int(os.getenv("GMA_PORT", "30000"))
GMA_USER = os.getenv("GMA_USER", "administrator")
GMA_PASSWORD = os.getenv("GMA_PASSWORD", "admin")

# Global GMA2 client instance
_client: GMA2TelnetClient | None = None
_connected: bool = False
_client_lock = asyncio.Lock()


def set_gma2_client(client: GMA2TelnetClient) -> None:
    """
    Set the global GMA2 client instance.

    Args:
        client: GMA2TelnetClient instance
    """
    global _client, _connected
    _client = client
    _connected = client is not None


async def get_client() -> GMA2TelnetClient:
    """
    Get or create a telnet client instance (async).

    On first call, establishes connection and login. Subsequent calls return
    the already connected client. If the connection has dropped, reconnects
    automatically. Uses an asyncio.Lock to prevent concurrent connection attempts.
    """
    global _client, _connected

    async with _client_lock:
        # Check if existing connection is still healthy
        if _client is not None and _connected and not _client.is_connected:
            logger.warning("Connection lost, reconnecting...")
            _connected = False

        if _client is None or not _connected:
            _client = GMA2TelnetClient(
                host=GMA_HOST,
                port=GMA_PORT,
                user=GMA_USER,
                password=GMA_PASSWORD,
            )
            try:
                await _client.connect()
                await _client.login()
                _connected = True
                logger.info(f"Connected to grandMA2: {GMA_HOST}:{GMA_PORT}")
            except Exception:
                _connected = False
                raise

        return _client


def parse_listvar(raw: str, filter_prefix: str | None = None) -> dict[str, str]:
    """Parse ListVar telnet output into a {$NAME: value} dict.

    ListVar lines have the format:  $Global : $VARNAME = VALUE
    """
    variables: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if "=" not in line or line.startswith("["):
            continue
        # Strip scope prefix: "$Global : $VARNAME = VALUE" → "$VARNAME = VALUE"
        if " : " in line:
            _, _, line = line.partition(" : ")
            line = line.strip()
        name, _, value = line.partition("=")
        name = name.strip().lstrip("$")
        value = value.strip()
        if not name:
            continue
        if filter_prefix is None or name.upper().startswith(filter_prefix.upper()):
            variables[f"${name}"] = value
    return variables
