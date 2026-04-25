#!/usr/bin/env python3
"""
Automated EDR System - Central Orchestrator
============================================

This is the main entry point for the entire EDR system.
It orchestrates the agent, detection engine, response engine, and API backend.

Usage:
    python main.py                    # Start backend API (default: http://127.0.0.1:8000)
    python main.py --frontend         # Start both backend and frontend
    python main.py --backend-only     # Start only the backend
    python main.py --help             # Show help

Environment Variables:
    EDR_SESSION_SECRET      - Session encryption secret (required for production)
    EDR_BACKEND_HOST        - Backend API host (default: 127.0.0.1)
    EDR_BACKEND_PORT        - Backend API port (default: 8000)
    EDR_FRONTEND_PORT       - Frontend dev server port (default: 5173)
    EDR_WATCH_PATH          - Path to monitor for file events (default: backend/watched)
    EDR_AUTO_START_AGENT    - Auto-start endpoint agent (default: true)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("edr.main")


class EDROrchestrator:
    """Main orchestrator for the EDR system."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        # Configuration
        self.backend_host = os.getenv("EDR_BACKEND_HOST", "127.0.0.1")
        self.backend_port = int(os.getenv("EDR_BACKEND_PORT", "8000"))
        self.frontend_port = int(os.getenv("EDR_FRONTEND_PORT", "5173"))
        
        # Subprocesses
        self.backend_process = None
        self.frontend_process = None

    def validate_environment(self) -> bool:
        """Validate that required files and environment are present."""
        logger.info("Validating environment...")
        
        # Check Python version
        if sys.version_info < (3, 11):
            logger.error(f"Python 3.11+ required, found {sys.version}")
            return False
        
        logger.info(f"✓ Python version: {sys.version.split()[0]}")
        
        # Check backend directory
        if not self.backend_dir.exists():
            logger.error(f"Backend directory not found: {self.backend_dir}")
            return False
        logger.info(f"✓ Backend directory found")
        
        # Check requirements.txt
        requirements_path = self.backend_dir / "requirements.txt"
        if not requirements_path.exists():
            logger.error(f"requirements.txt not found: {requirements_path}")
            return False
        logger.info(f"✓ Requirements file found")
        
        # Check config files
        config_dir = self.backend_dir / "config"
        if not config_dir.exists():
            logger.error(f"Config directory not found: {config_dir}")
            return False
        
        rules_path = config_dir / "rules.json"
        if not rules_path.exists():
            logger.error(f"Rules file not found: {rules_path}")
            return False
        logger.info(f"✓ Rules file found")
        
        settings_path = config_dir / "settings.json"
        if not settings_path.exists():
            logger.error(f"Settings file not found: {settings_path}")
            return False
        logger.info(f"✓ Settings file found")
        
        # Validate rules.json
        try:
            with open(rules_path) as f:
                rules = json.load(f)
                if not isinstance(rules, dict) or "rules" not in rules:
                    logger.error("Invalid rules.json format")
                    return False
                logger.info(f"✓ Loaded {len(rules['rules'])} detection rules")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid rules.json: {e}")
            return False
        
        return True

    def start_backend(self) -> bool:
        """Start the FastAPI backend server."""
        logger.info("Starting backend server...")
        
        env = os.environ.copy()
        
        # Set session secret if not already set
        if not env.get("EDR_SESSION_SECRET"):
            logger.warning(
                "⚠ EDR_SESSION_SECRET not set. Using default (INSECURE for production!)"
            )
            env["EDR_SESSION_SECRET"] = "change-this-secret-in-production"
        
        try:
            # Use uvicorn directly via Python module
            self.backend_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.app:app",
                    "--host",
                    self.backend_host,
                    "--port",
                    str(self.backend_port),
                    "--reload",
                ],
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            
            logger.info(f"✓ Backend started (PID: {self.backend_process.pid})")
            logger.info(f"  → API available at http://{self.backend_host}:{self.backend_port}")
            logger.info(f"  → Docs available at http://{self.backend_host}:{self.backend_port}/docs")
            
            # Give backend time to start
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            return False

    def start_frontend(self) -> bool:
        """Start the React frontend dev server."""
        logger.info("Starting frontend server...")
        
        if not self.frontend_dir.exists():
            logger.warning("Frontend directory not found, skipping frontend startup")
            return False
        
        try:
            # Check if node_modules exists
            node_modules = self.frontend_dir / "node_modules"
            if not node_modules.exists():
                logger.info("Installing frontend dependencies...")
                npm_install = subprocess.run(
                    ["npm", "install"],
                    cwd=str(self.frontend_dir),
                    capture_output=True,
                    timeout=120,
                )
                if npm_install.returncode != 0:
                    logger.error("Failed to install frontend dependencies")
                    logger.error(npm_install.stderr.decode())
                    return False
                logger.info("✓ Dependencies installed")
            
            # Start dev server
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            
            logger.info(f"✓ Frontend started (PID: {self.frontend_process.pid})")
            logger.info(f"  → Frontend available at http://localhost:{self.frontend_port}")
            
            # Give frontend time to start
            time.sleep(3)
            return True
            
        except FileNotFoundError:
            logger.error("npm not found. Please install Node.js and npm")
            return False
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return False

    def print_startup_info(self) -> None:
        """Print startup information."""
        logger.info("=" * 70)
        logger.info("EDR System Started Successfully!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("🔍 Backend API")
        logger.info(f"   URL: http://{self.backend_host}:{self.backend_port}")
        logger.info(f"   Docs: http://{self.backend_host}:{self.backend_port}/docs")
        logger.info("")
        
        if self.frontend_process:
            logger.info("🎨 Frontend")
            logger.info(f"   URL: http://localhost:{self.frontend_port}")
            logger.info("")
        
        logger.info("📋 Default Credentials")
        logger.info("   Email: admin@edr.local")
        logger.info("   Password: SecurePassword123!")
        logger.info("")
        logger.info("Press Ctrl+C to stop all services")
        logger.info("=" * 70)

    def cleanup(self, signum: int = None, frame: object = None) -> None:
        """Clean shutdown of all services."""
        logger.info("\nShutting down EDR system...")
        
        if self.frontend_process:
            logger.info("Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            logger.info("✓ Frontend stopped")
        
        if self.backend_process:
            logger.info("Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            logger.info("✓ Backend stopped")
        
        logger.info("EDR system stopped")
        sys.exit(0)

    def run_backend_only(self) -> NoReturn:
        """Run only the backend server."""
        logger.info("Starting EDR System (Backend Only)")
        logger.info("-" * 70)
        
        if not self.validate_environment():
            sys.exit(1)
        
        if not self.start_backend():
            sys.exit(1)
        
        self.print_startup_info()
        
        try:
            # Keep the main process running
            if self.backend_process:
                self.backend_process.wait()
        except KeyboardInterrupt:
            self.cleanup()

    def run_full_stack(self) -> NoReturn:
        """Run the complete EDR stack (backend + frontend)."""
        logger.info("Starting EDR System (Full Stack)")
        logger.info("-" * 70)
        
        if not self.validate_environment():
            sys.exit(1)
        
        if not self.start_backend():
            sys.exit(1)
        
        if not self.start_frontend():
            logger.warning("Frontend failed to start, continuing with backend only")
        
        self.print_startup_info()
        
        try:
            # Keep the main process running
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("Backend process exited unexpectedly")
                    self.cleanup()
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.warning("Frontend process exited")
                    
        except KeyboardInterrupt:
            self.cleanup()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated EDR System Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start backend only
  python main.py --frontend         # Start backend + frontend
  python main.py --backend-only     # Explicit backend-only mode

Environment Variables:
  EDR_SESSION_SECRET                # Session encryption secret
  EDR_BACKEND_HOST                  # Backend API host (default: 127.0.0.1)
  EDR_BACKEND_PORT                  # Backend API port (default: 8000)
  EDR_FRONTEND_PORT                 # Frontend dev port (default: 5173)
        """,
    )
    
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Start both backend and frontend servers",
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Start only the backend server (default)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="EDR System v0.3.0",
    )
    
    args = parser.parse_args()
    
    orchestrator = EDROrchestrator()
    
    # Set up signal handlers for clean shutdown
    import signal
    signal.signal(signal.SIGINT, orchestrator.cleanup)
    signal.signal(signal.SIGTERM, orchestrator.cleanup)
    
    # Determine which mode to run
    if args.frontend:
        orchestrator.run_full_stack()
    else:
        orchestrator.run_backend_only()


if __name__ == "__main__":
    main()
