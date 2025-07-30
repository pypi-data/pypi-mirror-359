import requests
url = "http://localhost:7860/api/v1/run/a8f8b68c-6186-4daf-b075-4024bb2b0570"  # The complete API endpoint URL for this flow

# Request payload configuration
payload = {
    "input_value": "hello world!",  # The input value to be processed by the flow
    "output_type": "text",  # Specifies the expected output format
    "input_type": "text",  
    "tweaks": {
        "TextInput-FCe1H": {"input_value": "epaaa"},  # Example tweak to adjust the flow's behavior
        "TextInput-ZLrFC": {"input_value": "e"}  # Another example tweak
    },
}

# Request headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Send API request
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes

    # Print response
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except ValueError as e:
    print(f"Error parsing response: {e}")
    