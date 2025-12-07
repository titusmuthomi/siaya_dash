# Siaya Mission Fundraiser Dashboard

A real-time dashboard for tracking contributions to the Siaya Mission fundraiser campaign.

## Features

- **Aggregated Statistics**: Total contributions, contributor count, and average contribution
- **Latest Contributor**: Real-time display of the most recent donor
- **Campaign Progress**: Overall fundraising progress and targets
- **Auto-refresh**: Dashboard updates every 30 seconds
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
siaya_dashboard/
├── app.py                  # Flask API server
├── requirements.txt        # Python dependencies
├── templates/
│   └── dashboard.html     # Dashboard UI
└── README.md              # This file
```

## API Endpoints

### 1. `/api/summary`
Returns aggregated contribution data:
```json
{
  "status": "success",
  "total": 123400,
  "total_contributors": 40,
  "last_contributor": {
    "name": "John Doe",
    "contact": "254712345678",
    "institution": "JKUAT",
    "grad_year": "2020",
    "chapter": "Nairobi",
    "amount": 500
  }
}
```

### 2. `/api/contributors`
Returns all contributor records:
```json
{
  "status": "success",
  "count": 40,
  "contributors": [...]
}
```

### 3. `/`
Serves the dashboard HTML page

## Installation

1. **Install Python** (3.8 or higher)
   - Download from [python.org](https://www.python.org/downloads/)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask Server**
   ```bash
   python app.py
   ```

2. **Access the Dashboard**
   - Open your browser and go to: `http://localhost:5000`
   - Or access from network: `http://YOUR_IP_ADDRESS:5000`

3. **Test the API**
   - Summary endpoint: `http://localhost:5000/api/summary`
   - All contributors: `http://localhost:5000/api/contributors`

## Data Sources

- **AUSAA Contributions**: `https://dev.ausaakenya.com/api/transactions/given/14`
- **JKUSDA Fundraiser**: `https://fundraisers.jkusdachurch.org/fundraiser/6/` (displayed as static data)

## Customization

### Change the Data Source
Edit `app.py` line 8:
```python
CONTRIBUTOR_API = "YOUR_API_URL_HERE"
```

### Modify Auto-refresh Interval
Edit `templates/dashboard.html` line 398:
```javascript
setInterval(loadDashboard, 30000);  // 30000ms = 30 seconds
```

### Update JKUSDA Statistics
Edit the static values in `templates/dashboard.html` around lines 250-280.

## Deployment

### Option 1: Local Network
- Run the server with `host='0.0.0.0'` (already configured)
- Access from any device on your network using your computer's IP address

### Option 2: Cloud Hosting (Heroku, PythonAnywhere, etc.)
1. Create a `Procfile`:
   ```
   web: python app.py
   ```
2. Deploy following your hosting provider's instructions

### Option 3: Production Server
- Use a production WSGI server like Gunicorn:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 app:app
  ```

## Troubleshooting

### Port Already in Use
Change the port in `app.py` line 61:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### CORS Errors
CORS is already enabled via `flask-cors`. If you still face issues, check your browser console.

### API Connection Issues
- Verify the contributor API is accessible
- Check your internet connection
- Ensure no firewall is blocking the requests

## License

This project is created for the AUSAA Kenya Siaya Mission fundraiser campaign.
