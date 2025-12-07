from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# API Configuration
CONTRIBUTOR_API = "https://dev.ausaakenya.com/api/transactions/given/14"

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """
    Aggregates contributor data and returns:
    - total: Sum of all contributions
    - last_contributor: The most recent contributor record
    """
    try:
        # Fetch data from the contributor API
        response = requests.get(CONTRIBUTOR_API, timeout=10)
        response.raise_for_status()

        contributors = response.json()

        # Check if data exists
        if not contributors or len(contributors) == 0:
            return jsonify({
                'error': 'No contributor data available'
            }), 404

        # Calculate total amount
        total = sum(item['amount'] for item in contributors)

        # Get last contributor (last record in the array)
        last_contributor = contributors[-1]

        return jsonify({
            'status': 'success',
            'total': total,
            'total_contributors': len(contributors),
            'last_contributor': last_contributor
        })

    except requests.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch contributor data: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/contributors', methods=['GET'])
def get_all_contributors():
    """
    Returns all contributor records from the source API
    """
    try:
        response = requests.get(CONTRIBUTOR_API, timeout=10)
        response.raise_for_status()

        contributors = response.json()

        return jsonify({
            'status': 'success',
            'count': len(contributors),
            'contributors': contributors
        })

    except requests.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch contributor data: {str(e)}'
        }), 500

@app.route('/')
def dashboard():
    """
    Serves the main dashboard page
    """
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
