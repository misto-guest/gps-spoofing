# 📍 GPS Campaign Manager - API Reference

Complete API documentation for the GPS Campaign Manager v2.2.

**Base URL**: `http://localhost:5002`

**Content-Type**: `application/json`

---

## 📊 Dashboard API

### Get Statistics

Get dashboard statistics including total campaigns, completed, running, and success rate.

```http
GET /api/dashboard/stats
```

**Response:**
```json
{
  "total_campaigns": 150,
  "completed": 120,
  "running": 5,
  "success_rate": 80
}
```

**Fields:**
- `total_campaigns` (integer): Total number of campaigns
- `completed` (integer): Number of completed campaigns
- `running` (integer): Number of currently running campaigns
- `success_rate` (integer): Success rate percentage (0-100)

---

### Get Chart Data

Get data for dashboard charts including status breakdown, account mode distribution, duration distribution, and 30-day trend.

```http
GET /api/dashboard/charts
```

**Response:**
```json
{
  "by_status": [
    {"status": "completed", "count": 120},
    {"status": "running", "count": 5},
    {"status": "pending", "count": 15},
    {"status": "failed", "count": 10}
  ],
  "by_mode": [
    {"account_mode": "normal", "count": 100},
    {"account_mode": "aggressive", "count": 30},
    {"account_mode": "stealth", "count": 20}
  ],
  "duration_distribution": [
    {"range": "< 1 hour", "count": 30},
    {"range": "1-4 hours", "count": 50},
    {"range": "4-8 hours", "count": 40},
    {"range": "> 8 hours", "count": 30}
  ],
  "trend_30days": [
    {"date": "2026-01-01", "count": 10},
    {"date": "2026-01-02", "count": 15}
  ]
}
```

**Fields:**
- `by_status` (array): Campaign count by status
- `by_mode` (array): Campaign count by account mode
- `duration_distribution` (array): Campaign count by duration range
- `trend_30days` (array): Campaign count per day for last 30 days

---

### Get Active Campaigns

Get list of active campaigns (pending or running status).

```http
GET /api/campaigns/active
```

**Response:**
```json
[
  {
    "id": "48c940cd",
    "name": "Test Campaign",
    "device_id": "device-1",
    "account_mode": "normal",
    "duration_hours": 4,
    "status": "running",
    "current_step": "Monitoring activity...",
    "progress": 60,
    "created_at": "2026-02-03 10:00:00",
    "started_at": "2026-02-03 10:01:00"
  }
]
```

**Fields:**
- `id` (string): Unique campaign identifier
- `name` (string): Campaign name
- `device_id` (string, optional): Associated device ID
- `account_mode` (string): Account mode (normal/aggressive/stealth)
- `duration_hours` (integer): Campaign duration in hours
- `status` (string): Campaign status (pending/running/completed/failed)
- `current_step` (string): Current execution step
- `progress` (float): Progress percentage (0-100)
- `created_at` (string): Creation timestamp
- `started_at` (string, optional): Start timestamp

---

## 🎯 Campaign Management API

### Create Campaign

Create a new GPS spoofing campaign.

```http
POST /api/campaigns
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "My Campaign",
  "device_id": "device-1",
  "account_mode": "normal",
  "duration_hours": 4
}
```

**Parameters:**
- `name` (string, required): Campaign name (1-100 characters)
- `device_id` (string, optional): Device ID to assign (max 50 characters)
- `account_mode` (string, optional): Account mode
  - Values: `"normal"`, `"aggressive"`, `"stealth"`
  - Default: `"normal"`
- `duration_hours` (integer, optional): Duration in hours
  - Range: 1-24
  - Default: 1

**Response (201 Created):**
```json
{
  "success": true,
  "campaign_id": "48c940cd",
  "message": "Campaign created successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Campaign name is required"
}
```

---

### Start Campaign

Start a pending campaign.

```http
POST /api/campaigns/{campaign_id}/start
```

**URL Parameters:**
- `campaign_id` (string, required): Campaign ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Campaign started"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Campaign not found"
}
```

**Socket.IO Event Emitted:**
```json
{
  "event": "campaign_started",
  "data": {
    "campaign_id": "48c940cd"
  }
}
```

---

### Delete Campaign

Delete a campaign and its logs.

```http
DELETE /api/campaigns/{campaign_id}
```

**URL Parameters:**
- `campaign_id` (string, required): Campaign ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Campaign deleted"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Error message"
}
```

---

## 🔌 Socket.IO Events

### Client → Server Events

#### Connect
```javascript
socket.on('connect', () => {
  console.log('Connected to server');
});
```

#### Disconnect
```javascript
socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

#### Refresh Dashboard
```javascript
socket.emit('refresh_dashboard');
```

**Server Response Event:**
```javascript
socket.on('dashboard_refreshed', (data) => {
  console.log('Dashboard refreshed', data);
});
```

---

### Server → Client Events

#### Connection Established
```javascript
socket.on('connect', (data) => {
  console.log(data.message); // "Connected to GPS Campaign Manager"
});
```

#### Campaign Created
```javascript
socket.on('campaign_created', (data) => {
  console.log('New campaign:', data.campaign_id);
  // Update UI
});
```

**Data:**
```json
{
  "campaign_id": "48c940cd",
  "name": "My Campaign"
}
```

#### Campaign Started
```javascript
socket.on('campaign_started', (data) => {
  console.log('Campaign started:', data.campaign_id);
  // Update UI to show running status
});
```

**Data:**
```json
{
  "campaign_id": "48c940cd"
}
```

#### Campaign Progress
```javascript
socket.on('campaign_progress', (data) => {
  console.log('Progress:', data.progress, '%');
  console.log('Step:', data.current_step);
  // Update progress bar
});
```

**Data:**
```json
{
  "campaign_id": "48c940cd",
  "current_step": "Monitoring activity...",
  "progress": 60
}
```

#### Campaign Completed
```javascript
socket.on('campaign_completed', (data) => {
  console.log('Campaign completed:', data.campaign_id);
  // Update UI to show completed status
});
```

**Data:**
```json
{
  "campaign_id": "48c940cd",
  "status": "completed"
}
```

---

## 📝 Code Examples

### Python

#### Create Campaign
```python
import requests

url = "http://localhost:5002/api/campaigns"
payload = {
    "name": "Test Campaign",
    "device_id": "device-1",
    "account_mode": "normal",
    "duration_hours": 4
}
response = requests.post(url, json=payload)
print(response.json())
# Output: {'success': True, 'campaign_id': '48c940cd', 'message': 'Campaign created successfully'}
```

#### Start Campaign
```python
campaign_id = "48c940cd"
url = f"http://localhost:5002/api/campaigns/{campaign_id}/start"
response = requests.post(url)
print(response.json())
# Output: {'success': True, 'message': 'Campaign started'}
```

#### Get Statistics
```python
url = "http://localhost:5002/api/dashboard/stats"
response = requests.get(url)
stats = response.json()
print(f"Total campaigns: {stats['total_campaigns']}")
print(f"Success rate: {stats['success_rate']}%")
```

---

### JavaScript (Browser)

#### Create Campaign
```javascript
const response = await fetch('http://localhost:5002/api/campaigns', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Test Campaign',
    device_id: 'device-1',
    account_mode: 'normal',
    duration_hours: 4
  })
});

const data = await response.json();
console.log(data);
// Output: {success: true, campaign_id: "48c940cd", message: "Campaign created successfully"}
```

#### Connect with Socket.IO
```javascript
const socket = io('http://localhost:5002');

socket.on('connect', () => {
  console.log('Connected to GPS Campaign Manager');
});

socket.on('campaign_created', (data) => {
  console.log('New campaign created:', data.campaign_id);
  alert('New campaign: ' + data.name);
});

socket.on('campaign_progress', (data) => {
  console.log(`Campaign progress: ${data.progress}%`);
  console.log(`Current step: ${data.current_step}`);
  // Update progress bar in UI
});
```

---

### cURL

#### Create Campaign
```bash
curl -X POST http://localhost:5002/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "device_id": "device-1",
    "account_mode": "normal",
    "duration_hours": 4
  }'
```

**Response:**
```json
{
  "success": true,
  "campaign_id": "48c940cd",
  "message": "Campaign created successfully"
}
```

#### Start Campaign
```bash
curl -X POST http://localhost:5002/api/campaigns/48c940cd/start
```

#### Get Statistics
```bash
curl http://localhost:5002/api/dashboard/stats
```

#### Delete Campaign
```bash
curl -X DELETE http://localhost:5002/api/campaigns/48c940cd
```

---

## 🔒 Authentication (Future Enhancement)

Currently, the API does not require authentication. This is planned for future releases.

**Planned Implementation:**
```http
GET /api/dashboard/stats
Authorization: Bearer <jwt_token>
```

---

## ⚠️ Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## 📊 Rate Limiting (Future Enhancement)

Currently, there are no rate limits on API endpoints. This is planned for future releases.

**Planned Implementation:**
- 200 requests per day per user
- 50 requests per hour per user
- 10 requests per minute for campaign creation

---

## 🧪 Testing the API

### Using Postman

1. Import API endpoints into Postman
2. Set base URL to `http://localhost:5002`
3. Create requests with appropriate headers and bodies
4. Send requests and view responses

### Using Python Script
```python
import requests

def test_api():
    # Create campaign
    response = requests.post('http://localhost:5002/api/campaigns', json={
        'name': 'Test Campaign',
        'duration_hours': 1
    })
    print('Create:', response.json())

    campaign_id = response.json()['campaign_id']

    # Start campaign
    response = requests.post(f'http://localhost:5002/api/campaigns/{campaign_id}/start')
    print('Start:', response.json())

    # Get stats
    response = requests.get('http://localhost:5002/api/dashboard/stats')
    print('Stats:', response.json())

if __name__ == '__main__':
    test_api()
```

---

## 📚 Additional Resources

- **Main README**: [GPS-README.md](GPS-README.md)
- **Enhancement Proposals**: [GPS-ENHANCEMENTS.md](GPS-ENHANCEMENTS.md)
- **Original Documentation**: [GPS-CAMPAIGN-COMPLETE.md](GPS-CAMPAIGN-COMPLETE.md)

---

**API Version**: 2.2
**Last Updated**: 2026-02-03
**Base URL**: http://localhost:5002

**Happy API integration!** 🚀
