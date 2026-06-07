from app.core.event_bus import Event

"""
事件序列化工具类，提供将事件对象转换为可序列化格式的功能，主要用于日志记录、调试和数据分析等场景。
事件序列化工具类的主要职责包括：
1. serialize_events：将一系列事件对象转换为字典列表，保留事件的类型、来源、时间戳和数据内容，同时过滤掉不必要的字段（如数据库连接信息）。
2. extract_teaching_reply：从一系列事件中提取与教学相关的回复信息，优先提取教学响应事件中的回复内容，如果没有找到，则尝试提取提示响应事件中的提示文本，最后尝试提取鼓励事件中的消息内容，如果都没有找到，则返回None。
"""
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
