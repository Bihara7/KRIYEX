"""Application service for persistent, local-first conversations."""

from datetime import UTC, datetime

from kriyex.domain.models import Chat, Message, MessageRole
from kriyex.infrastructure.database import Database


def _as_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ChatService:
    def __init__(self, database: Database) -> None:
        self._database = database
        self._private_mode = False
        self._private_messages: list[Message] = []
        self._private_chat_id = -1

    def set_private_mode(self, enabled: bool) -> None:
        self._private_mode = enabled
        if enabled:
            self._private_messages.clear()

    def is_private_mode(self) -> bool:
        return self._private_mode

    def create_chat(self, title: str = "New conversation") -> Chat:
        if self._private_mode:
            self._private_messages.clear()
            now = datetime.now(UTC)
            return Chat(self._private_chat_id, "Private conversation", now, now)
        with self._database.connection() as connection:
            cursor = connection.execute("INSERT INTO chats(title) VALUES (?)", (title,))
            row = connection.execute("SELECT * FROM chats WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return self._to_chat(row)

    def list_chats(self, search: str = "") -> list[Chat]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """SELECT * FROM chats WHERE title LIKE ?
                   ORDER BY pinned DESC, updated_at DESC, id DESC""",
                (f"%{search.strip()}%",),
            ).fetchall()
        return [self._to_chat(row) for row in rows]

    def rename_chat(self, chat_id: int, title: str) -> None:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("A chat title is required.")
        with self._database.connection() as connection:
            connection.execute(
                "UPDATE chats SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (clean_title, chat_id),
            )

    def set_pinned(self, chat_id: int, pinned: bool) -> None:
        with self._database.connection() as connection:
            connection.execute("UPDATE chats SET pinned = ? WHERE id = ?", (pinned, chat_id))

    def delete_chat(self, chat_id: int) -> None:
        with self._database.connection() as connection:
            connection.execute("DELETE FROM chats WHERE id = ?", (chat_id,))

    def messages(self, chat_id: int) -> list[Message]:
        if self._private_mode and chat_id == self._private_chat_id:
            return list(self._private_messages)
        with self._database.connection() as connection:
            rows = connection.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY id", (chat_id,)).fetchall()
        return [Message(row["id"], row["chat_id"], MessageRole(row["role"]), row["content"], _as_datetime(row["created_at"])) for row in rows]

    def add_message(self, chat_id: int, role: MessageRole, content: str) -> Message:
        if self._private_mode and chat_id == self._private_chat_id:
            message = Message(
                len(self._private_messages) + 1,
                chat_id,
                role,
                content,
                datetime.now(UTC),
            )
            self._private_messages.append(message)
            return message
        with self._database.connection() as connection:
            cursor = connection.execute("INSERT INTO messages(chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role.value, content))
            connection.execute("UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (chat_id,))
            row = connection.execute("SELECT * FROM messages WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return Message(row["id"], row["chat_id"], MessageRole(row["role"]), row["content"], _as_datetime(row["created_at"]))

    def start_turn(self, chat_id: int, prompt: str) -> list[Message]:
        self.add_message(chat_id, MessageRole.USER, prompt)
        self._set_initial_title(chat_id, prompt)
        return self.messages(chat_id)

    def complete_turn(self, chat_id: int, response: str) -> Message:
        return self.add_message(chat_id, MessageRole.ASSISTANT, response)

    def previous_user_message(self, chat_id: int) -> Message | None:
        """Return the user message immediately before the latest user turn."""
        user_messages = [
            message
            for message in self.messages(chat_id)
            if message.role == MessageRole.USER
        ]
        return user_messages[-2] if len(user_messages) >= 2 else None

    def _set_initial_title(self, chat_id: int, prompt: str) -> None:
        with self._database.connection() as connection:
            row = connection.execute("SELECT title FROM chats WHERE id = ?", (chat_id,)).fetchone()
            if row is None or row["title"] != "New conversation":
                return
            title = " ".join(prompt.split())[:60]
            connection.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))

    @staticmethod
    def _to_chat(row: object) -> Chat:
        return Chat(
            row["id"],
            row["title"],
            _as_datetime(row["created_at"]),
            _as_datetime(row["updated_at"]),
            bool(row["pinned"]),
        )
