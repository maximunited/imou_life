"""
Validation script for Imou Life integration setup.
This script helps validate configuration and identify potential issues.
"""

import asyncio
import json
import logging
from typing import Any, Dict

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImouSetupValidator:
    """Validator for Imou integration setup."""

    def __init__(self):
        self.session = None
        self.results = {}

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def test_api_connectivity(
        self, api_url: str, app_id: str, app_secret: str
    ) -> Dict[str, Any]:
        """Test connectivity to Imou API."""
        print("🔍 Testing API connectivity...")

        try:
            # Test basic connectivity
            start_time = asyncio.get_event_loop().time()
            async with self.session.get(api_url, timeout=10) as response:
                elapsed = asyncio.get_event_loop().time() - start_time

                if response.status == 200:
                    print(f"  ✓ API endpoint reachable in {elapsed:.2f}s")
                    return {"status": "success", "response_time": elapsed}
                else:
                    print(f"  ❌ API endpoint returned status {response.status}")
                    return {"status": "error", "status_code": response.status}

        except asyncio.TimeoutError:
            print("  ❌ API endpoint timeout (>10s)")
            return {"status": "timeout"}
        except Exception as e:
            print(f"  ❌ API connectivity error: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def test_device_connectivity(
        self, api_url: str, app_id: str, app_secret: str, device_id: str
    ) -> Dict[str, Any]:
        """Test device connectivity and response."""
        print("🔍 Testing device connectivity...")

        try:
            # This would need the actual Imou API client to test properly
            # For now, we'll simulate the test
            print("  ⚠️  Device connectivity test requires Imou API client")
            print("  ⚠️  Please check device status in Home Assistant logs")
            return {"status": "skipped", "reason": "requires_api_client"}

        except Exception as e:
            print(f"  ❌ Device connectivity error: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the integration configuration."""
        print("🔍 Validating configuration...")

        required_fields = ["api_url", "app_id", "app_secret", "device_id"]
        missing_fields = []

        for field in required_fields:
            if field not in config or not config[field]:
                missing_fields.append(field)

        if missing_fields:
            print(f"  ❌ Missing required fields: {', '.join(missing_fields)}")
            return {"status": "error", "missing_fields": missing_fields}

        print("  ✓ All required fields present")

        # Validate API URL format
        api_url = config["api_url"]
        if not api_url.startswith("https://"):
            print("  ⚠️  API URL should use HTTPS")

        # Validate device ID format (basic check)
        device_id = config["device_id"]
        if len(device_id) < 10:
            print("  ⚠️  Device ID seems too short")

        return {"status": "success"}

    async def run_validation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete validation process."""
        print("=== Imou Life Integration Setup Validation ===\n")

        # Validate configuration
        config_result = await self.validate_configuration(config)
        self.results["configuration"] = config_result

        if config_result["status"] == "error":
            print("\n❌ Configuration validation failed. Please fix the issues above.")
            return self.results

        # Test API connectivity
        api_result = await self.test_api_connectivity(
            config["api_url"], config["app_id"], config["app_secret"]
        )
        self.results["api_connectivity"] = api_result

        # Test device connectivity
        device_result = await self.test_device_connectivity(
            config["api_url"],
            config["app_id"],
            config["app_secret"],
            config["device_id"],
        )
        self.results["device_connectivity"] = device_result

        # Generate recommendations
        await self.generate_recommendations()

        return self.results

    async def generate_recommendations(self):
        """Generate recommendations based on validation results."""
        print("\n=== Recommendations ===")

        if self.results.get("api_connectivity", {}).get("status") == "timeout":
            print("🚨 API connectivity is slow (>10s):")
            print("  - Check your internet connection")
            print("  - Verify the API URL is correct")
            print("  - Consider using a different DNS server")
            print("  - Check if Imou servers are experiencing issues")

        if self.results.get("api_connectivity", {}).get("status") == "error":
            print("🚨 API connectivity failed:")
            print("  - Verify the API URL is correct")
            print("  - Check if the API endpoint is accessible")
            print("  - Verify your network allows HTTPS connections")

        print("\n📋 General recommendations:")
        print("  - Enable debug logging in Home Assistant")
        print("  - Check Home Assistant logs for detailed error messages")
        print("  - Verify your Imou account has proper permissions")
        print("  - Ensure your device is online and accessible")
        print("  - Consider increasing setup timeout if needed")


async def main():
    """Main function to run the validation."""
    # Example configuration - replace with your actual values
    example_config = {
        "api_url": "https://openapi.easy4ip.com/openapi",
        "app_id": "your_app_id_here",
        "app_secret": "your_app_secret_here",
        "device_id": "your_device_id_here",
    }

    print("⚠️  Please update the configuration in this script with your actual values")
    print("⚠️  Or modify the script to read from your Home Assistant configuration\n")

    async with ImouSetupValidator() as validator:
        results = await validator.run_validation(example_config)

        print("\n=== Validation Complete ===")
        print(f"Results: {json.dumps(results, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
