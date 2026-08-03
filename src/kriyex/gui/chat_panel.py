from html import escape

from PySide6.QtWidgets import QTextEdit

from kriyex.domain.models import Message


class ChatPanel(QTextEdit):
    """Main chat display."""

    def __init__(self) -> None:
        super().__init__()

        self.setReadOnly(True)
        self.setPlaceholderText("KRIYEX conversation will appear here...")

    def show_messages(self, messages: list[Message]) -> None:
        blocks = []
        for message in messages:
            speaker = "You" if message.role == "user" else "KRIYEX"
            color = "#87c7ff" if message.role == "user" else "#a7f3d0"
            content = escape(message.content).replace("\n", "<br>")
            blocks.append(f'<p><b style="color:{color}">{speaker}</b><br>{content}</p>')
        self.setHtml("".join(blocks))
        self.moveCursor(self.textCursor().MoveOperation.End)

    def begin_streaming_response(self) -> None:
        self.moveCursor(self.textCursor().MoveOperation.End)
        self.insertHtml('<p><b style="color:#a7f3d0">KRIYEX</b><br>')

    def append_stream_chunk(self, text: str) -> None:
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def end_streaming_response(self) -> None:
        self.moveCursor(self.textCursor().MoveOperation.End)
        self.insertHtml("</p>")
