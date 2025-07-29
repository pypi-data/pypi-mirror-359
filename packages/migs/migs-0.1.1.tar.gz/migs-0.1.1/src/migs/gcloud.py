import json
import os
import subprocess
import time
from typing import Dict, List, Optional, Union


class AuthenticationError(Exception):
    """Raised when gcloud authentication is required"""
    pass


class GCloudWrapper:
    """Wrapper for gcloud CLI commands"""
    
    def _run_command(self, cmd: List[str], json_output: bool = True) -> Optional[Union[Dict, List, str]]:
        """Run a gcloud command and return the output"""
        if json_output and "--format" not in cmd:
            cmd.extend(["--format", "json"])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if json_output:
                return json.loads(result.stdout) if result.stdout else None
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Check for auth errors
            error_lower = e.stderr.lower()
            if any(msg in error_lower for msg in [
                "not authenticated",
                "could not find default credentials",
                "application default credentials",
                "gcloud auth login"
            ]):
                raise AuthenticationError("Not authenticated. Please run: gcloud auth login")
            
            print(f"Command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            return None
    
    def list_migs(self) -> List[Dict]:
        """List all MIGs in the current project"""
        cmd = ["gcloud", "compute", "instance-groups", "managed", "list"]
        result = self._run_command(cmd)
        
        if not result:
            return []
        
        migs = []
        for mig in result:
            zone = mig["zone"].split("/")[-1] if "/" in mig["zone"] else mig["zone"]
            migs.append({
                "name": mig["name"],
                "zone": zone,
                "size": int(mig.get("size", 0)),
                "targetSize": int(mig.get("targetSize", 0))
            })
        
        return migs
    
    def get_mig_zone(self, mig_name: str) -> Optional[str]:
        """Get the zone for a specific MIG"""
        migs = self.list_migs()
        for mig in migs:
            if mig["name"] == mig_name:
                return mig["zone"]
        raise ValueError(f"MIG '{mig_name}' not found")
    
    def create_resize_request(self, mig_name: str, zone: str, count: int, run_duration: Optional[str] = None) -> str:
        """Create a resize request to add instances"""
        request_id = f"migs-resize-{int(time.time())}"
        
        cmd = [
            "gcloud", "compute", "instance-groups", "managed",
            "resize-requests", "create", mig_name,
            f"--resize-request={request_id}",
            f"--resize-by={count}",
            f"--zone={zone}"
        ]
        
        if run_duration:
            cmd.append(f"--requested-run-duration={run_duration}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Check for auth errors
            error_lower = result.stderr.lower()
            if any(msg in error_lower for msg in [
                "not authenticated",
                "could not find default credentials",
                "application default credentials",
                "gcloud auth login"
            ]):
                raise AuthenticationError("Not authenticated. Please run: gcloud auth login")
            raise Exception(f"Failed to create resize request: {result.stderr}")
        
        return request_id
    
    def wait_for_vm(self, mig_name: str, zone: str, request_id: str, timeout: int = 300, progress_callback=None) -> Optional[Dict]:
        """Wait for a VM to be created and return its info"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            cmd = [
                "gcloud", "compute", "instance-groups", "managed",
                "resize-requests", "describe", mig_name,
                f"--resize-request={request_id}",
                f"--zone={zone}"
            ]
            
            result = self._run_command(cmd)
            if result and result.get("state") == "SUCCEEDED":
                instances = self.list_instances(mig_name, zone)
                if instances:
                    # Use instance ID as a proxy for creation order (higher ID = newer)
                    newest = max(instances, key=lambda x: int(x.get("id", "0")))
                    # Use the 'name' field directly instead of parsing 'instance' URL
                    return self.get_instance_details(newest["name"], zone)
            
            if progress_callback:
                progress_callback()
            
            time.sleep(5)
        
        return None
    
    def list_instances(self, mig_name: str, zone: str) -> List[Dict]:
        """List instances in a MIG"""
        cmd = [
            "gcloud", "compute", "instance-groups", "managed",
            "list-instances", mig_name,
            f"--zone={zone}"
        ]
        
        result = self._run_command(cmd)
        return result if isinstance(result, list) else []
    
    def get_instance_details(self, instance_name: str, zone: str) -> Optional[Dict]:
        """Get detailed info about an instance"""
        cmd = [
            "gcloud", "compute", "instances", "describe",
            instance_name,
            f"--zone={zone}"
        ]
        
        result = self._run_command(cmd)
        if not result:
            return None
        
        external_ip = None
        for interface in result.get("networkInterfaces", []):
            for config in interface.get("accessConfigs", []):
                if config.get("natIP"):
                    external_ip = config["natIP"]
                    break
        
        # Get the current username using whoami
        # This matches what gcloud compute ssh uses by default
        try:
            username_result = subprocess.run(["whoami"], capture_output=True, text=True, check=True)
            username = username_result.stdout.strip()
        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to determine username. The 'whoami' command failed.")
        
        return {
            "name": instance_name,
            "zone": zone,
            "external_ip": external_ip,
            "username": username,
            "status": result.get("status")
        }
    
    def delete_vm(self, instance_name: str, zone: str, mig_name: str) -> bool:
        """Delete a VM from a MIG"""
        cmd = [
            "gcloud", "compute", "instance-groups", "managed",
            "delete-instances", mig_name,
            f"--instances={instance_name}",
            f"--zone={zone}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def ssh_to_vm(self, instance_name: str, zone: str, extra_args: Optional[List[str]] = None, env_file: Optional[str] = None):
        """SSH into a VM using gcloud"""
        # Upload .env file if provided
        self._upload_env_file(env_file, instance_name, zone)
        
        cmd = [
            "gcloud", "compute", "ssh", instance_name,
            f"--zone={zone}"
        ]
        
        # If we have an env file, modify the command to source it in the shell
        if env_file and not extra_args:
            # Create a command that sources the env file and then starts an interactive bash shell
            cmd.extend([
                "--",
                "bash", "-c",
                "if [ -f /tmp/.env ]; then set -a; source /tmp/.env; set +a; fi; exec bash -l"
            ])
        elif extra_args:
            cmd.append("--")
            cmd.extend(extra_args)
        
        subprocess.run(cmd)
    
    def scp_to_vm(self, local_path: str, instance_name: str, zone: str, remote_path: Optional[str] = None) -> bool:
        """Upload files to a VM using gcloud scp"""
        if remote_path:
            # If remote_path doesn't start with / or ~, make it relative to home
            if not remote_path.startswith(('/', '~')):
                remote_path = f"~/{remote_path}"
            target = f"{instance_name}:{remote_path}"
        else:
            target = f"{instance_name}:~/"
        
        cmd = [
            "gcloud", "compute", "scp",
            "--recurse",
            local_path,
            target,
            f"--zone={zone}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and result.stderr:
            print(f"Upload error: {result.stderr}")
        return result.returncode == 0
    
    def scp_from_vm(self, remote_path: str, instance_name: str, zone: str, local_path: Optional[str] = None) -> bool:
        """Download files from a VM using gcloud scp"""
        # If remote_path doesn't start with / or ~, make it relative to home
        if not remote_path.startswith(('/', '~')):
            remote_path = f"~/{remote_path}"
        source = f"{instance_name}:{remote_path}"
        
        if not local_path:
            local_path = "."
        
        cmd = [
            "gcloud", "compute", "scp",
            "--recurse",
            source,
            local_path,
            f"--zone={zone}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and result.stderr:
            print(f"Download error: {result.stderr}")
        return result.returncode == 0
    
    def check_ssh_connectivity(self, instance_name: str, zone: str) -> bool:
        """Check if SSH connectivity is available to a VM"""
        cmd = [
            "gcloud", "compute", "ssh", instance_name,
            f"--zone={zone}",
            "--command", "echo 'Connection successful'"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and "Connection successful" in result.stdout
        except subprocess.TimeoutExpired:
            return False
    
    def _upload_env_file(self, env_file: Optional[str], instance_name: str, zone: str) -> bool:
        """Upload .env file to VM if provided"""
        if not env_file:
            return True
            
        cmd = [
            "gcloud", "compute", "scp",
            env_file,
            f"{instance_name}:/tmp/.env",
            f"--zone={zone}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: Failed to upload .env file")
        return result.returncode == 0
    
    def run_script(self, script_path: str, instance_name: str, zone: str, session_name: str, script_args: Optional[List[str]] = None, env_file: Optional[str] = None) -> bool:
        """Upload and run a script on a VM in a tmux session"""
        script_name = os.path.basename(script_path)
        
        # First upload the script
        remote_script = f"/tmp/{script_name}"
        upload_cmd = [
            "gcloud", "compute", "scp",
            script_path,
            f"{instance_name}:{remote_script}",
            f"--zone={zone}"
        ]
        
        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # Upload .env file if provided
        self._upload_env_file(env_file, instance_name, zone)
        
        # Build the command with arguments
        cmd_with_args = remote_script
        if script_args:
            # Properly escape arguments for shell
            escaped_args = ' '.join(f"'{arg}'" for arg in script_args)
            cmd_with_args = f"{remote_script} {escaped_args}"
        
        # Build the full command with optional env sourcing
        if env_file:
            full_command = f"chmod +x {remote_script} && tmux new-session -d -s {session_name} bash -c 'set -a; source /tmp/.env; set +a; {cmd_with_args}'"
        else:
            full_command = f"chmod +x {remote_script} && tmux new-session -d -s {session_name} {cmd_with_args}"
        
        # Make script executable and run in tmux
        run_cmd = [
            "gcloud", "compute", "ssh", instance_name,
            f"--zone={zone}",
            "--command",
            full_command
        ]
        
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        return result.returncode == 0