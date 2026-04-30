"""Agent package."""

from backend.edr.agent.collectors import (
    CommandActivityCollector,
    ProcessCollector,
    NetworkCollector,
    FileCollector,
)
from backend.edr.agent.windows_collectors import (
    WindowsEventLogCollector,
    RegistryCollector,
    DNSCollector,
    ProcessInjectionDetector,
)
from backend.edr.agent.service import EndpointAgent
from backend.edr.agent.config import AgentConfig, DEFAULT_CONFIG, get_agent_config

__all__ = [
    "CommandActivityCollector",
    "ProcessCollector",
    "NetworkCollector",
    "FileCollector",
    "WindowsEventLogCollector",
    "RegistryCollector",
    "DNSCollector",
    "ProcessInjectionDetector",
    "EndpointAgent",
    "AgentConfig",
    "DEFAULT_CONFIG",
    "get_agent_config",
]
