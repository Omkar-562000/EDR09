"""Agent package."""

from backend.edr.agent.collectors import (
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
from backend.edr.agent.config import AgentConfig, DEFAULT_CONFIG, DEMO_CONFIG, get_agent_config
from backend.edr.agent.demo_data import DemoDataGenerator, get_demo_generator

__all__ = [
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
    "DEMO_CONFIG",
    "get_agent_config",
    "DemoDataGenerator",
    "get_demo_generator",
]
