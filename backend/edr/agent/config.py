"""
Agent configuration for hybrid endpoint data collection.

Controls:
- Collection interval (60 seconds by default)
- Windows collectors (enables real Event Log collection)
- Remote agent support (future multi-endpoint capability)
"""

from __future__ import annotations

from dataclasses import dataclass
@dataclass
class AgentConfig:
    """Configuration for endpoint agent."""
    
    # Collection timing
    interval_seconds: float = 60
    """Collection interval in seconds. Default 60s for low overhead."""
    
    # Windows data collection
    enable_windows_event_logs: bool = True
    """Enable Windows Event Log collection (Security, System, Application)."""
    
    enable_registry_monitoring: bool = True
    """Enable Registry modification monitoring for persistence detection."""
    
    enable_dns_collection: bool = True
    """Enable DNS query collection for C2 detection."""
    
    enable_process_injection_detection: bool = True
    """Enable process injection/memory activity detection."""
    
    # Hybrid agent support
    agent_mode: str = "local"
    """Agent mode: 'local' (this machine), 'remote' (remote endpoint), 'hybrid' (both)."""
    
    remote_agent_urls: list[str] = None
    """URLs of remote agents for hybrid collection."""
    
    def __post_init__(self):
        """Initialize list fields."""
        if self.remote_agent_urls is None:
            self.remote_agent_urls = []


# Default configuration - uses REAL WINDOWS DATA ONLY
DEFAULT_CONFIG = AgentConfig(
    interval_seconds=60,
    enable_windows_event_logs=True,
    enable_registry_monitoring=True,
    enable_dns_collection=True,
    enable_process_injection_detection=True,
    agent_mode="local",
)


def get_agent_config() -> AgentConfig:
    """Get the real-data endpoint agent configuration."""
    return DEFAULT_CONFIG
