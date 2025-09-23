#!/usr/bin/env python3
"""
Package the lambda function for deployment
"""

import os
import zipfile
import shutil
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for the lambda function"""
    
    # Create temp directory for packaging
    package_dir = Path("package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy source files
    source_files = [
        "lambda_function.py",
        "services/",
        "repositories/", 
        "utils/"
    ]
    
    for item in source_files:
        source_path = Path(item)
        if source_path.is_file():
            shutil.copy2(source_path, package_dir)
        elif source_path.is_dir():
            shutil.copytree(source_path, package_dir / source_path.name)
    
    # Create zip file
    zip_path = Path("strands_agent_lambda.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Cleanup
    shutil.rmtree(package_dir)
    
    print(f"Deployment package created: {zip_path}")
    print(f"Package size: {zip_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    create_deployment_package()