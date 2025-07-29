data = {
    "group_type": "template",
    "name": "sort_descending_excluding_zero_results",
    "description": "Descending sort excluding zero-activity - shows only active users and chats",
    "filters": {
        "users": {
            "min_messages": 1, 
            "show_zero_activity": False,
            "exclude_system_users": True,
            "system_users": ["Tg.Stati Sign.Me"]
        },
        "chats": {"min_messages": 1, "show_zero_activity": False}
    },
    "sorting": {"users": "desc", "chats": "desc"},
    "formatting": {
        "header": "<b><u>{date}</u></b>\n",
        "total": "Всего: <code>{total_messages}</code>\n",
        "user_group_header": "<b>User group {user_group}:</b>\n\n",
        "user_section_header": "",  # Clean format without section header
        "user_line": "{name}: <code>{messages}</code> - {percentage:.2f}%\n",
        "chat_section_header": "\n<b>Monitoring group {monitoring_group}:</b>\n",
        "chat_line": "{title}: <code>{messages}</code> - {percentage:.2f}%\n"
    },
    "options": {
        "show_percentages": True,
        "round_percentages": 2,
        "telegram_formatting": True,
        "max_message_length": 4096,
        "date_format": "%d-%m-%Y"  # Format like in the example: 09-06-2025
    },
    "created_at": "2025-01-24T10:00:00.000000",
    "updated_at": "2025-06-12T01:10:00.000000",
} 