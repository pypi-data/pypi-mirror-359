#!/usr/bin/env python3
import sys
import os
from io import StringIO
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit,
    QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QInputDialog,
    QListWidget, QLineEdit, QMessageBox, QSplitter, QPlainTextEdit, QTabWidget, QMenu
)
from PyQt6.QtGui import QKeySequence, QShortcut, QTextCharFormat, QColor, QSyntaxHighlighter, QPainter, QFont, QTextBlockFormat, QTextCursor, QIcon, QPixmap, QCloseEvent
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
        self.setTabStopDistance(font_metrics.horizontalAdvance(' ') * 4)  # Adjust 4 to your liking
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(12)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.65)
        self.setFont(font)
        fmt = QTextBlockFormat()
        fmt.setLineHeight(150, 4)  # 4 = ProportionalHeight
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setBlockFormat(fmt)
        self.setTextCursor(cursor)
        self.line_number_area = LineNumberArea(self)
        self.setViewportMargins(40, 0, 0, 0)
        self.textChanged.connect(self.updateLineNumberAreaWidth)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)
        self.cursorPositionChanged.connect(self.line_number_area.update)
        self.updateLineNumberAreaWidth()

    def lineNumberAreaSize(self):
        return self.lineNumberAreaWidth(), 0

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
            text_before = cursor.block().text()[:cursor_pos]
            if text_before.endswith("    "):
                for _ in range(4):
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

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setPen(QColor("#444"))
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        indent_width = self.fontMetrics().horizontalAdvance(" ")
        while block.isValid() and top <= event.rect().bottom():
            text = block.text()
            if text.strip():
                leading_spaces = len(text) - len(text.lstrip(" "))
                indent_levels = leading_spaces // 4  # <- updated
                for i in range(indent_levels):
                    x = (i + 1) * 4 * indent_width
                    painter.drawLine(x, top, x, bottom)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
    
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
                
    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

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
        self.editors[index] = (editor, commit_list, None, highlighter)
        QTimer.singleShot(100, lambda: editor.textChanged.connect(lambda i=index: self.mark_dirty(i)))
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
        text = self.search_bar.text()
        editor, _, _, _ = self.current_tab_data()
        if not editor or not text:
            self.search_matches = []
            self.search_count_label.setText("0 / 0")
            return

        doc = editor.document()
        cursor = QTextCursor(doc)
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#ffb86c"))

        self.search_matches = []
        while not cursor.isNull() and not cursor.atEnd():
            cursor = doc.find(text, cursor)
            if cursor.isNull():
                break
            self.search_matches.append(QTextCursor(cursor))

        selections = []
        for match in self.search_matches:
            selection = QTextEdit.ExtraSelection()
            selection.cursor = match
            selection.format = highlight_format
            selections.append(selection)

        editor.setExtraSelections(selections)

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

        editor, _, _, _ = self.current_tab_data()
        if not editor:
            return

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

    def show_git_line_dropdowns(self, editor, path, commit_hash):
        from difflib import unified_diff

        result = subprocess.run(
            ["git", "-C", os.path.dirname(path), "show", f"{commit_hash}:{os.path.basename(path)}"],
            check=True, capture_output=True, text=True
        )
        old_lines = result.stdout.splitlines()
        new_lines = editor.toPlainText().splitlines()
        doc = editor.document()
        diff = list(unified_diff(old_lines, new_lines, lineterm=''))
        line_index = 0
        for line in diff:
            if line.startswith("@@"):
                import re
                m = re.search(r"\+(\d+)", line)
                if m:
                    line_index = int(m.group(1)) - 1  # 1-based to 0-based
            elif line.startswith("+") and not line.startswith("+++"):
                if 0 <= line_index < len(old_lines):
                    old_text = old_lines[line_index]
                    self.insert_git_popup(editor, line_index, old_text)
                line_index += 1
            elif not line.startswith("-"):
                line_index += 1

    def insert_git_popup(self, editor, line_number, old_text):
        popup = GitLinePopup(line_number, old_text.strip(), self.revert_line)
        popup.setParent(editor.viewport())
        block = editor.document().findBlockByNumber(line_number)
        y = editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top()
        popup.move(editor.lineNumberAreaWidth() + 10, int(y))
        popup.show()
        self.active_git_popups.append(popup)

    def clear_all_git_popups(self):
        for popup in self.active_git_popups:
            popup.close()
        self.active_git_popups.clear()

    def run_in_terminal(self):
        editor,_,path,_=self.current_tab_data()
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

    def revert_line(self, line_number, old_text):
        editor, _, _, _ = self.current_tab_data()
        doc = editor.document()
        block = doc.findBlockByNumber(line_number)
        if not block.isValid():
            return
        cursor = QTextCursor(block)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(old_text)

    def show_commit_context_menu(self, position):
        item = self.commit_list.itemAt(position)
        if not item:
            return
        commit_hash = item.text().split()[0]
        menu = QMenu()
        view_action = menu.addAction("👁️ View Diff")
        revert_action = menu.addAction("🔄 Revert File to This Commit")
        copy_action = menu.addAction("📋 Copy File at This Commit")
        action = menu.exec(self.commit_list.mapToGlobal(position))
        if not action:
            return
        _, _, path, _ = self.current_tab_data()
        if not path:
            return
        if action == view_action:
            self.view_diff_popup(commit_hash, path)
        elif action == revert_action:
            self.revert_to_commit(commit_hash, path)
        elif action == copy_action:
            self.copy_old_version_to_clipboard(commit_hash, path)

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
        editor, _, path, _ = self.current_tab_data()
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

    def perform_search(self):
        text = self.search_bar.text()
        editor, _, _, _ = self.current_tab_data()
        if not editor:
            return
        doc = editor.document()
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#ffb86c"))
        self.search_matches = []
        cursor = QTextCursor(doc)
        while not cursor.isNull() and not cursor.atEnd():
            cursor = doc.find(text, cursor)
            if cursor.isNull():
                break
            self.search_matches.append(QTextCursor(cursor))
        # Show highlights
        selections = []
        for match_cursor in self.search_matches:
            selection = QTextEdit.ExtraSelection()
            selection.cursor = match_cursor
            selection.format = highlight_format
            selections.append(selection)
        editor.setExtraSelections(selections)
        # Snap to first match
        if self.search_matches:
            self.search_index = 0
            self.snap_to_search_match()

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
        editor.setExtraSelections(selections)

    def sync_commit_list_on_tab_switch(self, index):
        data = self.editors.get(index)
        if data:
            _, commit_list, _, _ = data
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
        self.editors[index] = (editor, commit_list, file_path, highlighter)
        self.update_commit_list_view(commit_list)
        self.original_texts[index] = editor.toPlainText()
        QTimer.singleShot(100, lambda: editor.textChanged.connect(lambda i=index: self.mark_dirty(i)))

    def close_tab(self, index):
        self.tabs.removeTab(index)
        self.editors.pop(index, None)

    def mark_dirty(self, idx):
        editor, _, _, _ = self.editors.get(idx, (None, None, None, None))
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
        return self.editors.get(idx, (None, None, None, None))

    def save_file(self):
        idx = self.tabs.currentIndex()
        if idx not in self.editors:
            return
        editor, commit_list, path, highlighter = self.editors[idx]
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
        editor, commit_list, _, highlighter = self.editors[idx]
        self.editors[idx] = (editor, commit_list, file_name, highlighter)
        self.tabs.setTabText(idx, os.path.basename(file_name))
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(editor.toPlainText())
            self.original_texts[idx] = editor.toPlainText()
        name = self.tabs.tabText(idx)
        if name.endswith("*"):
            self.tabs.setTabText(idx, name[:-1])

    def commit_changes(self):
        editor, commit_list, path, _ = self.current_tab_data()
        if not editor or not path:
            QMessageBox.warning(self, "No File", "Save the file before committing.")
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(editor.toPlainText())
        commit_msg = self.commit_input.text().strip() or f"autosnap at {self.current_time()}"
        repo_path = os.path.dirname(path)
        rel_path = os.path.relpath(path, repo_path)
        just_initialized = False
        try:
            subprocess.run(["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "-C", repo_path, "init"], check=True)
            subprocess.run(["git", "-C", repo_path, "config", "user.name", "CheesyMamas"], check=True)
            subprocess.run(["git", "-C", repo_path, "config", "user.email", "CheesyMamas@local"], check=True)
            QMessageBox.information(self, "Git Initialized", f"Repo created in:\n{repo_path}")
            just_initialized = True
        try:
            subprocess.run(["git", "-C", repo_path, "add", "--", rel_path], check=True)
            status = subprocess.run(["git", "-C", repo_path, "status", "--porcelain", "--", rel_path],
                                    capture_output=True, text=True)

            if not status.stdout.strip() and not just_initialized:
                QMessageBox.information(self, "Nothing to Commit", "No changes to this file.")
                return
            subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_msg], check=True)
            self.commit_input.clear()
            self.load_commit_history(path, commit_list)
            self.update_commit_list_view(commit_list)
            # 🔥 Add this:
            if commit_list.count() > 0:
                self.commit_list.setCurrentRow(0)
                self.highlight_commit_diff(self.commit_list.item(0))

        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Git Error", f"Something went wrong during commit:\n\n{e}")

    def load_commit_history(self, file_path, list_widget):
        repo_path = os.path.dirname(file_path)
        rel_path = os.path.relpath(file_path, repo_path)
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "log", "--pretty=format:%h %ad %s", "--date=short", "--", rel_path],
                check=True, capture_output=True, text=True
            )
            output = result.stdout.strip()
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
                _, current_commit_list, _, _ = self.editors[current_index]
                if current_commit_list == list_widget:
                    self.update_commit_list_view(current_commit_list)
        except subprocess.CalledProcessError:
            list_widget.clear()
            list_widget.addItem("Not in a Git repo yet. First commit will start the timeline.")

    def current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

class GitLinePopup(QWidget):
    def __init__(self, line_number, old_text, revert_callback):
        super().__init__()
        self.setStyleSheet("background-color: #3d3f58; border: 1px solid #ffb86c; padding: 2px;")
        self.line_number = line_number
        self.old_text = old_text
        self.label = QLabel(f"<b>Old Line {line_number + 1}:</b> {old_text.strip()}")
        self.label.setStyleSheet("color: #f8f8f2;")
        self.revert_btn = QPushButton("↩ Revert Line")
        self.revert_btn.setStyleSheet("padding: 1px 4px; font-size: 10px;")
        self.revert_btn.clicked.connect(lambda: revert_callback(line_number, old_text))
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        layout.addWidget(self.label)
        layout.addWidget(self.revert_btn)
        self.setLayout(layout)
        self.setFixedHeight(24)
        self.setFixedWidth(self.sizeHint().width())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)

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