from app.core.event_bus import Event


def serialize_events(events: list[Event], limit: int = 10) -> list[dict]:
    result = []
    for event in events[-limit:]:
        data = {
            key: value
            for key, value in event.data.items()
            if key != "db"
        }
        result.append(
            {
                "type": event.type.value,
                "source": event.source,
                "timestamp": event.timestamp.isoformat(),
                "data": data,
            }
        )
    return result


def extract_teaching_reply(events: list[Event]) -> str | None:
    for event in reversed(events):
        if event.type.value == "tutor.teaching_response":
            return event.data.get("response")
        if event.type.value == "hint.response":
            return event.data.get("hint_text")
        if event.type.value == "engagement.encouragement":
            return event.data.get("message")
    return None
