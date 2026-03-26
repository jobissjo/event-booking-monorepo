# Notification Service

Robyn-based notification microservice for the Event Booking backend.

## Features

- Stores notifications in a `notifications` table
- Publishes persisted notifications to SSE clients
- Publishes persisted notifications to WebSocket clients
- Supports generic notification creation plus booking-driven notification creation
- Uses the same JWT secret and algorithm pattern as the existing services
- Exposes Robyn OpenAPI docs at `/docs`

## Endpoints

- `GET /health`
- `POST /api/notifications-service/notifications`
- `POST /api/notifications-service/notifications/from-booking`
- `GET /api/notifications-service/notifications`
- `GET /api/notifications-service/notifications/:notification_id`
- `PATCH /api/notifications-service/notifications/:notification_id/read`
- `PATCH /api/notifications-service/notifications/read-all?user_id=1`
- `GET /api/notifications-service/stream?user_id=1`
- `WS /api/notifications-service/ws?user_id=1&token=<jwt>`

## Local run

```bash
pip install -r requirements.txt
python app/main.py
```
