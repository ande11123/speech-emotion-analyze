import streamlit as st
import json
import os
import re
from collections import Counter
import numpy as np
import pandas as pd

BUILTIN_CORPUS = {
    "emotion_dict": {
        "Affability": [
            "we", "us", "our", "ours", "ourselves", "everyone", "everybody",
            "friends", "friend", "hello", "hi", "hey", "remember", "do you",
            "have you", "believe", "together", "folks", "people", "listeners",
            "audience", "dear", "welcome", "greetings", "all of you",
            "each of you", "many of you", "some of you", "those of you",
            "let us", "let's", "share", "connect", "community", "fellow",
            "colleagues", "ladies and gentlemen", "good morning",
            "good afternoon", "good evening", "thank you for being here",
            "it is a pleasure", "honored to be here", "my friends",
            "dear friends", "kindred spirits", "like-minded", "stand with",
            "join me", "walk with", "side by side", "hand in hand",
            "united", "solidarity", "camaraderie", "kinship", "fellowship",
            "brotherhood", "sisterhood", "common ground", "shared vision",
            "collective", "togetherness", "oneness", "unity", "bond",
            "gather", "assemble", "congregate", "reunion", "gathering",
            "celebrate together", "march together", "dream together",
            "build together", "grow together", "learn together",
            "in this together", "one family", "global community",
            "human family", "citizens of the world"
        ],
        "Composure": [
            "first", "second", "third", "firstly", "secondly", "thirdly",
            "data shows", "data indicate", "research indicates",
            "research shows", "studies show", "studies indicate", "in fact",
            "specifically", "objectively", "statistically", "according to",
            "overall", "generally", "fundamentally", "essentially",
            "empirically", "quantitatively", "systematically", "analytically",
            "methodologically", "empirical", "evidence suggests",
            "evidence indicates", "the literature", "meta-analysis",
            "longitudinal study", "controlled experiment", "peer-reviewed",
            "scholarly", "academic", "theoretical framework", "hypothesis",
            "methodology", "analysis reveals", "findings suggest",
            "measurable", "observable", "verifiable", "replicable",
            "falsifiable", "paradigm", "model", "correlation", "causation",
            "variable", "coefficient", "significant", "insignificant",
            "p-value", "confidence interval", "standard deviation",
            "regression", "anova", "factor analysis", "cluster analysis",
            "qualitative", "quantitative", "mixed methods", "case study",
            "field study", "laboratory", "experiment", "treatment group",
            "control group", "sample size", "population", "generalize",
            "replicate", "validate", "calibrate", "benchmark", "baseline",
            "metric", "indicator", "parameter", "criterion", "taxonomy"
        ],
        "Conviction": [
            "must", "will", "undoubtedly", "unquestionably", "I believe",
            "essentially", "core", "inevitably", "certainly", "definitely",
            "absolutely", "necessarily", "decisively", "resolutely", "firmly",
            "unwaveringly", "categorically", "unequivocally", "assuredly",
            "undeniably", "incontrovertibly", "indisputably", "irrefutably",
            "conclusively", "demonstrably", "evidently", "manifestly",
            "unambiguously", "explicitly", "determinedly", "steadfastly",
            "uncompromisingly", "unflinchingly", "unhesitatingly",
            "conviction", "resolve", "determination", "perseverance",
            "dedication", "commitment", "shall", "ought", "duty",
            "obligation", "responsibility", "accountability", "principle",
            "creed", "doctrine", "tenet", "dogma", "ideology", "manifesto",
            "pledge", "vow", "oath", "swear", "guarantee", "promise",
            "assure", "ensure", "insist", "demand", "require", "mandate",
            "imperative", "crucial", "vital", "essential", "indispensable",
            "paramount", "supreme", "ultimate", "definitive", "authoritative",
            "binding", "non-negotiable", "sacrosanct", "inviolable",
            "unassailable", "unshakeable", "steadfast", "unbending",
            "unrelenting", "unyielding", "uncompromising"
        ],
        "Passion": [
            "let us", "let's", "strive", "fight", "rise", "advance",
            "forge ahead", "never retreat", "act now", "build together",
            "pursue", "endeavor", "persevere", "triumph", "conquer",
            "inspire", "empower", "transform", "revolutionize", "unleash",
            "ignite", "champion", "dedicate", "embrace", "seize",
            "mobilize", "galvanize", "propel", "accelerate", "breakthrough",
            "pioneer", "innovate", "reshape", "redefine", "transcend",
            "overcome", "prevail", "flourish", "thrive", "soar",
            "unprecedented", "extraordinary", "remarkable", "groundbreaking",
            "revolutionary", "game-changing", "paradigm shift", "milestone",
            "ardor", "fervor", "zeal", "enthusiasm", "vigor", "vitality",
            "energy", "fire", "flame", "burning", "blazing", "radiant",
            "luminous", "dazzling", "brilliant", "magnificent", "glorious",
            "sublime", "majestic", "grandeur", "splendor", "ecstasy",
            "elation", "exhilaration", "exuberance", "jubilation",
            "rapture", "bliss", "euphoria", "triumphant", "victorious",
            "champion", "heroic", "legendary", "iconic", "monumental",
            "epoch-making", "world-changing", "history-making", "trailblazing"
        ],
        "Deep Emotion": [
            "unforgettable", "moved", "grateful", "tribute", "never forget",
            "tears", "heartfelt", "warmth", "cherish", "memory", "honor",
            "thank", "appreciate", "beloved", "dear", "precious",
            "sentimental", "nostalgic", "compassion", "empathy",
            "tenderness", "devotion", "love", "affection", "admiration",
            "reverence", "awe", "wonder", "profound", "deeply", "soul",
            "spirit", "passionately", "earnestly", "sincerely", "genuinely",
            "authentically", "vulnerable", "intimate", "reflective",
            "contemplative", "meditative", "poignant", "touching",
            "moving", "heartwarming", "bittersweet", "melancholic",
            "sorrowful", "joyful", "euphoric", "blissful", "serene",
            "tranquil", "peaceful", "yearning", "longing", "pining",
            "wistful", "soulful", "spiritual", "transcendent", "ethereal",
            "celestial", "divine", "sacred", "hallowed", "reverent",
            "devout", "pious", "faithful", "loyal", "steadfast love",
            "enduring love", "unconditional", "boundless", "infinite",
            "eternal", "timeless", "everlasting", "perpetual", "abiding",
            "lingering", "haunting", "evocative", "resonant", "echoing"
        ],
        "Humor": [
            "surprisingly", "interestingly", "frankly", "actually",
            "you see", "ironically", "amusingly", "joke", "funny", "laugh",
            "humor", "witty", "comical", "lighthearted", "playful",
            "amusing", "entertaining", "chuckle", "grin", "smile",
            "paradox", "absurd", "ridiculous", "hilarious", "droll",
            "facetious", "jocular", "whimsical", "mischievous", "teasing",
            "banter", "quip", "jest", "pun", "sarcasm", "satire",
            "irony", "tongue-in-cheek", "wry", "dry humor",
            "self-deprecating", "deadpan", "giggle", "snicker", "titter",
            "chortle", "guffaw", "laughter", "comedy", "comedian",
            "farce", "slapstick", "parody", "spoof", "caricature",
            "burlesque", "travesty", "lampoon", "mockery", "ridicule",
            "derision", "scoff", "jeer", "taunt", "jibe", "gibe",
            "wisecrack", "crack", "one-liner", "punchline", "setup",
            "delivery", "timing", "cadence", "wit", "humorist",
            "satirist", "parodist", "caricaturist", "jester", "fool",
            "clown", "buffoon", "harlequin", "punch", "zinger"
        ],
        "Solemnity": [
            "regret", "crisis", "severe", "tragic", "cannot ignore",
            "harsh", "reality", "cost", "painful", "reflect",
            "concerning", "alarming", "devastating", "grave", "dire",
            "somber", "melancholy", "grievous", "lamentable", "woeful",
            "deplorable", "catastrophic", "calamitous", "ruinous",
            "destructive", "perilous", "hazardous", "jeopardy", "threat",
            "danger", "risk", "menace", "peril", "endanger", "critical",
            "urgent", "pressing", "acute", "intense", "drastic", "radical",
            "profoundly disturbing", "deeply troubling", "worrisome",
            "disconcerting", "unsettling", "distressing", "heartbreaking",
            "shattering", "crushing", "overwhelming", "staggering",
            "appalling", "mourn", "grieve", "lament", "bewail", "bemoan",
            "deplore", "rue", "sorrow", "woe", "anguish", "agony",
            "torment", "tribulation", "adversity", "hardship", "suffering",
            "misery", "despair", "hopelessness", "desolation", "gloom",
            "doom", "fate", "destiny", "inevitable", "inexorable",
            "relentless", "merciless", "pitiless", "unforgiving", "grim"
        ],
        "Critical Thinking": [
            "why", "could it be", "really", "essence", "conversely",
            "on the contrary", "however", "but", "question is", "challenge",
            "examine", "scrutinize", "analyze", "probe", "investigate",
            "contemplate", "ponder", "reconsider", "rethink", "question",
            "doubt", "debate", "argue", "dispute", "contest", "contradict",
            "paradox", "dilemma", "ambiguity", "nuance", "complexity",
            "intricacy", "subtlety", "sophistication", "layered",
            "multifaceted", "interdisciplinary", "cross-disciplinary",
            "meta-level", "deconstruct", "unpack", "unravel", "decipher",
            "decode", "interpret", "hermeneutics", "epistemology",
            "ontology", "teleology", "methodology", "pedagogy",
            "heuristic", "allegory", "metaphor", "synecdoche",
            "metonymy", "chiasmus", "anaphora", "epistrophe", "antithesis",
            "oxymoron", "aporia", "dialectic", "synthesis", "thesis",
            "antithesis", "socratic", "platonic", "aristotelian",
            "kantian", "hegelian", "nietzschean", "wittgensteinian",
            "foucaultian", "derrida", "semiotics", "linguistics",
            "pragmatics", "semantics", "syntax", "rhetoric", "logic",
            "ethics", "aesthetics", "metaphysics", "phenomenology",
            "existentialism", "structuralism", "post-structuralism",
            "deconstruction", "constructivism", "relativism", "absolutism"
        ]
    },
    "scene_rules": {
        "Academic Competition": {
            "opening": {"expected": ["Affability", "Humor"], "max_intensity": 6},
            "body_front": {"expected": ["Composure", "Deep Emotion", "Critical Thinking"], "max_intensity": 7},
            "body_back": {"expected": ["Conviction", "Critical Thinking", "Solemnity"], "min_intensity": 4},
            "ending": {"expected": ["Passion", "Deep Emotion", "Conviction"], "min_intensity": 6}
        },
        "Corporate Presentation": {
            "opening": {"expected": ["Affability", "Composure"], "max_intensity": 5},
            "body_front": {"expected": ["Composure", "Critical Thinking"], "max_intensity": 6},
            "body_back": {"expected": ["Conviction", "Composure"], "min_intensity": 3},
            "ending": {"expected": ["Conviction", "Composure"], "min_intensity": 4}
        },
        "Commemorative Address": {
            "opening": {"expected": ["Deep Emotion", "Composure"], "max_intensity": 6},
            "body_front": {"expected": ["Solemnity", "Composure", "Deep Emotion"], "max_intensity": 7},
            "body_back": {"expected": ["Conviction", "Passion"], "min_intensity": 5},
            "ending": {"expected": ["Passion", "Conviction", "Deep Emotion"], "min_intensity": 7}
        }
    }
}

NEGATION_WORDS = {
    "not", "no", "never", "neither", "nor", "cannot", "can't", "don't",
    "doesn't", "didn't", "won't", "wouldn't", "shouldn't", "couldn't",
    "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
    "hadn't", "without", "lack", "lacking", "absent", "devoid",
    "nothing", "nobody", "nowhere", "none", "hardly", "barely",
    "scarcely", "rarely", "seldom", "unlikely", "impossible"
}

DEGREE_ADVERBS = {
    "extremely": 2.0, "incredibly": 1.9, "tremendously": 1.8,
    "enormously": 1.8, "immensely": 1.7, "vastly": 1.7,
    "profoundly": 1.7, "deeply": 1.6, "intensely": 1.6,
    "fiercely": 1.6, "passionately": 1.6, "vehemently": 1.5,
    "strongly": 1.5, "powerfully": 1.5, "mightily": 1.5,
    "very": 1.4, "quite": 1.3, "rather": 1.2, "fairly": 1.1,
    "somewhat": 0.8, "slightly": 0.7, "a bit": 0.7,
    "a little": 0.6, "barely": 0.4, "scarcely": 0.4,
    "hardly": 0.3, "almost": 0.5, "nearly": 0.5
}

DEFAULT_RULES = BUILTIN_CORPUS["scene_rules"]["Academic Competition"]


class CorpusLoader:
    def __init__(self):
        self.base_corpus = None
        self.base_status = ""
        self.emobank = None
        self.emobank_status = ""
        self.benchmark = None
        self.benchmark_status = ""
        self.load_all()

    def load_all(self):
        self.base_corpus, self.base_status = self._load_base_corpus()
        self.emobank, self.emobank_status = self._load_emobank()
        self.benchmark, self.benchmark_status = self._load_benchmark()

    def _load_base_corpus(self, path="emotion_corpus.json"):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    corpus = json.load(f)
                if "emotion_dict" in corpus and "structure_rule" in corpus:
                    name = corpus.get("corpus_info", {}).get("name", "Custom Lexicon")
                    return corpus, f"[OK] Base lexicon loaded: {name}"
                else:
                    return BUILTIN_CORPUS, "[WARN] Lexicon format invalid; using built-in fallback"
            except Exception:
                return BUILTIN_CORPUS, "[WARN] Lexicon read failed; using built-in fallback"
        else:
            return BUILTIN_CORPUS, "[INFO] Using built-in English emotion lexicon (expanded)"

    def _load_emobank(self, path="emobank_processed.json"):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "word_vad" in data:
                    count = len(data["word_vad"])
                    return data, f"[OK] EmoBank VAD lexicon: {count} entries"
                else:
                    return None, "[WARN] EmoBank format invalid; VAD disabled"
            except Exception:
                return None, "[WARN] EmoBank read failed; VAD disabled"
        else:
            return None, "[INFO] EmoBank not detected; keyword-only mode"

    def _load_benchmark(self, path="benchmark_corpus.json"):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "ted_talks" in data or "american_rhetoric" in data:
                    ted_count = len(data.get("ted_talks", []))
                    ar_count = len(data.get("american_rhetoric", []))
                    return data, f"[OK] Benchmark corpus: TED {ted_count} | Rhetoric {ar_count}"
                else:
                    return None, "[WARN] Benchmark format invalid; comparison disabled"
            except Exception:
                return None, "[WARN] Benchmark read failed; comparison disabled"
        else:
            return None, "[INFO] Benchmark corpus not detected; comparison disabled"


class SpeechEmotionAnalyzer:
    def __init__(self, base_corpus, emobank=None, scene="Academic Competition"):
        self.corpus = base_corpus
        self.emotion_dict = self.corpus["emotion_dict"]
        self.emotions = list(self.emotion_dict.keys())
        self.emobank = emobank
        self.scene = scene
        self.rules = self.corpus.get("scene_rules", {}).get(scene, DEFAULT_RULES)

    def set_scene(self, scene):
        self.scene = scene
        self.rules = self.corpus.get("scene_rules", {}).get(scene, DEFAULT_RULES)

    def split_paragraphs(self, text):
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]
        return paragraphs

    def split_sentences(self, text):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def calc_vad(self, text):
        if self.emobank and "word_vad" in self.emobank:
            tokens = re.findall(r'[a-zA-Z]+', text.lower())
            v_list, a_list, d_list = [], [], []
            for w in tokens:
                if w in self.emobank["word_vad"]:
                    vad = self.emobank["word_vad"][w]
                    v_list.append(vad["v"])
                    a_list.append(vad["a"])
                    d_list.append(vad["d"])
            if v_list:
                return {
                    "v": round(sum(v_list) / len(v_list), 2),
                    "a": round(sum(a_list) / len(a_list), 2),
                    "d": round(sum(d_list) / len(d_list), 2)
                }
        emo_score = sum(
            len([kw for kw in kws if kw.lower() in text.lower()])
            for kws in self.emotion_dict.values()
        )
        arousal = min(9.0, emo_score * 1.2)
        positive_emos = ["Affability", "Passion", "Deep Emotion", "Humor", "Conviction"]
        negative_emos = ["Solemnity", "Critical Thinking"]
        pos_count = sum(
            1 for emo in positive_emos
            if any(kw.lower() in text.lower() for kw in self.emotion_dict[emo])
        )
        neg_count = sum(
            1 for emo in negative_emos
            if any(kw.lower() in text.lower() for kw in self.emotion_dict[emo])
        )
        valence = 5.0 + (pos_count - neg_count) * 0.7
        valence = max(1.0, min(9.0, valence))
        return {
            "v": round(valence, 2),
            "a": round(arousal, 2),
            "d": round(arousal * 0.75, 2)
        }

    def _detect_negation_context(self, text_lower, keyword, keyword_pos):
        prefix = text_lower[max(0, keyword_pos - 30):keyword_pos]
        prefix_words = re.findall(r'\b\w+\b', prefix)
        for w in prefix_words[-3:]:
            if w in NEGATION_WORDS:
                return True
        return False

    def _get_degree_multiplier(self, text_lower, keyword_pos):
        prefix = text_lower[max(0, keyword_pos - 40):keyword_pos]
        for adv, mult in DEGREE_ADVERBS.items():
            if adv in prefix:
                adv_pos = prefix.rfind(adv)
                between = prefix[adv_pos + len(adv):]
                if len(re.findall(r'\b\w+\b', between)) <= 3:
                    return mult
        return 1.0

    def detect_emotion_detail(self, text):
        text_lower = text.lower()
        scores = {}
        hit_keywords = {}
        negated_hits = {}

        for emo, keywords in self.emotion_dict.items():
            emo_score = 0.0
            hits = []
            negated = []
            for kw in keywords:
                kw_lower = kw.lower()
                start = 0
                while True:
                    pos = text_lower.find(kw_lower, start)
                    if pos == -1:
                        break
                    is_negated = self._detect_negation_context(text_lower, kw, pos)
                    degree_mult = self._get_degree_multiplier(text_lower, pos)
                    if is_negated:
                        negated.append(kw)
                        emo_score -= 0.5 * degree_mult
                    else:
                        hits.append(kw)
                        emo_score += 1.0 * degree_mult
                    start = pos + len(kw_lower)
            scores[emo] = round(emo_score, 2)
            hit_keywords[emo] = list(set(hits))
            negated_hits[emo] = list(set(negated))

        max_score = max(scores.values())
        if max_score <= 0:
            dominant_emo = "Neutral"
            intensity = 0.0
        else:
            dominant_emo = max(scores, key=scores.get)
            word_count = max(1, len(re.findall(r'\b\w+\b', text)))
            density = max_score / word_count * 100
            intensity = min(10.0, max_score * 1.2 + density * 0.25)

        mixed = []
        sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
        if sorted_scores[0][1] > 0 and len(sorted_scores) > 1:
            for emo, sc in sorted_scores[1:]:
                if sc > 0 and sc >= sorted_scores[0][1] * 0.6:
                    mixed.append(emo)

        vad = self.calc_vad(text)
        return {
            "dominant": dominant_emo,
            "intensity": round(intensity, 1),
            "scores": scores,
            "hit_keywords": hit_keywords,
            "negated_keywords": negated_hits,
            "mixed_emotions": mixed,
            "vad": vad
        }

    def detect_rhetorical_devices(self, text):
        devices = {}
        text_lower = text.lower()

        rq_count = len(re.findall(r'[^\n]*\?\s*$', text, re.MULTILINE))
        devices["rhetorical_questions"] = rq_count

        words = re.findall(r'\b[a-zA-Z]{4,}\b', text_lower)
        word_counts = Counter(words)
        repeated = {w: c for w, c in word_counts.items() if c >= 3}
        devices["repeated_words"] = repeated

        triples = re.findall(r'\b\w+\s*,\s*\w+\s*,\s*(?:and\s+)?\w+\b', text)
        devices["triples"] = len(triples)

        sentences = self.split_sentences(text)
        anaphora_count = 0
        for i in range(len(sentences) - 1):
            first_w1 = re.findall(r'\b\w+\b', sentences[i])
            first_w2 = re.findall(r'\b\w+\b', sentences[i + 1])
            if first_w1 and first_w2 and first_w1[0].lower() == first_w2[0].lower():
                anaphora_count += 1
        devices["anaphora"] = anaphora_count

        parallel = re.findall(r'\b(to \w+[^,]*),\s*(to \w+[^,]*),\s*(to \w+)', text)
        devices["parallelism"] = len(parallel)

        return devices

    def calc_readability(self, text):
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        word_count = len(words)
        sentences = self.split_sentences(text)
        sent_count = max(1, len(sentences))
        syllables = sum(self._count_syllables(w) for w in words)
        syllable_count = max(1, syllables)

        fre = 206.835 - 1.015 * (word_count / sent_count) - 84.6 * (syllable_count / word_count)
        fre = max(0, min(100, fre))

        fkgl = 0.39 * (word_count / sent_count) + 11.8 * (syllable_count / word_count) - 15.59

        if fre >= 80:
            level = "Very Easy (Grade 5-6)"
        elif fre >= 60:
            level = "Standard (Grade 7-9)"
        elif fre >= 40:
            level = "Difficult (Grade 10-12)"
        else:
            level = "Very Difficult (College+)"

        return {
            "flesch_reading_ease": round(fre, 1),
            "flesch_kincaid_grade": round(fkgl, 1),
            "level": level,
            "avg_syllables_per_word": round(syllable_count / word_count, 2)
        }

    def _count_syllables(self, word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        prev_char_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                count += 1
            prev_char_was_vowel = is_vowel
        if word.endswith("e") and count > 1:
            count -= 1
        return max(1, count)

    def detect_emotional_shifts(self, para_details):
        shifts = []
        for i in range(len(para_details) - 1):
            curr = para_details[i]
            nxt = para_details[i + 1]
            if curr["dominant"] != nxt["dominant"] and curr["dominant"] != "Neutral" and nxt["dominant"] != "Neutral":
                intensity_diff = abs(curr["intensity"] - nxt["intensity"])
                if intensity_diff >= 3:
                    shifts.append({
                        "from_para": curr["index"],
                        "to_para": nxt["index"],
                        "from_emotion": curr["dominant"],
                        "to_emotion": nxt["dominant"],
                        "intensity_change": round(intensity_diff, 1),
                        "abruptness": "High" if intensity_diff >= 5 else "Moderate"
                    })
        return shifts

    def analyze_structure(self, paragraphs):
        n = len(paragraphs)
        if n < 4:
            return {
                "opening": paragraphs[0:1] if n >= 1 else [],
                "body_front": paragraphs[1:2] if n >= 2 else [],
                "body_back": paragraphs[2:3] if n >= 3 else [],
                "ending": paragraphs[3:] if n >= 4 else []
            }
        opening_end = max(1, int(n * 0.15))
        body_front_end = int(n * 0.45)
        body_back_end = int(n * 0.75)
        return {
            "opening": paragraphs[:opening_end],
            "body_front": paragraphs[opening_end:body_front_end],
            "body_back": paragraphs[body_front_end:body_back_end],
            "ending": paragraphs[body_back_end:]
        }

    def get_vad_curve(self, paragraphs):
        curve = []
        n = len(paragraphs)
        for i, p in enumerate(paragraphs):
            vad = self.calc_vad(p)
            curve.append({
                "position": round((i + 1) / n, 2),
                "v": vad["v"],
                "a": vad["a"],
                "d": vad["d"]
            })
        return curve

    def full_analysis(self, text):
        paragraphs = self.split_paragraphs(text)
        structure = self.analyze_structure(paragraphs)
        structure_paragraph_index = self._map_structure_paragraphs(paragraphs, structure)

        para_details = []
        for i, p in enumerate(paragraphs):
            detail = self.detect_emotion_detail(p)
            short_text = (p[:80] + "...") if len(p) > 80 else p
            part = "Unknown"
            for pname, (start, end) in structure_paragraph_index.items():
                if start <= i < end:
                    part = pname
                    break
            para_details.append({
                "index": i + 1,
                "text": short_text,
                "full_text": p,
                "part": part,
                "dominant": detail["dominant"],
                "intensity": detail["intensity"],
                "scores": detail["scores"],
                "hit_keywords": detail["hit_keywords"],
                "negated_keywords": detail["negated_keywords"],
                "mixed_emotions": detail["mixed_emotions"],
                "vad": detail["vad"]
            })

        structure_emotion = {}
        structure_intensity = {}
        structure_vad = {}
        for part, paras in structure.items():
            if not paras:
                structure_emotion[part] = "Neutral"
                structure_intensity[part] = 0.0
                structure_vad[part] = {"v": 5.0, "a": 0.0, "d": 0.0}
                continue
            emo_list = [self.detect_emotion_detail(p)["dominant"] for p in paras]
            intensity_list = [self.detect_emotion_detail(p)["intensity"] for p in paras]
            vad_list = [self.calc_vad(p) for p in paras]
            structure_emotion[part] = Counter(emo_list).most_common(1)[0][0]
            structure_intensity[part] = round(sum(intensity_list) / len(intensity_list), 1)
            structure_vad[part] = {
                "v": round(sum(v["v"] for v in vad_list) / len(vad_list), 2),
                "a": round(sum(v["a"] for v in vad_list) / len(vad_list), 2),
                "d": round(sum(v["d"] for v in vad_list) / len(vad_list), 2)
            }

        intensity_list = [p["intensity"] for p in para_details]
        progression_score = self._evaluate_progression(intensity_list)
        diagnosis = self._detailed_diagnosis(para_details, structure)
        total_score = self._calculate_total_score(structure_emotion, progression_score, len(diagnosis))
        vad_curve = self.get_vad_curve(paragraphs)
        basic_info = self._basic_info(text, paragraphs)
        rhetorical = self.detect_rhetorical_devices(text)
        readability = self.calc_readability(text)
        emotional_shifts = self.detect_emotional_shifts(para_details)

        return {
            "basic_info": basic_info,
            "paragraphs": para_details,
            "structure_emotion": structure_emotion,
            "structure_intensity": structure_intensity,
            "structure_vad": structure_vad,
            "progression_score": progression_score,
            "diagnosis": diagnosis,
            "total_score": total_score,
            "total_paras": len(paragraphs),
            "total_chars": len(text),
            "vad_curve": vad_curve,
            "rhetorical_devices": rhetorical,
            "readability": readability,
            "emotional_shifts": emotional_shifts
        }

    def _basic_info(self, text, paragraphs):
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        word_count = len(words)
        duration_min = round(word_count / 130.0, 1)

        first_person_sg = len(re.findall(r'\b(I|me|my|mine|myself)\b', text, re.IGNORECASE))
        first_person_pl = len(re.findall(r'\b(we|us|our|ours|ourselves)\b', text, re.IGNORECASE))
        second_person = len(re.findall(r'\b(you|your|yours|yourself|yourselves)\b', text, re.IGNORECASE))
        third_person = len(re.findall(r'\b(he|she|it|they|them|their|his|her|its)\b', text, re.IGNORECASE))

        sentences = self.split_sentences(text)
        sent_count = len(sentences)
        avg_sent_len = round(word_count / max(1, sent_count), 1)

        sent_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        sent_length_std = round(float(np.std(sent_lengths)), 1) if sent_lengths else 0

        quotable = []
        for s in sentences:
            s_words = len(re.findall(r'\b\w+\b', s))
            if 8 <= s_words <= 25 and (',' in s or ';' in s or ':' in s):
                quotable.append(s)

        unique_words = set(w.lower() for w in words)
        ttr = round(len(unique_words) / max(1, word_count), 3)

        word_freq = Counter(w.lower() for w in words)
        hapax = sum(1 for c in word_freq.values() if c == 1)
        hapax_ratio = round(hapax / max(1, word_count), 3)

        conjunctions = len(re.findall(r'\b(and|but|or|so|yet|for|nor|because|although|however|therefore|moreover|furthermore|nevertheless|consequently)\b', text, re.IGNORECASE))
        conjunction_density = round(conjunctions / max(1, sent_count), 2)

        return {
            "word_count": word_count,
            "char_count": len(text),
            "para_count": len(paragraphs),
            "sentence_count": sent_count,
            "avg_sentence_length": avg_sent_len,
            "sentence_length_std": sent_length_std,
            "duration_min": duration_min,
            "first_person_sg": first_person_sg,
            "first_person_pl": first_person_pl,
            "second_person": second_person,
            "third_person": third_person,
            "quotable_count": len(quotable),
            "quotable_examples": quotable[:3],
            "lexical_diversity": ttr,
            "hapax_legomena": hapax,
            "hapax_ratio": hapax_ratio,
            "conjunction_density": conjunction_density
        }

    def _map_structure_paragraphs(self, paragraphs, structure):
        idx_map = {}
        current = 0
        for part, paras in structure.items():
            length = len(paras)
            idx_map[part] = (current, current + length)
            current += length
        return idx_map

    def _evaluate_progression(self, intensity_list):
        if len(intensity_list) < 3:
            return 6.0
        n = len(intensity_list)
        first_third = sum(intensity_list[:n // 3]) / max(1, n // 3)
        last_third = sum(intensity_list[-n // 3:]) / max(1, n // 3)
        base_score = 8.0 if last_third > first_third else 5.0
        mean_int = sum(intensity_list) / len(intensity_list)
        variance = sum((x - mean_int) ** 2 for x in intensity_list) / len(intensity_list)
        if variance < 3:
            base_score -= 1.5
        elif variance > 20:
            base_score -= 0.5
        return round(min(10.0, max(0.0, base_score)), 1)

    def _detailed_diagnosis(self, para_details, structure):
        part_names = {
            "opening": "Opening",
            "body_front": "Body (Front)",
            "body_back": "Body (Back)",
            "ending": "Ending"
        }
        diagnosis = []

        for part, paras in structure.items():
            if not paras:
                continue
            part_paras = [p for p in para_details if p["part"] == part]
            if not part_paras:
                continue
            dominant_emos = Counter([p["dominant"] for p in part_paras]).most_common(2)
            avg_intensity = sum(p["intensity"] for p in part_paras) / len(part_paras)

            rule = self.rules[part]
            expected = rule["expected"]
            main_emo = dominant_emos[0][0]

            if main_emo not in expected and main_emo != "Neutral":
                severity = "Moderate" if part in ["opening", "ending"] else "Mild"
                evidence = f"Dominant emotion '{main_emo}' detected in {part_names[part]}; expected categories: {', '.join(expected)}."
                recommendation = (
                    f"Revise {part_names[part].lower()} diction to shift from '{main_emo}' toward "
                    f"{'/'.join(expected)}. Replace high-arousal markers with calibrated alternatives."
                )
                diagnosis.append({
                    "type": "Emotion Category Mismatch",
                    "part": part_names[part],
                    "severity": severity,
                    "current": f"Dominant: {main_emo}",
                    "expected": f"Expected: {', '.join(expected)}",
                    "evidence": evidence,
                    "suggestion": recommendation
                })

            if "max_intensity" in rule and avg_intensity > rule["max_intensity"]:
                evidence = (
                    f"Mean intensity {avg_intensity:.1f}/10 exceeds the recommended ceiling "
                    f"of {rule['max_intensity']} for {part_names[part].lower()}."
                )
                recommendation = (
                    "Reduce emotional saturation: employ declarative syntax, attenuate intensifiers, "
                    "and reserve peak arousal for structural climaxes."
                )
                diagnosis.append({
                    "type": "Excessive Emotional Intensity",
                    "part": part_names[part],
                    "severity": "Mild",
                    "current": f"Mean intensity: {avg_intensity:.1f}/10",
                    "expected": f"Threshold: <= {rule['max_intensity']}",
                    "evidence": evidence,
                    "suggestion": recommendation
                })

            if "min_intensity" in rule and avg_intensity < rule["min_intensity"]:
                evidence = (
                    f"Mean intensity {avg_intensity:.1f}/10 falls below the recommended floor "
                    f"of {rule['min_intensity']} for {part_names[part].lower()}."
                )
                recommendation = (
                    "Amplify affective load: incorporate parallelism, rhetorical questions, "
                    "and intensifying adverbs to elevate audience engagement."
                )
                diagnosis.append({
                    "type": "Insufficient Emotional Intensity",
                    "part": part_names[part],
                    "severity": "Moderate",
                    "current": f"Mean intensity: {avg_intensity:.1f}/10",
                    "expected": f"Threshold: >= {rule['min_intensity']}",
                    "evidence": evidence,
                    "suggestion": recommendation
                })

        return diagnosis

    def _calculate_total_score(self, structure_emotion, progression_score, problem_count):
        base_score = 80.0
        base_score -= problem_count * 5.0
        base_score += progression_score * 2.0
        return round(max(0.0, min(100.0, base_score)), 1)


class SpeechPolisher:
    def __init__(self):
        self.polish_templates = {
            "Elevate Passion": [
                ("We need to move forward.",
                 "Let us forge ahead with unwavering resolve, transforming aspiration into achievement."),
                ("This is important.",
                 "This is not merely important—it is pivotal, a defining juncture that demands our fullest commitment.")
            ],
            "Attenuate to Composure": [
                ("This is absolutely the most critical issue we have ever faced!",
                 "This represents a significant challenge that warrants careful and systematic attention."),
                ("We must act immediately without any delay whatsoever!",
                 "We should consider a phased implementation strategy to address this matter effectively.")
            ],
            "Increase Affability": [
                ("Everyone has experienced this.",
                 "I suspect many of you in this room have encountered something remarkably similar."),
                ("My topic today is climate change.",
                 "Today, I would like to share with you a subject that has occupied my thoughts for some time.")
            ],
            "Strengthen Conviction": [
                ("This might be somewhat important.",
                 "The significance of this matter is unequivocal and demands our immediate and sustained attention."),
                ("I think this is the case.",
                 "I am convinced—beyond any reasonable doubt—that this represents the fundamental truth of the matter.")
            ]
        }

    def generate_polish_tips(self, diagnosis):
        polish_result = []
        for d in diagnosis:
            if d["type"] == "Insufficient Emotional Intensity" and d["part"] == "Ending":
                key = "Elevate Passion"
            elif d["type"] == "Excessive Emotional Intensity" and d["part"] == "Opening":
                key = "Attenuate to Composure"
            elif d["type"] == "Emotion Category Mismatch" and d["part"] == "Opening":
                key = "Increase Affability"
            elif d["type"] == "Insufficient Emotional Intensity":
                key = "Strengthen Conviction"
            elif d["type"] == "Excessive Emotional Intensity":
                key = "Attenuate to Composure"
            else:
                key = "Elevate Passion"

            examples = self.polish_templates.get(key, [])
            polish_result.append({
                "part": d["part"],
                "target": key,
                "examples": examples
            })
        return polish_result

    def generate_style_suggestion(self, basic_info, readability, rhetorical):
        tips = []

        if basic_info["quotable_count"] == 0:
            tips.append("No quotable sentences detected. Craft 1-2 memorable aphoristic statements.")
        elif basic_info["quotable_count"] < 2:
            tips.append("Quotable sentence density is low. Distill core arguments into concise parallel structures.")

        total_pronouns = (basic_info["first_person_sg"] + basic_info["first_person_pl"]
                          + basic_info["second_person"] + basic_info["third_person"])
        if total_pronouns > 0:
            second_ratio = basic_info["second_person"] / total_pronouns
            if second_ratio < 0.15:
                tips.append("Second-person address is sparse. Increase direct audience engagement.")
            first_sg_ratio = basic_info["first_person_sg"] / total_pronouns
            if first_sg_ratio > 0.5:
                tips.append("First-person singular pronouns dominate. Shift to plural 'we'/'our' for collective identity.")

        if basic_info["lexical_diversity"] < 0.4:
            tips.append("Lexical diversity (TTR) is below 0.40. Expand vocabulary to avoid repetition.")

        if basic_info["avg_sentence_length"] > 25:
            tips.append("Average sentence length exceeds 25 words. Introduce shorter sentences for rhythmic contrast.")
        elif basic_info["avg_sentence_length"] < 10:
            tips.append("Average sentence length is below 10 words. Incorporate complex sentences for nuance.")

        if readability["flesch_kincaid_grade"] > 14:
            tips.append(f"Readability grade level ({readability['flesch_kincaid_grade']}) is very high. Simplify syntax for broader accessibility.")
        elif readability["flesch_kincaid_grade"] < 6:
            tips.append(f"Readability grade level ({readability['flesch_kincaid_grade']}) is very low. Elevate diction for formal contexts.")

        if rhetorical["rhetorical_questions"] == 0:
            tips.append("No rhetorical questions detected. Consider incorporating 1-2 to engage audience reflection.")
        if rhetorical["anaphora"] == 0 and basic_info["word_count"] > 200:
            tips.append("No anaphora detected. Anaphora (repeated sentence openings) can amplify emotional impact.")
        if rhetorical["triples"] == 0:
            tips.append("No triple structures detected. Rule of three (A, B, C) enhances memorability.")

        if basic_info["sentence_length_std"] < 3:
            tips.append("Sentence length variance is low. Vary sentence length to create rhythmic tension and release.")

        return tips


class SpeechReviser:
    def __init__(self):
        self.polisher = SpeechPolisher()

    def generate_detailed_suggestions(self, analysis):
        return {
            "overall": self._overall_evaluation(analysis),
            "strengths": self._find_strengths(analysis),
            "problems": self._summarize_problems(analysis["diagnosis"]),
            "revision_guide": self._revision_guide(analysis),
            "polish_examples": self.polisher.generate_polish_tips(analysis["diagnosis"]),
            "extra_tips": self.polisher.generate_style_suggestion(
                analysis["basic_info"], analysis["readability"], analysis["rhetorical_devices"]
            ),
            "paragraph_tips": self._paragraph_tips(analysis["paragraphs"]),
            "emotional_shifts": analysis["emotional_shifts"]
        }

    def _overall_evaluation(self, analysis):
        score = analysis["total_score"]
        if score >= 90:
            grade = "Exceptional"
            comment = "Affective architecture is meticulously calibrated; sophisticated emotional pacing and structural coherence."
        elif score >= 75:
            grade = "Proficient"
            comment = "Overall affective framework is sound; targeted refinements at segment boundaries would elevate delivery."
        elif score >= 60:
            grade = "Developing"
            comment = "Basic structural logic is present, but affective misalignments require systematic recalibration."
        else:
            grade = "Foundational"
            comment = "Affective distribution lacks coherent design; structural re-architecture is recommended."
        return {
            "score": score, "grade": grade,
            "comment": comment,
            "progression": analysis["progression_score"]
        }

    def _find_strengths(self, analysis):
        strengths = []
        struc_emo = analysis["structure_emotion"]
        rules = DEFAULT_RULES

        if struc_emo["opening"] in rules["opening"]["expected"]:
            strengths.append("Opening affect is appropriately calibrated, establishing immediate rapport.")
        if struc_emo["ending"] in rules["ending"]["expected"]:
            strengths.append("Conclusion achieves requisite affective climax, leaving a durable impression.")
        if analysis["progression_score"] >= 7:
            strengths.append("Emotional progression demonstrates a well-constructed arc with effective build and release.")
        if not analysis["diagnosis"]:
            strengths.append("No affective misalignments detected; segment-level emotions conform to the structural model.")
        if analysis["basic_info"]["quotable_count"] >= 3:
            strengths.append("Quotable sentence density is commendable, enhancing memorability.")
        if analysis["basic_info"]["lexical_diversity"] >= 0.5:
            strengths.append("Lexical diversity is robust, indicating sophisticated and varied vocabulary.")
        if analysis["rhetorical_devices"]["anaphora"] >= 1:
            strengths.append("Anaphora detected, demonstrating deliberate rhetorical craftsmanship.")
        if analysis["rhetorical_devices"]["rhetorical_questions"] >= 2:
            strengths.append("Effective use of rhetorical questions to engage audience cognition.")
        if analysis["readability"]["flesch_reading_ease"] >= 50:
            strengths.append("Readability is well-calibrated for oral delivery (Flesch score adequate).")
        if not strengths:
            strengths.append("The draft possesses structural completeness and provides a viable foundation for refinement.")
        return strengths

    def _summarize_problems(self, diagnosis):
        if not diagnosis:
            return []
        problems = []
        for d in diagnosis:
            problems.append({
                "Segment": d["part"],
                "Finding": d["type"],
                "Severity": d["severity"],
                "Current State": d["current"],
                "Expected State": d["expected"],
                "Evidence": d["evidence"],
                "Recommendation": d["suggestion"]
            })
        return problems

    def _revision_guide(self, analysis):
        guides = []
        method_map = {
            "Elevate Passion": [
                "Fragment long sentences into shorter, staccato units to accelerate pacing",
                "Deploy anaphora, epistrophe, and rhetorical questions to amplify momentum",
                "Substitute neutral verbs with high-energy alternatives",
                "Incorporate direct calls to action and collective imperatives",
                "Use first-person plural to construct shared identity and collective agency"
            ],
            "Attenuate to Composure": [
                "Combine short sentences into complex, hypotactic structures to decelerate pacing",
                "Eliminate exclamatory constructions and superlative intensifiers",
                "Replace affective diction with neutral, descriptive terminology",
                "Embed empirical evidence and quantitative data to ground claims",
                "Remove hyperbolic and absolute modifiers"
            ],
            "Increase Affability": [
                "Introduce direct address ('you,' 'your') and collective pronouns ('we,' 'us')",
                "Deploy rhetorical questions to invite audience reflection",
                "Adopt a conversational register with colloquial connectives",
                "Incorporate brief personal anecdotes to humanize the speaker"
            ],
            "Strengthen Conviction": [
                "Employ modal verbs of necessity ('must,' 'will,' 'shall')",
                "Use definitional and categorical assertion patterns",
                "Eliminate hedging language ('might,' 'perhaps,' 'possibly')",
                "Prefix claims with 'essentially,' 'fundamentally,' or 'at its core'"
            ]
        }

        for d in analysis["diagnosis"]:
            if d["type"] == "Insufficient Emotional Intensity" and d["part"] == "Ending":
                key = "Elevate Passion"
            elif d["type"] == "Excessive Emotional Intensity" and d["part"] == "Opening":
                key = "Attenuate to Composure"
            elif d["type"] == "Emotion Category Mismatch" and d["part"] == "Opening":
                key = "Increase Affability"
            elif d["type"] == "Insufficient Emotional Intensity":
                key = "Strengthen Conviction"
            elif d["type"] == "Excessive Emotional Intensity":
                key = "Attenuate to Composure"
            else:
                key = "Elevate Passion"

            guides.append({
                "part": d["part"],
                "focus": d["type"],
                "methods": method_map.get(key, [])
            })
        return guides

    def _paragraph_tips(self, paragraphs):
        tips = []
        for p in paragraphs:
            tip = ""
            if p["intensity"] < 2:
                tip = "Affective load is minimal. Introduce affective diction or rhetorical devices."
            elif p["intensity"] > 8:
                tip = "Affective saturation is high. Ensure smooth transition with adjacent paragraphs."
            if p["dominant"] == "Neutral" and p["part"] == "ending":
                tip = "Conclusion lacks affective distinction. Introduce climactic language."
            word_count = len(re.findall(r'\b\w+\b', p["full_text"]))
            if word_count > 200:
                tip = "Paragraph exceeds 200 words. Consider segmentation for clarity."
            if p["mixed_emotions"]:
                tip += f" Mixed emotions detected: {', '.join(p['mixed_emotions'])}."
            if p["negated_keywords"] and any(p["negated_keywords"].values()):
                negated_all = [kw for kws in p["negated_keywords"].values() for kw in kws]
                if negated_all:
                    tip += f" Negated terms: {', '.join(negated_all[:3])}."
            if tip:
                tips.append({"para_index": p["index"], "tip": tip.strip()})
        return tips


CLASSICAL_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #FAF6EE 0%, #F0E8D8 100%);
    font-family: 'Georgia', 'Times New Roman', serif;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}
div[data-testid="stHeader"] {
    background: linear-gradient(180deg, #722F37 0%, #5A242B 100%);
    height: 70px;
    border-bottom: 3px solid #C9A961;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #722F37 0%, #5A242B 100%);
    border-right: 3px solid #C9A961;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: #E0C98F !important;
    font-family: 'Georgia', serif;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #C9A961 !important;
    font-family: 'Georgia', serif;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}
h1 {
    color: #722F37 !important;
    font-family: 'Georgia', 'Times New Roman', serif !important;
    font-weight: bold !important;
    text-align: center;
    letter-spacing: 2px;
    text-shadow: 1px 1px 2px rgba(201,169,97,0.3);
    padding-bottom: 10px;
    border-bottom: 2px solid #C9A961;
}
h2 {
    color: #722F37 !important;
    font-family: 'Georgia', serif !important;
    border-left: 5px solid #C9A961;
    padding-left: 12px;
    margin-top: 2rem;
}
h3 {
    color: #5A242B !important;
    font-family: 'Georgia', serif !important;
    font-style: italic;
}
p, li, span, div {
    font-family: 'Georgia', 'Times New Roman', serif;
    color: #2C1810;
}
textarea {
    background-color: #FDFBF5 !important;
    border: 2px solid #C9A961 !important;
    border-radius: 4px !important;
    color: #2C1810 !important;
    font-family: 'Georgia', serif !important;
    font-size: 15px !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
textarea:focus {
    border-color: #722F37 !important;
    box-shadow: 0 0 0 3px rgba(201,169,97,0.2) !important;
}
.stButton > button {
    background: linear-gradient(180deg, #722F37 0%, #5A242B 100%) !important;
    color: #E0C98F !important;
    font-family: 'Georgia', serif !important;
    font-weight: bold !important;
    border: 2px solid #C9A961 !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 1px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(180deg, #8B3A42 0%, #722F37 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(114,47,55,0.4);
    transform: translateY(-1px);
}
.stSelectbox > div > div > select {
    background-color: #FDFBF5 !important;
    border: 2px solid #C9A961 !important;
    color: #2C1810 !important;
    font-family: 'Georgia', serif !important;
}
.stNumberInput input, .stTextInput input {
    background-color: #FDFBF5 !important;
    border: 2px solid #C9A961 !important;
    color: #2C1810 !important;
    font-family: 'Georgia', serif !important;
}
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FDFBF5 0%, #F0E8D8 100%);
    border: 2px solid #C9A961;
    border-radius: 6px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
div[data-testid="stMetric"] label {
    color: #5C4033 !important;
    font-family: 'Georgia', serif !important;
    font-style: italic;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #722F37 !important;
    font-family: 'Georgia', serif !important;
    font-size: 1.8rem !important;
    font-weight: bold;
}
.stDataFrame {
    border: 2px solid #C9A961;
    border-radius: 4px;
    overflow: hidden;
}
.stDataFrame table {
    font-family: 'Georgia', serif !important;
}
.stDataFrame th {
    background: linear-gradient(180deg, #722F37 0%, #5A242B 100%) !important;
    color: #E0C98F !important;
    font-family: 'Georgia', serif !important;
}
.stDataFrame tr:nth-child(even) {
    background-color: #F0E8D8 !important;
}
.stDataFrame tr:hover {
    background-color: #E8DCC8 !important;
}
.streamlit-expanderHeader {
    background: linear-gradient(180deg, #F0E8D8 0%, #E8DCC8 100%);
    border: 1px solid #C9A961;
    border-radius: 4px;
    font-family: 'Georgia', serif !important;
    color: #722F37 !important;
    font-weight: bold !important;
}
.streamlit-expanderContent {
    background-color: #FDFBF5;
    border: 1px solid #C9A961;
    border-top: none;
    border-radius: 0 0 4px 4px;
}
.stSuccess {
    background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
    border-left: 5px solid #2E7D32;
    border-radius: 4px;
    font-family: 'Georgia', serif;
}
.stWarning {
    background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
    border-left: 5px solid #F57F17;
    border-radius: 4px;
    font-family: 'Georgia', serif;
}
.stInfo {
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    border-left: 5px solid #1565C0;
    border-radius: 4px;
    font-family: 'Georgia', serif;
}
.stError {
    background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
    border-left: 5px solid #C62828;
    border-radius: 4px;
    font-family: 'Georgia', serif;
}
pre {
    background-color: #FDFBF5 !important;
    border: 2px solid #C9A961 !important;
    border-radius: 4px !important;
    color: #2C1810 !important;
    font-family: 'Consolas', monospace !important;
    font-size: 13px !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #C9A961 50%, transparent 100%);
    margin: 2rem 0;
}
.stFileUploader {
    background-color: #FDFBF5;
    border: 2px dashed #C9A961;
    border-radius: 6px;
    padding: 1rem;
}
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(180deg, #F0E8D8 0%, #E8DCC8 100%);
    border-bottom: 3px solid #C9A961;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Georgia', serif !important;
    color: #5C4033 !important;
    font-weight: bold !important;
    padding: 0.8rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, #722F37 0%, #5A242B 100%) !important;
    color: #E0C98F !important;
    border-radius: 6px 6px 0 0;
}
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: #F0E8D8;
}
::-webkit-scrollbar-thumb {
    background: #C9A961;
    border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
    background: #722F37;
}
footer {
    background: linear-gradient(180deg, #5A242B 0%, #722F37 100%);
    color: #C9A961 !important;
    border-top: 3px solid #C9A961;
    font-family: 'Georgia', serif !important;
    padding: 1rem !important;
}
footer a {
    color: #E0C98F !important;
}
</style>
"""

st.set_page_config(
    page_title="Speech Optimizer — Classical Edition",
    page_icon="❦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CLASSICAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 20px 0;">
    <div style="font-size:42px; color:#C9A961;">❦</div>
    <h1 style="border:none; margin:0;">SPEECH OPTIMIZER</h1>
    <p style="color:#5C4033; font-style:italic; font-size:16px; margin-top:8px;">
        — Scientific Emotion Analysis & Refinement —
    </p>
    <div style="font-size:42px; color:#C9A961;">❦</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ❦ Settings")
    st.markdown("---")
    scene = st.selectbox(
        "Speech Context",
        ["Academic Competition", "Corporate Presentation", "Commemorative Address"]
    )
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <p style="color:#C9A961; font-style:italic; font-size:12px;">
            ❦ Classical Edition ❦<br>
            Speech Optimizer Pro
        </p>
    </div>
    """, unsafe_allow_html=True)


@st.cache_resource
def get_analyzer():
    loader = CorpusLoader()
    analyzer = SpeechEmotionAnalyzer(loader.base_corpus, loader.emobank, scene)
    reviser = SpeechReviser()
    return analyzer, reviser


analyzer, reviser = get_analyzer()
analyzer.set_scene(scene)

tab1, tab2 = st.tabs(["  📜 Text Analysis  ", "  📋 Batch Analysis  "])

with tab1:
    st.markdown("### ✒ Enter Your English Speech")
    text = st.text_area("", height=280, placeholder="Paste your English speech here...",
                         label_visibility="collapsed")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        analyze_clicked = st.button("✦ Analyze", use_container_width=True)
    with col_btn2:
        if st.button("✧ Clear", use_container_width=True):
            st.rerun()

    if analyze_clicked:
        if text.strip():
            with st.spinner("❦ Analyzing..."):
                analysis = analyzer.full_analysis(text)
                suggestions = reviser.generate_detailed_suggestions(analysis)
                basic = analysis["basic_info"]
                rhetorical = analysis["rhetorical_devices"]
                readability = analysis["readability"]

            st.markdown("---")
            st.markdown("### 📊 Overview")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Composite Score", f"{suggestions['overall']['score']}/100")
            c2.metric("Grade", suggestions["overall"]["grade"])
            c3.metric("Word Count", basic["word_count"])
            c4.metric("Est. Duration", f"{basic['duration_min']} min")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Lexical Diversity", basic["lexical_diversity"])
            c6.metric("Quotable Sentences", basic["quotable_count"])
            c7.metric("Progression Score", f"{analysis['progression_score']}/10")
            c8.metric("Sentences", basic["sentence_count"])

            st.markdown("")
            st.info(f"**Assessment:** {suggestions['overall']['comment']}")

            st.markdown("### 💪 Identified Strengths")
            for s in suggestions["strengths"]:
                st.markdown(f"- ✅ {s}")

            st.markdown("### 🔍 Diagnostic Findings")
            if suggestions["problems"]:
                for p in suggestions["problems"]:
                    with st.expander(f"❖ {p['Segment']} — {p['Finding']}  [{p['Severity']}]"):
                        st.markdown(f"**Evidence:** {p['Evidence']}")
                        st.markdown(f"**Current State:** {p['Current State']}")
                        st.markdown(f"**Expected State:** {p['Expected State']}")
                        st.markdown(f"**Recommendation:** {p['Recommendation']}")
            else:
                st.success("❦ No significant affective misalignments detected!")

            if suggestions["polish_examples"]:
                st.markdown("### ✏ Polishing Examples (Before → After)")
                for g in suggestions["polish_examples"]:
                    st.markdown(f"**[{g['part']}] {g['target']}**")
                    for before, after in g["examples"]:
                        cb, ca = st.columns(2)
                        cb.info(f"**Before:**\n{before}")
                        ca.success(f"**After:**\n{after}")

            if suggestions["extra_tips"]:
                st.markdown("### 💡 Stylistic Recommendations")
                for tip in suggestions["extra_tips"]:
                    st.markdown(f"- ❦ {tip}")

            if suggestions["paragraph_tips"]:
                st.markdown("### 📝 Paragraph-Level Micro-Suggestions")
                for tip in suggestions["paragraph_tips"]:
                    st.markdown(f"- **Paragraph {tip['para_index']}:** {tip['tip']}")

            if suggestions["emotional_shifts"]:
                st.markdown("### 📈 Emotional Shift Detection")
                for shift in suggestions["emotional_shifts"]:
                    st.warning(
                        f"Paragraph {shift['from_para']} → {shift['to_para']}: "
                        f"{shift['from_emotion']} → {shift['to_emotion']} "
                        f"(intensity delta: {shift['intensity_change']}, {shift['abruptness']})"
                    )

            st.markdown("### 🎭 Rhetorical Device Analysis")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Rhetorical Questions", rhetorical["rhetorical_questions"])
            rc2.metric("Anaphora", rhetorical["anaphora"])
            rc3.metric("Triple Structures", rhetorical["triples"])
            rc4.metric("Parallelism", rhetorical["parallelism"])

            st.markdown("### 📖 Readability Analysis")
            rb1, rb2, rb3 = st.columns(3)
            rb1.metric("Flesch Reading Ease", readability["flesch_reading_ease"])
            rb2.metric("Grade Level", readability["flesch_kincaid_grade"])
            rb3.metric("Difficulty", readability["level"])

        else:
            st.warning("❦ Please enter a speech before analyzing.")

with tab2:
    st.markdown("### 📂 Upload Multiple .txt Files for Batch Analysis")
    uploaded_files = st.file_uploader("Select speech files", type=["txt"],
                                       accept_multiple_files=True)

    if uploaded_files and st.button("✦ Run Batch Analysis", use_container_width=True):
        results = []
        progress = st.progress(0)
        for idx, f in enumerate(uploaded_files):
            text = f.read().decode("utf-8")
            analysis = analyzer.full_analysis(text)
            sug = reviser.generate_detailed_suggestions(analysis)
            results.append({
                "Filename": f.name,
                "Score": sug["overall"]["score"],
                "Grade": sug["overall"]["grade"],
                "Words": analysis["basic_info"]["word_count"],
                "Duration(min)": analysis["basic_info"]["duration_min"],
                "Opening Emotion": analysis["structure_emotion"]["opening"],
                "Ending Emotion": analysis["structure_emotion"]["ending"],
                "Quotable": analysis["basic_info"]["quotable_count"],
                "Readability": analysis["readability"]["flesch_kincaid_grade"],
                "Findings": len(analysis["diagnosis"]),
                "Primary Finding": (
                    f"{analysis['diagnosis'][0]['part']}: {analysis['diagnosis'][0]['type']}"
                    if analysis["diagnosis"] else "No significant findings"
                )
            })
            progress.progress((idx + 1) / len(uploaded_files))

        st.success(f"❦ Successfully analyzed {len(results)} speeches!")
        st.dataframe(results, use_container_width=True, hide_index=True)

        if results:
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "❖ Export CSV Report",
                data=csv,
                file_name="speech_batch_report.csv",
                mime="text/csv",
                use_container_width=True
            )

st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:15px;">
    <p style="color:#5C4033; font-style:italic; font-size:13px;">
        ❦ Speech Optimizer Pro · Classical Edition ❦<br>
        Scientific Emotion Analysis & Refinement
    </p>
</div>
""", unsafe_allow_html=True)
