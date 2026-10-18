"""Connectors: adapters to external services (see design ch09).

A connector wraps one service behind status() + call(). Credentials
are never passed in code: a connector asks security/credentials.py
for a value by *name* at call time.
"""
from muse_agent.connectors.base import Connector, ConnectorStatus
from muse_agent.connectors.registry import ConnectorRegistry
from muse_agent.connectors.echo import EchoConnector

__all__ = ["Connector", "ConnectorStatus", "ConnectorRegistry", "EchoConnector"]
