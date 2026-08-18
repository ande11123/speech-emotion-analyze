import json
import re
import os
import csv
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from collections import Counter
import numpy as np

try:
    import sounddevice as sd
    AUDIO_RECORD_AVAILABLE = True
except ImportError:
    AUDIO_RECORD_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import soundfile as sf
    AUDIO_FILE_AVAILABLE = True
except ImportError:
    AUDIO_FILE_AVAILABLE = False

try:
    import speech_recognition as sr
    ASR_AVAILABLE = True
except ImportError:
    ASR_AVAILABLE = False

# =====================================================================
# 1. EXPANDED BUILT-IN CORPUS (8 emotions x 80+ entries each)
# =====================================================================
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

# Negation words (reverse sentiment polarity)
NEGATION_WORDS = {
    "not", "no", "never", "neither", "nor", "cannot", "can't", "don't",
    "doesn't", "didn't", "won't", "wouldn't", "shouldn't", "couldn't",
    "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
    "hadn't", "without", "lack", "lacking", "absent", "devoid",
    "nothing", "nobody", "nowhere", "none", "hardly", "barely",
    "scarcely", "rarely", "seldom", "unlikely", "impossible"
}

# Degree adverbs (amplify or attenuate emotion intensity)
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

# Rhetorical device markers
RHETORICAL_MARKERS = {
    "anaphora": [r"\b(\w+)\b[^\n]*\n[^\n]*\b\1\b", r"(I have a dream[^\n]*\n){2,}"],
    "repetition": [r"\b(\w{3,})\b.*\b\1\b.*\b\1\b"],
    "rhetorical_question": [r"[^\n]*\?\s*$"],
    "triple": [r"\b\w+\s*,\s*\w+\s*,\s*\w+\b"],
    "parallelism": [r"\b(to \w+[^,]*),\s*(to \w+[^,]*),\s*(to \w+)"]
}

DEFAULT_RULES = BUILTIN_CORPUS["scene_rules"]["Academic Competition"]

# =====================================================================
# 2. Corpus Loader
# =====================================================================
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

# =====================================================================
# 3. Advanced Text Emotion Analysis Engine
# =====================================================================
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
        """Check if a keyword is negated within 3 words before it."""
        prefix = text_lower[max(0, keyword_pos - 30):keyword_pos]
        prefix_words = re.findall(r'\b\w+\b', prefix)
        for w in prefix_words[-3:]:
            if w in NEGATION_WORDS:
                return True
        return False

    def _get_degree_multiplier(self, text_lower, keyword_pos):
        """Check for degree adverbs within 3 words before keyword."""
        prefix = text_lower[max(0, keyword_pos - 40):keyword_pos]
        for adv, mult in DEGREE_ADVERBS.items():
            if adv in prefix:
                adv_pos = prefix.rfind(adv)
                between = prefix[adv_pos + len(adv):]
                if len(re.findall(r'\b\w+\b', between)) <= 3:
                    return mult
        return 1.0

    def detect_emotion_detail(self, text):
        """
        Advanced emotion detection with:
        - Negation handling (reverses polarity)
        - Degree adverb weighting (amplifies/attenuates intensity)
        - Sentence-level aggregation
        - Mixed emotion detection
        """
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

        # Detect mixed emotions (second strongest within 60% of strongest)
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
        """Detect rhetorical devices: anaphora, repetition, rhetorical questions, triples, parallelism."""
        devices = {}
        text_lower = text.lower()

        # Rhetorical questions
        rq_count = len(re.findall(r'[^\n]*\?\s*$', text, re.MULTILINE))
        devices["rhetorical_questions"] = rq_count

        # Repetition (word appears 3+ times)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text_lower)
        word_counts = Counter(words)
        repeated = {w: c for w, c in word_counts.items() if c >= 3}
        devices["repeated_words"] = repeated

        # Triple structures (A, B, and C)
        triples = re.findall(r'\b\w+\s*,\s*\w+\s*,\s*(?:and\s+)?\w+\b', text)
        devices["triples"] = len(triples)

        # Anaphora (same starting word across consecutive sentences)
        sentences = self.split_sentences(text)
        anaphora_count = 0
        for i in range(len(sentences) - 1):
            first_w1 = re.findall(r'\b\w+\b', sentences[i])
            first_w2 = re.findall(r'\b\w+\b', sentences[i + 1])
            if first_w1 and first_w2 and first_w1[0].lower() == first_w2[0].lower():
                anaphora_count += 1
        devices["anaphora"] = anaphora_count

        # Parallelism (to X, to Y, to Z)
        parallel = re.findall(r'\b(to \w+[^,]*),\s*(to \w+[^,]*),\s*(to \w+)', text)
        devices["parallelism"] = len(parallel)

        return devices

    def calc_readability(self, text):
        """Flesch-Kincaid readability metrics."""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        word_count = len(words)
        sentences = self.split_sentences(text)
        sent_count = max(1, len(sentences))
        syllables = sum(self._count_syllables(w) for w in words)
        syllable_count = max(1, syllables)

        # Flesch Reading Ease
        fre = 206.835 - 1.015 * (word_count / sent_count) - 84.6 * (syllable_count / word_count)
        fre = max(0, min(100, fre))

        # Flesch-Kincaid Grade Level
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
        """Detect abrupt emotional shifts between adjacent paragraphs."""
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

        # Sentence length variance (rhythm analysis)
        sent_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        sent_length_std = round(float(np.std(sent_lengths)), 1) if sent_lengths else 0

        quotable = []
        for s in sentences:
            s_words = len(re.findall(r'\b\w+\b', s))
            if 8 <= s_words <= 25 and (',' in s or ';' in s or ':' in s):
                quotable.append(s)

        unique_words = set(w.lower() for w in words)
        ttr = round(len(unique_words) / max(1, word_count), 3)

        # Hapax legomena (words used exactly once)
        word_freq = Counter(w.lower() for w in words)
        hapax = sum(1 for c in word_freq.values() if c == 1)
        hapax_ratio = round(hapax / max(1, word_count), 3)

        # Conjunction density (coherence indicator)
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

# =====================================================================
# 4. Audio File Analyzer (import wav files for emotion analysis)
# =====================================================================
class AudioFileAnalyzer:
    """
    Analyze pre-recorded audio files (.wav) for acoustic emotion features.
    Extracts: RMS loudness, zero-crossing rate, spectral centroid,
    pitch (F0 proxy), speech rate estimate, pause detection.
    """

    ACOUSTIC_EMOTION_MAP = [
        {"name": "Passion",      "loudness": (0.6, 1.0), "pitch_var": (0.4, 1.0)},
        {"name": "Conviction",   "loudness": (0.5, 0.8), "pitch_var": (0.1, 0.4)},
        {"name": "Deep Emotion", "loudness": (0.3, 0.6), "pitch_var": (0.3, 0.6)},
        {"name": "Affability",   "loudness": (0.2, 0.5), "pitch_var": (0.2, 0.5)},
        {"name": "Composure",    "loudness": (0.2, 0.5), "pitch_var": (0.0, 0.2)},
        {"name": "Solemnity",    "loudness": (0.1, 0.4), "pitch_var": (0.0, 0.2)},
        {"name": "Humor",        "loudness": (0.3, 0.6), "pitch_var": (0.5, 1.0)},
    ]

    def __init__(self, sample_rate=16000, frame_duration=0.5):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration)

    def analyze_file(self, file_path):
        """Load and analyze a .wav file."""
        if not AUDIO_FILE_AVAILABLE:
            return {"error": "soundfile library not installed. Run: pip install soundfile"}

        try:
            data, sr = sf.read(file_path)
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

        # Convert to mono if stereo
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        # Resample if needed (simple decimation)
        if sr != self.sample_rate:
            ratio = self.sample_rate / sr
            new_length = int(len(data) * ratio)
            indices = np.linspace(0, len(data) - 1, new_length).astype(int)
            data = data[indices]
            sr = self.sample_rate

        duration = len(data) / sr
        frames = self._split_frames(data)
        frame_results = []

        for i, frame in enumerate(frames):
            if len(frame) == 0:
                continue
            rms = float(np.sqrt(np.mean(frame ** 2)))
            loudness = min(1.0, rms * 8.0)
            zero_crossings = float(np.sum(np.abs(np.diff(np.sign(frame)))) / len(frame))
            pitch_var = min(1.0, zero_crossings * 20.0)

            # Spectral centroid (brightness proxy)
            spectral_centroid = self._spectral_centroid(frame, sr)

            emotion, confidence = self._classify_emotion(loudness, pitch_var)

            frame_results.append({
                "time": round(i * self.frame_duration, 2),
                "loudness": round(loudness, 3),
                "pitch_var": round(pitch_var, 3),
                "spectral_centroid": round(spectral_centroid, 1),
                "emotion": emotion,
                "confidence": round(confidence, 2)
            })

        return self._generate_summary(frame_results, duration, sr)

    def _split_frames(self, data):
        frames = []
        for i in range(0, len(data), self.frame_size):
            frames.append(data[i:i + self.frame_size])
        return frames

    def _spectral_centroid(self, frame, sr):
        """Compute spectral centroid as a proxy for pitch/brightness."""
        if len(frame) < 2:
            return 0.0
        fft = np.abs(np.fft.rfft(frame))
        freqs = np.fft.rfftfreq(len(frame), 1.0 / sr)
        if np.sum(fft) == 0:
            return 0.0
        centroid = np.sum(freqs * fft) / np.sum(fft)
        return min(5000.0, centroid)

    def _classify_emotion(self, loudness, pitch_var):
        best_score = 0.0
        best_emo = "Neutral"
        for rule in self.ACOUSTIC_EMOTION_MAP:
            l_ok = rule["loudness"][0] <= loudness <= rule["loudness"][1]
            p_ok = rule["pitch_var"][0] <= pitch_var <= rule["pitch_var"][1]
            if l_ok and p_ok:
                l_center = (rule["loudness"][0] + rule["loudness"][1]) / 2
                p_center = (rule["pitch_var"][0] + rule["pitch_var"][1]) / 2
                score = 1.0 - abs(loudness - l_center) * 0.8 - abs(pitch_var - p_center) * 0.6
                if score > best_score:
                    best_score = score
                    best_emo = rule["name"]
        if loudness < 0.05:
            best_emo = "Pause"
            best_score = 0.9
        return best_emo, max(0.0, min(1.0, best_score))

    def _generate_summary(self, frame_results, duration, sr):
        if not frame_results:
            return {"error": "No audio frames analyzed"}

        emo_counts = Counter(
            [c["emotion"] for c in frame_results if c["emotion"] != "Pause"]
        )
        main_emo = emo_counts.most_common(1)[0][0] if emo_counts else "Neutral"

        loudness_list = np.array([c["loudness"] for c in frame_results])
        avg_loudness = float(np.mean(loudness_list))
        max_loudness = float(np.max(loudness_list))
        loudness_std = float(np.std(loudness_list))

        centroid_list = np.array([c["spectral_centroid"] for c in frame_results if c["spectral_centroid"] > 0])
        avg_centroid = float(np.mean(centroid_list)) if len(centroid_list) > 0 else 0.0

        n = len(frame_results)
        sections = {
            "Opening":      (0, int(n * 0.15)),
            "Body (Front)": (int(n * 0.15), int(n * 0.45)),
            "Body (Back)":  (int(n * 0.45), int(n * 0.75)),
            "Ending":       (int(n * 0.75), n)
        }

        section_result = {}
        for name, (start, end) in sections.items():
            seg = frame_results[start:end]
            if not seg:
                section_result[name] = {"dominant_emotion": "Neutral", "avg_loudness": 0.0}
                continue
            seg_emos = Counter([c["emotion"] for c in seg if c["emotion"] != "Pause"])
            dom_emo = seg_emos.most_common(1)[0][0] if seg_emos else "Neutral"
            avg_loud = float(np.mean([c["loudness"] for c in seg]))
            section_result[name] = {
                "dominant_emotion": dom_emo,
                "avg_loudness": round(avg_loud, 3)
            }

        # Pause analysis
        pause_count = sum(1 for c in frame_results if c["emotion"] == "Pause")
        pause_ratio = pause_count / len(frame_results)

        # Speech rate estimate (voiced frames / duration)
        voiced_frames = sum(1 for c in frame_results if c["emotion"] != "Pause")
        speech_rate = round(voiced_frames * self.frame_duration / max(0.1, duration), 2)

        # Dynamic range
        dynamic_range = round(max_loudness - float(np.min(loudness_list)), 3)

        diagnosis = []
        suggestions = []

        if avg_loudness < 0.2:
            diagnosis.append("Mean vocal intensity is below the recommended projection threshold.")
            suggestions.append("Increase diaphragmatic support and raise overall vocal amplitude.")
        elif avg_loudness > 0.7:
            diagnosis.append("Sustained high vocal intensity may cause listener fatigue.")
            suggestions.append("Introduce deliberate decrescendos in transitional passages.")

        if loudness_std < 0.1:
            diagnosis.append("Vocal dynamics are excessively flat (low standard deviation).")
            suggestions.append("Employ contrastive stress and modulate volume between segments.")
        elif loudness_std > 0.35:
            diagnosis.append("Vocal amplitude fluctuates sharply.")
            suggestions.append("Stabilize breath management and practice smooth volume transitions.")

        if pause_ratio > 0.3:
            diagnosis.append(f"Pause ratio ({pause_ratio:.1%}) exceeds recommended range.")
            suggestions.append("Rehearse transitions to reduce disfluent pauses.")
        elif pause_ratio < 0.05:
            diagnosis.append(f"Pause ratio ({pause_ratio:.1%}) is below recommended range.")
            suggestions.append("Insert deliberate pauses before key claims.")

        score = 75.0
        if 0.1 < loudness_std < 0.3:
            score += 8.0
        if 0.2 <= avg_loudness <= 0.6:
            score += 5.0
        if 0.05 <= pause_ratio <= 0.25:
            score += 5.0
        score = min(100.0, max(0.0, score))

        return {
            "duration_sec": round(duration, 1),
            "sample_rate": sr,
            "main_emotion": main_emo,
            "emotion_distribution": dict(emo_counts),
            "avg_loudness": round(avg_loudness, 3),
            "max_loudness": round(max_loudness, 3),
            "loudness_variance": round(loudness_std, 3),
            "avg_spectral_centroid": round(avg_centroid, 1),
            "dynamic_range": dynamic_range,
            "pause_ratio": round(pause_ratio, 3),
            "speech_rate_ratio": speech_rate,
            "sections": section_result,
            "diagnosis": diagnosis,
            "suggestions": suggestions,
            "total_score": round(score, 1),
            "frame_results": frame_results
        }

# =====================================================================
# 5. ASR Transcriber (speech-to-text, optional)
# =====================================================================
class ASRTranscriber:
    """
    Speech-to-text using SpeechRecognition library.
    Supports Google Web Speech API (free, requires internet).
    Transcribed text can be fed into the text emotion analyzer.
    """

    def __init__(self):
        self.available = ASR_AVAILABLE
        self.recognizer = sr.Recognizer() if ASR_AVAILABLE else None

    def transcribe_audio_file(self, file_path, language="en-US"):
        """Transcribe a .wav file to text."""
        if not self.available:
            return {"error": "SpeechRecognition not installed. Run: pip install SpeechRecognition"}

        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio, language=language)
            return {"success": True, "text": text, "language": language}
        except sr.UnknownValueError:
            return {"error": "Speech could not be understood. Try a clearer recording."}
        except sr.RequestError as e:
            return {"error": f"ASR service error: {str(e)}. Check internet connection."}
        except Exception as e:
            return {"error": f"Transcription failed: {str(e)}"}

    def transcribe_microphone(self, duration=10, language="en-US"):
        """Record from microphone and transcribe."""
        if not self.available:
            return {"error": "SpeechRecognition not installed."}
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=duration + 2)
            text = self.recognizer.recognize_google(audio, language=language)
            return {"success": True, "text": text, "language": language}
        except Exception as e:
            return {"error": f"Microphone transcription failed: {str(e)}"}

# =====================================================================
# 6. Live Speech Acoustic Analyzer (upgraded)
# =====================================================================
class LiveSpeechAnalyzer:
    ACOUSTIC_EMOTION_MAP = [
        {"name": "Passion",      "loudness": (0.6, 1.0), "pitch_var": (0.4, 1.0)},
        {"name": "Conviction",   "loudness": (0.5, 0.8), "pitch_var": (0.1, 0.4)},
        {"name": "Deep Emotion", "loudness": (0.3, 0.6), "pitch_var": (0.3, 0.6)},
        {"name": "Affability",   "loudness": (0.2, 0.5), "pitch_var": (0.2, 0.5)},
        {"name": "Composure",    "loudness": (0.2, 0.5), "pitch_var": (0.0, 0.2)},
        {"name": "Solemnity",    "loudness": (0.1, 0.4), "pitch_var": (0.0, 0.2)},
        {"name": "Humor",        "loudness": (0.3, 0.6), "pitch_var": (0.5, 1.0)},
    ]

    def __init__(self, sample_rate=16000, chunk_duration=0.5):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.is_recording = False
        self.audio_data = []
        self.chunk_results = []
        self.stream = None
        self.callback = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"[Audio status] {status}")

        rms = float(np.sqrt(np.mean(indata ** 2)))
        loudness = min(1.0, rms * 8.0)

        zero_crossings = float(np.sum(np.abs(np.diff(np.sign(indata)))) / len(indata))
        pitch_var = min(1.0, zero_crossings * 20.0)

        # Spectral centroid (pitch/brightness proxy)
        if len(indata) >= 2:
            fft = np.abs(np.fft.rfft(indata.flatten()))
            freqs = np.fft.rfftfreq(len(indata), 1.0 / self.sample_rate)
            if np.sum(fft) > 0:
                spectral_centroid = float(np.sum(freqs * fft) / np.sum(fft))
            else:
                spectral_centroid = 0.0
        else:
            spectral_centroid = 0.0

        emotion, confidence = self._classify_emotion(loudness, pitch_var)

        chunk_result = {
            "time": len(self.chunk_results) * self.chunk_duration,
            "loudness": round(loudness, 3),
            "pitch_var": round(pitch_var, 3),
            "spectral_centroid": round(min(5000.0, spectral_centroid), 1),
            "emotion": emotion,
            "confidence": round(confidence, 2)
        }

        self.chunk_results.append(chunk_result)
        self.audio_data.extend(indata.flatten().tolist())

        if self.callback:
            self.callback(chunk_result)

    def _classify_emotion(self, loudness, pitch_var):
        best_score = 0.0
        best_emo = "Neutral"
        for rule in self.ACOUSTIC_EMOTION_MAP:
            l_ok = rule["loudness"][0] <= loudness <= rule["loudness"][1]
            p_ok = rule["pitch_var"][0] <= pitch_var <= rule["pitch_var"][1]
            if l_ok and p_ok:
                l_center = (rule["loudness"][0] + rule["loudness"][1]) / 2
                p_center = (rule["pitch_var"][0] + rule["pitch_var"][1]) / 2
                score = 1.0 - abs(loudness - l_center) * 0.8 - abs(pitch_var - p_center) * 0.6
                if score > best_score:
                    best_score = score
                    best_emo = rule["name"]
        if loudness < 0.05:
            best_emo = "Pause"
            best_score = 0.9
        return best_emo, max(0.0, min(1.0, best_score))

    def start_recording(self, callback=None):
        if self.is_recording:
            return
        self.is_recording = True
        self.audio_data = []
        self.chunk_results = []
        self.callback = callback
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_recording = False

    def get_summary(self):
        if not self.chunk_results:
            return None

        total_duration = len(self.chunk_results) * self.chunk_duration

        emo_counts = Counter(
            [c["emotion"] for c in self.chunk_results if c["emotion"] != "Pause"]
        )
        main_emo = emo_counts.most_common(1)[0][0] if emo_counts else "Neutral"

        loudness_list = np.array([c["loudness"] for c in self.chunk_results])
        avg_loudness = float(np.mean(loudness_list))
        max_loudness = float(np.max(loudness_list))
        loudness_std = float(np.std(loudness_list))

        centroid_list = np.array([c["spectral_centroid"] for c in self.chunk_results if c["spectral_centroid"] > 0])
        avg_centroid = float(np.mean(centroid_list)) if len(centroid_list) > 0 else 0.0

        n = len(self.chunk_results)
        sections = {
            "Opening":      (0, int(n * 0.15)),
            "Body (Front)": (int(n * 0.15), int(n * 0.45)),
            "Body (Back)":  (int(n * 0.45), int(n * 0.75)),
            "Ending":       (int(n * 0.75), n)
        }

        section_result = {}
        for name, (start, end) in sections.items():
            seg = self.chunk_results[start:end]
            if not seg:
                section_result[name] = {"dominant_emotion": "Neutral", "avg_loudness": 0.0}
                continue
            seg_emos = Counter([c["emotion"] for c in seg if c["emotion"] != "Pause"])
            dom_emo = seg_emos.most_common(1)[0][0] if seg_emos else "Neutral"
            avg_loud = float(np.mean([c["loudness"] for c in seg]))
            section_result[name] = {
                "dominant_emotion": dom_emo,
                "avg_loudness": round(avg_loud, 3)
            }

        diagnosis = []
        suggestions = []

        if avg_loudness < 0.2:
            diagnosis.append("Mean vocal intensity is below the recommended projection threshold.")
            suggestions.append("Increase diaphragmatic support and raise overall vocal amplitude.")
        elif avg_loudness > 0.7:
            diagnosis.append("Sustained high vocal intensity may cause listener fatigue.")
            suggestions.append("Introduce deliberate decrescendos in transitional passages.")

        if loudness_std < 0.1:
            diagnosis.append("Vocal dynamics are excessively flat (low standard deviation).")
            suggestions.append("Employ contrastive stress and modulate volume between segments.")
        elif loudness_std > 0.35:
            diagnosis.append("Vocal amplitude fluctuates sharply.")
            suggestions.append("Stabilize breath management and practice smooth volume transitions.")

        pause_count = sum(1 for c in self.chunk_results if c["emotion"] == "Pause")
        pause_ratio = pause_count / len(self.chunk_results)
        if pause_ratio > 0.3:
            diagnosis.append(f"Pause ratio ({pause_ratio:.1%}) exceeds recommended range.")
            suggestions.append("Rehearse transitions to reduce disfluent pauses.")
        elif pause_ratio < 0.05:
            diagnosis.append(f"Pause ratio ({pause_ratio:.1%}) is below recommended range.")
            suggestions.append("Insert deliberate pauses before key claims.")

        dynamic_range = round(max_loudness - float(np.min(loudness_list)), 3)

        score = 75.0
        if 0.1 < loudness_std < 0.3:
            score += 8.0
        if 0.2 <= avg_loudness <= 0.6:
            score += 5.0
        if 0.05 <= pause_ratio <= 0.25:
            score += 5.0
        score = min(100.0, max(0.0, score))

        return {
            "duration_sec": round(total_duration, 1),
            "main_emotion": main_emo,
            "emotion_distribution": dict(emo_counts),
            "avg_loudness": round(avg_loudness, 3),
            "max_loudness": round(max_loudness, 3),
            "loudness_variance": round(loudness_std, 3),
            "avg_spectral_centroid": round(avg_centroid, 1),
            "dynamic_range": dynamic_range,
            "pause_ratio": round(pause_ratio, 3),
            "sections": section_result,
            "diagnosis": diagnosis,
            "suggestions": suggestions,
            "total_score": round(score, 1),
            "chunk_results": self.chunk_results
        }

# =====================================================================
# 7. Speech Polishing Module (upgraded)
# =====================================================================
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

        # Readability-based tips
        if readability["flesch_kincaid_grade"] > 14:
            tips.append(f"Readability grade level ({readability['flesch_kincaid_grade']}) is very high. Simplify syntax for broader accessibility.")
        elif readability["flesch_kincaid_grade"] < 6:
            tips.append(f"Readability grade level ({readability['flesch_kincaid_grade']}) is very low. Elevate diction for formal contexts.")

        # Rhetorical device tips
        if rhetorical["rhetorical_questions"] == 0:
            tips.append("No rhetorical questions detected. Consider incorporating 1-2 to engage audience reflection.")
        if rhetorical["anaphora"] == 0 and basic_info["word_count"] > 200:
            tips.append("No anaphora detected. Anaphora (repeated sentence openings) can amplify emotional impact.")
        if rhetorical["triples"] == 0:
            tips.append("No triple structures detected. Rule of three (A, B, C) enhances memorability.")

        # Rhythm analysis
        if basic_info["sentence_length_std"] < 3:
            tips.append("Sentence length variance is low. Vary sentence length to create rhythmic tension and release.")

        return tips

# =====================================================================
# 8. Benchmark Comparison Module
# =====================================================================
class BenchmarkComparer:
    def __init__(self, benchmark_data, analyzer):
        self.data = benchmark_data
        self.analyzer = analyzer

    def available(self):
        return self.data is not None

    def list_benchmarks(self):
        items = []
        if self.data:
            for item in self.data.get("ted_talks", []):
                items.append({
                    "source": "TED", "id": item["id"],
                    "title": item["title"], "speaker": item["speaker"],
                    "tags": item.get("tags", [])
                })
            for item in self.data.get("american_rhetoric", []):
                items.append({
                    "source": "American Rhetoric", "id": item["id"],
                    "title": item["title"], "speaker": item["speaker"],
                    "tags": item.get("tags", [])
                })
        return items

    def compare(self, user_analysis, benchmark_id):
        if not self.data:
            return None

        target = None
        for item in self.data.get("ted_talks", []):
            if item["id"] == benchmark_id:
                target = item
                break
        if not target:
            for item in self.data.get("american_rhetoric", []):
                if item["id"] == benchmark_id:
                    target = item
                    break
        if not target:
            return None

        user_curve = user_analysis["vad_curve"]
        bench_curve = target["vad_curve"]

        diff_points = []
        for up in user_curve:
            closest = min(bench_curve, key=lambda x: abs(x["position"] - up["position"]))
            diff = round(up["a"] - closest["a"], 2)
            diff_points.append({
                "position": up["position"],
                "user_arousal": up["a"],
                "bench_arousal": closest["a"],
                "diff": diff
            })

        structure_diff = {}
        part_names = {
            "opening": "Opening", "body_front": "Body (Front)",
            "body_back": "Body (Back)", "ending": "Ending"
        }
        for part in ["opening", "body_front", "body_back", "ending"]:
            user_emo = user_analysis["structure_emotion"][part]
            bench_emo = target["emotion_structure"].get(part, "N/A")
            structure_diff[part] = {
                "part_name": part_names[part],
                "user": user_emo,
                "benchmark": bench_emo,
                "match": user_emo == bench_emo
            }

        match_count = sum(1 for v in structure_diff.values() if v["match"])
        similarity = round(match_count / 4 * 100, 1)

        return {
            "benchmark_title": target["title"],
            "benchmark_speaker": target["speaker"],
            "structure_diff": structure_diff,
            "arousal_diff": diff_points,
            "similarity": similarity,
            "suggestion": self._generate_compare_suggestion(structure_diff, diff_points)
        }

    def _generate_compare_suggestion(self, structure_diff, diff_points):
        tips = []
        for part, info in structure_diff.items():
            if not info["match"]:
                tips.append(
                    f"{info['part_name']}: your draft emphasizes '{info['user']}', "
                    f"whereas the benchmark employs '{info['benchmark']}'. "
                    f"Consider aligning the affective register."
                )
        avg_diff = sum(p["diff"] for p in diff_points) / len(diff_points)
        if avg_diff > 1:
            tips.append("Overall arousal exceeds the benchmark. Consider strategic deceleration.")
        elif avg_diff < -1:
            tips.append("Overall arousal is below the benchmark. Elevate affective intensity.")
        if not tips:
            tips.append("Affective structure aligns closely with the benchmark.")
        return tips

# =====================================================================
# 9. Revision Suggestion Module (upgraded)
# =====================================================================
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

# =====================================================================
# 10. Batch Grading Module (upgraded)
# =====================================================================
class BatchGrader:
    def __init__(self, analyzer, reviser):
        self.analyzer = analyzer
        self.reviser = reviser

    def batch_analyze(self, folder_path):
        results = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                text = None
                for encoding in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            text = f.read()
                        break
                    except Exception:
                        continue
                if text is None:
                    continue

                analysis = self.analyzer.full_analysis(text)
                suggestions = self.reviser.generate_detailed_suggestions(analysis)
                results.append({
                    "Filename": filename,
                    "Word Count": analysis["basic_info"]["word_count"],
                    "Est. Duration (min)": analysis["basic_info"]["duration_min"],
                    "Paragraphs": analysis["total_paras"],
                    "Composite Score": suggestions["overall"]["score"],
                    "Grade": suggestions["overall"]["grade"],
                    "Opening Emotion": analysis["structure_emotion"]["opening"],
                    "Body-Front Emotion": analysis["structure_emotion"]["body_front"],
                    "Body-Back Emotion": analysis["structure_emotion"]["body_back"],
                    "Ending Emotion": analysis["structure_emotion"]["ending"],
                    "Progression Score": analysis["progression_score"],
                    "Quotable Sentences": analysis["basic_info"]["quotable_count"],
                    "Lexical Diversity": analysis["basic_info"]["lexical_diversity"],
                    "Readability Grade": analysis["readability"]["flesch_kincaid_grade"],
                    "Rhetorical Devices": analysis["rhetorical_devices"]["anaphora"] + analysis["rhetorical_devices"]["triples"],
                    "Findings Count": len(analysis["diagnosis"]),
                    "Primary Strength": "; ".join(suggestions["strengths"][:2]),
                    "Primary Finding": (
                        f"{analysis['diagnosis'][0]['part']}: {analysis['diagnosis'][0]['type']}"
                        if analysis["diagnosis"] else "No significant findings"
                    ),
                    "Key Recommendation": (
                        suggestions["problems"][0]["Recommendation"]
                        if suggestions["problems"] else "Maintain current quality"
                    )
                })
        return results

    def export_report(self, results, output_path="speech_optimizer_batch_report.csv"):
        if not results:
            return "No results available for export."
        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        return f"Batch report exported to: {output_path}"

# =====================================================================
# 11. GUI Main Application (upgraded with 5 tabs)
# =====================================================================
class SpeechAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Optimizer Pro — Scientific Emotion Analysis & Refinement")
        self.root.geometry("1280x920")

        self.loader = CorpusLoader()
        self.text_analyzer = SpeechEmotionAnalyzer(
            self.loader.base_corpus, self.loader.emobank, scene="Academic Competition"
        )
        self.reviser = SpeechReviser()
        self.comparer = BenchmarkComparer(self.loader.benchmark, self.text_analyzer)
        self.grader = BatchGrader(self.text_analyzer, self.reviser)
        self.audio_analyzer = AudioFileAnalyzer()
        self.asr = ASRTranscriber()

        self.live_analyzer = LiveSpeechAnalyzer() if AUDIO_RECORD_AVAILABLE else None
        self.live_data = []
        self.live_max_points = 100

        self.batch_results = []
        self.current_text_analysis = None

        self.create_widgets()

    def create_widgets(self):
        # ===== 高级古典典藏版配色 =====
        self.C_IVORY = "#FAF6EE"  # 象牙白（主背景）
        self.C_PARCHMENT = "#F0E8D8"  # 仿古纸（面板）
        self.C_PARCHMENT_DARK = "#E8DCC8"  # 深古纸
        self.C_BURGUNDY = "#722F37"  # 深酒红（主色）
        self.C_BURGUNDY_DARK = "#5A242B"
        self.C_GOLD = "#C9A961"  # 鎏金
        self.C_GOLD_LIGHT = "#E0C98F"
        self.C_INK = "#2C1810"  # 深墨棕（主文字）
        self.C_INK_LIGHT = "#5C4033"  # 浅墨棕
        self.C_GREEN = "#2F4F4F"  # 墨绿
        self.C_RED = "#8B2500"  # 朱红
        self.FONT_DISPLAY = ("Georgia", 22, "bold")
        self.FONT_TITLE = ("Georgia", 14, "bold")
        self.FONT_BODY = ("Georgia", 10)
        self.FONT_SMALL = ("Georgia", 9)
        self.FONT_DATA = ("Consolas", 9)
        self.FONT_DECO = ("Georgia", 13, "italic")

        self.root.configure(bg=self.C_IVORY)

        # ===== ttk 样式 =====
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Lux.TFrame", background=self.C_IVORY)
        style.configure("Lux.TNotebook", background=self.C_IVORY, borderwidth=0)
        style.configure("Lux.TNotebook.Tab",
                        background=self.C_PARCHMENT_DARK,
                        foreground=self.C_INK_LIGHT,
                        padding=[22, 10],
                        font=("Georgia", 10, "bold"))
        style.map("Lux.TNotebook.Tab",
                  background=[("selected", self.C_BURGUNDY)],
                  foreground=[("selected", self.C_GOLD_LIGHT)])

        style.configure("Lux.TLabelframe",
                        background=self.C_PARCHMENT,
                        borderwidth=3, relief="groove")
        style.configure("Lux.TLabelframe.Label",
                        background=self.C_PARCHMENT,
                        foreground=self.C_BURGUNDY,
                        font=("Georgia", 11, "bold"))

        style.configure("Lux.TButton",
                        background=self.C_BURGUNDY,
                        foreground=self.C_GOLD_LIGHT,
                        font=("Georgia", 9, "bold"),
                        padding=[14, 7], borderwidth=2)
        style.map("Lux.TButton",
                  background=[("active", self.C_BURGUNDY_DARK)],
                  foreground=[("active", "#FFFFFF")])

        style.configure("Lux.TCombobox",
                        fieldbackground=self.C_IVORY,
                        background=self.C_PARCHMENT_DARK,
                        foreground=self.C_INK,
                        font=("Georgia", 10),
                        arrowcolor=self.C_BURGUNDY)

        style.configure("Lux.TEntry",
                        fieldbackground=self.C_IVORY,
                        foreground=self.C_INK,
                        insertcolor=self.C_BURGUNDY)

        style.configure("Lux.Treeview",
                        background=self.C_IVORY,
                        foreground=self.C_INK,
                        fieldbackground=self.C_IVORY,
                        font=("Georgia", 9), rowheight=30)
        style.configure("Lux.Treeview.Heading",
                        background=self.C_BURGUNDY,
                        foreground=self.C_GOLD_LIGHT,
                        font=("Georgia", 9, "bold"))
        style.map("Lux.Treeview",
                  background=[("selected", self.C_GOLD)],
                  foreground=[("selected", self.C_INK)])

        style.configure("Lux.Horizontal.TScrollbar",
                        background=self.C_PARCHMENT_DARK,
                        troughcolor=self.C_IVORY)

        # ===== 顶部装饰标题栏 =====
        header = tk.Frame(self.root, bg=self.C_BURGUNDY, height=90)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # 顶部金线
        tk.Frame(header, bg=self.C_GOLD, height=3).pack(fill=tk.X, side=tk.TOP)
        tk.Frame(header, bg=self.C_GOLD_LIGHT, height=1).pack(fill=tk.X, side=tk.TOP)

        header_inner = tk.Frame(header, bg=self.C_BURGUNDY)
        header_inner.pack(fill=tk.BOTH, expand=True, padx=20)

        # 左侧装饰
        left_deco = tk.Frame(header_inner, bg=self.C_BURGUNDY)
        left_deco.pack(side=tk.LEFT, padx=10)
        tk.Label(left_deco, text="❦", font=("Georgia", 28),
                 fg=self.C_GOLD, bg=self.C_BURGUNDY).pack()

        # 中间标题
        title_center = tk.Frame(header_inner, bg=self.C_BURGUNDY)
        title_center.pack(side=tk.LEFT, expand=True)
        tk.Label(title_center, text="SPEECH OPTIMIZER",
                 font=self.FONT_DISPLAY, fg=self.C_GOLD_LIGHT,
                 bg=self.C_BURGUNDY).pack(pady=(8, 0))
        tk.Label(title_center, text="— Scientific Emotion Analysis & Refinement —",
                 font=self.FONT_DECO, fg=self.C_GOLD,
                 bg=self.C_BURGUNDY).pack()

        # 右侧装饰
        right_deco = tk.Frame(header_inner, bg=self.C_BURGUNDY)
        right_deco.pack(side=tk.RIGHT, padx=10)
        tk.Label(right_deco, text="❦", font=("Georgia", 28),
                 fg=self.C_GOLD, bg=self.C_BURGUNDY).pack()

        # 底部金线
        tk.Frame(header, bg=self.C_GOLD_LIGHT, height=1).pack(fill=tk.X, side=tk.BOTTOM)
        tk.Frame(header, bg=self.C_GOLD, height=3).pack(fill=tk.X, side=tk.BOTTOM)

        # ===== 状态栏 =====
        status_bar = tk.Frame(self.root, bg=self.C_PARCHMENT_DARK, height=28)
        status_bar.pack(fill=tk.X, padx=16, pady=(4, 0))
        status_bar.pack_propagate(False)

        status_left = tk.Frame(status_bar, bg=self.C_PARCHMENT_DARK)
        status_left.pack(side=tk.LEFT, padx=10)
        tk.Label(status_left, text="✦ Corpus: " + self.loader.base_status.split("]")[
            1].strip() if "]" in self.loader.base_status else self.loader.base_status,
                 font=("Consolas", 8), fg=self.C_GREEN, bg=self.C_PARCHMENT_DARK).pack(side=tk.LEFT, padx=8)
        tk.Label(status_left, text="✦ VAD: " + self.loader.emobank_status.split("]")[
            1].strip() if "]" in self.loader.emobank_status else self.loader.emobank_status,
                 font=("Consolas", 8), fg="#1565c0", bg=self.C_PARCHMENT_DARK).pack(side=tk.LEFT, padx=8)
        tk.Label(status_left, text="✦ Benchmark: " + self.loader.benchmark_status.split("]")[
            1].strip() if "]" in self.loader.benchmark_status else self.loader.benchmark_status,
                 font=("Consolas", 8), fg="#6A1B9A", bg=self.C_PARCHMENT_DARK).pack(side=tk.LEFT, padx=8)

        status_right = tk.Frame(status_bar, bg=self.C_PARCHMENT_DARK)
        status_right.pack(side=tk.RIGHT, padx=10)
        audio_st = "Audio OK" if AUDIO_RECORD_AVAILABLE else "Audio disabled"
        asr_st = "ASR OK" if ASR_AVAILABLE else "ASR disabled"
        tk.Label(status_right, text=f"🎙 {audio_st}  |  📝 {asr_st}",
                 font=("Consolas", 8), fg=self.C_BURGUNDY, bg=self.C_PARCHMENT_DARK).pack()

        # ===== 标签页 =====
        notebook = ttk.Notebook(self.root, style="Lux.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        self.single_frame = ttk.Frame(notebook, style="Lux.TFrame")
        notebook.add(self.single_frame, text="  📜  Text Analysis  ")
        self.create_single_tab()

        self.live_frame = ttk.Frame(notebook, style="Lux.TFrame")
        notebook.add(self.live_frame, text="  🎙  Live Recording  ")
        self.create_live_tab()

        self.audio_file_frame = ttk.Frame(notebook, style="Lux.TFrame")
        notebook.add(self.audio_file_frame, text="  🎵  Audio File  ")
        self.create_audio_file_tab()

        self.bench_frame = ttk.Frame(notebook, style="Lux.TFrame")
        notebook.add(self.bench_frame, text="  📚  Benchmark  ")
        self.create_benchmark_tab()

        self.batch_frame = ttk.Frame(notebook, style="Lux.TFrame")
        notebook.add(self.batch_frame, text="  📋  Batch Grading  ")
        self.create_batch_tab()

    def create_single_tab(self):
        content = ttk.Frame(self.single_frame, style="Lux.TFrame")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧
        left = ttk.LabelFrame(content, text="  ✒  Speech Text Input  ",
                              style="Lux.TLabelframe", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        scene_bar = tk.Frame(left, bg=self.C_PARCHMENT)
        scene_bar.pack(fill=tk.X, padx=4, pady=(0, 8))
        tk.Label(scene_bar, text="❖ Context:", font=self.FONT_BODY,
                 fg=self.C_INK, bg=self.C_PARCHMENT).pack(side=tk.LEFT)
        self.scene_var = tk.StringVar(value="Academic Competition")
        ttk.Combobox(scene_bar, textvariable=self.scene_var,
                     values=["Academic Competition", "Corporate Presentation", "Commemorative Address"],
                     state="readonly", width=24, style="Lux.TCombobox").pack(side=tk.LEFT, padx=8)

        self.text_input = scrolledtext.ScrolledText(
            left, wrap=tk.WORD, font=("Georgia", 11), undo=True,
            bg="#FDFBF5", fg=self.C_INK, insertbackground=self.C_BURGUNDY,
            relief="sunken", borderwidth=2, padx=8, pady=8)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        btn_bar = tk.Frame(left, bg=self.C_PARCHMENT)
        btn_bar.pack(fill=tk.X, padx=4, pady=(8, 0))
        ttk.Button(btn_bar, text="✦ Analyze", style="Lux.TButton",
                   command=self.analyze_single).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="✧ Clear", style="Lux.TButton",
                   command=lambda: self.text_input.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="↻ Reload", style="Lux.TButton",
                   command=self.reload_all).pack(side=tk.RIGHT, padx=3)
        ttk.Button(btn_bar, text="❖ Export", style="Lux.TButton",
                   command=self.export_single_report).pack(side=tk.RIGHT, padx=3)

        # 右侧
        right = ttk.LabelFrame(content, text="  📖  Analysis Report  ",
                               style="Lux.TLabelframe", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.result_text = scrolledtext.ScrolledText(
            right, wrap=tk.WORD, font=("Consolas", 9), state=tk.DISABLED,
            bg="#FDFBF5", fg=self.C_INK, insertbackground=self.C_BURGUNDY,
            relief="sunken", borderwidth=2, padx=8, pady=8)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 配置报告文字标签
        self.result_text.tag_config("h1", foreground=self.C_BURGUNDY,
                                    font=("Georgia", 12, "bold"))
        self.result_text.tag_config("h2", foreground=self.C_GOLD,
                                    font=("Georgia", 10, "bold"))
        self.result_text.tag_config("gold", foreground=self.C_GOLD)
        self.result_text.tag_config("green", foreground=self.C_GREEN)
        self.result_text.tag_config("red", foreground=self.C_RED)

    def create_live_tab(self):
        if not AUDIO_RECORD_AVAILABLE or not MATPLOTLIB_AVAILABLE:
            tip = ("Live recording requires:\n\npip install sounddevice numpy matplotlib\n\n"
                   "Restart after installation.")
            tk.Label(self.live_frame, text=tip, font=("Georgia", 13),
                     fg=self.C_RED, bg=self.C_IVORY, justify="center").pack(pady=120)
            return

        ctrl = tk.Frame(self.live_frame, bg=self.C_IVORY)
        ctrl.pack(fill=tk.X, padx=16, pady=12)

        self.record_btn = ttk.Button(ctrl, text="● Start Recording", style="Lux.TButton",
                                     command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=5)

        self.live_status_var = tk.StringVar(value="❦ Ready. Click Start Recording to begin.")
        tk.Label(ctrl, textvariable=self.live_status_var, font=self.FONT_BODY,
                 fg=self.C_INK_LIGHT, bg=self.C_IVORY).pack(side=tk.LEFT, padx=15)

        ttk.Button(ctrl, text="❖ Generate Report", style="Lux.TButton",
                   command=self.generate_live_report).pack(side=tk.RIGHT, padx=5)

        plot_frame = ttk.LabelFrame(self.live_frame, text="  📊  Real-time Acoustic Analysis  ",
                                    style="Lux.TLabelframe", padding=8)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.live_fig = Figure(figsize=(10, 3.2), dpi=100, facecolor="#FDFBF5")
        self.ax_loudness = self.live_fig.add_subplot(211)
        self.ax_emotion = self.live_fig.add_subplot(212)
        self.live_fig.tight_layout()

        self.live_canvas = FigureCanvasTkAgg(self.live_fig, master=plot_frame)
        self.live_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        for ax in [self.ax_loudness, self.ax_emotion]:
            ax.set_facecolor("#FDFBF5")
            ax.tick_params(colors=self.C_INK_LIGHT)
            for spine in ax.spines.values():
                spine.set_color(self.C_GOLD)

        self.ax_loudness.set_title("Vocal Intensity (RMS)", fontsize=10, color=self.C_BURGUNDY)
        self.ax_loudness.set_ylim(0, 1)
        self.line_loudness, = self.ax_loudness.plot([], [], color=self.C_RED, linewidth=1.8)

        self.ax_emotion.set_title("Affective Intensity", fontsize=10, color=self.C_BURGUNDY)
        self.ax_emotion.set_ylim(0, 1)
        self.line_emotion, = self.ax_emotion.plot([], [], color=self.C_BURGUNDY, linewidth=1.8)

        info = ttk.LabelFrame(self.live_frame, text="  🎙  Current State  ",
                              style="Lux.TLabelframe", padding=8)
        info.pack(fill=tk.X, padx=16, pady=4)

        self.current_emo_var = tk.StringVar(value="Emotion: —")
        self.current_loud_var = tk.StringVar(value="Loudness: —")
        self.current_pitch_var = tk.StringVar(value="Pitch Var: —")
        self.duration_var = tk.StringVar(value="Elapsed: 0.0 s")

        for var, color in [(self.current_emo_var, self.C_RED),
                           (self.current_loud_var, self.C_INK),
                           (self.current_pitch_var, self.C_INK)]:
            tk.Label(info, textvariable=var, font=("Georgia", 11, "bold"),
                     fg=color, bg=self.C_PARCHMENT).pack(side=tk.LEFT, padx=25, pady=4)
        tk.Label(info, textvariable=self.duration_var, font=("Georgia", 10),
                 fg=self.C_INK_LIGHT, bg=self.C_PARCHMENT).pack(side=tk.RIGHT, padx=25, pady=4)

        report_frame = ttk.LabelFrame(self.live_frame, text="  📖  Recording Report  ",
                                      style="Lux.TLabelframe", padding=8)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.live_result_text = scrolledtext.ScrolledText(
            report_frame, wrap=tk.WORD, font=("Consolas", 9), state=tk.DISABLED,
            bg="#FDFBF5", fg=self.C_INK, relief="sunken", borderwidth=2, height=7)
        self.live_result_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def create_audio_file_tab(self):
        top = tk.Frame(self.audio_file_frame, bg=self.C_IVORY)
        top.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(top, text="❖ Audio File (.wav):", font=self.FONT_BODY,
                 fg=self.C_INK, bg=self.C_IVORY).pack(side=tk.LEFT)
        self.audio_path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.audio_path_var, width=50,
                  style="Lux.TEntry").pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Browse", style="Lux.TButton",
                   command=self.select_audio_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="✦ Analyze Audio", style="Lux.TButton",
                   command=self.analyze_audio_file).pack(side=tk.LEFT, padx=10)

        if ASR_AVAILABLE:
            ttk.Button(top, text="📝 Transcribe (ASR)", style="Lux.TButton",
                       command=self.transcribe_audio).pack(side=tk.LEFT, padx=4)
            tk.Label(top, text="(Google API, online)", font=("Georgia", 8, "italic"),
                     fg=self.C_INK_LIGHT, bg=self.C_IVORY).pack(side=tk.LEFT, padx=2)

        content = tk.Frame(self.audio_file_frame, bg=self.C_IVORY)
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        if MATPLOTLIB_AVAILABLE:
            plot_f = ttk.LabelFrame(content, text="  📈  Audio Emotion Curve  ",
                                    style="Lux.TLabelframe", padding=6)
            plot_f.pack(fill=tk.X, padx=2, pady=2)
            self.audio_fig = Figure(figsize=(10, 2.3), dpi=100, facecolor="#FDFBF5")
            self.ax_audio = self.audio_fig.add_subplot(111)
            self.ax_audio.set_facecolor("#FDFBF5")
            self.ax_audio.tick_params(colors=self.C_INK_LIGHT)
            for spine in self.ax_audio.spines.values():
                spine.set_color(self.C_GOLD)
            self.audio_fig.tight_layout()
            self.audio_canvas = FigureCanvasTkAgg(self.audio_fig, master=plot_f)
            self.audio_canvas.get_tk_widget().pack(fill=tk.X, padx=4, pady=4)
            self.ax_audio.set_title("Loudness & Pitch Over Time", fontsize=10, color=self.C_BURGUNDY)
            self.line_audio_loud, = self.ax_audio.plot([], [], color=self.C_RED, linewidth=1.2, label="Loudness")
            self.line_audio_pitch, = self.ax_audio.plot([], [], color=self.C_BURGUNDY, linewidth=1.2, label="Pitch")
            self.ax_audio.legend(loc="upper right", fontsize=8, facecolor=self.C_PARCHMENT)

        report_f = ttk.LabelFrame(content, text="  📖  Audio Analysis Report  ",
                                  style="Lux.TLabelframe", padding=8)
        report_f.pack(fill=tk.BOTH, expand=True, padx=2, pady=4)
        self.audio_result_text = scrolledtext.ScrolledText(
            report_f, wrap=tk.WORD, font=("Consolas", 9), state=tk.DISABLED,
            bg="#FDFBF5", fg=self.C_INK, relief="sunken", borderwidth=2)
        self.audio_result_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def create_benchmark_tab(self):
        if not self.comparer.available():
            tk.Label(self.bench_frame,
                     text="❦ Benchmark corpus not detected.\nPlace 'benchmark_corpus.json' in the application directory.",
                     font=("Georgia", 12), fg=self.C_INK_LIGHT, bg=self.C_IVORY,
                     justify="center").pack(pady=100)
            return

        left = ttk.LabelFrame(self.bench_frame, text="  📚  Benchmark Library  ",
                              style="Lux.TLabelframe", padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.bench_listbox = tk.Listbox(left, width=48, height=26,
                                        bg="#FDFBF5", fg=self.C_INK,
                                        selectbackground=self.C_GOLD,
                                        selectforeground=self.C_INK,
                                        font=("Georgia", 9), relief="sunken", borderwidth=2)
        self.bench_listbox.pack(padx=4, pady=4)
        self.bench_items = self.comparer.list_benchmarks()
        for item in self.bench_items:
            self.bench_listbox.insert(tk.END, f"  [{item['source']}]  {item['title']} — {item['speaker']}")

        ttk.Button(left, text="✦ Compare", style="Lux.TButton",
                   command=self.do_compare).pack(pady=8)

        right = ttk.LabelFrame(self.bench_frame, text="  📊  Comparison Results  ",
                               style="Lux.TLabelframe", padding=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.compare_text = scrolledtext.ScrolledText(
            right, wrap=tk.WORD, font=("Georgia", 10), state=tk.DISABLED,
            bg="#FDFBF5", fg=self.C_INK, relief="sunken", borderwidth=2, padx=10, pady=10)
        self.compare_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def create_batch_tab(self):
        top = tk.Frame(self.batch_frame, bg=self.C_IVORY)
        top.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(top, text="❖ Speech Folder:", font=self.FONT_BODY,
                 fg=self.C_INK, bg=self.C_IVORY).pack(side=tk.LEFT)
        self.folder_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.folder_var, width=52,
                  style="Lux.TEntry").pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Browse", style="Lux.TButton",
                   command=self.select_folder).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="✦ Run Batch Analysis", style="Lux.TButton",
                   command=self.run_batch).pack(side=tk.LEFT, padx=10)

        table_f = ttk.LabelFrame(self.batch_frame, text="  📋  Batch Results  ",
                                 style="Lux.TLabelframe", padding=8)
        table_f.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        columns = ("Filename", "Score", "Grade", "Words", "Duration",
                   "Opening", "Ending", "Quotable", "Readability", "Findings", "Primary Finding")
        self.tree = ttk.Treeview(table_f, columns=columns, show="headings",
                                 height=18, style="Lux.Treeview")
        widths = [175, 55, 80, 55, 65, 80, 80, 65, 75, 65, 230]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w" if col in ["Filename", "Primary Finding"] else "center")

        sb = ttk.Scrollbar(table_f, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        bottom = tk.Frame(self.batch_frame, bg=self.C_IVORY)
        bottom.pack(fill=tk.X, padx=16, pady=10)
        tk.Label(bottom, text="❦ CSV export contains 19 detailed metrics.",
                 font=("Georgia", 9, "italic"), fg=self.C_INK_LIGHT,
                 bg=self.C_IVORY).pack(side=tk.LEFT)
        ttk.Button(bottom, text="❖ Export CSV Report", style="Lux.TButton",
                   command=self.export_batch).pack(side=tk.RIGHT)


    # -----------------------------------------------------------------
    # Text analysis functions
    # -----------------------------------------------------------------
    def change_scene(self, event=None):
        scene = self.scene_var.get()
        self.text_analyzer.set_scene(scene)

    def reload_all(self):
        self.loader.load_all()
        self.text_analyzer = SpeechEmotionAnalyzer(
            self.loader.base_corpus, self.loader.emobank, scene=self.scene_var.get()
        )
        self.comparer = BenchmarkComparer(self.loader.benchmark, self.text_analyzer)
        messagebox.showinfo("Reload Complete", "All corpora have been reloaded.")

    def analyze_single(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Required", "Please paste a speech text before analyzing.")
            return

        analysis = self.text_analyzer.full_analysis(text)
        self.current_text_analysis = analysis
        suggestions = self.reviser.generate_detailed_suggestions(analysis)
        basic = analysis["basic_info"]
        rhetorical = analysis["rhetorical_devices"]
        readability = analysis["readability"]

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)

        # 1. Overview
        self.result_text.insert(tk.END, "═" * 72 + "\n", "gold")
        self.result_text.insert(tk.END, "  1. SPEECH OVERVIEW\n", "h1")
        self.result_text.insert(tk.END, "═" * 72 + "\n\n", "gold")
        ov = suggestions["overall"]
        self.result_text.insert(tk.END, f"  Composite Score:      {ov['score']} / 100\n")
        self.result_text.insert(tk.END, f"  Performance Grade:    {ov['grade']}\n")
        self.result_text.insert(tk.END, f"  Word Count:           {basic['word_count']}\n")
        self.result_text.insert(tk.END, f"  Character Count:      {basic['char_count']}\n")
        self.result_text.insert(tk.END, f"  Paragraphs:           {basic['para_count']}\n")
        self.result_text.insert(tk.END, f"  Sentences:            {basic['sentence_count']}\n")
        self.result_text.insert(tk.END, f"  Avg Sentence Length:  {basic['avg_sentence_length']} words\n")
        self.result_text.insert(tk.END, f"  Sentence Length Std:  {basic['sentence_length_std']} words\n")
        self.result_text.insert(tk.END, f"  Est. Duration:        {basic['duration_min']} min (130 wpm)\n")
        self.result_text.insert(tk.END, f"  Lexical Diversity:    {basic['lexical_diversity']} (TTR)\n")
        self.result_text.insert(tk.END, f"  Hapax Legomena:       {basic['hapax_legomena']} ({basic['hapax_ratio']})\n")
        self.result_text.insert(tk.END, f"  Conjunction Density:  {basic['conjunction_density']} / sentence\n")
        self.result_text.insert(tk.END, f"  Quotable Sentences:   {basic['quotable_count']}\n")
        self.result_text.insert(tk.END, f"  Progression Score:    {ov['progression']} / 10\n")
        self.result_text.insert(tk.END, f"\n  Assessment: {ov['comment']}\n\n")

        # Readability
        self.result_text.insert(tk.END, "  Readability Metrics:\n")
        self.result_text.insert(tk.END, f"    Flesch Reading Ease: {readability['flesch_reading_ease']} ({readability['level']})\n")
        self.result_text.insert(tk.END, f"    Flesch-Kincaid Grade: {readability['flesch_kincaid_grade']}\n")
        self.result_text.insert(tk.END, f"    Avg Syllables/Word: {readability['avg_syllables_per_word']}\n\n")

        # Pronoun distribution
        self.result_text.insert(tk.END, "  Pronoun Distribution:\n")
        self.result_text.insert(tk.END, f"    1st sg (I/me/my):     {basic['first_person_sg']}\n")
        self.result_text.insert(tk.END, f"    1st pl (we/us/our):   {basic['first_person_pl']}\n")
        self.result_text.insert(tk.END, f"    2nd (you/your):       {basic['second_person']}\n")
        self.result_text.insert(tk.END, f"    3rd (he/she/they):    {basic['third_person']}\n\n")

        # 2. Strengths
        self.result_text.insert(tk.END, "=" * 72 + "\n")
        self.result_text.insert(tk.END, "2. IDENTIFIED STRENGTHS\n")
        self.result_text.insert(tk.END, "=" * 72 + "\n\n")
        for i, s in enumerate(suggestions["strengths"], 1):
            self.result_text.insert(tk.END, f"  [{i}] {s}\n")
        self.result_text.insert(tk.END, "\n")

        # 3. Rhetorical devices
        self.result_text.insert(tk.END, "=" * 72 + "\n")
        self.result_text.insert(tk.END, "3. RHETORICAL DEVICE ANALYSIS\n")
        self.result_text.insert(tk.END, "=" * 72 + "\n\n")
        self.result_text.insert(tk.END, f"  Rhetorical Questions: {rhetorical['rhetorical_questions']}\n")
        self.result_text.insert(tk.END, f"  Anaphora (repeated openings): {rhetorical['anaphora']}\n")
        self.result_text.insert(tk.END, f"  Triple Structures (A, B, C): {rhetorical['triples']}\n")
        self.result_text.insert(tk.END, f"  Parallelism (to X, to Y, to Z): {rhetorical['parallelism']}\n")
        if rhetorical["repeated_words"]:
            top_repeated = sorted(rhetorical["repeated_words"].items(), key=lambda x: -x[1])[:5]
            self.result_text.insert(tk.END, f"  Most Repeated Words: {', '.join(f'{w}({c})' for w, c in top_repeated)}\n")
        self.result_text.insert(tk.END, "\n")

        # 4. Arousal curve
        self.result_text.insert(tk.END, "=" * 72 + "\n")
        self.result_text.insert(tk.END, "4. AROUSAL CURVE (position-normalized)\n")
        self.result_text.insert(tk.END, "=" * 72 + "\n\n")
        curve = analysis["vad_curve"]
        self.result_text.insert(tk.END, "  ")
        for point in curve:
            height = int(point["a"] / 9 * 8)
            bar = "#" * height if height > 0 else "."
            self.result_text.insert(tk.END, bar + " ")
        self.result_text.insert(tk.END, "\n  Opening" + " " * max(1, len(curve) * 2 - 14) + "Ending\n\n")

        # 5. Emotional shifts
        if suggestions["emotional_shifts"]:
            self.result_text.insert(tk.END, "=" * 72 + "\n")
            self.result_text.insert(tk.END, "5. EMOTIONAL SHIFT DETECTION\n")
            self.result_text.insert(tk.END, "=" * 72 + "\n\n")
            for shift in suggestions["emotional_shifts"]:
                self.result_text.insert(tk.END,
                    f"  Para {shift['from_para']} -> {shift['to_para']}: "
                    f"{shift['from_emotion']} -> {shift['to_emotion']} "
                    f"(intensity delta: {shift['intensity_change']}, {shift['abruptness']})\n")
            self.result_text.insert(tk.END, "\n")

        # 6. Paragraph-level detail
        self.result_text.insert(tk.END, "=" * 72 + "\n")
        self.result_text.insert(tk.END, "6. PARAGRAPH-LEVEL EMOTION ANALYSIS\n")
        self.result_text.insert(tk.END, "=" * 72 + "\n\n")
        part_name_cn = {
            "opening": "Opening", "body_front": "Body-F",
            "body_back": "Body-B", "ending": "Ending"
        }
        for p in analysis["paragraphs"]:
            part_cn = part_name_cn.get(p["part"], p["part"])
            vad = p["vad"]
            self.result_text.insert(tk.END,
                f"  Para {p['index']:2d} [{part_cn:6s}] Dominant: {p['dominant']:14s} "
                f"Intensity: {p['intensity']:4.1f}/10\n")
            if p["mixed_emotions"]:
                self.result_text.insert(tk.END, f"           Mixed: {', '.join(p['mixed_emotions'])}\n")
            self.result_text.insert(tk.END,
                f"           VAD: V={vad['v']:5.2f}  A={vad['a']:5.2f}  D={vad['d']:5.2f}\n")
            self.result_text.insert(tk.END, f"           Text: {p['text']}\n")

            all_hits = []
            for emo, kws in p["hit_keywords"].items():
                if kws:
                    all_hits.append(f"{emo}: {', '.join(kws)}")
            if all_hits:
                self.result_text.insert(tk.END, f"           Keywords: {' | '.join(all_hits)}\n")

            all_negated = []
            for emo, kws in p["negated_keywords"].items():
                if kws:
                    all_negated.extend(kws)
            if all_negated:
                self.result_text.insert(tk.END, f"           Negated: {', '.join(all_negated)}\n")
            self.result_text.insert(tk.END, "\n")

        # 7. Structural emotion distribution
        self.result_text.insert(tk.END, "=" * 72 + "\n")
        self.result_text.insert(tk.END, "7. STRUCTURAL EMOTION DISTRIBUTION\n")
        self.result_text.insert(tk.END, "=" * 72 + "\n\n")
        part_names = {
            "opening": "Opening", "body_front": "Body (Front)",
            "body_back": "Body (Back)", "ending": "Ending"
        }
        for part, emo in analysis["structure_emotion"].items():
            intensity = analysis["structure_intensity"][part]
            vad = analysis["structure_vad"][part]
            self.result_text.insert(tk.END,
                f"  {part_names[part]:14s}: {emo:14s}  Intensity={intensity:4.1f}/10  "
                f"V={vad['v']:5.2f} A={vad['a']:5.2f} D={vad['d']:5.2f}\n")
        self.result_text.insert(tk.END, "\n")

        # 8. Diagnostic findings
        self.result_text.insert(tk.END, "=" * 72 + "\n")
        self.result_text.insert(tk.END, "8. DIAGNOSTIC FINDINGS\n")
        self.result_text.insert(tk.END, "=" * 72 + "\n\n")
        if suggestions["problems"]:
            for i, p in enumerate(suggestions["problems"], 1):
                self.result_text.insert(tk.END,
                    f"  Finding {i}: {p['Segment']} — {p['Finding']}  [{p['Severity']}]\n")
                self.result_text.insert(tk.END, f"    Evidence:   {p['Evidence']}\n")
                self.result_text.insert(tk.END, f"    Current:    {p['Current State']}\n")
                self.result_text.insert(tk.END, f"    Expected:   {p['Expected State']}\n")
                self.result_text.insert(tk.END, f"    Recommend:  {p['Recommendation']}\n\n")
        else:
            self.result_text.insert(tk.END, "  No significant affective misalignments detected.\n\n")

        # 9. Polish examples
        if suggestions["polish_examples"]:
            self.result_text.insert(tk.END, "=" * 72 + "\n")
            self.result_text.insert(tk.END, "9. POLISHING EXAMPLES (Before -> After)\n")
            self.result_text.insert(tk.END, "=" * 72 + "\n\n")
            for i, g in enumerate(suggestions["polish_examples"], 1):
                self.result_text.insert(tk.END, f"  [{g['part']}] Strategy: {g['target']}\n")
                for before, after in g["examples"]:
                    self.result_text.insert(tk.END, f"    Before: {before}\n")
                    self.result_text.insert(tk.END, f"    After:  {after}\n")
                self.result_text.insert(tk.END, "\n")

        # 10. Stylistic recommendations
        if suggestions["extra_tips"]:
            self.result_text.insert(tk.END, "=" * 72 + "\n")
            self.result_text.insert(tk.END, "10. STYLISTIC RECOMMENDATIONS\n")
            self.result_text.insert(tk.END, "=" * 72 + "\n\n")
            for tip in suggestions["extra_tips"]:
                self.result_text.insert(tk.END, f"  - {tip}\n")
            self.result_text.insert(tk.END, "\n")

        # 11. Paragraph-level micro-suggestions
        if suggestions["paragraph_tips"]:
            self.result_text.insert(tk.END, "=" * 72 + "\n")
            self.result_text.insert(tk.END, "11. PARAGRAPH-LEVEL MICRO-SUGGESTIONS\n")
            self.result_text.insert(tk.END, "=" * 72 + "\n\n")
            for tip in suggestions["paragraph_tips"]:
                self.result_text.insert(tk.END, f"  - Paragraph {tip['para_index']}: {tip['tip']}\n")

        self.result_text.see("1.0")
        self.result_text.config(state=tk.DISABLED)

    def export_single_report(self):
        if not self.current_text_analysis:
            messagebox.showwarning("No Analysis", "Please analyze a speech before exporting.")
            return
        content = self.result_text.get("1.0", tk.END)
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Report", "*.txt")],
            title="Save Analysis Report",
            initialfile="speech_analysis_report.txt"
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Export Complete", f"Report saved to:\n{save_path}")

    # -----------------------------------------------------------------
    # Live recording functions
    # -----------------------------------------------------------------
    def toggle_recording(self):
        if not self.live_analyzer.is_recording:
            self.live_data = []
            self.live_analyzer.start_recording(callback=self._on_audio_chunk)
            self.record_btn.config(text="Stop Recording")
            self.live_status_var.set("Recording in progress... Speak into the microphone.")
        else:
            self.live_analyzer.stop_recording()
            self.record_btn.config(text="Start Recording")
            self.live_status_var.set("Recording stopped. Click Generate Report for full analysis.")

    def _on_audio_chunk(self, chunk):
        self.live_data.append(chunk)
        self.current_emo_var.set(f"Emotion: {chunk['emotion']}")
        self.current_loud_var.set(f"Loudness: {chunk['loudness']:.3f}")
        self.current_pitch_var.set(f"Pitch Var: {chunk['pitch_var']:.3f}")
        self.duration_var.set(f"Elapsed: {chunk['time']:.1f} s")
        if len(self.live_data) % 2 == 0:
            self._update_live_plot()

    def _update_live_plot(self):
        n = min(len(self.live_data), self.live_max_points)
        data = self.live_data[-n:]
        times = [d["time"] for d in data]
        loudness = [d["loudness"] for d in data]
        emo_intensity = [d["confidence"] * d["loudness"] for d in data]

        self.line_loudness.set_data(times, loudness)
        self.line_emotion.set_data(times, emo_intensity)

        x_max = max(times[-1], 1)
        self.ax_loudness.set_xlim(max(0, x_max - 20), x_max)
        self.ax_emotion.set_xlim(max(0, x_max - 20), x_max)

        self.live_canvas.draw_idle()

    def generate_live_report(self):
        if not self.live_analyzer.chunk_results:
            messagebox.showwarning("No Recording", "Please record audio before generating a report.")
            return

        summary = self.live_analyzer.get_summary()
        if not summary:
            return

        self.live_result_text.config(state=tk.NORMAL)
        self.live_result_text.delete("1.0", tk.END)

        self.live_result_text.insert(tk.END, "=" * 60 + "\n")
        self.live_result_text.insert(tk.END, "RECORDING ANALYSIS SUMMARY\n")
        self.live_result_text.insert(tk.END, "=" * 60 + "\n\n")
        self.live_result_text.insert(tk.END, f"  Duration:            {summary['duration_sec']} seconds\n")
        self.live_result_text.insert(tk.END, f"  Composite Score:     {summary['total_score']} / 100\n")
        self.live_result_text.insert(tk.END, f"  Dominant Emotion:    {summary['main_emotion']}\n")
        self.live_result_text.insert(tk.END, f"  Mean Loudness:       {summary['avg_loudness']} (0-1)\n")
        self.live_result_text.insert(tk.END, f"  Peak Loudness:       {summary['max_loudness']}\n")
        self.live_result_text.insert(tk.END, f"  Loudness Std Dev:    {summary['loudness_variance']}\n")
        self.live_result_text.insert(tk.END, f"  Dynamic Range:       {summary['dynamic_range']}\n")
        self.live_result_text.insert(tk.END, f"  Avg Spectral Centroid:{summary['avg_spectral_centroid']} Hz\n")
        self.live_result_text.insert(tk.END, f"  Pause Ratio:         {summary['pause_ratio']:.1%}\n\n")

        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        self.live_result_text.insert(tk.END, "EMOTION DISTRIBUTION\n")
        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        total_chunks = sum(summary["emotion_distribution"].values())
        for emo, count in sorted(summary["emotion_distribution"].items(), key=lambda x: -x[1]):
            pct = count / max(1, total_chunks) * 100
            bar = "#" * int(pct / 5)
            self.live_result_text.insert(tk.END, f"  {emo:14s}: {count:4d} ({pct:5.1f}%) {bar}\n")
        self.live_result_text.insert(tk.END, "\n")

        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        self.live_result_text.insert(tk.END, "FOUR-SEGMENT STRUCTURAL ANALYSIS\n")
        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        for seg, info in summary["sections"].items():
            self.live_result_text.insert(tk.END,
                f"  {seg:14s}: Dominant={info['dominant_emotion']:14s}  "
                f"Mean Loudness={info['avg_loudness']:.3f}\n")
        self.live_result_text.insert(tk.END, "\n")

        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        self.live_result_text.insert(tk.END, "DIAGNOSTIC FINDINGS\n")
        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        if summary["diagnosis"]:
            for i, d in enumerate(summary["diagnosis"], 1):
                self.live_result_text.insert(tk.END, f"  [{i}] {d}\n")
        else:
            self.live_result_text.insert(tk.END, "  No significant acoustic anomalies detected.\n")

            self.live_result_text.insert(tk.END, "\n")

        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        self.live_result_text.insert(tk.END, "RECOMMENDATIONS\n")
        self.live_result_text.insert(tk.END, "-" * 40 + "\n")
        if summary["suggestions"]:
            for i, s in enumerate(summary["suggestions"], 1):
                self.live_result_text.insert(tk.END, f"  [{i}] {s}\n")
        else:
            self.live_result_text.insert(tk.END, "  Maintain current vocal delivery technique.\n")

        self.live_result_text.see("1.0")
        self.live_result_text.config(state=tk.DISABLED)

    # -----------------------------------------------------------------
    # Audio file analysis functions
    # -----------------------------------------------------------------
    def select_audio_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("WAV Audio", "*.wav"), ("All Files", "*.*")]
        )
        if file_path:
            self.audio_path_var.set(file_path)

    def analyze_audio_file(self):
        file_path = self.audio_path_var.get()
        if not file_path:
            messagebox.showwarning("No File", "Please select an audio file first.")
            return
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", "The selected file does not exist.")
            return

        result = self.audio_analyzer.analyze_file(file_path)
        if "error" in result:
            messagebox.showerror("Analysis Failed", result["error"])
            return

        # Update plot
        if MATPLOTLIB_AVAILABLE:
            times = [f["time"] for f in result["frame_results"]]
            loudness = [f["loudness"] for f in result["frame_results"]]
            pitch = [f["pitch_var"] for f in result["frame_results"]]
            self.line_audio_loud.set_data(times, loudness)
            self.line_audio_pitch.set_data(times, pitch)
            self.ax_audio.set_xlim(0, max(times[-1], 1))
            self.ax_audio.set_ylim(0, 1)
            self.audio_canvas.draw_idle()

        # Update report
        self.audio_result_text.config(state=tk.NORMAL)
        self.audio_result_text.delete("1.0", tk.END)

        self.audio_result_text.insert(tk.END, "=" * 60 + "\n")
        self.audio_result_text.insert(tk.END, "AUDIO FILE ANALYSIS REPORT\n")
        self.audio_result_text.insert(tk.END, "=" * 60 + "\n\n")
        self.audio_result_text.insert(tk.END, f"  File:                {os.path.basename(file_path)}\n")
        self.audio_result_text.insert(tk.END, f"  Duration:            {result['duration_sec']} seconds\n")
        self.audio_result_text.insert(tk.END, f"  Sample Rate:         {result['sample_rate']} Hz\n")
        self.audio_result_text.insert(tk.END, f"  Composite Score:     {result['total_score']} / 100\n")
        self.audio_result_text.insert(tk.END, f"  Dominant Emotion:    {result['main_emotion']}\n")
        self.audio_result_text.insert(tk.END, f"  Mean Loudness:       {result['avg_loudness']} (0-1)\n")
        self.audio_result_text.insert(tk.END, f"  Peak Loudness:       {result['max_loudness']}\n")
        self.audio_result_text.insert(tk.END, f"  Loudness Std Dev:    {result['loudness_variance']}\n")
        self.audio_result_text.insert(tk.END, f"  Dynamic Range:       {result['dynamic_range']}\n")
        self.audio_result_text.insert(tk.END, f"  Avg Spectral Centroid:{result['avg_spectral_centroid']} Hz\n")
        self.audio_result_text.insert(tk.END, f"  Pause Ratio:         {result['pause_ratio']:.1%}\n")
        self.audio_result_text.insert(tk.END, f"  Speech Rate Ratio:   {result['speech_rate_ratio']}\n\n")

        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        self.audio_result_text.insert(tk.END, "EMOTION DISTRIBUTION\n")
        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        total = sum(result["emotion_distribution"].values())
        for emo, count in sorted(result["emotion_distribution"].items(), key=lambda x: -x[1]):
            pct = count / max(1, total) * 100
            bar = "#" * int(pct / 5)
            self.audio_result_text.insert(tk.END, f"  {emo:14s}: {count:4d} ({pct:5.1f}%) {bar}\n")
        self.audio_result_text.insert(tk.END, "\n")

        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        self.audio_result_text.insert(tk.END, "FOUR-SEGMENT STRUCTURAL ANALYSIS\n")
        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        for seg, info in result["sections"].items():
            self.audio_result_text.insert(tk.END,
                f"  {seg:14s}: Dominant={info['dominant_emotion']:14s}  "
                f"Mean Loudness={info['avg_loudness']:.3f}\n")
        self.audio_result_text.insert(tk.END, "\n")

        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        self.audio_result_text.insert(tk.END, "DIAGNOSTIC FINDINGS\n")
        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        if result["diagnosis"]:
            for i, d in enumerate(result["diagnosis"], 1):
                self.audio_result_text.insert(tk.END, f"  [{i}] {d}\n")
        else:
            self.audio_result_text.insert(tk.END, "  No significant acoustic anomalies detected.\n")
        self.audio_result_text.insert(tk.END, "\n")

        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        self.audio_result_text.insert(tk.END, "RECOMMENDATIONS\n")
        self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
        if result["suggestions"]:
            for i, s in enumerate(result["suggestions"], 1):
                self.audio_result_text.insert(tk.END, f"  [{i}] {s}\n")
        else:
            self.audio_result_text.insert(tk.END, "  Maintain current vocal delivery technique.\n")

        self.audio_result_text.see("1.0")
        self.audio_result_text.config(state=tk.DISABLED)

    def transcribe_audio(self):
        """ASR: transcribe audio file to text, then auto-send to Text Analysis tab."""
        file_path = self.audio_path_var.get()
        if not file_path:
            messagebox.showwarning("No File", "Please select an audio file first.")
            return
        if not ASR_AVAILABLE:
            messagebox.showwarning("ASR Unavailable",
                "SpeechRecognition not installed.\nRun: pip install SpeechRecognition")
            return

        self.audio_result_text.config(state=tk.NORMAL)
        self.audio_result_text.delete("1.0", tk.END)
        self.audio_result_text.insert(tk.END, "Transcribing... (requires internet, may take a few seconds)\n")
        self.audio_result_text.update()

        result = self.asr.transcribe_audio_file(file_path, language="en-US")

        self.audio_result_text.delete("1.0", tk.END)
        if "error" in result:
            self.audio_result_text.insert(tk.END, f"Transcription failed:\n{result['error']}\n")
        else:
            text = result["text"]
            self.audio_result_text.insert(tk.END, "=" * 60 + "\n")
            self.audio_result_text.insert(tk.END, "ASR TRANSCRIPTION RESULT\n")
            self.audio_result_text.insert(tk.END, "=" * 60 + "\n\n")
            self.audio_result_text.insert(tk.END, f"  Language: {result['language']}\n")
            self.audio_result_text.insert(tk.END, f"  Word Count: {len(text.split())}\n\n")
            self.audio_result_text.insert(tk.END, text + "\n\n")
            self.audio_result_text.insert(tk.END, "-" * 40 + "\n")
            self.audio_result_text.insert(tk.END, "Text has been copied to the Text Analysis tab.\n")
            self.audio_result_text.insert(tk.END, "Switch to that tab and click Analyze for full emotion analysis.\n")

            # Copy transcribed text to the text input
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", text)

        self.audio_result_text.see("1.0")
        self.audio_result_text.config(state=tk.DISABLED)

    # -----------------------------------------------------------------
    # Benchmark comparison functions
    # -----------------------------------------------------------------
    def do_compare(self):
        if not self.current_text_analysis:
            messagebox.showwarning("No Analysis", "Please analyze a speech in the Text Analysis tab first.")
            return
        idx = self.bench_listbox.curselection()
        if not idx:
            messagebox.showwarning("Selection Required", "Please select a benchmark speech from the list.")
            return

        bench_id = self.bench_items[idx[0]]["id"]
        result = self.comparer.compare(self.current_text_analysis, bench_id)
        if not result:
            messagebox.showerror("Comparison Failed", "Unable to perform comparison.")
            return

        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)

        self.compare_text.insert(tk.END, f"Benchmark: \"{result['benchmark_title']}\"\n")
        self.compare_text.insert(tk.END, f"Speaker:   {result['benchmark_speaker']}\n")
        self.compare_text.insert(tk.END, f"Structural Similarity: {result['similarity']}%\n\n")

        self.compare_text.insert(tk.END, "-" * 50 + "\n")
        self.compare_text.insert(tk.END, "STRUCTURAL EMOTION COMPARISON\n")
        self.compare_text.insert(tk.END, "-" * 50 + "\n\n")
        for part, info in result["structure_diff"].items():
            status = "MATCH" if info["match"] else "DIFFER"
            self.compare_text.insert(tk.END, f"  {info['part_name']:14s}: [{status}]\n")
            self.compare_text.insert(tk.END, f"    Your draft:  {info['user']}\n")
            self.compare_text.insert(tk.END, f"    Benchmark:   {info['benchmark']}\n\n")

        self.compare_text.insert(tk.END, "-" * 50 + "\n")
        self.compare_text.insert(tk.END, "OPTIMIZATION RECOMMENDATIONS\n")
        self.compare_text.insert(tk.END, "-" * 50 + "\n\n")
        for i, tip in enumerate(result["suggestion"], 1):
            self.compare_text.insert(tk.END, f"  [{i}] {tip}\n")

        self.compare_text.config(state=tk.DISABLED)

    # -----------------------------------------------------------------
    # Batch grading functions
    # -----------------------------------------------------------------
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing speech .txt files")
        if folder:
            self.folder_var.set(folder)

    def run_batch(self):
        folder = self.folder_var.get()
        if not folder:
            messagebox.showwarning("Folder Required", "Please select a folder containing speech files.")
            return
        self.batch_results = self.grader.batch_analyze(folder)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in self.batch_results:
            self.tree.insert("", tk.END, values=(
                r["Filename"], r["Composite Score"], r["Grade"],
                r["Word Count"], r["Est. Duration (min)"],
                r["Opening Emotion"], r["Ending Emotion"],
                r["Quotable Sentences"], r["Readability Grade"],
                r["Findings Count"], r["Primary Finding"]
            ))
        messagebox.showinfo("Batch Complete", f"Successfully analyzed {len(self.batch_results)} speeches.")

    def export_batch(self):
        if not self.batch_results:
            messagebox.showwarning("No Results", "Please run batch analysis before exporting.")
            return
        msg = self.grader.export_report(self.batch_results)
        messagebox.showinfo("Export Complete", msg)

# =====================================================================
# Application Entry Point
# =====================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"+{x}+{y}")
    app = SpeechAssistantApp(root)
    root.mainloop()
