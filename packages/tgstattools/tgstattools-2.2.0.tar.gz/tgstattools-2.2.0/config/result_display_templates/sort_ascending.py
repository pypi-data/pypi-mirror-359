data = {
    "group_type": "template",
    "name": "sort_ascending",
    "description": "Ascending sort - shows all users and chats in ascending order including zero activity",
    "filters": {
        "users": {"min_messages": 0, "show_zero_activity": True},
        "chats": {"min_messages": 0, "show_zero_activity": True}
    },
    "sorting": {"users": "asc", "chats": "asc"},
    "formatting": {
        "header": "<b><u>{date}</u></b>\n",
        "total": "Всего: <code>{total_messages}</code>\n",
        "user_group_header": "<b>Группа пользователей:</b> {user_group}\n\n",
        "user_section_header": "",  # Clean format without section header
        "user_line": "{name}: <code>{messages}</code> - {percentage:.2f}%\n",
        "chat_section_header": "\n<b>Статистика по чатам ({monitoring_group}):</b>\n",
        "chat_line": "{title}: <code>{messages}</code> - {percentage:.2f}%\n"
    },
    "options": {
        "show_percentages": True,
        "round_percentages": 2,
        "telegram_formatting": True,
        "max_message_length": 4096,
        "date_format": "%d-%m-%Y"
    },
    "created_at": "2025-06-12T01:00:00.000000",
    "updated_at": "2025-06-12T01:20:00.000000",
} 