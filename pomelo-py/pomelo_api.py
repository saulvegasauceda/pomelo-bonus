from flask import Flask, request, jsonify
from flask_cors import CORS
from event_parser import DataManager

app = Flask(__name__)
CORS(app)  # Allow all origins for development; restrict in production.

manager = DataManager(credit_limit=1000)

# Define an endpoint to get a summary
@app.route('/api/get_summary', methods=['GET'])
def get_summary():
    try:
        result = manager.summarize()
        return jsonify({'summary': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/submit_event', methods=['POST'])
def submit_payment():
    try:
        data = request.get_json()  # Get the JSON data from the request
        event_type = data.get('eventType')
        event_time = data.get('eventTime')
        txn_id = data.get('txnId')
        amount = data.get('amount')

        response_data = {
            'message': 'Payment data received successfully',
            'event_type': event_type,
            'event_time': event_time,
            'txn_id': txn_id,
            'amount': amount
        }

        manager.parse_event(data)
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
