"""
Simple test file for AskPablos API package.

This file demonstrates how to use the AskPablos API client to make real requests.
Replace the placeholder credentials with your actual API keys to test.
"""

from askpablos_api import AskPablos
import json


def test_basic_get_request():
    """Test basic GET request functionality."""
    print("Testing basic GET request...")

    # Initialize the client with your credentials
    client = AskPablos(
        api_key="SNXLjcXYG4RSCHA2uFPeMXaeyOTVTdhI",
        secret_key="485A4373B3452B7D27A2F25A45865"
    )

    try:
        # Simple GET request
        response = client.get("https://uk.farnell.com/panasonic/eehza1e101xp/cap-alu-elec-hybrid-100uf-25v/dp/2753119", browser=True, rotate_proxy=True)

        # response = client.get("https://httpbin.org/ip", browser=True)
        print(response.status_code)
        print("-" * 50)
        return True
    except Exception as e:
        print(e)
        return False


def test_spa_website_with_browser():
    """Test SPA website with browser automation - your example."""
    print("Testing SPA website with browser=True...")

    client = AskPablos(
        api_key="your_api_key",
        secret_key="your_secret_key"
    )

    try:
        # Your exact example
        response = client.get(
            "https://spa-website.com",
            browser=True
        )
        print(f"✅ SPA request with browser successful!")
        print(f"Status Code: {response['status_code']}")
        print(f"Content Length: {len(response['content'])} characters")
        print(f"Time Taken: {response['time_taken']}s")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ SPA request failed: {e}")
        return False


def test_api_with_params():
    """Test API request with query parameters."""
    print("Testing API request with parameters...")

    client = AskPablos(
        api_key="your_api_key",
        secret_key="your_secret_key"
    )

    try:
        response = client.get(
            "https://httpbin.org/get",
            params={"page": "1", "limit": "10", "test": "askpablos"}
        )
        print(f"✅ API request with params successful!")
        print(f"Status Code: {response['status_code']}")
        print(f"Response Content: {response['content'][:200]}...")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ API request with params failed: {e}")
        return False


def test_custom_headers():
    """Test request with custom headers."""
    print("Testing request with custom headers...")

    client = AskPablos(
        api_key="your_api_key",
        secret_key="your_secret_key"
    )

    try:
        response = client.get(
            "https://httpbin.org/headers",
            headers={"User-Agent": "AskPablos-Test-Client", "X-Test": "true"}
        )
        print(f"✅ Request with custom headers successful!")
        print(f"Status Code: {response['status_code']}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Request with headers failed: {e}")
        return False


def test_different_options():
    """Test request with different proxy options."""
    print("Testing request with different options...")

    client = AskPablos(
        api_key="your_api_key",
        secret_key="your_secret_key"
    )

    try:
        response = client.get(
            "https://httpbin.org/user-agent",
            browser=False,
            rotate_proxy=True,
            timeout=30,
            user_agent="Mozilla/5.0 (AskPablos Bot)"
        )
        print(f"✅ Request with options successful!")
        print(f"Status Code: {response['status_code']}")
        print(f"Response: {response['content']}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Request with options failed: {e}")
        return False


test_basic_get_request()

# def run_all_tests():
#     """Run all test functions."""
#     print("=" * 60)
#     print("🚀 Starting AskPablos API Tests")
#     print("=" * 60)
#     print()
#
#     tests = [
#         test_basic_get_request,
#         test_spa_website_with_browser,
#         test_api_with_params,
#         test_custom_headers,
#         test_different_options
#     ]
#
#     passed = 0
#     total = len(tests)
#
#     for test in tests:
#         if test():
#             passed += 1
#         print()
#
#     print("=" * 60)
#     print(f"📊 Test Results: {passed}/{total} tests passed")
#     print("=" * 60)
#
#     if passed == total:
#         print("🎉 All tests passed! Your AskPablos API package is working correctly.")
#     else:
#         print("⚠️  Some tests failed. Check your API credentials and connection.")


if __name__ == "__main__":
    print("AskPablos API Test Suite")
    print("=" * 60)
    print("IMPORTANT: Replace 'your_api_key' and 'your_secret_key' with real credentials!")
    print("=" * 60)
    print()

    # Uncomment the line below to run all tests
    # run_all_tests()

    # Or run individual tests:
    print("To run tests, uncomment one of these lines:")
    print("# run_all_tests()  # Run all tests")
    print("# test_basic_get_request()  # Test basic GET")
    print("# test_spa_website_with_browser()  # Test your SPA example")
