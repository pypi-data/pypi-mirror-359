"""
CyborgDB Package Installer
Downloads and installs cyborgdb_core package at startup with optimized single API call
"""

import os
import sys
import requests
import subprocess
import platform
import tempfile
import logging
import importlib.metadata
import shutil
from urllib.parse import urlparse, unquote
from typing import Dict, Any, Optional, Tuple
from packaging import version
from .utils.endpoints import PACKAGE_ENDPOINT

logger = logging.getLogger(__name__)

def get_service_version() -> str:
    """
    Get the current service version from package metadata.
    This should match the version tagged in GitHub for cyborgdb-service.
    """
    try:
        # DEBUG: List all installed packages
        import importlib.metadata
        all_packages = [dist.metadata['name'] for dist in importlib.metadata.distributions()]
        logger.debug(f"All installed packages containing 'cyborg': {[p for p in all_packages if 'cyborg' in p.lower()]}")
    
        # Try to get version from the current package (cyborgdb-service)
        raw_version = importlib.metadata.version("cyborgdb-service")
        logger.debug(f"Raw service version from metadata: {raw_version}")
        
        # Handle development versions like "0.1.dev132"
        if any(tag in raw_version for tag in [".dev", ".staging"]):
            base_version = raw_version.split(".dev")[0].split(".staging")[0]
            # Ensure it has patch version
            if base_version.count('.') == 1:
                base_version += ".0"
            logger.debug(f"Development version detected, using base: {base_version}")
            return base_version
        
        return raw_version
    except importlib.metadata.PackageNotFoundError:
        # This should not happen in normal usage since this code IS part of cyborgdb-service
        logger.debug("Could not find cyborgdb-service package metadata - this installer should be part of cyborgdb-service")
        # Return a safe fallback, but this indicates a packaging issue
        fallback_version = "0.1.0"
        logger.debug(f"Using fallback version: {fallback_version}")
        return fallback_version

def get_minimum_package_version(service_version: str) -> str:
    """
    Calculate the minimum viable package version based on service version.
    Returns major.minor.0 of the service version.
    
    Examples:
    - Service v1.2.3 -> Minimum package v1.2.0
    - Service v2.1.5-alpha -> Minimum package v2.1.0
    """
    try:
        parsed_version = version.parse(service_version)
        min_version = f"{parsed_version.major}.{parsed_version.minor}.0"
        logger.debug(f"Minimum package version for service v{service_version}: v{min_version}")
        return min_version
    except Exception as e:
        logger.warning(f"Failed to parse service version {service_version}: {e}")
        return "0.10.0"  # Safe fallback

def get_system_info(current_version: str = None) -> Dict[str, Any]:
    """Get system information for package request"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    logger.debug(f"Raw platform info - system: {system}, machine: {machine}, python: {python_version}")
    
    # Map system names
    if system == "linux":
        os_name = "linux"
    elif system == "darwin":
        os_name = "darwin"
    else:
        raise ValueError(f"Unsupported OS: {system}")
    
    # Map architecture
    if machine in ["x86_64", "amd64"]:
        arch = "x86_64"  
    elif machine in ["aarch64", "arm64"]:
        arch = "aarch64"
    else:
        raise ValueError(f"Unsupported architecture: {machine}")
    
    # Get service version and calculate minimum package version
    service_version = get_service_version()
    minimum_package_version = get_minimum_package_version(service_version)
    
    # Use current version if available, otherwise use minimum required version
    effective_version = current_version or minimum_package_version
    
    system_info = {
        "pythonVersion": python_version,
        "os": os_name,
        "arch": arch,
        "serviceVersion": service_version,
        "minimumPackageVersion": minimum_package_version,
        "requestedVersion": effective_version
    }
    
    logger.debug(f"Generated system info: {system_info}")
    
    # Validate that all fields are non-empty strings
    for key, value in system_info.items():
        if not value or not isinstance(value, str) or value.strip() == "":
            raise ValueError(f"Invalid {key}: {value}")
    
    return system_info

def get_installed_package_version(package_name: str) -> Optional[str]:
    """Get version of installed package, return None if not installed"""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def is_version_compatible(package_version: str, service_version: str) -> bool:
    """
    Check if package version is compatible with service version.
    Package must be >= minimum required version (major.minor.0 of service).
    Development versions (e.g., 0.11.0.dev0) are considered compatible 
    with their base version (e.g., 0.11.0).
    """
    try:
        min_required = get_minimum_package_version(service_version)
        package_parsed = version.parse(package_version)
        min_required_parsed = version.parse(min_required)
        
        logger.debug(f"Version compatibility check: package={package_version}, service={service_version}, min_required={min_required}")
        
        # For development versions, compare base version
        if package_parsed.is_prerelease:
            # Create a base version without pre-release suffix
            package_base = version.Version(f"{package_parsed.major}.{package_parsed.minor}.{package_parsed.micro}")
            logger.debug(f"Comparing dev version base {package_base} >= {min_required_parsed}")
            is_compatible = package_base >= min_required_parsed
            logger.debug(f"Development version compatibility result: {is_compatible}")
            return is_compatible
        
        # For release versions, standard comparison
        is_compatible = package_parsed >= min_required_parsed
        logger.debug(f"Release version compatibility result: {is_compatible}")
        return is_compatible
        
    except Exception as e:
        logger.error(f"Version compatibility check failed: {e}")
        return False

def get_cloud_package_info(api_key: str, api_url: str, current_version: str = None) -> Optional[dict]:
    """Get package info (version + download URL) from the cloud"""
    system_info = get_system_info(current_version)
    
    headers = {
        "x-api-key": f"{api_key}",
        "Content-Type": "application/json"
    }
    
    logger.debug(f"Requesting package info from: {api_url}")
    logger.debug(f"Request payload: {system_info}")
    
    try:
        response = requests.post(
            api_url, 
            json=system_info, 
            headers=headers, 
            timeout=30
        )
        
        logger.debug(f"Response status: {response.status_code}")
        if response.status_code != 200:
            logger.debug(f"Response body: {response.text}")
            return None
        
        package_info = response.json()
        logger.debug(f"Package info response: {package_info}")
        download_url = package_info.get("downloadUrl", "")
        
        # Extract version from wheel filename
        parsed_url = urlparse(download_url)
        filename = os.path.basename(parsed_url.path)
        filename = unquote(filename)
        
        logger.debug(f"Wheel filename from Lambda: {filename}")
        
        if filename and filename.endswith(".whl"):
            parts = filename.split("-")
            if len(parts) >= 2:
                version_str = parts[1]
                logger.debug(f"Version extracted: {version_str}")
                
                # Verify the returned version meets minimum requirements
                service_version = get_service_version()
                is_compatible = is_version_compatible(version_str, service_version)
                logger.debug(f"Cloud package version {version_str} compatibility with service {service_version}: {is_compatible}")
                
                if not is_compatible:
                    logger.warning(f"Cloud returned incompatible version {version_str}, minimum required: {get_minimum_package_version(service_version)}")
                    return None
                
                return {
                    "version": version_str,
                    "download_url": download_url,
                    "checksum": package_info.get("checksum"),
                    "filename": filename
                }
        else:
            logger.debug(f"Invalid filename format or not a wheel: {filename}")
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get cloud package info: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def get_pypi_version(package_name: str) -> Optional[str]:
    """Get latest version from PyPI for lite package"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_version = data["info"]["version"]
            
            # Check if the latest PyPI version is compatible
            service_version = get_service_version()
            if is_version_compatible(latest_version, service_version):
                return latest_version
            else:
                logger.warning(f"Latest PyPI version {latest_version} is incompatible with service v{service_version}")
                # You might want to search through older versions here
                return None
    except Exception as e:
        logger.debug(f"Failed to get PyPI version for {package_name}: {e}")
    return None

def is_safe_update(current_version: str, latest_version: str, service_version: str = None) -> bool:
    """
    Check if update is safe and compatible.
    - Must be compatible with service version
    - Only allow patch version updates for existing installations
    - Allow major upgrades only if current version is below minimum required
    """
    try:
        current = version.parse(current_version)
        latest = version.parse(latest_version)
        
        # Always check service compatibility first
        if service_version and not is_version_compatible(latest_version, service_version):
            logger.debug(f"Update blocked: {latest_version} incompatible with service {service_version}")
            return False
        
        # If current version is below minimum required, allow upgrade to minimum
        if service_version:
            min_required = version.parse(get_minimum_package_version(service_version))
            if current < min_required:
                logger.debug(f"Allowing upgrade from {current_version} to {latest_version} to meet minimum requirement")
                return latest >= min_required
        
        # Standard patch-only update logic for compatible versions
        same_major_minor = (current.major == latest.major and current.minor == latest.minor)
        
        if not same_major_minor:
            return False
            
        # If patch versions are the same, allow prerelease -> release upgrade
        if current.micro == latest.micro:
            return current.is_prerelease and not latest.is_prerelease
        
        # For different patch versions, must be higher patch and not downgrade to prerelease
        return latest.micro > current.micro and not latest.is_prerelease
        
    except Exception as e:
        logger.debug(f"Version comparison failed: {e}")
        return False

def needs_update_core() -> tuple[bool, str, Optional[str], Optional[str]]:
    """
    Check if installed packages need updating (considering service compatibility)
    Returns: (needs_update, package_type, current_version, latest_version)
    """
    api_key = os.getenv("CYBORGDB_API_KEY")
    service_version = get_service_version()
    
    # Check for cyborgdb-core first
    core_version = get_installed_package_version("cyborgdb-core")
    if core_version:
        # Check if current version is compatible with service
        if not is_version_compatible(core_version, service_version):
            logger.debug(f"Current cyborgdb-core v{core_version} is incompatible with service v{service_version}, update required")
            if api_key:
                package_info = get_cloud_package_info(api_key, PACKAGE_ENDPOINT, core_version)
                if package_info:
                    return True, "core", core_version, package_info["version"]
            return True, "none", None, None  # Force fresh installation
        
        if api_key:
            package_info = get_cloud_package_info(api_key, PACKAGE_ENDPOINT, core_version)
            
            if package_info:
                cloud_version = package_info["version"]
                if is_safe_update(core_version, cloud_version, service_version):
                    return True, "core", core_version, cloud_version
                elif version.parse(cloud_version) > version.parse(core_version):
                    # Higher patch version available
                    logger.debug(f"CyborgDB Core v{cloud_version} is available (current: v{core_version})")
                    return False, "core", core_version, cloud_version
                
                return False, "core", core_version, cloud_version
        
        return False, "core", core_version, None
    
    # No core package installed
    return True, "none", None, None

def needs_update_lite() -> tuple[bool, str, Optional[str], Optional[str]]:
    """
    Check if cyborgdb-lite needs updating (considering service compatibility)
    Returns: (needs_update, package_type, current_version, latest_version)
    """
    service_version = get_service_version()

    # Check for cyborgdb-lite
    lite_version = get_installed_package_version("cyborgdb-lite")
    if lite_version:
        # Check compatibility with service
        if not is_version_compatible(lite_version, service_version):
            logger.debug(f"Current cyborgdb-lite v{lite_version} is incompatible with service v{service_version}, update required")
            pypi_version = get_pypi_version("cyborgdb-lite")
            if pypi_version:
                return True, "lite", lite_version, pypi_version
            return True, "none", None, None  # Force fresh installation
        
        pypi_version = get_pypi_version("cyborgdb-lite")
        
        if pypi_version:
            if is_safe_update(lite_version, pypi_version, service_version):
                return True, "lite", lite_version, pypi_version
            elif version.parse(pypi_version) > version.parse(lite_version):
                # Higher patch version available  
                logger.debug(f"CyborgDB Lite v{pypi_version} is available (current: v{lite_version})")
                return False, "lite", lite_version, pypi_version
            
            return False, "lite", lite_version, pypi_version
        
        return False, "lite", lite_version, None
    
    # No package installed
    return True, "none", None, None

def download_package_from_url(download_url: str, filename: str, expected_checksum: str = None) -> str:
    """Download package directly from provided URL"""
    logger.debug(f"Downloading package: {filename}")
    logger.debug(f"Download URL: {download_url}")
    
    try:
        # Download the wheel file
        wheel_response = requests.get(download_url, timeout=120)
        wheel_response.raise_for_status()
        
        # Validate checksum if provided
        if expected_checksum:
            import hashlib
            actual_checksum = hashlib.sha256(wheel_response.content).hexdigest()
            if actual_checksum != expected_checksum:
                raise ValueError(f"Checksum mismatch. Expected: {expected_checksum}, Got: {actual_checksum}")
            logger.debug("Package checksum validated successfully")
        
        # Save to temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, filename)

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(wheel_response.content)
        
        logger.debug(f"Saved wheel to: {temp_file_path}")
        return temp_file_path
            
    except requests.RequestException as e:
        raise ValueError(f"Network error during package download: {e}")

def install_wheel(wheel_path: str) -> None:
    """Install the downloaded wheel package"""
    logger.debug(f"Installing package from: {wheel_path}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", wheel_path, "--force-reinstall"
        ], capture_output=True, text=True, check=True)
        
        logger.info("Package installed successfully!")
        if result.stdout:
            logger.debug(result.stdout)
        
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Package installation failed: {e.stderr}")
    finally:
        # Clean up wheel file
        try:
            temp_dir = os.path.dirname(wheel_path)
            shutil.rmtree(temp_dir)
            logger.debug(f"Deleted temporary directory: {temp_dir}")
        except OSError as e:
            logger.debug(f"Failed to delete wheel file {wheel_path}: {e}")

def install_lite() -> None:
    """Install the latest cyborgdb-lite package"""
    try:
        # Get compatible version
        compatible_version = get_pypi_version("cyborgdb-lite")
        if not compatible_version:
            raise ValueError("No compatible cyborgdb-lite version found")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", f"cyborgdb-lite=={compatible_version}"
        ], capture_output=True, text=True, check=True)

        logger.debug("CyborgDB Lite package installed successfully!")
        if result.stdout:
            logger.debug(result.stdout)

    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to install cyborgdb-lite: {e.stderr}")

def install_cyborgdb_core() -> bool:
    """Main package installation function with service version compatibility"""
    service_version = get_service_version()
    logger.debug(f"CyborgDB Service version: {service_version}")
    logger.debug(f"Minimum required package version: {get_minimum_package_version(service_version)}")
    
    # Check if update is needed
    update_needed, package_type, current_version, latest_version = needs_update_core()
    
    if not update_needed:
        if package_type == "core":
            logger.info(f"CyborgDB Core is up to date (v{current_version})")
        elif package_type == "lite":
            logger.info(f"CyborgDB Lite is up to date (v{current_version})")
        return package_type == "core"
    
    # Log update information
    if package_type == "core" and current_version:
        logger.info(f"Updating CyborgDB Core from v{current_version} to v{latest_version}")
    elif package_type == "lite" and current_version:
        logger.info(f"Updating CyborgDB Lite from v{current_version} to v{latest_version}")
    else:
        logger.info("Installing CyborgDB package (no previous version found)")
    
    # Get configuration from environment
    api_key = os.getenv("CYBORGDB_API_KEY")
    if not api_key:
        logger.info("CYBORGDB_API_KEY not found, installing cyborgdb-lite instead")
        try:
            install_lite()
            new_version = get_installed_package_version("cyborgdb-lite")
            logger.info(f"CyborgDB Lite v{new_version} installed successfully")
            return False
        except Exception as lite_error:
            raise ValueError(
                "CYBORGDB_API_KEY environment variable is required for cyborgdb-core installation. "
                f"Fallback to cyborgdb-lite also failed: {lite_error}\n"
                "Please set your API key using one of these methods:\n"
                "1. Environment variable: export CYBORGDB_API_KEY=your_key_here\n"
                "2. .env file: echo 'CYBORGDB_API_KEY=your_key_here' > .env\n"
                "3. Docker run: docker run -e CYBORGDB_API_KEY=your_key_here ...\n"
                "4. Docker compose: CYBORGDB_API_KEY=your_key_here docker-compose up"
            )
    
    try:
        logger.info("=== Installing/Updating CyborgDB Core Package ===")
        
        # Get package info (version + download URL) in single API call
        package_info = get_cloud_package_info(api_key, PACKAGE_ENDPOINT, current_version)
        if not package_info:
            raise ValueError("Failed to get compatible package information from cloud")
        
        logger.debug(f"Package info received: {package_info['filename']} (v{package_info['version']})")
        
        # Download directly using provided URL
        wheel_path = download_package_from_url(
            package_info["download_url"], 
            package_info["filename"],
            package_info.get("checksum")
        )
        
        install_wheel(wheel_path)
        new_version = get_installed_package_version("cyborgdb-core")
        logger.info(f"=== CyborgDB Core v{new_version} Installation Complete ===")
        return True
        
    except Exception as e:
        logger.info(f"CyborgDB Core installation failed: {e}")
        logger.debug("Attempting to install cyborgdb-lite as fallback")

        update_needed, package_type, current_version, latest_version = needs_update_lite()

        if update_needed:
            try:
                install_lite()
                new_version = get_installed_package_version("cyborgdb-lite")
                logger.info(f"CyborgDB Lite v{new_version} installed successfully as fallback")
                return False
            except Exception as lite_error:
                logger.error(f"Fallback installation also failed: {lite_error}")
                raise ValueError(f"Both cyborgdb-core and cyborgdb-lite installation failed. Core: {e}, Lite: {lite_error}")
        else:
            logger.info(f"CyborgDB Lite v{current_version} does not require update")

def verify_installation() -> bool:
    """Verify that the installation was successful and packages are importable"""
    try:
        # Try to import cyborgdb_core first
        import cyborgdb_core
        version_str = get_installed_package_version("cyborgdb-core")
        service_version = get_service_version()
        
        if is_version_compatible(version_str, service_version):
            logger.debug(f"CyborgDB Core v{version_str} loaded successfully (compatible with service v{service_version})")
            return True
        else:
            logger.warning(f"CyborgDB Core v{version_str} loaded but may be incompatible with service v{service_version}")
            return True
    except ImportError:
        try:
            # Fall back to cyborgdb_lite
            import cyborgdb_lite
            version_str = get_installed_package_version("cyborgdb-lite")
            service_version = get_service_version()
            
            if is_version_compatible(version_str, service_version):
                logger.debug(f"CyborgDB Lite v{version_str} loaded successfully (compatible with service v{service_version})")
            else:
                logger.warning(f"CyborgDB Lite v{version_str} loaded but may be incompatible with service v{service_version}")
            return False
        except ImportError as e:
            logger.error(f"Failed to import any cyborgdb package: {e}")
            raise ValueError("CyborgDB package installation verification failed")