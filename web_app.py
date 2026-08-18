import streamlit as st
import json
import os
import re
from collections import Counter
import numpy as np

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

# 页面配置
st.set_page_config(page_title="Speech Optimizer", layout="wide")
st.title("🎤 Speech Optimizer — 演讲情绪分析")

# 侧边栏
st.sidebar.header("设置")
scene = st.sidebar.selectbox(
    "演讲场景",
    ["Academic Competition", "Corporate Presentation", "Commemorative Address"]
)

# 初始化分析器
@st.cache_resource
def get_analyzer():
    loader = CorpusLoader()
    analyzer = SpeechEmotionAnalyzer(loader.base_corpus, loader.emobank, scene)
    reviser = SpeechReviser()
    return analyzer, reviser

analyzer, reviser = get_analyzer()
analyzer.set_scene(scene)

# 主界面
tab1, tab2 = st.tabs(["📝 文本分析", "📊 批量分析"])

with tab1:
    text = st.text_area("粘贴你的英文演讲稿", height=300)
    
    if st.button("开始分析", type="primary"):
        if text.strip():
            with st.spinner("分析中..."):
                analysis = analyzer.full_analysis(text)
                suggestions = reviser.generate_detailed_suggestions(analysis)
                basic = analysis["basic_info"]
            
            # 显示结果
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("综合评分", f"{suggestions['overall']['score']}/100")
            col2.metric("等级", suggestions["overall"]["grade"])
            col3.metric("词数", basic["word_count"])
            col4.metric("预估时长", f"{basic['duration_min']} min")
            
            st.subheader("📋 评估")
            st.write(suggestions["overall"]["comment"])
            
            st.subheader("💪 优点")
            for s in suggestions["strengths"]:
                st.write(f"✅ {s}")
            
            st.subheader("🔍 诊断发现")
            if suggestions["problems"]:
                for p in suggestions["problems"]:
                    with st.expander(f"{p['Segment']} — {p['Finding']} [{p['Severity']}]"):
                        st.write(f"**证据：** {p['Evidence']}")
                        st.write(f"**当前：** {p['Current State']}")
                        st.write(f"**期望：** {p['Expected State']}")
                        st.write(f"**建议：** {p['Recommendation']}")
            else:
                st.success("未发现明显问题！")
            
            st.subheader("✏️ 润色示例")
            for g in suggestions["polish_examples"]:
                st.write(f"**[{g['part']}] {g['target']}**")
                for before, after in g["examples"]:
                    col_a, col_b = st.columns(2)
                    col_a.info(f"Before: {before}")
                    col_b.success(f"After: {after}")
        else:
            st.warning("请先输入演讲稿")

with tab2:
    st.write("上传多个 .txt 文件进行批量分析")
    uploaded_files = st.file_uploader("选择演讲稿", type=["txt"], accept_multiple_files=True)
    
    if uploaded_files and st.button("批量分析"):
        results = []
        for f in uploaded_files:
            text = f.read().decode("utf-8")
            analysis = analyzer.full_analysis(text)
            sug = reviser.generate_detailed_suggestions(analysis)
            results.append({
                "文件名": f.name,
                "评分": sug["overall"]["score"],
                "等级": sug["overall"]["grade"],
                "词数": analysis["basic_info"]["word_count"],
                "开场情绪": analysis["structure_emotion"]["opening"],
                "结尾情绪": analysis["structure_emotion"]["ending"]
            })
        st.dataframe(results)

st.sidebar.markdown("---")
st.sidebar.caption("Speech Optimizer Pro | Powered by Streamlit")
