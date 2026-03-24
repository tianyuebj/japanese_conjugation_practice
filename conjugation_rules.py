# -*- coding: utf-8 -*-
"""日语变形规则引擎"""

# 变形规则说明
CONJUGATION_EXPLANATIONS = {
    'verb': {
        'ichidan': {
            'masu': '一段动词：去掉る，加ます',
            'te': '一段动词：去掉る，加て',
            'ta': '一段动词：去掉る，加た',
            'nai': '一段动词：去掉る，加ない',
            'potential': '一段动词：去掉る，加られる',
            'passive': '一段动词：去掉る，加られる',
            'causative': '一段动词：去掉る，加させる'
        },
        'godan': {
            'masu': '五段动词：词尾变i段 + ます',
            'te': '五段动词：う/つ/る→って，む/ぶ/ぬ→んで，く→いて，ぐ→いで，す→して',
            'ta': '五段动词：う/つ/る→った，む/ぶ/ぬ→んだ，く→いた，ぐ→いだ，す→した',
            'nai': '五段动词：词尾变a段 + ない',
            'potential': '五段动词：词尾变e段 + る',
            'passive': '五段动词：词尾变a段 + れる',
            'causative': '五段动词：词尾变a段 + せる'
        },
        'suru': {
            'masu': 'サ变动词：する → します',
            'te': 'サ变动词：する → して',
            'ta': 'サ变动词：する → した',
            'nai': 'サ变动词：する → しない',
            'potential': 'サ变动词：する → できる',
            'passive': 'サ变动词：する → される',
            'causative': 'サ变动词：する → させる'
        },
        'kuru': {
            'masu': 'カ变动词：来る → 来ます',
            'te': 'カ变动词：来る → 来て',
            'ta': 'カ变动词：来る → 来た',
            'nai': 'カ变动词：来る → 来ない',
            'potential': 'カ变动词：来る → 来られる',
            'passive': 'カ变动词：来る → 来られる',
            'causative': 'カ变动词：来る → 来させる'
        }
    },
    'i-adj': {
        'te': 'い形容词：去掉い，加くて',
        'past': 'い形容词：去掉い，加かった',
        'negative': 'い形容词：去掉い，加くない',
        'adverb': 'い形容词：去掉い，加く'
    }
}

# 词性名称
WORD_TYPE_NAMES = {
    'ichidan': '一段动词',
    'godan': '五段动词',
    'suru': 'サ变动词',
    'kuru': 'カ变动词',
    'i-adj': 'い形容词',
    'na-adj': 'な形容词'
}

class VerbConjugator:
    IRREGULAR_VERBS = {
        'する': {'masu':'します','te':'して','ta':'した','nai':'しない','potential':'できる','passive':'される','causative':'させる'},
        '来る': {'masu':'来ます','te':'来て','ta':'来た','nai':'来ない','potential':'来られる','passive':'来られる','causative':'来させる'},
        '行く': {'te':'行って','ta':'行った'}
    }
    GODAN_STEMS = {
        'う':{'a':'わ','i':'い','e':'え','o':'お'}, 'く':{'a':'か','i':'き','e':'け','o':'こ'},
        'ぐ':{'a':'が','i':'ぎ','e':'げ','o':'ご'}, 'す':{'a':'さ','i':'し','e':'せ','o':'そ'},
        'つ':{'a':'た','i':'ち','e':'て','o':'と'}, 'ぬ':{'a':'な','i':'に','e':'ね','o':'の'},
        'ぶ':{'a':'ば','i':'び','e':'べ','o':'ぼ'}, 'む':{'a':'ま','i':'み','e':'め','o':'も'},
        'る':{'a':'ら','i':'り','e':'れ','o':'ろ'}
    }

    @staticmethod
    def identify_verb_type(verb):
        if verb.endswith('する'): return 'suru'
        if verb == '来る': return 'kuru'
        if verb.endswith('る') and len(verb)>=2 and verb[-2] in 'えけせてねへめれげぜでべぺいきしちにひみりぎじぢびぴ':
            return 'ichidan'
        return 'godan'

    @staticmethod
    def conjugate(verb, form_type, verb_type=None):
        if not verb_type: verb_type = VerbConjugator.identify_verb_type(verb)
        if verb in VerbConjugator.IRREGULAR_VERBS and form_type in VerbConjugator.IRREGULAR_VERBS[verb]:
            return VerbConjugator.IRREGULAR_VERBS[verb][form_type]
        if verb_type == 'ichidan':
            stem = verb[:-1]
            return {'masu':stem+'ます','te':stem+'て','ta':stem+'た','nai':stem+'ない',
                   'potential':stem+'られる','passive':stem+'られる','causative':stem+'させる'}.get(form_type, verb)
        if verb_type == 'godan':
            last, stem = verb[-1], verb[:-1]
            if last not in VerbConjugator.GODAN_STEMS: return verb
            s = VerbConjugator.GODAN_STEMS[last]
            if form_type == 'te':
                if last in 'うつる': return stem + s['i'][:-1] + 'って'
                if last in 'むぶぬ': return stem + s['i'][:-1] + 'んで'
                if last == 'く': return stem + 'いて'
                if last == 'ぐ': return stem + 'いで'
                if last == 'す': return stem + 'して'
            elif form_type == 'ta':
                if last in 'うつる': return stem + s['i'][:-1] + 'った'
                if last in 'むぶぬ': return stem + s['i'][:-1] + 'んだ'
                if last == 'く': return stem + 'いた'
                if last == 'ぐ': return stem + 'いだ'
                if last == 'す': return stem + 'した'
            return {'masu':stem+s['i']+'ます','nai':stem+s['a']+'ない','potential':stem+s['e']+'る',
                   'passive':stem+s['a']+'れる','causative':stem+s['a']+'せる'}.get(form_type, verb)
        return verb

    @staticmethod
    def get_all_forms(verb, verb_type=None):
        if not verb_type: verb_type = VerbConjugator.identify_verb_type(verb)
        forms = ['masu','te','ta','nai','potential','passive','causative']
        return {f: VerbConjugator.conjugate(verb, f, verb_type) for f in forms}

class AdjectiveConjugator:
    @staticmethod
    def conjugate(adj, form_type, adj_type='i'):
        if adj_type == 'i':
            if adj == 'いい': adj = 'よい'
            stem = adj[:-1]
            return {'te':stem+'くて','past':stem+'かった','negative':stem+'くない','adverb':stem+'く'}.get(form_type, adj)
        elif adj_type == 'na':
            return {'te':adj+'で','past':adj+'だった','negative':adj+'じゃない','adverb':adj+'に'}.get(form_type, adj)
        return adj

    @staticmethod
    def get_all_forms(adj, adj_type='i'):
        forms = ['te','past','negative','adverb']
        return {f: AdjectiveConjugator.conjugate(adj, f, adj_type) for f in forms}
