# Activity Service

RabbitMQ-backed activity feed service for the Event Booking backend.

## Why RabbitMQ

RabbitMQ is the better fit here than Kafka because this project needs lightweight service-to-service activity events, durable queues, and simple routing without Kafka's operational overhead.

## Event Contract

Other services should publish JSON messages like:

```json
{
  "user_id": 1,
  "message": "Created booking for event 7, seat A-10.",
  "source": "booking-service",
  "created_at": "2026-03-26T18:30:00+00:00"
}
```

Only `user_id` and `message` are required.

## Endpoints

- `GET /health`
- `GET /api/activity-service/activities`
- `GET /api/activity-service/activities/{activity_id}`

Authenticated users only see their own activities.
