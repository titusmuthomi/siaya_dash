from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# API Configuration
CONTRIBUTOR_API = "https://ausaakenya.com/api/transactions/totalperAccount/38"
JKUSDA_FUNDRAISER_URL = "https://fundraisers.jkusdachurch.org/fundraiser/6/"

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

        data = response.json()

        # Check if data exists
        if not data or 'total' not in data:
            return jsonify({
                'error': 'No contributor data available'
            }), 404

        # Extract total and last contributor
        total = data.get('total', 0)
        last_contribution = data.get('last_contribution', {})

        # Format last contributor to match old structure
        last_contributor = {
            'name': last_contribution.get('name', 'N/A'),
            'amount': int(last_contribution.get('amount', 0)) if last_contribution.get('amount') else 0,
            'created_at': last_contribution.get('created_at', None)
        }

        return jsonify({
            'status': 'success',
            'total': total,
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

@app.route('/api/combined-stats', methods=['GET'])
def get_combined_stats():
    """
    Returns combined statistics from both AUSAA and JKUSDA sources
    """
    try:
        # Fetch AUSAA data
        ausaa_response = requests.get(CONTRIBUTOR_API, timeout=10)
        ausaa_response.raise_for_status()
        ausaa_data = ausaa_response.json()

        ausaa_total = ausaa_data.get('total', 0)
        last_contribution = ausaa_data.get('last_contribution', {})
        ausaa_last = {
            'name': last_contribution.get('name', 'N/A'),
            'amount': int(last_contribution.get('amount', 0)) if last_contribution.get('amount') else 0,
            'created_at': last_contribution.get('created_at', None)
        }

        # Fetch JKUSDA data
        jkusda_response = requests.get(JKUSDA_FUNDRAISER_URL, timeout=10)
        jkusda_response.raise_for_status()
        soup = BeautifulSoup(jkusda_response.text, 'html.parser')
        text_content = soup.get_text()

        # Helper function
        def extract_number(text):
            if not text:
                return 0
            cleaned = re.sub(r'[Ksh,\s]', '', text)
            try:
                return int(cleaned)
            except ValueError:
                return 0

        # Extract JKUSDA stats
        jkusda_stats = {}

        target_match = re.search(r'TARGET:\s*\*?\*?(\d+)', text_content, re.IGNORECASE)
        if target_match:
            jkusda_stats['target'] = int(target_match.group(1))
        else:
            jkusda_stats['target'] = 3500000

        raised_match = re.search(r'TOTAL CONTRIBUTED.*?Ksh\s*([\d,]+)', text_content, re.IGNORECASE | re.DOTALL)
        jkusda_stats['total_raised'] = extract_number(raised_match.group(1)) if raised_match else 0

        contributors_match = re.search(r'NUMBER OF CONTRIBUTORS.*?(\d{1,5})', text_content, re.IGNORECASE | re.DOTALL)
        jkusda_stats['total_contributors'] = int(contributors_match.group(1)) if contributors_match else 0

        monthly_match = re.search(r'THIS MONTH.*?Ksh\s*([\d,]+)', text_content, re.IGNORECASE | re.DOTALL)
        jkusda_stats['this_month'] = extract_number(monthly_match.group(1)) if monthly_match else 0

        today_match = re.search(r'TODAY.*?Ksh\s*([\d,]+)', text_content, re.IGNORECASE | re.DOTALL)
        jkusda_stats['today'] = extract_number(today_match.group(1)) if today_match else 0

        # Calculate combined totals
        combined_total = ausaa_total + jkusda_stats['total_raised']
        combined_contributors = jkusda_stats['total_contributors']  # Only JKUSDA provides contributor count
        target = jkusda_stats['target']
        percentage = round((combined_total / target) * 100, 1) if target > 0 else 0

        return jsonify({
            'status': 'success',
            'combined': {
                'total_raised': combined_total,
                'total_contributors': combined_contributors,
                'target': target,
                'percentage': percentage,
                'remaining': target - combined_total
            },
            'ausaa': {
                'total': ausaa_total,
                'last_contributor': ausaa_last
            },
            'jkusda': jkusda_stats
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/jkusda-stats', methods=['GET'])
def get_jkusda_stats():
    """
    Scrapes JKUSDA fundraiser page and returns live statistics
    """
    try:
        # Fetch the JKUSDA fundraiser page
        response = requests.get(JKUSDA_FUNDRAISER_URL, timeout=10)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Helper function to extract numbers from text
        def extract_number(text):
            if not text:
                return 0
            # Remove "Ksh", commas, and whitespace, then extract number
            cleaned = re.sub(r'[Ksh,\s]', '', text)
            try:
                return int(cleaned)
            except ValueError:
                return 0

        # Extract statistics (adjust selectors based on actual page structure)
        stats = {}

        # Try to find the data - this will need to be adjusted based on actual HTML structure
        text_content = soup.get_text()

        # Extract target amount (look for "TARGET:" followed by a number)
        target_match = re.search(r'TARGET:\s*\*?\*?(\d+)', text_content, re.IGNORECASE)
        if target_match:
            stats['target'] = int(target_match.group(1))

        # Extract total raised (look for "TOTAL CONTRIBUTED" section)
        raised_match = re.search(r'TOTAL CONTRIBUTED.*?Ksh\s*([\d,]+)', text_content, re.IGNORECASE | re.DOTALL)
        if raised_match:
            stats['total_raised'] = extract_number(raised_match.group(1))

        # Extract contributors count (look for "NUMBER OF CONTRIBUTORS")
        contributors_match = re.search(r'NUMBER OF CONTRIBUTORS.*?(\d{1,5})', text_content, re.IGNORECASE | re.DOTALL)
        if contributors_match:
            stats['total_contributors'] = int(contributors_match.group(1))

        # Extract monthly total (look for "THIS MONTH'S DATA")
        monthly_match = re.search(r'THIS MONTH.*?Ksh\s*([\d,]+)', text_content, re.IGNORECASE | re.DOTALL)
        if monthly_match:
            stats['this_month'] = extract_number(monthly_match.group(1))

        # Extract today's total (look for "TODAY" section)
        today_match = re.search(r'TODAY.*?Ksh\s*([\d,]+)', text_content, re.IGNORECASE | re.DOTALL)
        if today_match:
            stats['today'] = extract_number(today_match.group(1))

        # Extract latest donation (look for amount with "mins ago" or "minutes ago")
        latest_match = re.search(r'Ksh\s*([\d,]+).*?(\d+)\s*mins?\s*ago', text_content, re.IGNORECASE | re.DOTALL)
        if latest_match:
            stats['latest_donation'] = extract_number(latest_match.group(1))

        # Set defaults if not found
        stats.setdefault('target', 3500000)
        stats.setdefault('total_raised', 0)
        stats.setdefault('total_contributors', 0)
        stats.setdefault('this_month', 0)
        stats.setdefault('today', 0)
        stats.setdefault('latest_donation', 0)

        # Calculate percentage
        if stats['target'] > 0:
            stats['percentage'] = round((stats['total_raised'] / stats['target']) * 100, 1)
        else:
            stats['percentage'] = 0

        return jsonify({
            'status': 'success',
            'stats': stats
        })

    except requests.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch JKUSDA data: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred while parsing JKUSDA data: {str(e)}'
        }), 500

@app.route('/')
def dashboard():
    """
    Serves the main dashboard page
    """
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
