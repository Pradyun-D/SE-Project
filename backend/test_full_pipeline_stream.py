import sys

import requests


API_URL = "http://127.0.0.1:8000"


def main() -> None:
    health = requests.get(f"{API_URL}/health", timeout=30)
    health.raise_for_status()
    print(f"API health: {health.json()}")

    request = {
        "minimal_requirement": (
            "Users should link savings accounts and fetch financial statements using PAN and DOB "
            "with consent management, audit logging, and secure data retention."
        ),
        "scale": "Medium",
        "use_rag": True,
        "human_approved": True,
        "max_new_tokens": 2048,
        "temperature": 0.3,
        "top_p": 0.95,
    }
    response = requests.post(
        f"{API_URL}/generate",
        json=request,
        timeout=3600,
    )
    response.raise_for_status()
    result = response.json()
    print(f"Stream saved to: {result['stream_file']}")
    print(f"Response saved to: {result['response_file']}")
    print(f"Retrieved sources: {len(result['sources'])}")
    print(f"Extracted requirements: {len(result['extracted_requirements'])}")
    print("Full pipeline completed.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        print(f"Full pipeline stream failed: {error}")
        sys.exit(1)