#!/usr/bin/env python
"""
External IP Blocking Verification
Run from a different machine to verify IP blocking is working
"""

import socket
import subprocess
import sys
import time
from pathlib import Path


def test_ping(target_ip: str, timeout: int = 2) -> bool:
    """Test if target is reachable via ping"""
    try:
        # Cross-platform ping
        if sys.platform == "win32":
            cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), target_ip]
        else:
            cmd = ["ping", "-c", "1", "-W", str(timeout * 1000), target_ip]
        
        result = subprocess.run(cmd, capture_output=True, timeout=timeout + 1)
        return result.returncode == 0
    except Exception as e:
        return False


def test_http(target_url: str, timeout: int = 5) -> bool:
    """Test if HTTP endpoint is reachable"""
    try:
        import urllib.request
        import urllib.error
        
        with urllib.request.urlopen(target_url, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, socket.timeout):
        return False
    except Exception:
        return False


def test_tcp_connection(host: str, port: int, timeout: int = 3) -> bool:
    """Test if TCP port is reachable"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="External IP Blocking Verification"
    )
    parser.add_argument(
        "target",
        help="Target IP or hostname (e.g., 192.168.1.100)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Target port (default: 8000)"
    )
    parser.add_argument(
        "--test",
        choices=["ping", "http", "tcp", "all"],
        default="all",
        help="Test method"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"  EXTERNAL IP BLOCKING VERIFICATION")
    print(f"{'='*70}")
    
    print(f"\n🎯 Target: {args.target}:{args.port}")
    print(f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # PING Test
    if args.test in ["ping", "all"]:
        print("📡 PING Test:")
        reachable = test_ping(args.target)
        status = "✓ REACHABLE" if reachable else "✗ BLOCKED"
        print(f"   {status}\n")
        results["ping"] = reachable
    
    # TCP Test
    if args.test in ["tcp", "all"]:
        print("🔌 TCP Connection Test:")
        reachable = test_tcp_connection(args.target, args.port)
        status = "✓ REACHABLE" if reachable else "✗ BLOCKED"
        print(f"   {status}\n")
        results["tcp"] = reachable
    
    # HTTP Test
    if args.test in ["http", "all"]:
        print("🌐 HTTP Endpoint Test:")
        url = f"http://{args.target}:{args.port}/api/health"
        reachable = test_http(url)
        status = "✓ REACHABLE" if reachable else "✗ BLOCKED"
        print(f"   {status}\n")
        results["http"] = reachable
    
    # Summary
    print(f"{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}\n")
    
    for test_name, result in results.items():
        status = "✓ REACHABLE" if result else "✗ BLOCKED"
        print(f"  {test_name.upper():10} {status}")
    
    all_blocked = all(not v for v in results.values())
    any_blocked = any(not v for v in results.values())
    
    if all_blocked:
        print("\n✅ IP SUCCESSFULLY BLOCKED")
        print("   All connection methods failed (as expected)")
    elif any_blocked:
        reachable = sum(1 for v in results.values() if v)
        print(f"\n⚠ PARTIALLY REACHABLE ({reachable}/{len(results)} methods)")
        print("   Some connection types are blocked, others are open")
    else:
        print("\n❌ IP FULLY REACHABLE")
        print("   All connection methods succeeded")
        print("   Firewall rules may not be working")
    
    print(f"\n{'='*70}\n")
    
    return 0 if all_blocked else 1


if __name__ == "__main__":
    sys.exit(main())
