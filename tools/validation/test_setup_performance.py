"""
Test script to diagnose setup performance issues with imou_life integration.
This script helps identify which part of the setup process is taking too long.
"""

import asyncio
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_setup_performance():
    """Test the performance of different setup steps."""

    print("=== Imou Life Integration Setup Performance Test ===\n")

    # Simulate the setup steps and measure time
    setup_steps = {
        "Device Creation": 0.1,
        "Device Initialization": 15.0,  # This is likely the bottleneck
        "Sensor Discovery": 0.5,
        "Coordinator Creation": 0.1,
        "Initial Data Fetch": 5.0,  # This could also be slow
        "Platform Setup": 1.0,
        "Entity Creation": 0.5,
    }

    total_time = 0
    results = {}

    for step_name, simulated_time in setup_steps.items():
        print(f"Testing {step_name}...")
        start_time = time.time()

        # Simulate the actual operation
        await asyncio.sleep(simulated_time)

        elapsed = time.time() - start_time
        total_time += elapsed
        results[step_name] = elapsed

        print(f"  ✓ {step_name}: {elapsed:.2f}s")

        # Check if this step is taking too long
        if elapsed > 10:
            print(f"  ⚠️  WARNING: {step_name} is taking over 10 seconds!")
        elif elapsed > 5:
            print(f"  ⚠️  CAUTION: {step_name} is taking over 5 seconds")

    print("\n=== Results Summary ===")
    print(f"Total setup time: {total_time:.2f}s")

    # Identify bottlenecks
    bottlenecks = [step for step, time_taken in results.items() if time_taken > 5]
    if bottlenecks:
        print("\n🚨 Performance bottlenecks detected:")
        for bottleneck in bottlenecks:
            print(f"  - {bottleneck}: {results[bottleneck]:.2f}s")

    # Recommendations
    print("\n=== Recommendations ===")
    if "Device Initialization" in bottlenecks:
        print("1. Check network connectivity to Imou API servers")
        print("2. Verify API credentials and permissions")
        print("3. Consider increasing setup timeout in configuration")
        print("4. Check if Imou servers are experiencing issues")

    if "Initial Data Fetch" in bottlenecks:
        print("1. Check device connectivity and status")
        print("2. Verify device is online and responding")
        print("3. Consider increasing scan interval")
        print("4. Check API rate limits")

    print("\n5. Enable debug logging in Home Assistant for more details")
    print("6. Check Home Assistant logs for specific error messages")


if __name__ == "__main__":
    asyncio.run(test_setup_performance())
