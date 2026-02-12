#!/usr/bin/env python3
"""
Android GPS Controller - Control Android GPS spoofing apps via ADB
Supports Fake Traveler and Mock my GPS
"""

import subprocess
import json
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AndroidGPSController:
    """Control Android GPS spoofing apps via ADB"""

    # Supported apps
    APP_FAKE_TRAVELER = "com.igork.fakegps"
    APP_MOCK_MY_GPS = "com.example.mockgps"

    def __init__(self, device_id: Optional[str] = None, app_package: str = APP_FAKE_TRAVELER):
        """
        Initialize Android GPS controller

        Args:
            device_id: ADB device ID (None for first available device)
            app_package: Package name of GPS spoofing app
        """
        self.device_id = device_id
        self.app_package = app_package

    def _run_adb_command(self, command_parts: List[str]) -> Tuple[bool, str]:
        """
        Run ADB command and return result

        Args:
            command_parts: List of command parts

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            # Build command
            cmd = ["adb"]
            if self.device_id:
                cmd.extend(["-s", self.device_id])
            cmd.extend(command_parts)

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            output = result.stdout.strip()

            if not success and result.stderr:
                output += f"\nError: {result.stderr.strip()}"

            return success, output

        except subprocess.TimeoutExpired:
            logger.error(f"ADB command timed out: {' '.join(cmd)}")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"ADB command error: {str(e)}")
            return False, str(e)

    def list_connected_devices(self) -> List[Dict[str, str]]:
        """
        List all connected Android devices

        Returns:
            List of device info dicts with 'id' and 'status'
        """
        success, output = self._run_adb_command(["devices", "-l"])

        if not success:
            logger.error(f"Failed to list devices: {output}")
            return []

        devices = []
        lines = output.split('\n')[1:]  # Skip header

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) >= 2:
                device_info = {
                    'id': parts[0],
                    'status': parts[1]
                }

                # Extract device model if available
                for part in parts[2:]:
                    if part.startswith('model:'):
                        device_info['model'] = part.split(':', 1)[1]
                    elif part.startswith('device:'):
                        device_info['device'] = part.split(':', 1)[1]

                devices.append(device_info)

        return devices

    def check_device_connected(self) -> bool:
        """
        Check if the specified device is connected

        Returns:
            True if device is connected
        """
        if not self.device_id:
            return True  # Will use first available device

        devices = self.list_connected_devices()
        return any(d['id'] == self.device_id for d in devices)

    def enable_mock_location(self) -> bool:
        """
        Enable mock location for the GPS app

        Returns:
            True if successful
        """
        logger.info(f"Enabling mock location for {self.app_package}")

        success, output = self._run_adb_command([
            "shell", "appops", "set",
            self.app_package, "android:mock_location", "allow"
        ])

        if success:
            logger.info(f"Mock location enabled for {self.app_package}")
        else:
            logger.error(f"Failed to enable mock location: {output}")

        return success

    def disable_mock_location(self) -> bool:
        """
        Disable mock location for the GPS app

        Returns:
            True if successful
        """
        logger.info(f"Disabling mock location for {self.app_package}")

        success, output = self._run_adb_command([
            "shell", "appops", "set",
            self.app_package, "android:mock_location", "deny"
        ])

        if success:
            logger.info(f"Mock location disabled for {self.app_package}")
        else:
            logger.error(f"Failed to disable mock location: {output}")

        return success

    def set_location(self, latitude: float, longitude: float) -> bool:
        """
        Set GPS location on Android device

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            True if successful
        """
        logger.info(f"Setting location: {latitude}, {longitude}")

        # Method 1: Broadcast intent (preferred for Fake Traveler)
        success, output = self._run_adb_command([
            "shell", "am", "broadcast",
            "-a", f"{self.app_package}.SET_LOCATION",
            "--es", "lat", str(latitude),
            "--es", "lng", str(longitude)
        ])

        if success:
            logger.info(f"Location set successfully: {latitude}, {longitude}")
            return True

        # Method 2: Start activity with coordinates (fallback)
        logger.info("Trying alternative method: activity start")
        success, output = self._run_adb_command([
            "shell", "am", "start",
            "-n", f"{self.app_package}/.MainActivity",
            "--es", "latitude", str(latitude),
            "--es", "longitude", str(longitude),
            "--ez", "start_mock", "true"
        ])

        if success:
            logger.info(f"Location set via activity: {latitude}, {longitude}")
            return True

        logger.error(f"Failed to set location: {output}")
        return False

    def start_mocking(self) -> bool:
        """
        Start location mocking

        Returns:
            True if successful
        """
        logger.info("Starting location mocking")

        success, output = self._run_adb_command([
            "shell", "am", "start",
            "-n", f"{self.app_package}/.MainActivity",
            "--ez", "start_mock", "true"
        ])

        if success:
            logger.info("Location mocking started")
        else:
            logger.error(f"Failed to start mocking: {output}")

        return success

    def stop_mocking(self) -> bool:
        """
        Stop location mocking

        Returns:
            True if successful
        """
        logger.info("Stopping location mocking")

        # Method 1: Broadcast stop command
        success, output = self._run_adb_command([
            "shell", "am", "broadcast",
            "-a", f"{self.app_package}.STOP_MOCK"
        ])

        if success:
            logger.info("Location mocking stopped")
            return True

        # Method 2: Force stop the app (fallback)
        logger.info("Trying force stop")
        success, output = self._run_adb_command([
            "shell", "am", "force-stop", self.app_package
        ])

        if success:
            logger.info("App force-stopped")
        else:
            logger.error(f"Failed to stop mocking: {output}")

        return success

    def set_route(self, coordinates: List[Tuple[float, float]], speed_kmh: float = 5.0) -> bool:
        """
        Set route for movement simulation

        Args:
            coordinates: List of (lat, lng) tuples
            speed_kmh: Speed in km/h

        Returns:
            True if successful
        """
        logger.info(f"Setting route with {len(coordinates)} points at {speed_kmh} km/h")

        # Convert coordinates to JSON
        route_json = json.dumps(coordinates)

        success, output = self._run_adb_command([
            "shell", "am", "broadcast",
            "-a", f"{self.app_package}.SET_ROUTE",
            "--es", "route", route_json,
            "--es", "speed", str(speed_kmh)
        ])

        if success:
            logger.info("Route set successfully")
        else:
            logger.error(f"Failed to set route: {output}")

        return success

    def get_device_location(self) -> Optional[Dict[str, float]]:
        """
        Get current device location (for verification)

        Returns:
            Dict with 'latitude' and 'longitude' or None
        """
        success, output = self._run_adb_command([
            "shell", "dumpsys", "location"
        ])

        if not success:
            return None

        # Parse location from dumpsys output
        # This is a simplified parser - may need adjustment based on actual output
        try:
            for line in output.split('\n'):
                if 'mLocation' in line or 'latitude=' in line:
                    # Extract latitude and longitude
                    # (Implementation depends on actual output format)
                    pass
        except Exception as e:
            logger.error(f"Failed to parse location: {str(e)}")

        return None

    def get_device_info(self) -> Optional[Dict[str, str]]:
        """
        Get detailed device information

        Returns:
            Dict with device properties or None
        """
        success, output = self._run_adb_command([
            "shell", "getprop"
        ])

        if not success:
            return None

        props = {}
        for line in output.split('\n'):
            if ': [' in line:
                key, value = line.split(':[', 1)
                props[key.strip()] = value.rstrip(']')

        return props

    def install_app(self, apk_path: str) -> bool:
        """
        Install APK on device

        Args:
            apk_path: Path to APK file

        Returns:
            True if successful
        """
        logger.info(f"Installing APK: {apk_path}")

        success, output = self._run_adb_command([
            "install", "-r", apk_path
        ])

        if success:
            logger.info("APK installed successfully")
        else:
            logger.error(f"Failed to install APK: {output}")

        return success

    def check_app_installed(self, package: Optional[str] = None) -> bool:
        """
        Check if app is installed

        Args:
            package: Package name (defaults to self.app_package)

        Returns:
            True if app is installed
        """
        package = package or self.app_package

        success, output = self._run_adb_command([
            "shell", "pm", "list", "packages", package
        ])

        if success and package in output:
            logger.info(f"App {package} is installed")
            return True

        logger.warning(f"App {package} is not installed")
        return False

    def grant_permissions(self) -> bool:
        """
        Grant necessary permissions to GPS app

        Returns:
            True if successful
        """
        logger.info(f"Granting permissions to {self.app_package}")

        permissions = [
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.ACCESS_BACKGROUND_LOCATION"
        ]

        all_success = True
        for permission in permissions:
            success, output = self._run_adb_command([
                "shell", "pm", "grant", self.app_package, permission
            ])

            if not success:
                logger.warning(f"Failed to grant {permission}: {output}")
                all_success = False
            else:
                logger.info(f"Granted {permission}")

        return all_success

    def take_screenshot(self, output_path: str) -> bool:
        """
        Take device screenshot

        Args:
            output_path: Path to save screenshot

        Returns:
            True if successful
        """
        logger.info(f"Taking screenshot: {output_path}")

        # Capture screenshot to device
        success, output = self._run_adb_command([
            "shell", "screencap", "-p", "/sdcard/screenshot.png"
        ])

        if not success:
            logger.error(f"Failed to capture screenshot: {output}")
            return False

        # Pull screenshot to computer
        success, output = self._run_adb_command([
            "pull", "/sdcard/screenshot.png", output_path
        ])

        if success:
            logger.info(f"Screenshot saved: {output_path}")
        else:
            logger.error(f"Failed to pull screenshot: {output}")

        return success


def test_connection():
    """Test ADB connection and list devices"""
    controller = AndroidGPSController()
    devices = controller.list_connected_devices()

    print("Connected Android Devices:")
    for device in devices:
        print(f"  - ID: {device['id']}")
        print(f"    Status: {device['status']}")
        if 'model' in device:
            print(f"    Model: {device['model']}")

    return devices


if __name__ == "__main__":
    # Test ADB connection
    test_connection()
