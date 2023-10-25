import requests
from datetime import datetime

# Define the URL where you want to send the POST request
url = 'http://127.0.0.1:5000/api/submit_event'

# Create a Python dictionary representing your JSON data
# Get the current date and time
current_time = datetime.now()

# Convert the current time to a timestamp
timestamp = current_time.timestamp()

transaction_data = [
    {
        "eventType": "TXN_AUTHED",
        "eventTime": datetime.now().timestamp(),
        "txnId": "t1",
        "amount": 900,
    },

    {
        "eventType": "TXN_SETTLED",
        "eventTime": datetime.now().timestamp(),
        "txnId": "t1",
        "amount": 850,
    },

    {
        "eventType": "TXN_AUTHED",
        "eventTime": datetime.now().timestamp(),
        "txnId": "t2",
        "amount": 50,
    },
    {
        "eventType": "PAYMENT_INITIATED",
        "eventTime": datetime.now().timestamp(),
        "txnId": "p1",
        "amount": -100,
    },
    {
        "eventType": "PAYMENT_POSTED",
        "eventTime": datetime.now().timestamp(),
        "txnId": "p1",
    }
]


headers = {
    'Content-Type': 'application/json',
}

for transaction in transaction_data:
    # Send the POST request
    response = requests.post(url, json=transaction, headers=headers)

    # Check the response
    if response.status_code == 200:
        print('Request was successful.')
        print(response.json())  # Parse the JSON response if applicable
    else:
        print(f'Request failed with status code {response.status_code}:')
        print(response.text)  # Print the response content

