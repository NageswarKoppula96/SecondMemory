from telegram import KeyboardButton, ReplyKeyboardMarkup


MEMORIES_BUTTON = "🧠 Memories"
TASKS_BUTTON = "✅ Tasks"
REMINDERS_BUTTON = "⏰ Reminders"
CHAT_BUTTON = "🤖 Chat"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(MEMORIES_BUTTON), KeyboardButton(TASKS_BUTTON)],
            [KeyboardButton(REMINDERS_BUTTON), KeyboardButton(CHAT_BUTTON)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )