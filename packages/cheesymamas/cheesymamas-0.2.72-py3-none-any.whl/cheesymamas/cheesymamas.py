#!/usr/bin/env python3
import sys
import os
import re
from io import StringIO
from difflib import SequenceMatcher
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit,
    QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QInputDialog,
    QListWidget, QLineEdit, QMessageBox, QSplitter, QPlainTextEdit, QTabWidget, QMenu
)
from PyQt6.QtGui import QKeySequence, QShortcut, QTextCharFormat, QColor, QSyntaxHighlighter, QPainter, QFont, QTextBlockFormat, QTextCursor, QIcon, QPixmap, QCloseEvent, QCursor, QTextDocument
from PyQt6.QtCore import Qt, QRegularExpression, QRect, QSize, QTimer

PENDING_PATH_FILE = os.path.expanduser("~/.local/share/CheesyMamas/pending_open.txt")
INSTANCE_LOCK = os.path.expanduser("~/.local/share/CheesyMamas/instance.lock")

class BaseHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

class PythonHighlighter(BaseHighlighter):
    def __init__(self, document):
        super().__init__(document)
        def rule(pattern, color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self.rules.append((QRegularExpression(pattern), fmt))
        for kw in [
            "def", "class", "if", "elif", "else", "try", "except", "finally",
            "for", "while", "with", "as", "import", "from", "return", "pass",
            "raise", "break", "continue", "and", "or", "not", "is", "in", "lambda", "yield"
        ]:
            rule(rf"\b{kw}\b", "#ff79c6", True)
        rule(r"\b(True|False|None)\b", "#bd93f9", True)
        rule(r'"[^"\\]*(\\.[^"\\]*)*"', "#f1fa8c")
        rule(r"'[^'\\]*(\\.[^'\\]*)*'", "#f1fa8c")
        rule(r"#.*", "#6272a4")
        rule(r"\b\d+\b", "#8be9fd")
        rule(r"\bdef\s+(\w+)", "#50fa7b", True)
        rule(r"\bclass\s+(\w+)", "#8be9fd", True)


class CHighlighter(BaseHighlighter):
    def __init__(self, document):
        super().__init__(document)
        def rule(pattern, color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self.rules.append((QRegularExpression(pattern), fmt))
        for kw in [
            "int", "float", "char", "if", "else", "while", "return", "void",
            "for", "struct", "typedef", "const"
        ]:
            rule(rf"\b{kw}\b", "#ff79c6", True)
        rule(r'"[^"\\]*(\\.[^"\\]*)*"', "#f1fa8c")
        rule(r"//.*", "#6272a4")
        rule(r"\b\d+\b", "#8be9fd")


class LatexHighlighter(BaseHighlighter):
    def __init__(self, document):
        super().__init__(document)
        def rule(pattern, color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self.rules.append((QRegularExpression(pattern), fmt))
        rule(r"\\[a-zA-Z]+", "#ff79c6", True)
        rule(r"\$[^$]*\$", "#8be9fd")
        rule(r"%.*", "#6272a4")

class SmartTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.tab_width = 7
        font_metrics = self.fontMetrics()
        tab_stop = self.tab_width * font_metrics.horizontalAdvance(' ')
        self.setTabStopDistance(tab_stop)

        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(12)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.65)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFont(font)

        fmt = QTextBlockFormat()
        fmt.setLineHeight(150, 4)
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setBlockFormat(fmt)
        self.setTextCursor(cursor)

        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setParent(self)
        self.line_number_area.raise_()
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_line_number_area_width()
        self.viewport().update()
        if hasattr(self, "line_number_area"):
            self.line_number_area.update()

    def update_line_number_area_width(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(self.viewport().geometry().left() - self.lineNumberAreaWidth(),
                  self.viewport().geometry().top(),
                  self.lineNumberAreaWidth(),
                  self.viewport().height())
        )

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")  # Insert 4 spaces
        elif event.key() == Qt.Key.Key_Backtab:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            if line.startswith("    "):
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor, 4)
                cursor.removeSelectedText()
        elif event.key() == Qt.Key.Key_Backspace:
            cursor_pos = cursor.positionInBlock()
            block_text = cursor.block().text()
            text_before = block_text[:cursor_pos]

            # If we're inside leading indentation
            if text_before.strip() == "":
                spaces_to_delete = cursor_pos % 4 or 4
                for _ in range(spaces_to_delete):
                    cursor.deletePreviousChar()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Auto-indent new line
            current_line = cursor.block().text()
            leading_spaces = len(current_line) - len(current_line.lstrip(" "))
            indent = " " * leading_spaces
            super().keyPressEvent(event)
            cursor = self.textCursor()
            cursor.insertText(indent)
        else:
            super().keyPressEvent(event)

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.viewport().setCursor(QCursor(Qt.CursorShape.IBeamCursor))

    def handle_bash_button(self):
        bash_path = os.path.expanduser("~/.local/share/CheesyMamas/bash_script.sh")
        if not os.path.exists(bash_path):
            script, ok = QInputDialog.getMultiLineText(self, "Bash Script", "What’s your bash script or terminal commands?")
            if ok and script.strip():
                os.makedirs(os.path.dirname(bash_path), exist_ok=True)
                with open(bash_path, "w") as f:
                    f.write(script)
                QMessageBox.information(self, "Saved", "Bash script saved. You can run it anytime now.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Run Bash or New Lines?")
        msg.setText("Do you want to run your saved Bash script or enter new lines?")
        bash_btn = msg.addButton("Bash", QMessageBox.ButtonRole.AcceptRole)
        edit_btn = msg.addButton("New Lines", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == bash_btn:
            self.run_saved_bash()
        elif clicked == edit_btn:
            script, ok = QInputDialog.getMultiLineText(self, "Edit Bash Script", "Enter your updated bash commands:")
            if ok and script.strip():
                with open(bash_path, "w") as f:
                    f.write(script)
                QMessageBox.information(self, "Updated", "Script updated.")

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1f29"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#888"))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def insertFromMimeData(self, source):
        cursor = self.textCursor()

        if cursor.hasSelection():
            cursor.removeSelectedText()

        doc = self.document()
        pasted_text = source.text()
        current_line = cursor.block().text()
        leading_whitespace = current_line[:len(current_line) - len(current_line.lstrip())]
        lines = pasted_text.splitlines()
        if not lines:
            return
        adjusted_lines = []
        for i, line in enumerate(lines):
            if line.strip() == "":
                adjusted_lines.append("")
            elif i == 0:
                adjusted_lines.append(line)
            else:
                adjusted_lines.append(leading_whitespace + line)
        result = "\n".join(adjusted_lines)
        cursor.beginEditBlock()
        cursor.insertText(result)
        cursor.endEditBlock()
        self.setExtraSelections([])
        cursor.setPosition(cursor.position())
        self.setTextCursor(cursor)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setPen(QColor("#444"))  # Or any soft color you like

        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        indent_width = self.fontMetrics().horizontalAdvance(" ")

        while block.isValid() and top <= event.rect().bottom():
            text = block.text()
            if text.strip():
                leading_spaces = len(text) - len(text.lstrip(" "))
                indent_levels = leading_spaces // 4  # assuming 4-space tabs
                for i in range(indent_levels):
                    x = (i + 1) * 4 * indent_width
                    painter.drawLine(x, top, x, bottom)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)

class CheesyMamas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cheesy Mamas")
        self.resize(1000, 700)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_commit_list_on_tab_switch)
        self.commit_list = QListWidget()
        self.original_texts = {}
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("background-color: #1e1f29; color: #f8f8f2; font-family: Monospace; font-size: 12px;")
        self.output_console.setFixedHeight(100)
        self.commit_list.itemClicked.connect(self.highlight_commit_diff)
        self.commit_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.commit_list.customContextMenuRequested.connect(self.show_commit_context_menu)
        self.editors = {}
        self.active_git_popups = []
        self.diff_editor = None
        self.diff_splitter = None
        self.commit_input = QLineEdit()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.bash_button = QPushButton("Bash")
        self.bash_button.setFixedSize(70, 28)
        self.bash_button.setToolTip("Run or Edit Bash Script")
        self.bash_button.setStyleSheet("""
            QPushButton {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #ffb86c;
                padding: 3px 6px;
            }
            QPushButton:hover {
                background-color: #ffb86c;
                color: #282a36;
            }
        """)
        self.bash_button.clicked.connect(self.handle_bash_button)
        self.search_count_label = QLabel("")
        self.search_next_btn = QPushButton("▶")
        self.search_prev_btn = QPushButton("◀")
        self.search_next_btn.setFixedWidth(24)
        self.search_prev_btn.setFixedWidth(24)
        self.search_next_btn.clicked.connect(self.search_next)
        self.search_prev_btn.clicked.connect(self.search_prev)
        self.search_bar.textChanged.connect(self.perform_search)
        self.commit_button = QPushButton(QIcon.fromTheme("vcs-commit"), "Commit")
        self.new_button = QPushButton(QIcon.fromTheme("document-new"), "New")
        self.open_button = QPushButton(QIcon.fromTheme("document-open"), "Open")
        self.save_button = QPushButton(QIcon.fromTheme("document-save"), "Save")
        self.save_as_button = QPushButton(QIcon.fromTheme("document-save-as"), "Save As")
        # Layouts
        self.init_ui()
        self.bind_shortcuts()
        QTimer.singleShot(0,self.setup_output_streams)

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
                font-size: 14px;
            }
            QTabBar::tab {
                background: #44475a;
                color: #f8f8f2;
                padding: 5px 10px;
                border: 1px solid #ffb86c;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffb86c;
                color: #282a36;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #ffb86c;
                top: -1px;
            }
            QPushButton {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #ffb86c;
                padding: 3px 6px;
            }
            QPushButton:hover {
                background-color: #ffb86c;
                color: #282a36;
            }
            QLineEdit {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #ffb86c;
                padding: 3px;
            }
            QListWidget {
                background-color: #1e1f29;
                border: 1px solid #ffb86c;
                padding: 4px;
            }
            QScrollBar:vertical {
                background: #282a36;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ffb86c;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        file_buttons = QHBoxLayout()
        file_buttons.addWidget(self.new_button)
        file_buttons.addWidget(self.open_button)
        file_buttons.addWidget(self.save_button)
        file_buttons.addWidget(self.save_as_button)
        file_buttons.addWidget(self.commit_input)
        file_buttons.addWidget(self.commit_button)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_in_terminal)
        self.language_toggle = QComboBox()
        self.language_toggle.addItems(["Python", "C", "LaTeX"])
        self.language_toggle.setStyleSheet("background-color: #44475a; color: #f8f8f2; border: 1px solid #ffb86c; padding: 3px;")
        file_buttons.addWidget(self.language_toggle)
        self.language_toggle.currentTextChanged.connect(self.update_highlighter)
        file_buttons.addWidget(self.run_button)
        right_pane = QVBoxLayout()
        right_pane.addWidget(self.commit_list)
        self.clear_git_button = QPushButton("🧹 Clear Suggestions")
        self.clear_git_button.clicked.connect(self.clear_all_git_popups)
        self.clear_git_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3f58;
                color: #ffb86c;
                border: 1px solid #ffb86c;
                padding: 2px 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ffb86c;
                color: #282a36;
            }
        """)
        right_pane.addWidget(self.clear_git_button)
        #
        right_pane.addWidget(self.output_console)
        #
        splitter = QSplitter()
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Logo setup
        self.logo_label = QLabel()
        icon_path = os.path.expanduser("~/.local/share/CheesyMamas/CheesyMamas.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaledToHeight(48, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setContentsMargins(0, 0, 6, 0)
        else:
            self.logo_label.setText("🧀")
        self.search_controls_widget = QWidget()
        search_controls = QHBoxLayout(self.search_controls_widget)
        search_controls.setContentsMargins(0, 0, 0, 0)
        search_controls.addWidget(self.logo_label)
        search_controls.addWidget(self.search_bar)
        search_controls.addWidget(self.bash_button)
        search_controls.addStretch()
        search_controls.addWidget(self.search_prev_btn)
        search_controls.addWidget(self.search_next_btn)
        search_controls.addWidget(self.search_count_label)
        left_layout.addWidget(self.search_controls_widget)
        left_layout.addLayout(file_buttons)
        left_layout.addWidget(self.tabs)
        splitter.addWidget(left_widget)
        right_widget = QWidget()
        right_widget.setLayout(right_pane)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().addWidget(splitter)
        self.setCentralWidget(container)
        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_file)
        self.save_as_button.clicked.connect(self.save_file_as)
        self.commit_button.clicked.connect(self.commit_changes)
        self.search_controls_widget.show()
    
    def find_git_root(self, path):
        current = os.path.realpath(path)
        while True:
            if os.path.isdir(os.path.join(current, ".git")):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                return None
            current = parent
            
    def start_file_relay_watch(self):
        self.last_seen_paths = set()
        self.file_relay_timer = QTimer()
        self.file_relay_timer.setParent(self)
        self.file_relay_timer.timeout.connect(self.check_pending_file_opens)
        self.file_relay_timer.start(1000)  # Check every second

    def check_pending_file_opens(self):
        if not os.path.exists(PENDING_PATH_FILE):
            return
        try:
            with open(PENDING_PATH_FILE, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            if lines:
                for line in lines:
                    if os.path.exists(line) and line not in self.last_seen_paths:
                        self.open_file_path(line)
                        self.last_seen_paths.add(line)
            with open(PENDING_PATH_FILE, "w") as f:
                pass  # Clear it
        except Exception as e:
            print(f"[relay check failed]: {e}")

    def new_file(self):
        editor = SmartTextEdit()
        editor.setPlainText("")  # empty doc
        self.language_toggle.setCurrentText("Python")
        highlighter = PythonHighlighter(editor.document())
        commit_list = QListWidget()
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(editor)
        index = self.tabs.addTab(tab, "Untitled")
        self.tabs.setCurrentIndex(index)
        self.editors[index] = (editor, commit_list, None, highlighter, None)
        QTimer.singleShot(100, lambda: (
            editor.textChanged.connect(lambda i=index: self.mark_dirty(i)),
            self.search_bar.textChanged.emit(self.search_bar.text())  # retrigger search
        ))
        self.original_texts[index] = editor.toPlainText()
        self.commit_list.clear()
        self.commit_list.addItem("New unsaved file.")

    def setup_output_streams(self):
        class EmittingStream:
            def __init__(self,append_fn):
                self.append_fn=append_fn
            def write(self,text):
                if text.strip():
                    try:
                        self.append_fn(text)
                    except Exception:
                        pass
            def flush(self):
                pass
        sys.stdout=EmittingStream(lambda t:self.output_console.append(t))
        sys.stderr=EmittingStream(lambda t:self.output_console.append(f"[stderr] {t}"))

    def perform_search(self):
        text = self.search_bar.text().rstrip()
        editor_data = self.current_tab_data()
        if not editor_data or len(editor_data) < 1 or editor_data[0] is None:
            self.search_matches = []
            self.search_count_label.setText("0 / 0")
            return

        editor = editor_data[0]
        text = self.search_bar.text().rstrip()  # Trim trailing space
        if not text:
            self.search_matches = []
            editor.setExtraSelections([])
            self.search_count_label.setText("0 / 0")
            return

        doc = editor.document()
        cursor = QTextCursor(doc)
        cursor.setPosition(0)  # Start at the beginning

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#ffb86c"))

        self.search_matches = []
        selections = []

        while True:
            cursor = doc.find(text, cursor, QTextDocument.FindFlag(0))
            if cursor.isNull():
                break
            self.search_matches.append(QTextCursor(cursor))
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = highlight_format
            selections.append(selection)

        editor.setExtraSelections(selections)  # Replace, not extend

        if self.search_matches:
            self.search_index = 0
            self.snap_to_search_match()
        else:
            self.search_index = -1
            self.search_count_label.setText("0 / 0")

    def handle_bash_button(self):
        bash_path = os.path.expanduser("~/.local/share/CheesyMamas/bash_script.sh")
        if not os.path.exists(bash_path):
            script, ok = QInputDialog.getMultiLineText(self, "Bash Script", "What’s your bash script or terminal commands?")
            if ok and script.strip():
                os.makedirs(os.path.dirname(bash_path), exist_ok=True)
                with open(bash_path, "w") as f:
                    f.write(script)
                QMessageBox.information(self, "Saved", "Bash script saved. You can run it anytime now.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Run Bash or New Lines?")
        msg.setText("Do you want to run your saved Bash script or enter new lines?")
        bash_btn = msg.addButton("Bash", QMessageBox.ButtonRole.AcceptRole)
        edit_btn = msg.addButton("New Lines", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == bash_btn:
            self.run_saved_bash()
        elif clicked == edit_btn:
            script, ok = QInputDialog.getMultiLineText(self, "Edit Bash Script", "Enter your updated bash commands:")
            if ok and script.strip():
                with open(bash_path, "w") as f:
                    f.write(script)
                QMessageBox.information(self, "Updated", "Script updated.")

    def run_saved_bash(self):
        bash_path = os.path.expanduser("~/.local/share/CheesyMamas/bash_script.sh")
        try:
            subprocess.Popen(["x-terminal-emulator", "-e", f"bash '{bash_path}'"])
        except Exception as e:
            QMessageBox.warning(self, "Run Failed", f"Could not run Bash script:\n{e}")

    def snap_to_search_match(self):
        if not self.search_matches:
            return

        editor_data = self.current_tab_data()
        if not editor_data or len(editor_data) < 1:
            return
        editor = editor_data[0]

        cursor = self.search_matches[self.search_index]
        editor.setTextCursor(cursor)
        editor.centerCursor()

        self.search_count_label.setText(f"{self.search_index + 1} / {len(self.search_matches)}")

    def search_next(self):
        if not hasattr(self, 'search_matches') or not self.search_matches:
            return
        self.search_index = (self.search_index + 1) % len(self.search_matches)
        self.snap_to_search_match()

    def search_prev(self):
        if not hasattr(self, 'search_matches') or not self.search_matches:
            return
        self.search_index = (self.search_index - 1) % len(self.search_matches)
        self.snap_to_search_match()

    def highlight_matching_defs(self, editor_a, editor_b):
        def find_defs(editor):
            lines = editor.toPlainText().splitlines()
            defs = {}
            for idx, line in enumerate(lines):
                match = re.match(r'^\s*(def|class)\s+(\w+)', line)
                if match:
                    defs[match.group(2)] = idx
            return defs

        defs_a = find_defs(editor_a)
        defs_b = find_defs(editor_b)
        matched = sorted(set(defs_a.keys()) & set(defs_b.keys()))

        colors = [
            "#8be9fd", "#ffb86c", "#bd93f9", "#ff79c6", "#50fa7b",
            "#f1fa8c", "#6272a4", "#ffaa66", "#66ff99", "#99ddff"
        ]

        extra_a = editor_a.extraSelections()
        extra_b = editor_b.extraSelections()

        for i, name in enumerate(matched):
            color = QColor(colors[i % len(colors)])
            fmt = QTextCharFormat()
            fmt.setBackground(color)

            block_a = editor_a.document().findBlockByNumber(defs_a[name])
            block_b = editor_b.document().findBlockByNumber(defs_b[name])

            if block_a.isValid():
                sel = QTextEdit.ExtraSelection()
                sel.cursor = QTextCursor(block_a)
                sel.format = fmt
                extra_a.append(sel)

            if block_b.isValid():
                sel = QTextEdit.ExtraSelection()
                sel.cursor = QTextCursor(block_b)
                sel.format = fmt
                extra_b.append(sel)

        editor_a.setExtraSelections(extra_a)
        editor_b.setExtraSelections(extra_b)

    def highlight_diff_blocks(self, old_editor, new_editor):
        old_lines = old_editor.toPlainText().splitlines()
        new_lines = new_editor.toPlainText().splitlines()
        matcher = SequenceMatcher(None, old_lines, new_lines)

        red = QTextCharFormat()
        red.setBackground(QColor("#ff5555"))
        red.setForeground(QColor("#ffffff"))

        green = QTextCharFormat()
        green.setBackground(QColor("#50fa7b"))
        green.setForeground(QColor("#000000"))

        yellow = QTextCharFormat()
        yellow.setBackground(QColor("#f1fa8c"))
        yellow.setForeground(QColor("#000000"))

        old_sel = []
        new_sel = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "delete":
                for idx in range(i1, i2):
                    blk = old_editor.document().findBlockByNumber(idx)
                    if blk.isValid():
                        sel = QTextEdit.ExtraSelection()
                        cursor = QTextCursor(blk)
                        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                        sel.cursor = cursor
                        sel.format = red
                        old_sel.append(sel)
            elif tag == "insert":
                for idx in range(j1, j2):
                    blk = new_editor.document().findBlockByNumber(idx)
                    if blk.isValid():
                        sel = QTextEdit.ExtraSelection()
                        cursor = QTextCursor(blk)
                        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                        sel.cursor = cursor
                        sel.format = green
                        new_sel.append(sel)
            elif tag == "replace":
                for idx in range(j1, j2):
                    blk = new_editor.document().findBlockByNumber(idx)
                    if blk.isValid():
                        sel = QTextEdit.ExtraSelection()
                        cursor = QTextCursor(blk)
                        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                        sel.cursor = cursor
                        sel.format = yellow
                        new_sel.append(sel)

        old_editor.setExtraSelections(old_editor.extraSelections() + old_sel)
        new_editor.setExtraSelections(new_editor.extraSelections() + new_sel)

        old_editor.viewport().update()
        new_editor.viewport().update()
        old_editor.repaint()
        new_editor.repaint()

        if hasattr(old_editor, "line_number_area"):
            old_editor.line_number_area.update()
        if hasattr(new_editor, "line_number_area"):
            new_editor.line_number_area.update()

    def show_git_line_dropdowns(self, editor, path, commit_hash):
        current_tab_idx = self.tabs.currentIndex()
        abs_path = os.path.realpath(path)
        repo_path = self.find_git_root(abs_path)
        if not repo_path:
            QMessageBox.warning(self, "Git Error", "This file is not inside a Git repository.")
            return

        rel_path = os.path.relpath(abs_path, repo_path)

        # 🛡️ Check if the file exists at the commit before calling git show
        exists = subprocess.run(
            ["git", "-C", repo_path, "cat-file", "-e", f"{commit_hash}:{rel_path}"],
            capture_output=True
        )
        if exists.returncode != 0:
            QMessageBox.warning(self, "Not Available", f"This file didn’t exist yet at commit {commit_hash}.\nSo there’s nothing to show.")
            return

        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "show", f"{commit_hash}:{rel_path}"],
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Git Show Failed", f"Could not load this file from commit {commit_hash}.\n\nGit error:\n{e}")
            return

        old_lines = result.stdout.splitlines()

        old_editor = SmartTextEdit()
        old_editor.setPlainText("\n".join(old_lines))
        old_editor.setReadOnly(True)
        old_editor.highlighter = PythonHighlighter(old_editor.document())
        self.diff_editor = old_editor

        # Unpack current editor data
        if len(self.editors[current_tab_idx]) == 5:
            editor, commit_list, _, highlighter, old_splitter = self.editors[current_tab_idx]
        else:
            editor, commit_list, _, highlighter = self.editors[current_tab_idx]
            old_splitter = None

        if old_splitter:
            old_splitter.setParent(None)
            old_splitter.deleteLater()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(editor)
        splitter.addWidget(old_editor)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([2, 1])

        tab_widget = self.tabs.widget(current_tab_idx)
        layout = tab_widget.layout()
        self.highlight_matching_defs(editor, old_editor)
        layout.addWidget(splitter)

        # Save updated state with splitter
        self.editors[current_tab_idx] = (editor, commit_list, path, highlighter, splitter)
        self.highlight_diff_blocks(old_editor, editor)
    def clear_all_git_popups(self):
        idx = self.tabs.currentIndex()
        editor_data = self.editors[idx]

        if len(editor_data) == 5:
            editor, commit_list, path, highlighter, splitter = editor_data
        else:
            editor, commit_list, path, highlighter = editor_data
            splitter = None

        if splitter:
            main_editor = splitter.widget(0)
            old_editor = splitter.widget(1)

            if isinstance(main_editor, QPlainTextEdit):
                main_editor.setExtraSelections([])

            if isinstance(old_editor, QPlainTextEdit):
                old_editor.setExtraSelections([])

            main_editor.viewport().update()
            old_editor.viewport().update()

            splitter.setParent(None)
            splitter.deleteLater()

            tab_widget = self.tabs.widget(idx)
            layout = tab_widget.layout()
            layout.addWidget(main_editor)

            self.editors[idx] = (main_editor, commit_list, path, highlighter)

    def run_in_terminal(self):
        data = self.current_tab_data()
        if len(data) == 5:
            editor, _, path, _, _ = data
        else:
            editor, _, path, _ = data
        if not path:
            QMessageBox.warning(self,"No File","Save the file before running.")
            return
        with open(path,"w",encoding="utf-8") as f:
            f.write(editor.toPlainText())
        language=self.language_toggle.currentText()
        try:
            if language=="Python":
                subprocess.Popen(["x-terminal-emulator","-e",f"python3 '{path}'"])
            elif language=="C":
                out_path=os.path.splitext(path)[0]
                subprocess.Popen(["x-terminal-emulator","-e","bash","-c",f"gcc '{path}' -o '{out_path}' && '{out_path}'; read -n1"])
            elif language=="LaTeX":
                folder=os.path.dirname(path)
                filename=os.path.basename(path)
                pdflatex="/usr/local/texlive/2025/bin/x86_64-linux/pdflatex"
                subprocess.Popen(["x-terminal-emulator","-e","bash","-c",f"cd '{folder}' && '{pdflatex}' -interaction=nonstopmode '{filename}'; read -n1 -p 'Press any key to close…'"])
        except Exception as e:
            QMessageBox.warning(self,"Run Error",f"Could not execute:\n{e}")
    
    def delete_commit(self, commit_hash, path):
        repo_path = os.path.dirname(os.path.realpath(path))

        reply = QMessageBox.question(
            self,
            "Delete Commit",
            f"Are you sure you want to permanently delete commit {commit_hash}?\n\nThis action rewrites Git history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Check if it's the most recent commit (HEAD)
            result = subprocess.run(
                ["git", "-C", repo_path, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True
            )
            head_commit = result.stdout.strip()

            if commit_hash != head_commit:
                QMessageBox.warning(
                    self,
                    "Only HEAD Deletable",
                    "Only the most recent commit (HEAD) can be deleted using this method."
                )
                return

            # Safely delete HEAD commit only
            subprocess.run([
                "git", "-C", repo_path, "reset", "--hard", "HEAD~1"
            ], check=True)

            QMessageBox.information(self, "Commit Deleted", f"Deleted most recent commit {commit_hash}.")
            self.load_commit_history(path, self.commit_list)

        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Delete Failed", f"Could not delete commit:\n\n{e}")
            
    def show_commit_context_menu(self, position):
        item = self.commit_list.itemAt(position)
        if not item:
            return
        commit_hash = item.text().split()[0]

        menu = QMenu()
        view_action = menu.addAction("👁️ View Diff")
        revert_action = menu.addAction("🔄 Revert File to This Commit")
        copy_action = menu.addAction("📋 Copy File at This Commit")
        delete_action = menu.addAction("🗑️ Delete This Commit")  # 🧁 new option!

        action = menu.exec(self.commit_list.mapToGlobal(position))
        if not action:
            return

        data = self.current_tab_data()
        if len(data) == 5:
            _, _, path, _, _ = data
        else:
            _, _, path, _ = data
        if not path:
            return

        if action == view_action:
            self.view_diff_popup(commit_hash, path)
        elif action == revert_action:
            self.revert_to_commit(commit_hash, path)
        elif action == copy_action:
            self.copy_old_version_to_clipboard(commit_hash, path)
        elif action == delete_action:
            self.delete_commit(commit_hash, path)

    def view_diff_popup(self, commit_hash, path):
        try:
            result = subprocess.run(
                ["git", "-C", os.path.dirname(path), "diff", f"{commit_hash}^!", "--", path],
                check=True, capture_output=True, text=True
            )
            diff_text = result.stdout.strip() or "[No diff content]"
            # Scrollable popup
            scroll_area = QTextEdit()
            scroll_area.setReadOnly(True)
            scroll_area.setPlainText(diff_text)
            scroll_area.setStyleSheet("background-color: #1e1f29; color: #f8f8f2; font-family: Monospace;")
            scroll_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            dlg = QMainWindow(self)
            dlg.setWindowTitle(f"Diff: {commit_hash}")
            dlg.setCentralWidget(scroll_area)
            dlg.resize(800, 500)
            dlg.show()
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Error", f"Could not show diff:\n{e}")

    def revert_to_commit(self, commit_hash, path):
        reply = QMessageBox.question(
            self, "Revert File",
            f"Revert this file to commit {commit_hash}?\n(This will overwrite current contents)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = subprocess.run(
                    ["git", "-C", os.path.dirname(path), "show", f"{commit_hash}:{os.path.basename(path)}"],
                    check=True, capture_output=True, text=True
                )
                editor, _, _, _ = self.current_tab_data()
                editor.setPlainText(result.stdout)
            except subprocess.CalledProcessError as e:
                QMessageBox.warning(self, "Error", f"Could not revert file:\n{e}")

    def copy_old_version_to_clipboard(self, commit_hash, path):
        try:
            result = subprocess.run(
                ["git", "-C", os.path.dirname(path), "show", f"{commit_hash}:{os.path.basename(path)}"],
                check=True, capture_output=True, text=True
            )
            QApplication.clipboard().setText(result.stdout)
            QMessageBox.information(self, "Copied", f"Contents from {commit_hash} copied to clipboard.")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Error", f"Could not copy contents:\n{e}")

    def highlight_commit_diff(self, item):
        text = item.text()
        if text.startswith("No commits yet") or "Not in a Git repo" in text:
            return  # Don't try to highlight a fake commit message
        commit_hash = text.split()[0]
        data = self.current_tab_data()
        if len(data) == 5:
            editor, _, path, _, _ = data
        else:
            editor, _, path, _ = data
        if not editor or not path:
            return
        try:
            self.show_git_line_dropdowns(editor, path, commit_hash)
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Git Diff Error", f"Could not get diff:\n\n{e}")

    def parse_changed_lines(self, diff_output):
        import re
        lines = []
        current_line = 0
        for line in diff_output.splitlines():
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line = int(match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                lines.append(current_line)
                current_line += 1
            elif not line.startswith("-"):
                current_line += 1
        return lines

    def closeEvent(self, event: QCloseEvent):
        if hasattr(self, 'file_relay_timer'):
                self.file_relay_timer.stop()
        unsaved_tabs = []

        for idx, (editor, _, path, _) in self.editors.items():
            if self.tabs.tabText(idx).endswith("*"):
                unsaved_tabs.append((idx, path))
        if not unsaved_tabs:
            event.accept()
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("You have unsaved changes.\nWould you like to save before exiting?")
        msg.setStandardButtons(QMessageBox.StandardButton.Save |
                               QMessageBox.StandardButton.Discard |
                               QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.Save)
        choice = msg.exec()
        if choice == QMessageBox.StandardButton.Save:
            for idx in [i for i, _ in unsaved_tabs]:
                self.tabs.setCurrentIndex(idx)
                self.save_file()
            event.accept()
        elif choice == QMessageBox.StandardButton.Discard:
            event.accept()
        else:  # Cancel
            event.ignore()

    def show_search_bar(self):
        if not self.search_controls_widget.isVisible():
            self.search_controls_widget.show()

        self.search_bar.setFocus()
        self.search_bar.selectAll()
        self.perform_search()  # immediately highlight on open

    def highlight_lines(self, editor, line_numbers):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#44475a"))
        selections = []
        doc = editor.document()
        for line in line_numbers:
            block = doc.findBlockByNumber(line - 1)
            if block.isValid():
                selection = QTextEdit.ExtraSelection()
                selection.cursor = QTextCursor(block)
                selection.cursor.clearSelection()
                selection.format = fmt
                selections.append(selection)
        existing = editor.extraSelections()
        existing.extend(selections)
        editor.setExtraSelections(existing)

    def sync_commit_list_on_tab_switch(self, index):
        data = self.editors.get(index)
        if data:
            commit_list = data[1]
            self.update_commit_list_view(commit_list)
        else:
            self.commit_list.clear()
            self.commit_list.addItem("No file open.")

    def update_commit_list_view(self, commit_list):
        self.commit_list.clear()
        for i in range(commit_list.count()):
            self.commit_list.addItem(commit_list.item(i).text())

    def bind_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+G"), self, self.commit_changes)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.next_tab)
        QShortcut(QKeySequence("Ctrl+F"), self, self.show_search_bar)
        self.new_button.clicked.connect(self.new_file)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File")
        if not file_name:
            return
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
        editor = SmartTextEdit()
        editor.setPlainText(content)
        self.tabs.setTabText(self.tabs.count(), os.path.basename(file_name))
        highlighter = PythonHighlighter(editor.document())
        commit_list = QListWidget()
        self.load_commit_history(file_name, commit_list)
        # Create tab content layout
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(editor)
        # Add tab and get its index
        index = self.tabs.addTab(tab, os.path.basename(file_name))
        self.tabs.setCurrentIndex(index)
        # Store everything before syncing the sidebar
        self.editors[index] = (editor, commit_list, file_name, highlighter)
        # Update the right-side commit view
        self.update_commit_list_view(commit_list)
        # Mark as dirty when edited
        self.original_texts[index] = editor.toPlainText()
        QTimer.singleShot(100, lambda: editor.textChanged.connect(lambda i=index: self.mark_dirty(i)))

    def open_file_path(self, file_path):
        if not os.path.exists(file_path):
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        editor = SmartTextEdit()
        editor.setPlainText(content)
        self.tabs.setTabText(self.tabs.count(), os.path.basename(file_path))
        highlighter = PythonHighlighter(editor.document())
        commit_list = QListWidget()
        self.load_commit_history(file_path, commit_list)
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(editor)
        index = self.tabs.addTab(tab, os.path.basename(file_path))
        self.tabs.setCurrentIndex(index)
        self.editors[index] = (editor, commit_list, file_path, highlighter, None)
        self.update_commit_list_view(commit_list)
        self.original_texts[index] = editor.toPlainText()
        QTimer.singleShot(100, lambda: editor.textChanged.connect(lambda i=index: self.mark_dirty(i)))

    def close_tab(self, index):
        self.tabs.removeTab(index)
        self.editors.pop(index, None)

    def mark_dirty(self, idx):
        data = self.editors.get(idx)
        if not data:
            return

        editor = data[0]
        if not editor:
            return

        current = editor.toPlainText()
        original = self.original_texts.get(idx, "")
        name = self.tabs.tabText(idx)
        if current != original:
            if not name.endswith("*"):
                self.tabs.setTabText(idx, name + "*")
        else:
            if name.endswith("*"):
                self.tabs.setTabText(idx, name[:-1])

    def next_tab(self):
        idx = self.tabs.currentIndex()
        count = self.tabs.count()
        self.tabs.setCurrentIndex((idx + 1) % count)

    def current_tab_data(self):
        idx = self.tabs.currentIndex()
        data = self.editors.get(idx, (None, None, None, None))
        if len(data) == 5:
            return data
        else:
            return (*data, None)

    def save_file(self):
        idx = self.tabs.currentIndex()
        if idx not in self.editors:
            return
        editor_data = self.editors[idx]
        if len(editor_data) == 5:
            editor, commit_list, path, highlighter, splitter = editor_data
        else:
            editor, commit_list, path, highlighter = editor_data
            splitter = None
        if not path:
            self.save_file_as()
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(editor.toPlainText())
            self.original_texts[idx] = editor.toPlainText()
        name = self.tabs.tabText(idx)
        if name.endswith("*"):
            self.tabs.setTabText(idx, name[:-1])

    def update_highlighter(self):
        idx = self.tabs.currentIndex()
        if idx not in self.editors:
            return
        editor, commit_list, path, _ = self.editors[idx]
        language = self.language_toggle.currentText()
        if language == "Python":
            highlighter = PythonHighlighter(editor.document())
        elif language == "C":
            highlighter = CHighlighter(editor.document())
        elif language == "LaTeX":
            highlighter = LatexHighlighter(editor.document())
        self.editors[idx] = (editor, commit_list, path, highlighter)
        highlighter.rehighlight()

    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if not file_name:
            return
        idx = self.tabs.currentIndex()
        if idx not in self.editors:
            return

        data = self.editors[idx]
        if len(data) == 5:
            editor, commit_list, _, highlighter, _ = data
        else:
            editor, commit_list, _, highlighter = data

        self.editors[idx] = (editor, commit_list, file_name, highlighter, None)
        self.tabs.setTabText(idx, os.path.basename(file_name))
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(editor.toPlainText())
            self.original_texts[idx] = editor.toPlainText()

        name = self.tabs.tabText(idx)
        if name.endswith("*"):
            self.tabs.setTabText(idx, name[:-1])

    def commit_changes(self):
        data = self.current_tab_data()
        if not data:
            return

        if len(data) == 5:
            editor, commit_list, path, _, splitter = data
        else:
            editor, commit_list, path, _ = data
            splitter = None

        if not editor or not path:
            QMessageBox.warning(self, "No File", "Save the file before committing.")
            return

        with open(path, 'w', encoding='utf-8') as f:
            f.write(editor.toPlainText())

        commit_msg = self.commit_input.text().strip() or f"autosnap at {self.current_time()}"
        abs_path = os.path.realpath(path)
        repo_path = self.find_git_root(abs_path)
        if not repo_path:
            QMessageBox.warning(self, "Git Error", "This file is not inside a Git repository.")
            return

        rel_path = os.path.relpath(abs_path, repo_path)
        just_initialized = False
        first_commit = False

        try:
            subprocess.run(["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "-C", repo_path, "init"], check=True)
            subprocess.run(["git", "-C", repo_path, "config", "user.name", "CheesyMamas"], check=True)
            subprocess.run(["git", "-C", repo_path, "config", "user.email", "CheesyMamas@local"], check=True)
            just_initialized = True

        # Ensure file is inside the repo
        if not os.path.realpath(path).startswith(os.path.realpath(repo_path)):
            QMessageBox.warning(self, "Invalid File Location", "File must be located within the initialized Git repository.")
            return

        try:
            # Forcefully add and verify that Git sees the file
            print(f"[DEBUG] abs_path: {abs_path}")
            print(f"[DEBUG] repo_path: {repo_path}")
            print(f"[DEBUG] rel_path: {rel_path}")
            print(f"[DEBUG] File exists: {os.path.exists(abs_path)}")
            add_result = subprocess.run(["git", "-C", repo_path, "add", rel_path], capture_output=True, text=True)
            verify = subprocess.run(["git", "-C", repo_path, "diff", "--cached", "--name-status"], capture_output=True, text=True)
            print("[DEBUG] Cached diff:\n", verify.stdout)

            # Confirm staging worked
            status_check = subprocess.run(["git", "-C", repo_path, "status", "--porcelain", "--", rel_path], capture_output=True, text=True)
            if not status_check.stdout.strip():
                QMessageBox.warning(self, "Git Add Failed", f"The file '{rel_path}' was not staged for commit.\n\nCheck if it's ignored, outside the repo, or misaligned.")
                return

            # Check if the file has been committed before
            log_check = subprocess.run(
                ["git", "-C", repo_path, "log", "--pretty=format:%h", "--", rel_path],
                capture_output=True, text=True
            )
            if log_check.returncode != 0 or not log_check.stdout.strip():
                first_commit = True

            status = subprocess.run(
                ["git", "-C", repo_path, "status", "--porcelain", "--", rel_path],
                capture_output=True, text=True
            )

            if not first_commit and not status.stdout.strip() and not just_initialized:
                QMessageBox.information(self, "Nothing to Commit", "No changes to this file.")
                return

            subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_msg], check=True)

            idx = self.tabs.currentIndex()
            highlighter = self.editors[idx][3]
            self.editors[idx] = (editor, commit_list, path, highlighter, None)
            self.commit_input.clear()
            self.load_commit_history(path, commit_list)
            self.update_commit_list_view(commit_list)

            if commit_list.count() > 0:
                self.commit_list.setCurrentRow(0)
                self.highlight_commit_diff(self.commit_list.item(0))

            name = self.tabs.tabText(idx)
            if name.endswith("*"):
                self.tabs.setTabText(idx, name[:-1])

            self.clear_all_git_popups()

        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Git Error", f"Something went wrong during commit:\n\n{e}")

    def load_commit_history(self, file_path, list_widget):
        abs_path = os.path.realpath(file_path)
        repo_path = self.find_git_root(abs_path)
        if not repo_path:
            list_widget.clear()
            list_widget.addItem("Not in a Git repo yet. First commit will start the timeline.")
            return

        rel_path = os.path.relpath(abs_path, repo_path)
        try:
            try:
                result = subprocess.run(
                    ["git", "-C", repo_path, "log", "--pretty=format:%h %ad %s", "--date=short", "--", rel_path],
                    check=True, capture_output=True, text=True
                )
                output = result.stdout.strip()
            except subprocess.CalledProcessError:
                output = ""
            # Update the hidden commit_list tied to the tab
            list_widget.clear()
            if output:
                for line in output.split("\n"):
                    list_widget.addItem(line)
            else:
                list_widget.addItem("No commits yet.")
            # Also update the visible sidebar immediately
            current_index = self.tabs.currentIndex()
            if current_index in self.editors:
                current_commit_list = self.editors[current_index][1]
                if current_commit_list == list_widget:
                    self.update_commit_list_view(current_commit_list)
        except subprocess.CalledProcessError:
            list_widget.clear()
            list_widget.addItem("Not in a Git repo yet. First commit will start the timeline.")

    def current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    print("🧀 Launching...")
    os.makedirs(os.path.dirname(PENDING_PATH_FILE), exist_ok=True)

    # Use a simple lock file to check for an already-running instance
    lock_file = os.path.expanduser("~/.local/share/CheesyMamas/instance.lock")
    file_to_open = sys.argv[1] if len(sys.argv) > 1 else None
    already_running = os.path.exists(lock_file) and file_to_open and not file_to_open.endswith("cheesymamas.py")

    # If another instance is running, just append to the relay
    if file_to_open and already_running:
        try:
            with open(PENDING_PATH_FILE, "a") as f:
                f.write(file_to_open + "\n")
            print(f"📂 Relayed file to running instance: {file_to_open}")
            sys.exit(0)
        except Exception as e:
            print(f"[relay write failed]: {e}")
            sys.exit(1)

    # Start the main application
    app = QApplication(sys.argv)
    try:
        # Create the lock
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

        window = CheesyMamas()
        window.start_file_relay_watch()
        print("✅ Window built")
        window.show()
        if file_to_open:
            QTimer.singleShot(100, lambda: window.open_file_path(file_to_open))
        print("✅ Window shown")
        exit_code = app.exec()
    except Exception as e:
        print("💥 Exception during startup:")
        import traceback
        traceback.print_exc()
        exit_code = 1
    finally:
        # Clean up the lock file
        if os.path.exists(lock_file):
            os.remove(lock_file)
        if window and hasattr(window, 'file_relay_timer'):
            window.file_relay_timer.stop()
            window.file_relay_timer.deleteLater()

    sys.exit(exit_code)
