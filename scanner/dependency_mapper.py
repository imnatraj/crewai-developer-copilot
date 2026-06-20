import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, List

class DependencyMapper:
    """
    Layer 2 Static Analysis Dependency Engine.
    Executes madge and dependency-cruiser to capture structural relations.
    """
    def __init__(self, copilot_dir: str = None):
        if copilot_dir is None:
            # Assume we are in /home/acer/Downloads/crewai-developer-copilot
            self.copilot_dir = Path(__file__).resolve().parent.parent
        else:
            self.copilot_dir = Path(copilot_dir)
            
        self.madge_bin = self.copilot_dir / "node_modules" / ".bin" / "madge"
        self.depcruise_bin = self.copilot_dir / "node_modules" / ".bin" / "depcruise"

    def run_madge(self, target_path: str) -> Dict[str, List[str]]:
        """
        Runs madge on target path and returns parsed JSON.
        """
        # Fallback to 'npx madge' if local bin is not found
        cmd = [str(self.madge_bin)] if self.madge_bin.exists() else ["npx", "madge"]
        cmd.extend(["--json", target_path])
        
        try:
            # Exclude node_modules from search by default via cwd/env parameters if needed
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                check=False
            )
            
            # Extract JSON output
            if result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Look for JSON block in output
                    start_idx = result.stdout.find("{")
                    end_idx = result.stdout.rfind("}")
                    if start_idx != -1 and end_idx != -1:
                        return json.loads(result.stdout[start_idx:end_idx+1])
            return {}
        except Exception as e:
            # Return empty mapping on error
            return {}

    def run_dependency_cruiser(self, target_path: str) -> Dict[str, Any]:
        """
        Runs dependency-cruiser on target path and returns parsed JSON.
        """
        cmd = [str(self.depcruise_bin)] if self.depcruise_bin.exists() else ["npx", "depcruise"]
        cmd.extend(["--output-type", "json", "--exclude", "node_modules", target_path])
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    start_idx = result.stdout.find("{")
                    end_idx = result.stdout.rfind("}")
                    if start_idx != -1 and end_idx != -1:
                        return json.loads(result.stdout[start_idx:end_idx+1])
            return {}
        except Exception as e:
            return {}

    def get_dependencies(self, target_path: str) -> List[Dict[str, str]]:
        """
        Retrieves all dependency relationships in format [{"source": "...", "target": "..."}].
        """
        madge_data = self.run_madge(target_path)
        dependencies = []
        
        for source, targets in madge_data.items():
            # Clean paths
            clean_source = source.replace("\\", "/")
            for target in targets:
                clean_target = target.replace("\\", "/")
                dependencies.append({
                    "source": clean_source,
                    "target": clean_target,
                    "type": "madge"
                })
                
        # Supplement with dependency-cruiser details if needed
        cruise_data = self.run_dependency_cruiser(target_path)
        modules = cruise_data.get("modules", [])
        for mod in modules:
            source = mod.get("source", "").replace("\\", "/")
            for dep in mod.get("dependencies", []):
                target = dep.get("resolved", "").replace("\\", "/")
                dep_type = "package" if dep.get("coreModule", False) else "relative"
                
                # Check if relationship already exists
                exists = any(d["source"] == source and d["target"] == target for d in dependencies)
                if not exists and source and target:
                    dependencies.append({
                        "source": source,
                        "target": target,
                        "type": dep_type
                    })
                    
        return dependencies
