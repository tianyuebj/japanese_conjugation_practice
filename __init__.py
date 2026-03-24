# -*- coding: utf-8 -*-
from aqt import mw, gui_hooks
from aqt.qt import QAction, QKeySequence
from aqt.utils import showInfo
from .ui_dialog import PracticeDialog
from .word_extractor import extract_word_from_card

def on_practice_conjugation():
    """启动变形练习"""
    if not mw.reviewer.card:
        showInfo("请先开始复习卡片")
        return

    # 从当前卡片提取单词
    result = extract_word_from_card(mw.reviewer.card)

    if result is None:
        showInfo("无法从当前卡片中识别日语单词")
        return

    word, word_type, verb_type, furigana, word_type_name = result

    # 启动练习对话框
    dialog = PracticeDialog(mw, word, word_type, verb_type, furigana, word_type_name)
    dialog.exec()

def add_practice_button(card):
    """在复习界面添加练习按钮"""
    btn_style = "padding: 6px 16px; background-color: #4CAF50 !important; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px;"

    button_js = f"""
        (function() {{
            function insertBtn() {{
                var existing = document.getElementById('practice-btn');
                if (existing) existing.remove();
                var btn = document.createElement('button');
                btn.id = 'practice-btn';
                btn.textContent = '练习变形';
                btn.setAttribute('style', '{btn_style}');
                btn.onclick = function() {{ pycmd('practice_conjugation'); }};

                var outer = document.getElementById('outer');
                if (outer) {{
                    outer.style.display = 'flex';
                    outer.style.alignItems = 'center';
                    outer.style.justifyContent = 'center';
                    outer.style.gap = '8px';
                    outer.appendChild(btn);
                }} else {{
                    var wrapper = document.createElement('div');
                    wrapper.style.cssText = 'text-align:center; margin: 4px 0;';
                    wrapper.appendChild(btn);
                    document.body.appendChild(wrapper);
                }}
            }}
            setTimeout(insertBtn, 50);
        }})();
    """
    mw.reviewer.bottom.web.eval(button_js)

# 注册快捷键
action = QAction("练习变形", mw)
action.setShortcut(QKeySequence("Ctrl+J"))
action.triggered.connect(on_practice_conjugation)
mw.form.menuTools.addAction(action)

# 注册钩子
gui_hooks.reviewer_did_show_question.append(add_practice_button)
gui_hooks.reviewer_did_show_answer.append(add_practice_button)

# 处理按钮点击
def handle_pycmd(handled, cmd, context):
    if cmd == "practice_conjugation":
        on_practice_conjugation()
        return (True, None)
    return handled

gui_hooks.webview_did_receive_js_message.append(handle_pycmd)
