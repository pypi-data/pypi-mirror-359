"""
Background Process Manager for Copper Sun Brass
Handles simple background process spawning as fallback.
"""

import subprocess
import sys
import os
import logging
import time
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class BackgroundProcessManager:
    """Manages simple background process spawning."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
    
    def start_background_process(self) -> Tuple[bool, str]:
        """Start simple background process."""
        try:
            # Cross-platform process creation
            kwargs = {}
            
            if sys.platform == "win32":
                # Windows: Create detached process
                kwargs['creationflags'] = subprocess.DETACHED_PROCESS
            else:
                # Unix: New session
                kwargs['start_new_session'] = True
            
            # Ensure log directory exists
            log_dir = self.project_root / ".brass"
            log_dir.mkdir(exist_ok=True)
            
            # Start background process
            process = subprocess.Popen([
                sys.executable, '-m', 'coppersun_brass', 'start',
                '--mode', 'adaptive',
                '--project', str(self.project_root)
            ],
            stdout=open(log_dir / "background.log", "w"),
            stderr=open(log_dir / "background.error.log", "w"),
            stdin=subprocess.DEVNULL,
            **kwargs
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if process.poll() is None:
                # Store PID for later reference
                pid_file = log_dir / "background.pid"
                pid_file.write_text(str(process.pid))
                
                return True, f"Background process started (PID: {process.pid})"
            else:
                return False, "Background process failed to start"
                
        except Exception as e:
            logger.error(f"Failed to start background process: {e}")
            return False, f"Background process start failed: {str(e)}"
    
    def is_background_running(self) -> bool:
        """Check if background process is running."""
        try:
            pid_file = self.project_root / ".brass" / "background.pid"
            if not pid_file.exists():
                return False
            
            pid = int(pid_file.read_text().strip())
            
            # Check if process is still running
            if sys.platform == "win32":
                result = subprocess.run([
                    "tasklist", "/FI", f"PID eq {pid}"
                ], capture_output=True, text=True)
                return str(pid) in result.stdout
            else:
                try:
                    os.kill(pid, 0)  # Send signal 0 to check if process exists
                    return True
                except OSError:
                    return False
                    
        except Exception:
            return False
    
    def stop_background_process(self) -> Tuple[bool, str]:
        """Stop background process."""
        try:
            pid_file = self.project_root / ".brass" / "background.pid"
            if not pid_file.exists():
                return True, "No background process found"
            
            pid = int(pid_file.read_text().strip())
            
            # Kill process
            if sys.platform == "win32":
                result = subprocess.run([
                    "taskkill", "/PID", str(pid), "/F"
                ], capture_output=True, text=True)
                success = result.returncode == 0
            else:
                try:
                    os.kill(pid, 15)  # SIGTERM
                    time.sleep(2)
                    os.kill(pid, 9)   # SIGKILL if still running
                    success = True
                except OSError:
                    success = True  # Process already dead
            
            # Clean up PID file
            pid_file.unlink(missing_ok=True)
            
            return success, "Background process stopped"
            
        except Exception as e:
            return False, f"Failed to stop background process: {str(e)}"