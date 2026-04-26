#!/usr/bin/env python
"""Test Windows collectors."""
from backend.edr.agent.windows_collectors import (
    WindowsEventLogCollector,
    RegistryCollector,
    DNSCollector,
    ProcessInjectionDetector,
)


def test_collectors():
    """Test each collector and report results."""
    collectors = [
        WindowsEventLogCollector(),
        RegistryCollector(),
        DNSCollector(),
        ProcessInjectionDetector(),
    ]
    
    for collector in collectors:
        name = collector.__class__.__name__
        try:
            events = collector.collect()
            print(f"✓ {name}: {len(events)} events")
            if events:
                print(f"  Sample: {events[0]['event_type']} - {events[0].get('title', 'N/A')}")
        except Exception as e:
            print(f"✗ {name}: {type(e).__name__}: {str(e)[:80]}")


if __name__ == "__main__":
    test_collectors()
