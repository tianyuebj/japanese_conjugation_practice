# -*- coding: utf-8 -*-
"""选择题生成器"""
import random
from .conjugation_rules import VerbConjugator, AdjectiveConjugator

FORM_NAMES = {
    'masu':'ます形', 'te':'て形', 'ta':'た形', 'nai':'ない形',
    'potential':'可能形', 'passive':'受身形', 'causative':'使役形',
    'past':'过去形', 'negative':'否定形', 'adverb':'副词形'
}

class QuizGenerator:
    @staticmethod
    def generate_full_quiz(word, word_type, verb_type=None):
        """生成全面模式的所有题目"""
        questions = []

        if word_type == 'verb':
            all_forms = VerbConjugator.get_all_forms(word, verb_type)
            for form_type, correct_answer in all_forms.items():
                q = QuizGenerator.generate_single_question(word, form_type, correct_answer, all_forms)
                questions.append(q)
        elif word_type == 'i-adj':
            all_forms = AdjectiveConjugator.get_all_forms(word, 'i')
            for form_type, correct_answer in all_forms.items():
                q = QuizGenerator.generate_single_question(word, form_type, correct_answer, all_forms)
                questions.append(q)

        return questions

    @staticmethod
    def generate_single_question(word, form_type, correct_answer, all_forms):
        """生成单个选择题"""
        # 生成干扰选项
        distractors = []
        for f, ans in all_forms.items():
            if f != form_type and ans != correct_answer:
                distractors.append(ans)

        # 选择3个干扰选项
        if len(distractors) >= 3:
            distractors = random.sample(distractors, 3)
        else:
            # 如果不够，生成一些错误变形
            while len(distractors) < 3:
                distractors.append(word + 'ます')  # 简单的错误示例

        # 组合选项并打乱
        options = [correct_answer] + distractors[:3]
        random.shuffle(options)

        return {
            'word': word,
            'form_type': form_type,
            'form_name': FORM_NAMES.get(form_type, form_type),
            'correct_answer': correct_answer,
            'options': options
        }
