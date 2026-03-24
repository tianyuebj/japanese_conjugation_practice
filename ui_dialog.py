# -*- coding: utf-8 -*-
"""练习对话框界面"""
import threading
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QScrollArea, QWidget, QGridLayout, Qt
)
from aqt.utils import showInfo


def _speak(text):
    """用 Windows SAPI 朗读日语文本（后台线程，不阻塞 UI）"""
    def _run():
        try:
            import win32com.client
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            # 优先选日语语音
            for voice in sapi.GetVoices():
                if "Japanese" in voice.GetDescription() or "ja" in voice.GetDescription().lower():
                    sapi.Voice = voice
                    break
            sapi.Speak(text)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()

# ── 颜色常量 ──────────────────────────────────────────────
CLR_BG        = "#F5F7FA"
CLR_CARD      = "#FFFFFF"
CLR_PRIMARY   = "#4A90D9"
CLR_SUCCESS   = "#27AE60"
CLR_ERROR     = "#E74C3C"
CLR_NEUTRAL   = "#ECF0F1"
CLR_TEXT      = "#2C3E50"
CLR_SUBTEXT   = "#7F8C8D"
CLR_BORDER    = "#DDE3EA"

STYLE_DIALOG = f"background-color: {CLR_BG};"

STYLE_HEADER = f"""
    background-color: {CLR_CARD};
    border-bottom: 1px solid {CLR_BORDER};
    padding: 16px 20px;
"""

STYLE_WORD = f"font-size: 22px; font-weight: bold; color: {CLR_TEXT};"
STYLE_FURIGANA = f"font-size: 14px; color: {CLR_SUBTEXT}; margin-left: 8px;"
STYLE_TYPE_BADGE = f"""
    font-size: 12px; color: {CLR_PRIMARY};
    background: #EBF4FF; border-radius: 10px;
    padding: 2px 10px; margin-left: 8px;
"""

STYLE_PROGRESS_BAR = f"""
    QProgressBar {{
        border: none; border-radius: 4px;
        background: {CLR_NEUTRAL}; height: 8px; text-align: center;
    }}
    QProgressBar::chunk {{
        background: {CLR_PRIMARY}; border-radius: 4px;
    }}
"""

STYLE_QUESTION = f"font-size: 17px; color: {CLR_TEXT}; padding: 20px 20px 8px 20px;"

STYLE_OPTION_DEFAULT = f"""
    QPushButton {{
        font-size: 16px; color: {CLR_TEXT};
        background: {CLR_CARD}; border: 2px solid {CLR_BORDER};
        border-radius: 10px; padding: 14px 18px;
        text-align: left;
    }}
    QPushButton:hover {{ border-color: {CLR_PRIMARY}; background: #F0F7FF; }}
"""
STYLE_OPTION_SELECTED = f"""
    QPushButton {{
        font-size: 16px; color: {CLR_PRIMARY};
        background: #EBF4FF; border: 2px solid {CLR_PRIMARY};
        border-radius: 10px; padding: 14px 18px; text-align: left;
    }}
"""
STYLE_OPTION_CORRECT = f"""
    QPushButton {{
        font-size: 16px; color: white;
        background: {CLR_SUCCESS}; border: 2px solid {CLR_SUCCESS};
        border-radius: 10px; padding: 14px 18px; text-align: left;
    }}
"""
STYLE_OPTION_WRONG = f"""
    QPushButton {{
        font-size: 16px; color: white;
        background: {CLR_ERROR}; border: 2px solid {CLR_ERROR};
        border-radius: 10px; padding: 14px 18px; text-align: left;
    }}
"""
STYLE_OPTION_DISABLED = f"""
    QPushButton {{
        font-size: 16px; color: {CLR_SUBTEXT};
        background: {CLR_NEUTRAL}; border: 2px solid {CLR_BORDER};
        border-radius: 10px; padding: 14px 18px; text-align: left;
    }}
"""

STYLE_FEEDBACK_OK   = f"font-size: 15px; font-weight: bold; color: {CLR_SUCCESS}; padding: 0 20px;"
STYLE_FEEDBACK_ERR  = f"font-size: 15px; font-weight: bold; color: {CLR_ERROR}; padding: 0 20px;"
STYLE_RULE          = f"font-size: 13px; color: {CLR_SUBTEXT}; padding: 4px 20px 12px 20px;"

STYLE_BTN_PRIMARY = f"""
    QPushButton {{
        font-size: 15px; font-weight: bold; color: white;
        background: {CLR_PRIMARY}; border: none; border-radius: 8px;
        padding: 10px 32px;
    }}
    QPushButton:hover {{ background: #3A7BC8; }}
    QPushButton:disabled {{ background: {CLR_NEUTRAL}; color: {CLR_SUBTEXT}; }}
"""

STYLE_STATS = f"font-size: 13px; color: {CLR_SUBTEXT}; padding: 8px 20px 0 20px;"


# ── 主对话框 ──────────────────────────────────────────────
class PracticeDialog(QDialog):
    def __init__(self, parent, word, word_type, verb_type, furigana=None, word_type_name=None):
        super().__init__(parent)
        self.word = word
        self.word_type = word_type
        self.verb_type = verb_type
        self.furigana = furigana
        self.word_type_name = word_type_name
        self.questions = []
        self.current_q = 0
        self.correct_count = 0
        self.selected_btn = None

        self.setWindowTitle(f"练习「{word}」的变形")
        self.setMinimumSize(680, 580)
        self.setStyleSheet(STYLE_DIALOG)

        from .quiz_generator import QuizGenerator
        self.questions = QuizGenerator.generate_full_quiz(word, word_type, verb_type)

        if not self.questions:
            showInfo("无法为此单词生成练习题")
            self.reject()
            return

        self._setup_ui()
        self._load_question()

    # ── 构建界面 ──────────────────────────────────────────
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 顶部信息栏
        header = QFrame()
        header.setStyleSheet(STYLE_HEADER)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 12, 20, 12)

        word_label = QLabel(self.word)
        word_label.setStyleSheet(STYLE_WORD)
        h_layout.addWidget(word_label)

        if self.furigana:
            furi_label = QLabel(f"（{self.furigana}）")
            furi_label.setStyleSheet(STYLE_FURIGANA)
            h_layout.addWidget(furi_label)

        if self.word_type_name:
            badge = QLabel(self.word_type_name)
            badge.setStyleSheet(STYLE_TYPE_BADGE)
            h_layout.addWidget(badge)

        h_layout.addStretch()

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(STYLE_STATS)
        h_layout.addWidget(self.stats_label)

        root.addWidget(header)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(self.questions))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(STYLE_PROGRESS_BAR)
        root.addWidget(self.progress_bar)

        # 内容区（可滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet(f"background: {CLR_BG};")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(24, 16, 24, 16)
        self.content_layout.setSpacing(10)

        # 题目文字
        self.question_label = QLabel()
        self.question_label.setStyleSheet(STYLE_QUESTION)
        self.question_label.setWordWrap(True)
        self.content_layout.addWidget(self.question_label)

        # 选项按钮（2列网格）
        self.option_buttons = []
        self.options_grid = QGridLayout()
        self.options_grid.setSpacing(10)
        for i in range(4):
            btn = QPushButton()
            btn.setStyleSheet(STYLE_OPTION_DEFAULT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._select_option(idx))
            self.option_buttons.append(btn)
            self.options_grid.addWidget(btn, i // 2, i % 2)
        self.content_layout.addLayout(self.options_grid)

        # 反馈 + 规则
        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        self.content_layout.addWidget(self.feedback_label)

        self.rule_label = QLabel()
        self.rule_label.setWordWrap(True)
        self.rule_label.setStyleSheet(STYLE_RULE)
        self.content_layout.addWidget(self.rule_label)

        self.content_layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll)

        # 底部按钮栏
        footer = QFrame()
        footer.setStyleSheet(f"background: {CLR_CARD}; border-top: 1px solid {CLR_BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 12, 24, 12)
        f_layout.addStretch()

        self.confirm_btn = QPushButton("确认答案")
        self.confirm_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self._check_answer)
        f_layout.addWidget(self.confirm_btn)

        self.next_btn = QPushButton("下一题 →")
        self.next_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        self.next_btn.setVisible(False)
        self.next_btn.clicked.connect(self._next_question)
        f_layout.addWidget(self.next_btn)

        root.addWidget(footer)

    # ── 题目逻辑 ──────────────────────────────────────────
    def _load_question(self):
        if self.current_q >= len(self.questions):
            self._show_summary()
            return

        q = self.questions[self.current_q]
        self.selected_btn = None

        self.progress_bar.setValue(self.current_q)
        self.question_label.setText(
            f"第 {self.current_q + 1} / {len(self.questions)} 题　　"
            f"请选择「{q['word']}」的 <b>{q['form_name']}</b>："
        )
        self.question_label.setTextFormat(Qt.TextFormat.RichText)

        for i, btn in enumerate(self.option_buttons):
            if i < len(q['options']):
                btn.setText(f"  {chr(0xFF21 + i)}　{q['options'][i]}")
                btn.setVisible(True)
                btn.setEnabled(True)
                btn.setStyleSheet(STYLE_OPTION_DEFAULT)
            else:
                btn.setVisible(False)

        self.feedback_label.setText("")
        self.rule_label.setText("")
        self.confirm_btn.setVisible(True)
        self.confirm_btn.setEnabled(False)
        self.next_btn.setVisible(False)
        self._update_stats()

    def _select_option(self, idx):
        self.selected_btn = idx
        for i, btn in enumerate(self.option_buttons):
            btn.setStyleSheet(STYLE_OPTION_SELECTED if i == idx else STYLE_OPTION_DEFAULT)
        self.confirm_btn.setEnabled(True)
        q = self.questions[self.current_q]
        _speak(q['options'][idx])

    def _check_answer(self):
        if self.selected_btn is None:
            return

        q = self.questions[self.current_q]
        selected_answer = q['options'][self.selected_btn]
        is_correct = selected_answer == q['correct_answer']

        # 高亮选项
        for i, btn in enumerate(self.option_buttons):
            if not btn.isVisible():
                continue
            opt = q['options'][i]
            if opt == q['correct_answer']:
                btn.setStyleSheet(STYLE_OPTION_CORRECT)
            elif i == self.selected_btn and not is_correct:
                btn.setStyleSheet(STYLE_OPTION_WRONG)
            else:
                btn.setStyleSheet(STYLE_OPTION_DISABLED)
            btn.setEnabled(False)

        if is_correct:
            self.feedback_label.setText("✓ 正确！")
            self.feedback_label.setStyleSheet(STYLE_FEEDBACK_OK)
            self.correct_count += 1
        else:
            self.feedback_label.setText(f"✗ 错误，正确答案是：{q['correct_answer']}")
            self.feedback_label.setStyleSheet(STYLE_FEEDBACK_ERR)

        # 规则说明
        from .conjugation_rules import CONJUGATION_EXPLANATIONS
        rule_text = ""
        if self.word_type == 'verb' and self.verb_type:
            rule_text = CONJUGATION_EXPLANATIONS.get('verb', {}).get(self.verb_type, {}).get(q['form_type'], '')
        elif self.word_type == 'i-adj':
            rule_text = CONJUGATION_EXPLANATIONS.get('i-adj', {}).get(q['form_type'], '')

        if rule_text:
            self.rule_label.setText(f"💡 {rule_text}　（{self.word} → {q['correct_answer']}）")
        else:
            self.rule_label.setText("")

        self.confirm_btn.setVisible(False)
        self.next_btn.setVisible(True)
        self._update_stats()

    def _next_question(self):
        self.current_q += 1
        self._load_question()

    def _update_stats(self):
        if self.current_q == 0:
            self.stats_label.setText("")
            return
        rate = int(self.correct_count / self.current_q * 100)
        self.stats_label.setText(f"正确率 {rate}%  {self.correct_count}/{self.current_q}")

    # ── 总结页面 ──────────────────────────────────────────
    def _highlight_conjugation(self, original, conjugated):
        stem = ""
        for i in range(min(len(original), len(conjugated))):
            if original[i] == conjugated[i]:
                stem += original[i]
            else:
                break
        if not stem and len(original) > 1:
            stem = original[:-1]
        changed = conjugated[len(stem):]
        return f"<span style='color:{CLR_TEXT};'>{stem}</span><span style='color:{CLR_SUCCESS}; font-weight:bold;'>{changed}</span>"

    def _show_summary(self):
        self.progress_bar.setValue(len(self.questions))
        rate = int(self.correct_count / len(self.questions) * 100)

        from .conjugation_rules import VerbConjugator, AdjectiveConjugator
        from aqt.qt import QTextEdit

        dlg = QDialog(self)
        dlg.setWindowTitle(f"「{self.word}」练习完成")
        dlg.setMinimumSize(560, 480)
        dlg.setStyleSheet(STYLE_DIALOG)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 成绩横幅
        banner_color = CLR_SUCCESS if rate >= 70 else CLR_ERROR
        banner = QFrame()
        banner.setStyleSheet(f"background: {banner_color}; padding: 20px;")
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(24, 20, 24, 20)

        score_label = QLabel(f"{rate}%")
        score_label.setStyleSheet("font-size: 48px; font-weight: bold; color: white;")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_layout.addWidget(score_label)

        detail_label = QLabel(f"答对 {self.correct_count} / {len(self.questions)} 题")
        detail_label.setStyleSheet("font-size: 16px; color: rgba(255,255,255,0.9);")
        detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_layout.addWidget(detail_label)

        layout.addWidget(banner)

        # 变形表
        table_title = QLabel(f"「{self.word}」的所有变形")
        table_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {CLR_TEXT}; padding: 16px 24px 8px 24px;")
        layout.addWidget(table_title)

        table_html = f"""
        <table style='width:100%; border-collapse:collapse; font-size:15px;'>
        <tr style='background:{CLR_PRIMARY}; color:white;'>
            <th style='padding:10px 16px; text-align:left;'>变形类型</th>
            <th style='padding:10px 16px; text-align:left;'>变形结果</th>
        </tr>"""

        form_names = {
            'masu':'ます形','te':'て形','ta':'た形','nai':'ない形',
            'potential':'可能形','passive':'受身形','causative':'使役形',
            'past':'过去形','negative':'否定形','adverb':'副词形'
        }

        if self.word_type == 'verb':
            all_forms = VerbConjugator.get_all_forms(self.word, self.verb_type)
        else:
            all_forms = AdjectiveConjugator.get_all_forms(self.word, 'i')

        for idx, (form_type, form_value) in enumerate(all_forms.items()):
            bg = CLR_CARD if idx % 2 == 0 else CLR_NEUTRAL
            name = form_names.get(form_type, form_type)
            highlighted = self._highlight_conjugation(self.word, form_value)
            table_html += f"<tr style='background:{bg};'><td style='padding:10px 16px; color:{CLR_SUBTEXT};'>{name}</td><td style='padding:10px 16px;'>{highlighted}</td></tr>"

        table_html += "</table>"

        table_view = QTextEdit()
        table_view.setHtml(table_html)
        table_view.setReadOnly(True)
        table_view.setStyleSheet("border: none; background: transparent; margin: 0 16px;")
        layout.addWidget(table_view)

        # 关闭按钮
        footer = QFrame()
        footer.setStyleSheet(f"background: {CLR_CARD}; border-top: 1px solid {CLR_BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 12, 24, 12)
        f_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        close_btn.clicked.connect(dlg.accept)
        f_layout.addWidget(close_btn)
        layout.addWidget(footer)

        dlg.exec()
        self.accept()
