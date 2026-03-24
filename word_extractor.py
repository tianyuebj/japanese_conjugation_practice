# -*- coding: utf-8 -*-
"""从Anki卡片提取日语单词"""
import re
from .conjugation_rules import VerbConjugator, WORD_TYPE_NAMES

def extract_word_from_card(card):
    """从当前卡片提取日语单词"""
    if not card: return None

    # 获取卡片内容
    note = card.note()
    question = note.fields[0] if note.fields else ""
    answer = note.fields[1] if len(note.fields) > 1 else ""

    # 提取日语单词（平假名、片假名、汉字）
    text = question + " " + answer

    # 尝试提取假名（通常在括号中）
    furigana_match = re.search(r'[（(]([ぁ-んァ-ヶー]+)[）)]', text)
    furigana = furigana_match.group(1) if furigana_match else None

    # 匹配日语单词
    match = re.search(r'[ぁ-んァ-ヶー一-龯]+', text)
    if not match: return None

    word = match.group(0)

    # 如果没有找到假名，尝试从单词本身提取（如果是纯假名）
    if not furigana and re.match(r'^[ぁ-ん]+$', word):
        furigana = word

    # 识别词性
    if word.endswith(('る','う','く','ぐ','す','つ','ぬ','ぶ','む')):
        verb_type = VerbConjugator.identify_verb_type(word)
        word_type_name = WORD_TYPE_NAMES.get(verb_type, verb_type)

        # 添加词性判断依据
        reason = ""
        if verb_type == 'suru':
            reason = "以する结尾"
        elif verb_type == 'kuru':
            reason = "来る是特殊动词"
        elif verb_type == 'ichidan':
            if len(word) >= 2:
                before_ru = word[-2]
                reason = f"る前是e段假名（{before_ru}）"
        elif verb_type == 'godan':
            last_char = word[-1]
            reason = f"词尾是{last_char}"

        full_type_name = f"{word_type_name}（{reason}）" if reason else word_type_name
        return (word, 'verb', verb_type, furigana, full_type_name)
    elif word.endswith('い') and len(word) > 1:
        return (word, 'i-adj', None, furigana, 'い形容词（以い结尾）')

    return None
