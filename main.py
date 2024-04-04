from flask import Flask, jsonify, request, session
import uuid
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

CLOUD_SERVER_URL = 'http://127.0.0.1:5000'  # Replace with your cloud server URL

@app.route('/startSession', methods=['GET'])
def start_session():
    if 'session_started' in session:
        print('Session already started')
        return jsonify({'error': 'Session is already in progressss.'}), 400
    # Generate a unique token ID
    token_id = str(uuid.uuid4())

    # Start a session for the kiosk
    session['token_id'] = token_id
    session['session_started'] = True

    # Start a session with the token ID in the cloud server
    session_started_response = requests.post(f'{CLOUD_SERVER_URL}/startSession', data={'token_id': token_id})

    if session_started_response.status_code == 200:
        return jsonify({'message': 'Session started successfully.', 'token_id': token_id}), 200
    else:
        # Rollback session start in the kiosk if cloud session start fails
        session.pop('token_id', None)
        session.pop('session_started', None)
        return jsonify({'error': 'Failed to start session in the cloud server.'}), 500

@app.route('/endSession', methods=['GET'])
def end_session():
    if 'session_started' not in session:
        return jsonify({'error': 'No session to end.'}), 400

    # Clear the session data
    session.clear()

    # Trigger end session route in the cloud server
    cloud_end_session_response = requests.get(f'{CLOUD_SERVER_URL}/endSession')

    if cloud_end_session_response.status_code == '200':
        return jsonify({'message': 'Session ended successfully.'}), 200
    else:
        return jsonify({'error': 'Failed to end session in the cloud serverrr.'}), 500
if __name__ == '__main__':
    app.run(port=3000, debug=True)
