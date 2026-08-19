
import matplotlib.pyplot as plt
import streamlit as st
import json
import os
import re
import io
import time
from collections import Counter
import numpy as np
import pandas as pd

try:
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    ASR_AVAILABLE = True
except ImportError:
    ASR_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from audiorecorder import audiorecorder
    RECORDER_AVAILABLE = True
except ImportError:
    RECORDER_AVAILABLE = False

BUILTIN_CORPUS = {
    "emotion_dict": {
        "Affability": ["we","us","our","ours","ourselves","everyone","everybody","friends","friend","hello","hi","hey","remember","do you","have you","believe","together","folks","people","listeners","audience","dear","welcome","greetings","all of you","each of you","many of you","some of you","those of you","let us","let's","share","connect","community","fellow","colleagues","ladies and gentlemen","good morning","good afternoon","good evening","thank you for being here","it is a pleasure","honored to be here","my friends","dear friends","kindred spirits","like-minded","stand with","join me","walk with","side by side","hand in hand","united","solidarity","camaraderie","kinship","fellowship","brotherhood","sisterhood","common ground","shared vision","collective","togetherness","oneness","unity","bond","gather","assemble","congregate","reunion","gathering","celebrate together","march together","dream together","build together","grow together","learn together","in this together","one family","global community","human family","citizens of the world"],
        "Composure": ["first","second","third","firstly","secondly","thirdly","data shows","data indicate","research indicates","research shows","studies show","studies indicate","in fact","specifically","objectively","statistically","according to","overall","generally","fundamentally","essentially","empirically","quantitatively","systematically","analytically","methodologically","empirical","evidence suggests","evidence indicates","the literature","meta-analysis","longitudinal study","controlled experiment","peer-reviewed","scholarly","academic","theoretical framework","hypothesis","methodology","analysis reveals","findings suggest","measurable","observable","verifiable","replicable","falsifiable","paradigm","model","correlation","causation","variable","coefficient","significant","insignificant","p-value","confidence interval","standard deviation","regression","anova","factor analysis","cluster analysis","qualitative","quantitative","mixed methods","case study","field study","laboratory","experiment","treatment group","control group","sample size","population","generalize","replicate","validate","calibrate","benchmark","baseline","metric","indicator","parameter","criterion","taxonomy"],
        "Conviction": ["must","will","undoubtedly","unquestionably","I believe","essentially","core","inevitably","certainly","definitely","absolutely","necessarily","decisively","resolutely","firmly","unwaveringly","categorically","unequivocally","assuredly","undeniably","incontrovertibly","indisputably","irrefutably","conclusively","demonstrably","evidently","manifestly","unambiguously","explicitly","determinedly","steadfastly","uncompromisingly","unflinchingly","unhesitatingly","conviction","resolve","determination","perseverance","dedication","commitment","shall","ought","duty","obligation","responsibility","accountability","principle","creed","doctrine","tenet","dogma","ideology","manifesto","pledge","vow","oath","swear","guarantee","promise","assure","ensure","insist","demand","require","mandate","imperative","crucial","vital","essential","indispensable","paramount","supreme","ultimate","definitive","authoritative","binding","non-negotiable","sacrosanct","inviolable","unassailable","unshakeable","steadfast","unbending","unrelenting","unyielding"],
        "Passion": ["let us","let's","strive","fight","rise","advance","forge ahead","never retreat","act now","build together","pursue","endeavor","persevere","triumph","conquer","inspire","empower","transform","revolutionize","unleash","ignite","champion","dedicate","embrace","seize","mobilize","galvanize","propel","accelerate","breakthrough","pioneer","innovate","reshape","redefine","transcend","overcome","prevail","flourish","thrive","soar","unprecedented","extraordinary","remarkable","groundbreaking","revolutionary","game-changing","paradigm shift","milestone","ardor","fervor","zeal","enthusiasm","vigor","vitality","energy","fire","flame","burning","blazing","radiant","luminous","dazzling","brilliant","magnificent","glorious","sublime","majestic","grandeur","splendor","ecstasy","elation","exhilaration","exuberance","jubilation","rapture","bliss","euphoria","triumphant","victorious","heroic","legendary","iconic","monumental","epoch-making","world-changing","history-making","trailblazing"],
        "Deep Emotion": ["unforgettable","moved","grateful","tribute","never forget","tears","heartfelt","warmth","cherish","memory","honor","thank","appreciate","beloved","dear","precious","sentimental","nostalgic","compassion","empathy","tenderness","devotion","love","affection","admiration","reverence","awe","wonder","profound","deeply","soul","spirit","passionately","earnestly","sincerely","genuinely","authentically","vulnerable","intimate","reflective","contemplative","meditative","poignant","touching","moving","heartwarming","bittersweet","melancholic","sorrowful","joyful","euphoric","blissful","serene","tranquil","peaceful","yearning","longing","pining","wistful","soulful","spiritual","transcendent","ethereal","celestial","divine","sacred","hallowed","reverent","devout","pious","faithful","loyal","steadfast love","enduring love","unconditional","boundless","infinite","eternal","timeless","everlasting","perpetual","abiding","lingering","haunting","evocative","resonant","echoing"],
        "Humor": ["surprisingly","interestingly","frankly","actually","you see","ironically","amusingly","joke","funny","laugh","humor","witty","comical","lighthearted","playful","amusing","entertaining","chuckle","grin","smile","paradox","absurd","ridiculous","hilarious","droll","facetious","jocular","whimsical","mischievous","teasing","banter","quip","jest","pun","sarcasm","satire","irony","tongue-in-cheek","wry","dry humor","self-deprecating","deadpan","giggle","snicker","titter","chortle","guffaw","laughter","comedy","comedian","farce","slapstick","parody","spoof","caricature","burlesque","travesty","lampoon","mockery","ridicule","derision","scoff","jeer","taunt","jibe","gibe","wisecrack","crack","one-liner","punchline","setup","delivery","timing","cadence","wit","humorist","satirist","parodist","caricaturist","jester","fool","clown","buffoon","harlequin","punch","zinger"],
        "Solemnity": ["regret","crisis","severe","tragic","cannot ignore","harsh","reality","cost","painful","reflect","concerning","alarming","devastating","grave","dire","somber","melancholy","grievous","lamentable","woeful","deplorable","catastrophic","calamitous","ruinous","destructive","perilous","hazardous","jeopardy","threat","danger","risk","menace","peril","endanger","critical","urgent","pressing","acute","intense","drastic","radical","profoundly disturbing","deeply troubling","worrisome","disconcerting","unsettling","distressing","heartbreaking","shattering","crushing","overwhelming","staggering","appalling","mourn","grieve","lament","bewail","bemoan","deplore","rue","sorrow","woe","anguish","agony","torment","tribulation","adversity","hardship","suffering","misery","despair","hopelessness","desolation","gloom","doom","fate","destiny","inevitable","inexorable","relentless","merciless","pitiless","unforgiving","grim"],
        "Critical Thinking": ["why","could it be","really","essence","conversely","on the contrary","however","but","question is","challenge","examine","scrutinize","analyze","probe","investigate","contemplate","ponder","reconsider","rethink","question","doubt","debate","argue","dispute","contest","contradict","paradox","dilemma","ambiguity","nuance","complexity","intricacy","subtlety","sophistication","layered","multifaceted","interdisciplinary","cross-disciplinary","meta-level","deconstruct","unpack","unravel","decipher","decode","interpret","hermeneutics","epistemology","ontology","teleology","methodology","pedagogy","heuristic","allegory","metaphor","synecdoche","metonymy","chiasmus","anaphora","epistrophe","antithesis","oxymoron","aporia","dialectic","synthesis","thesis","socratic","platonic","aristotelian","kantian","hegelian","nietzschean","wittgensteinian","foucaultian","derrida","semiotics","linguistics","pragmatics","semantics","syntax","rhetoric","logic","ethics","aesthetics","metaphysics","phenomenology","existentialism","structuralism","post-structuralism","deconstruction","constructivism","relativism","absolutism"]
    },
    "scene_rules": {
        "Academic Competition": {"opening":{"expected":["Affability","Humor"],"max_intensity":6},"body_front":{"expected":["Composure","Deep Emotion","Critical Thinking"],"max_intensity":7},"body_back":{"expected":["Conviction","Critical Thinking","Solemnity"],"min_intensity":4},"ending":{"expected":["Passion","Deep Emotion","Conviction"],"min_intensity":6}},
        "Corporate Presentation": {"opening":{"expected":["Affability","Composure"],"max_intensity":5},"body_front":{"expected":["Composure","Critical Thinking"],"max_intensity":6},"body_back":{"expected":["Conviction","Composure"],"min_intensity":3},"ending":{"expected":["Conviction","Composure"],"min_intensity":4}},
        "Commemorative Address": {"opening":{"expected":["Deep Emotion","Composure"],"max_intensity":6},"body_front":{"expected":["Solemnity","Composure","Deep Emotion"],"max_intensity":7},"body_back":{"expected":["Conviction","Passion"],"min_intensity":5},"ending":{"expected":["Passion","Conviction","Deep Emotion"],"min_intensity":7}}
    }
}

SLANG_DICT = {
    "Affability": ["sup","yo","wassup","hey guys","hiya","howdy","cheers","mate","buddy","pal","dude","fam"," squad","crew","homie","bestie","peeps","folks","y'all","ya","bruh","bro","sis","famjam","vibe check","good vibes","hype","lit","awesome","cool","nice","great","sweet","dope","sick","epic","legendary","iconic","slay","queen","king","goat","flex","clout","bae","boo","ride or die","day one","real one","solid","trust","respect","appreciate","shoutout","props","kudos","mad love","big love"],
    "Passion": ["hype","lit","fire","flame","go off","slay","kill it","crush it","nailed it","absolutely","totally","literally","deadass","fr fr","no cap","100%","periodt","and that's on","vibe","mood","aesthetic","obsessed","in love","craving","yearning","thirst","grind","hustle","rise up","level up","go hard","go big","all in","full send","bet","watch me","just do it","no excuses","never give up","keep going","push through","breakthrough","game changer","mind blown","blown away","speechless","wow","omg","woah","whoa","damn","hell yeah","hell yes","fuck yeah","yasss","yay","woohoo","let's go","c'mon","come on","do it"],
    "Humor": ["lol","lmao","lmfao","rofl","haha","hahaha","hehe","lul","kek","bruh","fr","cap","no cap","sus","sussy","mid","basic","cringe","cringey","savage","roast","clapback","receipts","spill the tea","tea","shade","throwing shade","okurrr","ok boomer"," Karen","Kevin","main character","NPC","rizz","gyatt","sigma","alpha","beta","cook","cooked","ratio","W","L","dub","slay","queen","iconic","legendary","hilarious","funny af","dead","dying","crying","screaming","vibrating","ascending","evaporating","deceased","I can't","I can't even","I'm dead","I'm crying","send help","wtf","what the","no way","no way","for real","actually","literally me","relatable","mood","big mood","whole mood"],
    "Solemnity": ["sad","depressed","heartbroken","devastated","crushed","broken","miserable","awful","terrible","horrible","dreadful","sucks","sucks ass","fml","my life is over","end it all","kill me","just end me","crying","sobbing","tears","hurt","hurts","pain","agony","suffering","torture","hell","nightmare","disaster","catastrophe","apocalypse","doomed","finished","over","done for","ruined","destroyed","annihilated","obliterated","wrecked","gutted","shattered","torn apart","lost","alone","lonely","empty","numb","void","darkness","despair","hopeless","giving up","no hope","why bother","what's the point","meaningless","pointless","futile","useless","worthless","trash","garbage","dogshit","ass","terrible","awful","the worst","worst ever","abysmal","dreadful","appalling","horrific","traumatic","PTSD","triggered","traumatized","scarred","damaged","broken beyond repair"],
    "Conviction": ["facts","fact","true","real","genuine","authentic","legit","no cap","deadass","fr fr","I swear","I promise","trust me","believe me","mark my words","mark my word","I guarantee","guaranteed","100%","period","periodt","end of story","case closed","that's that","and I mean that","I mean it","serious","for real","no joke","not kidding","I'm not kidding","truth","the truth","reality","actually","literally","exactly","precisely","absolutely","definitely","certainly","undoubtedly","unquestionably","inevitably","necessarily","must","have to","got to","gotta","need to","should","ought to","will","shall","do it","just do it","no excuses","no compromise","non-negotiable","deal breaker","hard pass","hard no","absolutely not","never","no way","not a chance","over my dead body"],
    "Deep Emotion": ["love","loved","loving","adore","adored","obsessed","obsession","infatuated","crush","smitten","heart eyes","🥺","😭","🥹","💔","❤️","💕","💖","💗","💓","💞","💘","💝","💟","feeling","feelings","emotions","emotional","tears","crying","sobbing","weep","weeping","moved","touched","tender","warm","cozy","soft","gentle","kind","caring","compassion","empathy","sympathy","nostalgia","nostalgic","memories","memory","remember","miss","missing","longing","yearning","wistful","soulful","deep","profound","meaningful","significant","special","precious","cherish","treasure","value","appreciate","grateful","thankful","blessed","fortunate","lucky","awe","wonder","amazed","astonished","stunned","speechless","overwhelmed","humbled","gratitude"],
    "Composure": ["actually","literally","basically","essentially","fundamentally","overall","generally","typically","usually","normally","commonly","frequently","often","regularly","consistently","constantly","continually","continuously","perpetually","invariably","inevitably","necessarily","certainly","definitely","absolutely","positively","emphatically","categorically","unequivocally","unambiguously","explicitly","specifically","precisely","exactly","accurately","correctly","properly","appropriately","suitably","fittingly","aptly","relevantly","pertinently","applicably","accordingly","consequently","therefore","thus","hence","so","ergo","wherefore","as a result","because of this","due to this","owing to this","on account of this","for this reason","for these reasons","in conclusion","to sum up","in summary","to summarize","in short","in brief","briefly","concisely","succinctly","compendiously","pithily","tersely","briefly","shortly"],
    "Critical Thinking": ["wait","hold on","hold up","wait a minute","wait a second","but","however","although","though","even though","despite","in spite of","regardless","nevertheless","nonetheless","notwithstanding","yet","still","even so","be that as it may","having said that","that said","on the other hand","on the contrary","conversely","in contrast","by contrast","in comparison","comparatively","relatively","comparatively speaking","relatively speaking","in some ways","in many ways","in certain respects","to some extent","to a certain degree","up to a point","partially","partly","somewhat","sort of","kind of","kinda","more or less","roughly","approximately","about","around","circa","give or take","plus or minus","so to speak","as it were","in a manner of speaking","if you will","shall we say","so to say","let's be real","let's be honest","frankly","honestly","truthfully","to be honest","to tell you the truth","if I'm being honest","no offense but","with all due respect","hear me out","listen","look","think about it","consider this","food for thought"]
}

NEGATION_WORDS = {"not","no","never","neither","nor","cannot","can't","don't","doesn't","didn't","won't","wouldn't","shouldn't","couldn't","isn't","aren't","wasn't","weren't","haven't","hasn't","hadn't","without","lack","lacking","absent","devoid","nothing","nobody","nowhere","none","hardly","barely","scarcely","rarely","seldom","unlikely","impossible"}

DEGREE_ADVERBS = {"extremely":2.0,"incredibly":1.9,"tremendously":1.8,"enormously":1.8,"immensely":1.7,"vastly":1.7,"profoundly":1.7,"deeply":1.6,"intensely":1.6,"fiercely":1.6,"passionately":1.6,"vehemently":1.5,"strongly":1.5,"powerfully":1.5,"mightily":1.5,"very":1.4,"quite":1.3,"rather":1.2,"fairly":1.1,"somewhat":0.8,"slightly":0.7,"a bit":0.7,"a little":0.6,"barely":0.4,"scarcely":0.4,"hardly":0.3,"almost":0.5,"nearly":0.5,"so":1.5,"totally":1.6,"absolutely":1.7,"literally":1.5,"completely":1.6,"entirely":1.5,"fully":1.4,"utterly":1.7,"thoroughly":1.5,"wholly":1.3}

DEFAULT_RULES = BUILTIN_CORPUS["scene_rules"]["Academic Competition"]

EMOTION_COLORS = {
    "Affability":"#2E7D32","Composure":"#1565C0","Conviction":"#E65100",
    "Passion":"#C62828","Deep Emotion":"#6A1B9A","Humor":"#F9A825",
    "Solemnity":"#37474F","Critical Thinking":"#00838F","Neutral":"#9E9E9E"
}


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
                with open(path,"r",encoding="utf-8") as f:
                    corpus = json.load(f)
                if "emotion_dict" in corpus and "structure_rule" in corpus:
                    name = corpus.get("corpus_info",{}).get("name","Custom Lexicon")
                    return corpus, f"[OK] Custom lexicon: {name}"
                else:
                    return BUILTIN_CORPUS, "[WARN] Format invalid; built-in fallback"
            except Exception:
                return BUILTIN_CORPUS, "[WARN] Read failed; built-in fallback"
        return BUILTIN_CORPUS, "[OK] Built-in lexicon (8 emotions, 640+ words)"

    def _load_emobank(self, path="emobank_processed.json"):
        if os.path.exists(path):
            try:
                with open(path,"r",encoding="utf-8") as f:
                    data = json.load(f)
                if "word_vad" in data:
                    return data, f"[OK] EmoBank VAD: {len(data['word_vad'])} entries"
                return None, "[WARN] EmoBank format invalid"
            except Exception:
                return None, "[WARN] EmoBank read failed"
        return None, "[INFO] EmoBank not found; keyword-only mode"

    def _load_benchmark(self, path="benchmark_corpus.json"):
        if os.path.exists(path):
            try:
                with open(path,"r",encoding="utf-8") as f:
                    data = json.load(f)
                if "ted_talks" in data or "american_rhetoric" in data:
                    return data, f"[OK] Benchmark loaded"
                return None, "[WARN] Benchmark format invalid"
            except Exception:
                return None, "[WARN] Benchmark read failed"
        return None, "[INFO] Benchmark not found"


class SmartAnalyzer:
    def __init__(self, base_corpus, emobank=None, scene="Academic Competition",
                 use_slang=True, use_vader=True, vader_weight=0.3):
        self.corpus = base_corpus
        self.emotion_dict = self.corpus["emotion_dict"]
        self.emotions = list(self.emotion_dict.keys())
        self.emobank = emobank
        self.scene = scene
        self.rules = self.corpus.get("scene_rules",{}).get(scene, DEFAULT_RULES)
        self.use_slang = use_slang
        self.use_vader = use_vader and VADER_AVAILABLE
        self.vader_weight = vader_weight
        self.vader = SentimentIntensityAnalyzer() if self.use_vader else None
        if self.use_slang:
            self._merge_slang()

    def _merge_slang(self):
        for emo, words in SLANG_DICT.items():
            if emo in self.emotion_dict:
                existing = set(w.lower() for w in self.emotion_dict[emo])
                for w in words:
                    if w.lower() not in existing:
                        self.emotion_dict[emo].append(w)

    def set_scene(self, scene):
        self.scene = scene
        self.rules = self.corpus.get("scene_rules",{}).get(scene, DEFAULT_RULES)

    def split_paragraphs(self, text):
        paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        return paras if paras else [text.strip()]

    def split_sentences(self, text):
        sents = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sents if s.strip()]

    def calc_vad(self, text):
        if self.emobank and "word_vad" in self.emobank:
            tokens = re.findall(r'[a-zA-Z]+', text.lower())
            v_list,a_list,d_list = [],[],[]
            for w in tokens:
                if w in self.emobank["word_vad"]:
                    vad = self.emobank["word_vad"][w]
                    v_list.append(vad["v"]); a_list.append(vad["a"]); d_list.append(vad["d"])
            if v_list:
                return {"v":round(sum(v_list)/len(v_list),2),"a":round(sum(a_list)/len(a_list),2),"d":round(sum(d_list)/len(d_list),2)}
        emo_score = sum(len([kw for kw in kws if kw.lower() in text.lower()]) for kws in self.emotion_dict.values())
        arousal = min(9.0, emo_score*1.2)
        pos = ["Affability","Passion","Deep Emotion","Humor","Conviction"]
        neg = ["Solemnity","Critical Thinking"]
        pos_c = sum(1 for e in pos if any(kw.lower() in text.lower() for kw in self.emotion_dict[e]))
        neg_c = sum(1 for e in neg if any(kw.lower() in text.lower() for kw in self.emotion_dict[e]))
        valence = max(1.0, min(9.0, 5.0+(pos_c-neg_c)*0.7))
        return {"v":round(valence,2),"a":round(arousal,2),"d":round(arousal*0.75,2)}

    def _negation_ctx(self, text_lower, kw_pos):
        prefix = text_lower[max(0,kw_pos-30):kw_pos]
        for w in re.findall(r'\b\w+\b', prefix)[-3:]:
            if w in NEGATION_WORDS: return True
        return False

    def _degree_mult(self, text_lower, kw_pos):
        prefix = text_lower[max(0,kw_pos-40):kw_pos]
        for adv,mult in DEGREE_ADVERBS.items():
            if adv in prefix:
                ap = prefix.rfind(adv)
                between = prefix[ap+len(adv):]
                if len(re.findall(r'\b\w+\b', between)) <= 3:
                    return mult
        return 1.0

    def detect_emotion(self, text):
        tl = text.lower()
        scores = {}
        hits = {}
        negated = {}
        for emo, keywords in self.emotion_dict.items():
            es = 0.0; h = []; ng = []
            for kw in keywords:
                kl = kw.lower()
                start = 0
                while True:
                    pos = tl.find(kl, start)
                    if pos == -1: break
                    is_neg = self._negation_ctx(tl, pos)
                    mult = self._degree_mult(tl, pos)
                    if is_neg:
                        ng.append(kw); es -= 0.5*mult
                    else:
                        h.append(kw); es += 1.0*mult
                    start = pos+len(kl)
            scores[emo] = round(es,2)
            hits[emo] = list(set(h))
            negated[emo] = list(set(ng))

        if self.use_vader and self.vader:
            vs = self.vader.polarity_scores(text)
            vader_pos = vs["pos"]; vader_neg = vs["neg"]; vader_neu = vs["neu"]
            vader_compound = vs["compound"]
            if vader_compound > 0.05:
                scores["Passion"] += vader_pos * 5 * self.vader_weight
                scores["Deep Emotion"] += vader_pos * 3 * self.vader_weight
                scores["Affability"] += vader_pos * 2 * self.vader_weight
            elif vader_compound < -0.05:
                scores["Solemnity"] += vader_neg * 5 * self.vader_weight
                scores["Critical Thinking"] += vader_neg * 2 * self.vader_weight
            if vader_neu > 0.7:
                scores["Composure"] += vader_neu * 2 * self.vader_weight

        max_s = max(scores.values())
        if max_s <= 0:
            dominant = "Neutral"; intensity = 0.0
        else:
            dominant = max(scores, key=scores.get)
            wc = max(1, len(re.findall(r'\b\w+\b', text)))
            density = max_s / wc * 100
            intensity = min(10.0, max_s*1.2 + density*0.25)

        mixed = []
        ss = sorted(scores.items(), key=lambda x:-x[1])
        if ss[0][1] > 0 and len(ss) > 1:
            for e,s in ss[1:]:
                if s > 0 and s >= ss[0][1]*0.5:
                    mixed.append(e)

        vad = self.calc_vad(text)
        vader_scores = {"pos":round(vs["pos"],3),"neg":round(vs["neg"],3),"neu":round(vs["neu"],3),"compound":round(vs["compound"],3)} if self.use_vader else None
        return {"dominant":dominant,"intensity":round(intensity,1),"scores":scores,"hit_keywords":hits,
                "negated_keywords":negated,"mixed_emotions":mixed,"vad":vad,"vader":vader_scores}

    def detect_rhetoric(self, text):
        tl = text.lower()
        devices = {}
        devices["rhetorical_questions"] = len(re.findall(r'[^\n]*\?\s*$', text, re.MULTILINE))
        words = re.findall(r'\b[a-zA-Z]{4,}\b', tl)
        wc = Counter(words)
        devices["repeated_words"] = {w:c for w,c in wc.items() if c >= 3}
        devices["triples"] = len(re.findall(r'\b\w+\s*,\s*\w+\s*,\s*(?:and\s+)?\w+\b', text))
        sents = self.split_sentences(text)
        anaphora = 0
        for i in range(len(sents)-1):
            w1 = re.findall(r'\b\w+\b', sents[i])
            w2 = re.findall(r'\b\w+\b', sents[i+1])
            if w1 and w2 and w1[0].lower()==w2[0].lower(): anaphora += 1
        devices["anaphora"] = anaphora
        devices["parallelism"] = len(re.findall(r'\b(to \w+[^,]*),\s*(to \w+[^,]*),\s*(to \w+)', text))
        emoji_pattern = re.compile("["u"\U0001F600-\U0001F64F"u"\U0001F300-\U0001F5FF"u"\U0001F680-\U0001F6FF"u"\U0001F1E0-\U0001F1FF""]+", flags=re.UNICODE)
        devices["emojis"] = len(emoji_pattern.findall(text))
        return devices

    def calc_readability(self, text):
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        wc = len(words)
        sents = self.split_sentences(text)
        sc = max(1, len(sents))
        syll = sum(self._count_syll(w) for w in words)
        syll_c = max(1, syll)
        fre = max(0, min(100, 206.835 - 1.015*(wc/sc) - 84.6*(syll_c/wc)))
        fkgl = 0.39*(wc/sc) + 11.8*(syll_c/wc) - 15.59
        level = "Very Easy (G5-6)" if fre>=80 else "Standard (G7-9)" if fre>=60 else "Difficult (G10-12)" if fre>=40 else "Very Difficult (College+)"
        return {"flesch_reading_ease":round(fre,1),"flesch_kincaid_grade":round(fkgl,1),"level":level,"avg_syllables_per_word":round(syll_c/wc,2)}

    def _count_syll(self, word):
        word = word.lower(); count = 0; vowels = "aeiouy"; prev = False
        for c in word:
            iv = c in vowels
            if iv and not prev: count += 1
            prev = iv
        if word.endswith("e") and count > 1: count -= 1
        return max(1, count)

    def analyze_structure(self, paragraphs):
        n = len(paragraphs)
        if n < 4:
            return {"opening":paragraphs[0:1] if n>=1 else [],"body_front":paragraphs[1:2] if n>=2 else [],
                    "body_back":paragraphs[2:3] if n>=3 else [],"ending":paragraphs[3:] if n>=4 else []}
        oe = max(1, int(n*0.15)); bfe = int(n*0.45); bbe = int(n*0.75)
        return {"opening":paragraphs[:oe],"body_front":paragraphs[oe:bfe],"body_back":paragraphs[bfe:bbe],"ending":paragraphs[bbe:]}

    def full_analysis(self, text):
        paragraphs = self.split_paragraphs(text)
        structure = self.analyze_structure(paragraphs)
        idx_map = {}
        cur = 0
        for part, paras in structure.items():
            idx_map[part] = (cur, cur+len(paras)); cur += len(paras)

        para_details = []
        for i, p in enumerate(paragraphs):
            detail = self.detect_emotion(p)
            sents = self.split_sentences(p)
            sent_details = [self.detect_emotion(s) for s in sents]
            part = "Unknown"
            for pn,(s,e) in idx_map.items():
                if s <= i < e: part = pn; break
            para_details.append({"index":i+1,"text":(p[:100]+"...") if len(p)>100 else p,"full_text":p,
                                 "part":part,"dominant":detail["dominant"],"intensity":detail["intensity"],
                                 "scores":detail["scores"],"hit_keywords":detail["hit_keywords"],
                                 "negated_keywords":detail["negated_keywords"],"mixed_emotions":detail["mixed_emotions"],
                                 "vad":detail["vad"],"vader":detail["vader"],"sentence_count":len(sents),
                                 "sentence_details":[{"text":s[:60],"dominant":sd["dominant"],"intensity":sd["intensity"]} for s,sd in zip(sents,sent_details)]})

        struc_emo = {}; struc_int = {}; struc_vad = {}
        for part, paras in structure.items():
            if not paras:
                struc_emo[part]="Neutral"; struc_int[part]=0.0; struc_vad[part]={"v":5.0,"a":0.0,"d":0.0}; continue
            el = [self.detect_emotion(p)["dominant"] for p in paras]
            il = [self.detect_emotion(p)["intensity"] for p in paras]
            vl = [self.calc_vad(p) for p in paras]
            struc_emo[part] = Counter(el).most_common(1)[0][0]
            struc_int[part] = round(sum(il)/len(il),1)
            struc_vad[part] = {"v":round(sum(v["v"] for v in vl)/len(vl),2),"a":round(sum(v["a"] for v in vl)/len(vl),2),"d":round(sum(v["d"] for v in vl)/len(vl),2)}

        il = [p["intensity"] for p in para_details]
        prog = self._eval_prog(il)
        diag = self._diagnosis(para_details, structure)
        total = self._total_score(struc_emo, prog, len(diag))
        basic = self._basic_info(text, paragraphs)
        rhetoric = self.detect_rhetoric(text)
        readability = self.calc_readability(text)
        shifts = self._detect_shifts(para_details)

        return {"basic_info":basic,"paragraphs":para_details,"structure_emotion":struc_emo,
                "structure_intensity":struc_int,"structure_vad":struc_vad,"progression_score":prog,
                "diagnosis":diag,"total_score":total,"total_paras":len(paragraphs),"vad_curve":self._vad_curve(paragraphs),
                "rhetorical_devices":rhetoric,"readability":readability,"emotional_shifts":shifts}

    def _basic_info(self, text, paragraphs):
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        wc = len(words)
        sents = self.split_sentences(text)
        sc = len(sents)
        return {"word_count":wc,"char_count":len(text),"para_count":len(paragraphs),"sentence_count":sc,
                "avg_sentence_length":round(wc/max(1,sc),1),"duration_min":round(wc/130.0,1),
                "first_person_sg":len(re.findall(r'\b(I|me|my|mine|myself)\b',text,re.I)),
                "first_person_pl":len(re.findall(r'\b(we|us|our|ours|ourselves)\b',text,re.I)),
                "second_person":len(re.findall(r'\b(you|your|yours|yourself|yourselves)\b',text,re.I)),
                "third_person":len(re.findall(r'\b(he|she|it|they|them|their|his|her|its)\b',text,re.I)),
                "lexical_diversity":round(len(set(w.lower() for w in words))/max(1,wc),3),
                "quotable_count":len([s for s in sents if 8<=len(re.findall(r'\b\w+\b',s))<=25 and (',' in s or ';' in s or ':' in s)]),
                "conjunction_density":round(len(re.findall(r'\b(and|but|or|so|yet|for|nor|because|although|however|therefore|moreover|furthermore|nevertheless|consequently)\b',text,re.I))/max(1,sc),2)}

    def _eval_prog(self, il):
        if len(il)<3: return 6.0
        n=len(il); ft=sum(il[:n//3])/max(1,n//3); lt=sum(il[-n//3:])/max(1,n//3)
        bs = 8.0 if lt>ft else 5.0
        mi=sum(il)/len(il); var=sum((x-mi)**2 for x in il)/len(il)
        if var<3: bs-=1.5
        elif var>20: bs-=0.5
        return round(min(10.0,max(0.0,bs)),1)

    def _diagnosis(self, para_details, structure):
        pn = {"opening":"Opening","body_front":"Body (Front)","body_back":"Body (Back)","ending":"Ending"}
        diag = []
        for part, paras in structure.items():
            if not paras: continue
            pp = [p for p in para_details if p["part"]==part]
            if not pp: continue
            de = Counter([p["dominant"] for p in pp]).most_common(2)
            ai = sum(p["intensity"] for p in pp)/len(pp)
            rule = self.rules[part]; expected = rule["expected"]; me = de[0][0]
            if me not in expected and me != "Neutral":
                sev = "Moderate" if part in ["opening","ending"] else "Mild"
                diag.append({"type":"Emotion Category Mismatch","part":pn[part],"severity":sev,
                             "current":f"Dominant: {me}","expected":f"Expected: {', '.join(expected)}",
                             "evidence":f"'{me}' detected in {pn[part]}; expected {', '.join(expected)}.",
                             "suggestion":f"Shift diction from '{me}' toward {'/'.join(expected)}."})
            if "max_intensity" in rule and ai > rule["max_intensity"]:
                diag.append({"type":"Excessive Intensity","part":pn[part],"severity":"Mild",
                             "current":f"Mean: {ai:.1f}/10","expected":f"<= {rule['max_intensity']}",
                             "evidence":f"Mean intensity {ai:.1f} exceeds ceiling {rule['max_intensity']}.",
                             "suggestion":"Reduce saturation; use declarative syntax and attenuate intensifiers."})
            if "min_intensity" in rule and ai < rule["min_intensity"]:
                diag.append({"type":"Insufficient Intensity","part":pn[part],"severity":"Moderate",
                             "current":f"Mean: {ai:.1f}/10","expected":f">= {rule['min_intensity']}",
                             "evidence":f"Mean intensity {ai:.1f} below floor {rule['min_intensity']}.",
                             "suggestion":"Amplify affective load via parallelism and intensifying adverbs."})
        return diag

    def _total_score(self, se, prog, pc):
        bs = 80.0 - pc*5.0 + prog*2.0
        return round(max(0.0,min(100.0,bs)),1)

    def _vad_curve(self, paragraphs):
        n=len(paragraphs); curve=[]
        for i,p in enumerate(paragraphs):
            v=self.calc_vad(p)
            curve.append({"position":round((i+1)/n,2),"v":v["v"],"a":v["a"],"d":v["d"]})
        return curve

    def _detect_shifts(self, pd):
        shifts=[]
        for i in range(len(pd)-1):
            c,nxt = pd[i],pd[i+1]
            if c["dominant"]!=nxt["dominant"] and c["dominant"]!="Neutral" and nxt["dominant"]!="Neutral":
                diff=abs(c["intensity"]-nxt["intensity"])
                if diff>=3:
                    shifts.append({"from_para":c["index"],"to_para":nxt["index"],"from_emotion":c["dominant"],
                                   "to_emotion":nxt["dominant"],"intensity_change":round(diff,1),
                                   "abruptness":"High" if diff>=5 else "Moderate"})
        return shifts


class AudioAnalyzer:
    ACOUSTIC_MAP = [
        {"name":"Passion","loudness":(0.6,1.0),"pitch_var":(0.4,1.0)},
        {"name":"Conviction","loudness":(0.5,0.8),"pitch_var":(0.1,0.4)},
        {"name":"Deep Emotion","loudness":(0.3,0.6),"pitch_var":(0.3,0.6)},
        {"name":"Affability","loudness":(0.2,0.5),"pitch_var":(0.2,0.5)},
        {"name":"Composure","loudness":(0.2,0.5),"pitch_var":(0.0,0.2)},
        {"name":"Solemnity","loudness":(0.1,0.4),"pitch_var":(0.0,0.2)},
        {"name":"Humor","loudness":(0.3,0.6),"pitch_var":(0.5,1.0)},
    ]

    def analyze(self, audio_bytes, sr=16000):
        try:
            import pydub
            audio_seg = pydub.AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio_seg = audio_seg.set_frame_rate(sr).set_channels(1)
            data = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            if audio_seg.sample_width == 2:
                data = data / 32768.0
            elif audio_seg.sample_width == 4:
                data = data / 2147483648.0
            elif audio_seg.sample_width == 1:
                data = (data - 128) / 128.0
        except ImportError:
            if not AUDIO_AVAILABLE:
                return {"error":"Install pydub: pip install pydub (requires ffmpeg)"}
            try:
                data, sr = sf.read(io.BytesIO(audio_bytes))
            except Exception as e:
                return {"error":f"Read failed: {e}"}
        except Exception as e:
            return {"error":f"Audio decode failed: {e}. Make sure ffmpeg is installed."}

        if len(data.shape)>1: data = np.mean(data,axis=1)
        duration = len(data)/sr
        frame_size = int(sr*0.5)
        frames = [data[i:i+frame_size] for i in range(0,len(data),frame_size)]
        results = []
        for i,frame in enumerate(frames):
            if len(frame)==0: continue
            rms = float(np.sqrt(np.mean(frame**2)))
            loudness = min(1.0, rms*8.0)
            zcr = float(np.sum(np.abs(np.diff(np.sign(frame))))/len(frame))
            pitch_var = min(1.0, zcr*20.0)
            emo, conf = self._classify(loudness, pitch_var)
            results.append({"time":round(i*0.5,2),"loudness":round(loudness,3),"pitch_var":round(pitch_var,3),
                            "emotion":emo,"confidence":round(conf,2)})
        return self._summary(results, duration, sr)

    def _classify(self, loudness, pitch_var):
        best_s=0.0; best_e="Neutral"
        for r in self.ACOUSTIC_MAP:
            if r["loudness"][0]<=loudness<=r["loudness"][1] and r["pitch_var"][0]<=pitch_var<=r["pitch_var"][1]:
                lc=(r["loudness"][0]+r["loudness"][1])/2; pc=(r["pitch_var"][0]+r["pitch_var"][1])/2
                s=1.0-abs(loudness-lc)*0.8-abs(pitch_var-pc)*0.6
                if s>best_s: best_s=s; best_e=r["name"]
        if loudness<0.05: best_e="Pause"; best_s=0.9
        return best_e, max(0.0,min(1.0,best_s))

    def _summary(self, results, duration, sr):
        if not results: return {"error":"No frames"}
        ec = Counter([c["emotion"] for c in results if c["emotion"]!="Pause"])
        main = ec.most_common(1)[0][0] if ec else "Neutral"
        ll = np.array([c["loudness"] for c in results])
        avg_l=float(np.mean(ll)); max_l=float(np.max(ll)); std_l=float(np.std(ll))
        n=len(results)
        sections = {"Opening":(0,int(n*0.15)),"Body (Front)":(int(n*0.15),int(n*0.45)),
                    "Body (Back)":(int(n*0.45),int(n*0.75)),"Ending":(int(n*0.75),n)}
        sec_res={}
        for name,(s,e) in sections.items():
            seg=results[s:e]
            if not seg: sec_res[name]={"dominant_emotion":"Neutral","avg_loudness":0.0}; continue
            se=Counter([c["emotion"] for c in seg if c["emotion"]!="Pause"])
            sec_res[name]={"dominant_emotion":se.most_common(1)[0][0] if se else "Neutral",
                           "avg_loudness":round(float(np.mean([c["loudness"] for c in seg])),3)}
        pause_ratio = sum(1 for c in results if c["emotion"]=="Pause")/len(results)
        score=75.0
        if 0.1<std_l<0.3: score+=8
        if 0.2<=avg_l<=0.6: score+=5
        if 0.05<=pause_ratio<=0.25: score+=5
        return {"duration_sec":round(duration,1),"sample_rate":sr,"main_emotion":main,
                "emotion_distribution":dict(ec),"avg_loudness":round(avg_l,3),"max_loudness":round(max_l,3),
                "loudness_variance":round(std_l,3),"pause_ratio":round(pause_ratio,3),
                "sections":sec_res,"total_score":round(min(100,max(0,score)),1),"frame_results":results}

LEARNED_FILE = "learned_words.json"

def load_local_learned(analyzer):
    if not os.path.exists(LEARNED_FILE):
        return 0
    try:
        with open(LEARNED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        existing = set()
        for words in analyzer.emotion_dict.values():
            existing.update(w.lower() for w in words)
        for item in data.get("words", []):
            w = item["word"].lower()
            if w not in existing:
                analyzer.emotion_dict.setdefault(item["emotion"], []).append(item["word"])
                existing.add(w)
                count += 1
        return count
    except Exception:
        return 0

def save_local_learned(word, emotion, confidence=0.5):
    try:
        if os.path.exists(LEARNED_FILE):
            with open(LEARNED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"words": [], "created": time.strftime("%Y-%m-%d %H:%M:%S")}
        existing_words = {item["word"].lower() for item in data["words"]}
        if word.lower() not in existing_words:
            data["words"].append({
                "word": word,
                "emotion": emotion,
                "confidence": confidence,
                "learned_at": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(LEARNED_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

CLASSICAL_CSS = """
<style>
.stApp{background:linear-gradient(135deg,#FAF6EE 0%,#F0E8D8 100%);font-family:'Georgia','Times New Roman',serif;}
.block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:1400px;}
div[data-testid="stHeader"]{background:linear-gradient(180deg,#5A1F26 0%,#3D1519 100%);height:60px;border-bottom:3px solid #C9A961;box-shadow:0 4px 12px rgba(0,0,0,0.3);}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#5A1F26 0%,#3D1519 100%);border-right:3px solid #C9A961;}
section[data-testid="stSidebar"] .stMarkdown,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] span,section[data-testid="stSidebar"] div{color:#F5E6C8!important;font-family:'Georgia',serif;}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3{color:#FFE9B0!important;font-family:'Georgia',serif;text-shadow:1px 1px 3px rgba(0,0,0,0.5);}
h1{color:#5A1F26!important;font-family:'Georgia',serif!important;font-weight:bold!important;text-align:center;letter-spacing:2px;padding-bottom:10px;border-bottom:2px solid #C9A961;}
h2{color:#5A1F26!important;font-family:'Georgia',serif!important;border-left:5px solid #C9A961;padding-left:12px;margin-top:1.5rem;font-weight:bold!important;}
h3{color:#3D1519!important;font-family:'Georgia',serif!important;font-style:italic;font-weight:bold!important;}
p,li,span,div{font-family:'Georgia','Times New Roman',serif;color:#1A0F0A;}
textarea{background-color:#FDFBF5!important;border:2px solid #C9A961!important;border-radius:6px!important;color:#1A0F0A!important;font-family:'Georgia',serif!important;font-size:15px!important;box-shadow:inset 0 2px 4px rgba(0,0,0,0.05);transition:all 0.3s ease;}
textarea:focus{border-color:#5A1F26!important;box-shadow:0 0 0 3px rgba(201,169,97,0.3)!important;}
.stButton>button{background:linear-gradient(180deg,#5A1F26 0%,#3D1519 100%)!important;color:#FFE9B0!important;font-family:'Georgia',serif!important;font-weight:bold!important;border:2px solid #C9A961!important;border-radius:6px!important;padding:0.55rem 1.3rem!important;letter-spacing:1px;box-shadow:0 3px 8px rgba(0,0,0,0.25);transition:all 0.25s cubic-bezier(0.4,0,0.2,1)!important;cursor:pointer;}
.stButton>button:hover{background:linear-gradient(180deg,#722F37 0%,#5A1F26 100%)!important;color:#FFFFFF!important;box-shadow:0 6px 16px rgba(90,31,38,0.5)!important;transform:translateY(-2px)!important;}
.stButton>button:active{transform:translateY(0)!important;box-shadow:0 2px 4px rgba(0,0,0,0.3)!important;}
.stButton>button p{color:#FFE9B0!important;}
.stSelectbox>div>div>select{background-color:#FDFBF5!important;border:2px solid #C9A961!important;color:#1A0F0A!important;font-family:'Georgia',serif!important;border-radius:4px;}
.stNumberInput input,.stTextInput input{background-color:#FDFBF5!important;border:2px solid #C9A961!important;color:#1A0F0A!important;font-family:'Georgia',serif!important;border-radius:4px;}
div[data-testid="stMetric"]{background:linear-gradient(135deg,#FDFBF5 0%,#F0E8D8 100%);border:2px solid #C9A961;border-radius:8px;padding:0.8rem;box-shadow:0 2px 8px rgba(0,0,0,0.1);transition:transform 0.2s ease;}
div[data-testid="stMetric"]:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.15);}
div[data-testid="stMetric"] label{color:#3D1519!important;font-family:'Georgia',serif!important;font-style:italic;font-weight:bold!important;font-size:0.9rem!important;}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{color:#5A1F26!important;font-family:'Georgia',serif!important;font-size:1.6rem!important;font-weight:bold;}
.stDataFrame{border:2px solid #C9A961;border-radius:6px;overflow:hidden;}
.stDataFrame th{background:linear-gradient(180deg,#5A1F26 0%,#3D1519 100%)!important;color:#FFE9B0!important;font-family:'Georgia',serif!important;font-weight:bold!important;}
.stDataFrame td{color:#1A0F0A!important;}
.stDataFrame tr:nth-child(even){background-color:#F0E8D8!important;}
.streamlit-expanderHeader{background:linear-gradient(180deg,#F0E8D8 0%,#E8DCC8 100%);border:1px solid #C9A961;border-radius:6px;font-family:'Georgia',serif!important;color:#5A1F26!important;font-weight:bold!important;transition:all 0.2s ease;}
.streamlit-expanderHeader:hover{background:linear-gradient(180deg,#E8DCC8 0%,#D4C5A9 100%);}
.streamlit-expanderContent{background-color:#FDFBF5;border:1px solid #C9A961;border-top:none;border-radius:0 0 6px 6px;}
.stSuccess{background:linear-gradient(135deg,#E8F5E9 0%,#C8E6C9 100%);border-left:5px solid #1B5E20;border-radius:6px;font-family:'Georgia',serif;}
.stSuccess p,.stSuccess div{color:#1B5E20!important;}
.stWarning{background:linear-gradient(135deg,#FFF8E1 0%,#FFECB3 100%);border-left:5px solid #E65100;border-radius:6px;font-family:'Georgia',serif;}
.stWarning p,.stWarning div{color:#E65100!important;}
.stInfo{background:linear-gradient(135deg,#E3F2FD 0%,#BBDEFB 100%);border-left:5px solid #0D47A1;border-radius:6px;font-family:'Georgia',serif;}
.stInfo p,.stInfo div{color:#0D47A1!important;}
.stError{background:linear-gradient(135deg,#FFEBEE 0%,#FFCDD2 100%);border-left:5px solid #B71C1C;border-radius:6px;font-family:'Georgia',serif;}
.stError p,.stError div{color:#B71C1C!important;}
pre{background-color:#FDFBF5!important;border:2px solid #C9A961!important;border-radius:6px!important;color:#1A0F0A!important;font-family:'Consolas',monospace!important;font-size:13px!important;}
hr{border:none;height:2px;background:linear-gradient(90deg,transparent 0%,#C9A961 50%,transparent 100%);margin:1.5rem 0;}
.stFileUploader{background-color:#FDFBF5;border:2px dashed #C9A961;border-radius:8px;padding:1rem;transition:all 0.2s ease;}
.stFileUploader:hover{border-color:#5A1F26;background-color:#FAF6EE;}
.stTabs [data-baseweb="tab-list"]{background:linear-gradient(180deg,#F0E8D8 0%,#E8DCC8 100%);border-bottom:3px solid #C9A961;gap:4px;border-radius:8px 8px 0 0;}
.stTabs [data-baseweb="tab"]{font-family:'Georgia',serif!important;color:#3D1519!important;font-weight:bold!important;padding:0.7rem 1.3rem!important;transition:all 0.2s ease;border-radius:6px 6px 0 0;}
.stTabs [data-baseweb="tab"]:hover{background:rgba(201,169,97,0.2);}
.stTabs [aria-selected="true"]{background:linear-gradient(180deg,#5A1F26 0%,#3D1519 100%)!important;color:#FFE9B0!important;}
.stTabs [aria-selected="true"] p{color:#FFE9B0!important;}
.stSlider > div > div > div {
    background-color: #E8DCC8 !important;
    height: 6px !important;
}
.stSlider > div > div > div > div {
    background-color: #5A1F26 !important;
    height: 6px !important;
}
.stSlider [data-testid="stThumbValue"] {
    color: #5A1F26 !important;
    font-weight: bold !important;
    font-size: 14px !important;
    background-color: #FFE9B0 !important;
    border: 2px solid #5A1F26 !important;
    border-radius: 50% !important;
    width: 28px !important;
    height: 28px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
}
.stSlider label {
    color: #3D1519 !important;
    font-weight: bold !important;
    font-size: 14px !important;
    font-family: 'Georgia', serif !important;
}
.stSlider p {
    color: #3D1519 !important;
    font-weight: bold !important;
}

footer{background:linear-gradient(180deg,#3D1519 0%,#5A1F26 100%);color:#FFE9B0!important;border-top:3px solid #C9A961;font-family:'Georgia',serif!important;padding:0.8rem!important;}
footer p,footer span,footer div{color:#FFE9B0!important;}
footer a{color:#F5E6C8!important;}
</style>
"""

st.set_page_config(page_title="Speech Optimizer — Classical Intelligence", page_icon="❦", layout="wide", initial_sidebar_state="expanded")
st.markdown(CLASSICAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:15px 0;">
    <div style="font-size:38px;color:#C9A961;">❦</div>
    <h1 style="border:none;margin:0;">SPEECH OPTIMIZER</h1>
    <p style="color:#5C4033;font-style:italic;font-size:15px;margin-top:6px;">— Intelligent Emotion Analysis · Classical Edition —</p>
    <div style="font-size:38px;color:#C9A961;">❦</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ❦ Analysis Settings")
    st.markdown("---")
    scene = st.selectbox("Speech Context", ["Academic Competition","Corporate Presentation","Commemorative Address"])
    st.markdown("---")
    st.markdown("#### ⚙ Intelligence Engine")
    use_slang = st.checkbox("Slang & Internet Lexicon", value=True, help="Enable LOL, LMAO, sus, mid, rizz etc.")
    use_vader = st.checkbox("VADER Sentiment AI", value=True, help="Neural-trained sentiment for social media text")
    vader_weight = st.slider("VADER Influence", 0.0, 1.0, 0.3, 0.05) if use_vader else 0.0
    st.markdown("---")
    st.markdown("#### 🎨 Report Detail")
    detail_level = st.radio("Granularity", ["Paragraph","Sentence","Word-level"], index=1)
    show_vader = st.checkbox("Show VADER Scores", value=True)
    show_keywords = st.checkbox("Show Hit Keywords", value=True)
    show_sentences = st.checkbox("Sentence Breakdown", value=True)
    st.markdown("---")
    st.markdown("#### 📊 Corpus Status")
    loader = CorpusLoader()
    st.caption(loader.base_status)
    st.caption(loader.emobank_status)
    st.caption(loader.benchmark_status)
    st.caption(f"VADER Engine: {'✅ Active' if VADER_AVAILABLE else '❌ Not installed'}")
    st.caption(f"Slang Lexicon: {'✅ 300+ terms' if use_slang else '⬜ Disabled'}")
    st.caption(f"Audio Engine: {'✅ Ready' if AUDIO_AVAILABLE else '❌ Not installed'}")
    local_count = 0
    if os.path.exists("learned_words.json"):
        try:
            with open("learned_words.json", "r", encoding="utf-8") as f:
                local_count = len(json.load(f).get("words", []))
        except Exception:
            pass
    st.caption(f"💾 Local Learned: {local_count} words (auto-saved)")
    st.markdown("---")
    st.markdown('<p style="text-align:center;color:#C9A961;font-style:italic;font-size:11px;">❦ Classical Intelligence Edition ❦</p>', unsafe_allow_html=True)


@st.cache_resource
def get_analyzer(scene, use_slang, use_vader, vader_weight):
    analyzer = SmartAnalyzer(loader.base_corpus, loader.emobank, scene, use_slang, use_vader, vader_weight)
    analyzer.original_dict = {emo: list(words) for emo, words in BUILTIN_CORPUS["emotion_dict"].items()}
    local_count = load_local_learned(analyzer)
    analyzer.local_learned_count = local_count
    return analyzer



analyzer = get_analyzer(scene, use_slang, use_vader, vader_weight)
audio_analyzer = AudioAnalyzer()

all_tabs = st.tabs(["  📜 Text Analysis  ", "  🎙 Recording Studio  ", "  🎵 Audio File  ", "  📋 Batch Analysis  ", "  🧠 Corpus Learning  "])
tab1, tab2, tab3, tab4, tab5 = all_tabs


with tab1:
    st.markdown("### ✒ Enter Your English Speech")
    text = st.text_area("", height=260, placeholder="Paste your English speech here... (supports slang, emojis, internet speech)", label_visibility="collapsed")

    cb1, cb2, cb3 = st.columns([1,1,4])
    with cb1: analyze_btn = st.button("✦ Analyze", use_container_width=True)
    with cb2:
        if st.button("✧ Clear", use_container_width=True): st.rerun()

    if analyze_btn and text.strip():
        with st.spinner("❦ Analyzing with intelligent engine..."):
            analysis = analyzer.full_analysis(text)
            basic = analysis["basic_info"]
            rhetoric = analysis["rhetorical_devices"]
            readability = analysis["readability"]

        st.markdown("---")
        st.markdown("### 📊 Composite Overview")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Score", f"{analysis['total_score']}/100")
        c2.metric("Grade", "Exceptional" if analysis['total_score']>=90 else "Proficient" if analysis['total_score']>=75 else "Developing" if analysis['total_score']>=60 else "Foundational")
        c3.metric("Words", basic["word_count"])
        c4.metric("Duration", f"{basic['duration_min']} min")
        c5,c6,c7,c8 = st.columns(4)
        c5.metric("Lexical Diversity", basic["lexical_diversity"])
        c6.metric("Quotable", basic["quotable_count"])
        c7.metric("Progression", f"{analysis['progression_score']}/10")
        c8.metric("Sentences", basic["sentence_count"])

        st.markdown("### 🧠 Emotional Architecture")
        for p in analysis["paragraphs"]:
            color = EMOTION_COLORS.get(p["dominant"], "#9E9E9E")
            with st.expander(f"📄 Paragraph {p['index']}  [{p['part']}]  —  {p['dominant']}  (Intensity: {p['intensity']}/10)", expanded=False):
                st.markdown(f"<div style='border-left:4px solid {color};padding-left:12px;color:{color};font-weight:bold;'>Dominant: {p['dominant']} | Intensity: {p['intensity']}/10</div>", unsafe_allow_html=True)
                st.caption(p["text"])
                if p["mixed_emotions"]:
                    st.info(f"Mixed emotions: {', '.join(p['mixed_emotions'])}")
                if show_vader and p["vader"]:
                    v = p["vader"]
                    st.caption(f"VADER → Positive:{v['pos']} Negative:{v['neg']} Neutral:{v['neu']} Compound:{v['compound']}")
                if show_keywords:
                    all_hits = []
                    for emo,kws in p["hit_keywords"].items():
                        if kws: all_hits.append(f"**{emo}**: {', '.join(kws[:8])}")
                    if all_hits: st.markdown("🔑 " + " | ".join(all_hits))
                    all_neg = [kw for kws in p["negated_keywords"].values() for kw in kws]
                    if all_neg: st.warning(f"Negated terms: {', '.join(all_neg[:5])}")
                if show_sentences and p["sentence_details"]:
                    st.markdown("**Sentence-by-sentence:**")
                    for sd in p["sentence_details"]:
                        sc = EMOTION_COLORS.get(sd["dominant"],"#999")
                        st.markdown(f"<span style='color:{sc};'>●</span> [{sd['dominant']} {sd['intensity']}/10] {sd['text']}", unsafe_allow_html=True)

        st.markdown("### 🏗 Structural Emotion Map")
        for part in ["opening","body_front","body_back","ending"]:
            emo = analysis["structure_emotion"][part]
            intens = analysis["structure_intensity"][part]
            color = EMOTION_COLORS.get(emo,"#999")
            bar_len = int(intens * 10)
            st.markdown(f"**{part.title()}**: <span style='color:{color};font-weight:bold;'>{emo}</span> | Intensity: {'█'*bar_len}{'░'*(100-bar_len)} {intens}/10", unsafe_allow_html=True)

        st.markdown("### 🔍 Diagnostic Findings")
        if analysis["diagnosis"]:
            for d in analysis["diagnosis"]:
                sev_color = "#C62828" if d["severity"]=="Moderate" else "#E65100"
                with st.expander(f"⚠ {d['part']} — {d['type']} [{d['severity']}]"):
                    st.markdown(f"**Evidence:** {d['evidence']}")
                    st.markdown(f"**Current:** {d['current']}")
                    st.markdown(f"**Expected:** {d['expected']}")
                    st.success(f"💡 {d['suggestion']}")
        else:
            st.success("❦ No affective misalignments detected!")

        st.markdown("### 🎭 Rhetorical Devices")
        r1,r2,r3,r4,r5 = st.columns(5)
        r1.metric("Rhetorical Q", rhetoric["rhetorical_questions"])
        r2.metric("Anaphora", rhetoric["anaphora"])
        r3.metric("Triples", rhetoric["triples"])
        r4.metric("Parallelism", rhetoric["parallelism"])
        r5.metric("Emojis", rhetoric.get("emojis",0))

        st.markdown("### 📈 Emotional Shifts")
        if analysis["emotional_shifts"]:
            for s in analysis["emotional_shifts"]:
                st.warning(f"Para {s['from_para']}→{s['to_para']}: {s['from_emotion']} → {s['to_emotion']} (Δ{s['intensity_change']}, {s['abruptness']})")
        else:
            st.info("No abrupt emotional shifts detected.")

        st.markdown("### 📖 Readability")
        rb1,rb2,rb3 = st.columns(3)
        rb1.metric("Flesch Ease", readability["flesch_reading_ease"])
        rb2.metric("Grade Level", readability["flesch_kincaid_grade"])
        rb3.metric("Difficulty", readability["level"])
        if auto_learn if 'auto_learn' in dir() else True:
            tokens = re.findall(r'[a-zA-Z]+', text.lower())
            all_known = set()
            for words in analyzer.emotion_dict.values():
                all_known.update(w.lower() for w in words)
            all_known.update(NEGATION_WORDS)
            new_found = [w for w in set(tokens) if len(w)>=3 and w not in all_known]
            if new_found:
                st.caption(f"🧠 Auto-learning discovered {len(new_found)} potential new words — review them in the Corpus Learning tab.")

with tab2:
    st.markdown("### 🎙 Professional Recording Studio")
    st.caption("AU-style acoustic analysis · waveform · spectrum · emotion mapping")

    if RECORDER_AVAILABLE:
        col_rec1, col_rec2 = st.columns([1, 2])

        with col_rec1:
            st.markdown("#### 🎤 Record")
            audio = audiorecorder("● Click to Record", "■ Stop Recording")

            if len(audio) > 0:
                st.audio(audio.export().read(), format="audio/wav")

                try:
                    import pydub
                    seg = pydub.AudioSegment.from_file(io.BytesIO(audio.export().read()))
                    samples = np.array(seg.get_array_of_samples())
                    if seg.channels == 2:
                        samples = samples.reshape((-1, 2)).mean(axis=1)
                    sr = seg.frame_rate
                    duration = len(samples) / sr
                    samples_float = samples.astype(np.float32) / 32768.0
                except Exception as e:
                    st.error(f"Audio decode error: {e}")
                    samples_float = np.array([])
                    sr = 16000
                    duration = 0

                if len(samples_float) > 0:
                    st.markdown("#### 📊 Audio Parameters")
                    p1, p2 = st.columns(2)
                    p1.metric("Duration", f"{duration:.2f}s")
                    p2.metric("Sample Rate", f"{sr} Hz")
                    p3, p4 = st.columns(2)
                    p3.metric("Channels", "Mono" if seg.channels == 1 else "Stereo")
                    p4.metric("Peak Amp", f"{np.max(np.abs(samples_float)):.3f}")
                    p5, p6 = st.columns(2)
                    p5.metric("RMS Level", f"{np.sqrt(np.mean(samples_float**2)):.3f}")
                    p6.metric("Zero Crossings", f"{np.sum(np.abs(np.diff(np.sign(samples_float))))}")

        with col_rec2:
            if len(audio) > 0 and len(samples_float) > 0:
                st.markdown("#### 📈 Waveform (Time Domain)")
                fig_wave, ax_wave = plt.subplots(figsize=(10, 2.5), dpi=100)
                times = np.linspace(0, duration, len(samples_float))
                ax_wave.plot(times, samples_float, color="#5A1F26", linewidth=0.5, alpha=0.8)
                ax_wave.fill_between(times, samples_float, 0, color="#C9A961", alpha=0.3)
                ax_wave.set_facecolor("#FDFBF5")
                ax_wave.set_xlabel("Time (s)", color="#3D1519", fontsize=9)
                ax_wave.set_ylabel("Amplitude", color="#3D1519", fontsize=9)
                ax_wave.set_title("Audio Waveform", color="#5A1F26", fontsize=11, fontweight="bold")
                ax_wave.tick_params(colors="#5C4033", labelsize=8)
                for spine in ax_wave.spines.values():
                    spine.set_color("#C9A961")
                ax_wave.set_xlim(0, duration)
                fig_wave.tight_layout()
                st.pyplot(fig_wave)
                plt.close(fig_wave)

                st.markdown("#### 🎚 Spectrum (Frequency Domain)")
                fig_spec, ax_spec = plt.subplots(figsize=(10, 2.5), dpi=100)
                n_fft = min(2048, len(samples_float))
                freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
                spectrum = np.abs(np.fft.rfft(samples_float[:n_fft]))
                spectrum_db = 20 * np.log10(spectrum / np.max(spectrum) + 1e-10)
                ax_spec.plot(freqs, spectrum_db, color="#722F37", linewidth=0.8)
                ax_spec.fill_between(freqs, spectrum_db, -100, color="#C9A961", alpha=0.25)
                ax_spec.set_facecolor("#FDFBF5")
                ax_spec.set_xlabel("Frequency (Hz)", color="#3D1519", fontsize=9)
                ax_spec.set_ylabel("Level (dB)", color="#3D1519", fontsize=9)
                ax_spec.set_title("Frequency Spectrum", color="#5A1F26", fontsize=11, fontweight="bold")
                ax_spec.tick_params(colors="#5C4033", labelsize=8)
                for spine in ax_spec.spines.values():
                    spine.set_color("#C9A961")
                ax_spec.set_xlim(0, min(8000, sr / 2))
                ax_spec.set_ylim(-100, 5)
                fig_spec.tight_layout()
                st.pyplot(fig_spec)
                plt.close(fig_spec)

                st.markdown("#### 📉 Spectrogram")
                fig_sg, ax_sg = plt.subplots(figsize=(10, 2.5), dpi=100)
                Pxx, freqs_sg, bins, im = ax_sg.specgram(
                    samples_float, NFFT=1024, Fs=sr, noverlap=512,
                    cmap="YlOrRd", vmin=-40, vmax=0
                )
                ax_sg.set_facecolor("#FDFBF5")
                ax_sg.set_xlabel("Time (s)", color="#3D1519", fontsize=9)
                ax_sg.set_ylabel("Freq (Hz)", color="#3D1519", fontsize=9)
                ax_sg.set_title("Spectrogram", color="#5A1F26", fontsize=11, fontweight="bold")
                ax_sg.tick_params(colors="#5C4033", labelsize=8)
                ax_sg.set_ylim(0, min(8000, sr / 2))
                cbar = fig_sg.colorbar(im, ax=ax_sg)
                cbar.set_label("dB", color="#3D1519", fontsize=8)
                cbar.ax.tick_params(colors="#5C4033", labelsize=7)
                fig_sg.tight_layout()
                st.pyplot(fig_sg)
                plt.close(fig_sg)

        if len(audio) > 0 and len(samples_float) > 0:
            st.markdown("---")
            if st.button("✦ Analyze Acoustic Emotion", use_container_width=True, type="primary"):
                with st.spinner("❦ Analyzing acoustic features..."):
                    result = audio_analyzer.analyze(audio.export().read())

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown("#### 🧠 Acoustic Emotion Analysis")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Duration", f"{result['duration_sec']}s")
                    m2.metric("Dominant", result["main_emotion"])
                    m3.metric("Score", f"{result['total_score']}/100")
                    m4.metric("Pause Ratio", f"{result['pause_ratio']:.1%}")

                    m5, m6, m7 = st.columns(3)
                    m5.metric("Avg Loudness", result["avg_loudness"])
                    m6.metric("Peak Loudness", result["max_loudness"])
                    m7.metric("Dynamics (std)", result["loudness_variance"])

                    st.markdown("##### Emotion Distribution")
                    ed_col1, ed_col2 = st.columns([1, 1])
                    with ed_col1:
                        fig_emo, ax_emo = plt.subplots(figsize=(5, 3), dpi=100)
                        emos = list(result["emotion_distribution"].keys())
                        counts = list(result["emotion_distribution"].values())
                        colors = [EMOTION_COLORS.get(e, "#999") for e in emos]
                        bars = ax_emo.barh(emos, counts, color=colors, edgecolor="#C9A961")
                        ax_emo.set_facecolor("#FDFBF5")
                        ax_emo.set_xlabel("Frames", color="#3D1519", fontsize=9)
                        ax_emo.set_title("Emotion Distribution", color="#5A1F26", fontsize=11, fontweight="bold")
                        ax_emo.tick_params(colors="#5C4033", labelsize=8)
                        for spine in ax_emo.spines.values():
                            spine.set_color("#C9A961")
                        fig_emo.tight_layout()
                        st.pyplot(fig_emo)
                        plt.close(fig_emo)

                    with ed_col2:
                        st.markdown("##### Structural Analysis")
                        for seg, info in result["sections"].items():
                            color = EMOTION_COLORS.get(info["dominant_emotion"], "#999")
                            st.markdown(
                                f"<div style='padding:6px 10px;margin:3px 0;border-left:4px solid {color};"
                                f"background:#FDFBF5;border-radius:4px;'>"
                                f"<b>{seg}</b>: <span style='color:{color};font-weight:bold;'>{info['dominant_emotion']}</span> "
                                f"| Loudness: {info['avg_loudness']}</div>",
                                unsafe_allow_html=True
                            )

                    st.markdown("##### Loudness Over Time")
                    fig_lt, ax_lt = plt.subplots(figsize=(10, 2), dpi=100)
                    times_f = [f["time"] for f in result["frame_results"]]
                    louds = [f["loudness"] for f in result["frame_results"]]
                    pitches = [f["pitch_var"] for f in result["frame_results"]]
                    ax_lt.plot(times_f, louds, color="#5A1F26", linewidth=1.2, label="Loudness")
                    ax_lt.plot(times_f, pitches, color="#C9A961", linewidth=1.2, label="Pitch Variation")
                    ax_lt.set_facecolor("#FDFBF5")
                    ax_lt.set_xlabel("Time (s)", color="#3D1519", fontsize=9)
                    ax_lt.set_ylabel("Level", color="#3D1519", fontsize=9)
                    ax_lt.set_title("Loudness & Pitch Curve", color="#5A1F26", fontsize=11, fontweight="bold")
                    ax_lt.tick_params(colors="#5C4033", labelsize=8)
                    for spine in ax_lt.spines.values():
                        spine.set_color("#C9A961")
                    ax_lt.legend(fontsize=8, facecolor="#FDFBF5", edgecolor="#C9A961")
                    fig_lt.tight_layout()
                    st.pyplot(fig_lt)
                    plt.close(fig_lt)

                    if ASR_AVAILABLE:
                        st.markdown("---")
                        st.markdown("##### 📝 Transcribe to Text (Optional)")
                        if st.button("Transcribe with ASR (Google API)"):
                            with st.spinner("Transcribing..."):
                                try:
                                    r = sr.Recognizer()
                                    with sr.AudioFile(io.BytesIO(audio.export().read())) as source:
                                        ad = r.record(source)
                                    txt = r.recognize_google(ad, language="en-US")
                                    st.success("Transcription complete!")
                                    st.text_area("Transcribed text:", txt, height=100)
                                    st.info("Copy this text to the Text Analysis tab for full emotion analysis.")
                                except Exception as e:
                                    st.error(f"Transcription failed: {e}")
    else:
        st.error("streamlit-audiorecorder not installed. Run: pip install streamlit-audiorecorder")
        st.code("pip install streamlit-audiorecorder pydub")

with tab3:
    st.markdown("### 🎵 Upload Audio File")
    st.info("Upload a .wav or .mp3 file for acoustic emotion analysis.")
    up = st.file_uploader("Choose audio file", type=["wav","mp3","ogg","flac","m4a","aac","wma"])
    if up is not None:
        st.audio(up, format="audio/wav")
        if st.button("✦ Analyze Audio File", use_container_width=True):
            with st.spinner("❦ Analyzing..."):
                result = audio_analyzer.analyze(up.read())
            if "error" in result:
                st.error(result["error"])
            else:
                st.markdown("---")
                m1,m2,m3,m4 = st.columns(4)
                m1.metric("Duration", f"{result['duration_sec']}s")
                m2.metric("Dominant", result["main_emotion"])
                m3.metric("Score", f"{result['total_score']}/100")
                m4.metric("Pause Ratio", f"{result['pause_ratio']:.1%}")
                st.markdown("#### Emotion Distribution")
                for emo,cnt in sorted(result["emotion_distribution"].items(), key=lambda x:-x[1]):
                    color = EMOTION_COLORS.get(emo,"#999")
                    pct = cnt/sum(result["emotion_distribution"].values())*100
                    st.markdown(f"<span style='color:{color};'>●</span> **{emo}**: {'█'*int(pct/5)} {pct:.1f}%", unsafe_allow_html=True)
                st.markdown("#### Structural Analysis")
                for seg,info in result["sections"].items():
                    st.markdown(f"**{seg}**: {info['dominant_emotion']} (loudness: {info['avg_loudness']})")

with tab4:
    st.markdown("### 📂 Batch Analysis")
    files = st.file_uploader("Upload multiple .txt files", type=["txt"], accept_multiple_files=True)
    if files and st.button("✦ Run Batch Analysis", use_container_width=True):
        results = []
        prog = st.progress(0)
        for idx,f in enumerate(files):
            t = f.read().decode("utf-8")
            a = analyzer.full_analysis(t)
            results.append({"File":f.name,"Score":a["total_score"],"Words":a["basic_info"]["word_count"],
                            "Opening":a["structure_emotion"]["opening"],"Ending":a["structure_emotion"]["ending"],
                            "Quotable":a["basic_info"]["quotable_count"],"Findings":len(a["diagnosis"]),
                            "Primary":a["diagnosis"][0]["type"] if a["diagnosis"] else "None"})
            prog.progress((idx+1)/len(files))
        st.success(f"❦ Analyzed {len(results)} speeches!")
        st.dataframe(results, use_container_width=True, hide_index=True)
        if results:
            df = pd.DataFrame(results)
            st.download_button("❖ Export CSV", df.to_csv(index=False).encode("utf-8-sig"),
                               "batch_report.csv","text/csv",use_container_width=True)
tab5 = st.tabs(["  🧠 Corpus Learning  "])[0]

with tab5:
    st.markdown("### 🧠 Self-Learning Corpus Center")
    st.info("This module automatically discovers new words from analyzed speeches, infers their emotional polarity, and lets you approve them into the lexicon.")

    if "pending_words" not in st.session_state:
        st.session_state.pending_words = []
    if "learned_history" not in st.session_state:
        st.session_state.learned_history = []
        if os.path.exists(LEARNED_FILE):
            os.remove(LEARNED_FILE)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Current Lexicon", sum(len(v) for v in analyzer.emotion_dict.values()))
    with col_b:
        st.metric("Pending Review", len(st.session_state.pending_words))
    with col_c:
        st.metric("Total Learned", len(st.session_state.learned_history))

    st.markdown("---")
    st.markdown("#### 🔍 Discover New Words from Text")
    learn_text = st.text_area("Paste a speech to scan for new vocabulary:", height=120,
                              placeholder="The algorithm will extract words not in the current lexicon and estimate their emotional category...",
                              key="learn_input")
    auto_threshold = st.slider("Auto-approval confidence threshold", 0.5, 0.95, 0.75, 0.05,
                               help="Words above this confidence are auto-approved; below go to manual review.")

    if st.button("✦ Scan & Learn", use_container_width=True, key="scan_learn"):
        if learn_text.strip():
            with st.spinner("Scanning for new vocabulary..."):
                tokens = re.findall(r'[a-zA-Z]+', learn_text.lower())
                all_known = set()
                for words in analyzer.emotion_dict.values():
                    all_known.update(w.lower() for w in words)
                all_known.update(NEGATION_WORDS)
                all_known.update(w.lower() for w in DEGREE_ADVERBS.keys())

                token_freq = Counter(tokens)
                new_candidates = []
                vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None

                for word, freq in token_freq.most_common(100):
                    if len(word) < 3 or word in all_known:
                        continue
                    if word in {"the","and","for","are","but","not","you","all","any","can","had","her","was","one","our","out","day","get","has","him","his","how","man","new","now","old","see","two","way","who","boy","did","its","let","put","say","she","too","use","dad","mom","etc","per","via"}:
                        continue

                    context_window = []
                    words_list = learn_text.lower().split()
                    for i, w in enumerate(words_list):
                        if w == word:
                            start = max(0, i-5)
                            end = min(len(words_list), i+6)
                            context_window.extend(words_list[start:end])
                    context_str = " ".join(context_window)

                    vader_score = vader_analyzer.polarity_scores(context_str) if vader_analyzer else {"compound":0,"pos":0,"neg":0,"neu":1}

                    emo_scores = {}
                    for emo, keywords in analyzer.emotion_dict.items():
                        cooccur = sum(1 for kw in keywords if kw.lower() in context_str)
                        emo_scores[emo] = cooccur

                    if vader_score["compound"] > 0.1:
                        emo_scores["Passion"] += vader_score["pos"] * 3
                        emo_scores["Deep Emotion"] += vader_score["pos"] * 2
                        emo_scores["Affability"] += vader_score["pos"] * 2
                        emo_scores["Humor"] += vader_score["pos"] * 1.5
                    elif vader_score["compound"] < -0.1:
                        emo_scores["Solemnity"] += vader_score["neg"] * 4
                        emo_scores["Critical Thinking"] += vader_score["neg"] * 1.5

                    if emo_scores:
                        best_emo = max(emo_scores, key=emo_scores.get)
                        best_score = emo_scores[best_emo]
                        total = sum(emo_scores.values())
                        confidence = round(best_score / total, 2) if total > 0 else 0.3
                        confidence = min(0.95, confidence + (vader_score["pos"] + vader_score["neg"]) * 0.2)

                        if confidence >= 0.2:
                            new_candidates.append({
                                "word": word,
                                "frequency": freq,
                                "inferred_emotion": best_emo,
                                "confidence": round(confidence, 2),
                                "vader_compound": round(vader_score["compound"], 3),
                                "context": context_str[:120] + "..." if len(context_str) > 120 else context_str,
                                "status": "auto-approved" if confidence >= auto_threshold else "pending"
                            })

                auto_approved = [c for c in new_candidates if c["status"] == "auto-approved"]
                pending = [c for c in new_candidates if c["status"] == "pending"]

                all_existing = set()
                for words in analyzer.emotion_dict.values():
                    all_existing.update(w.lower() for w in words)
                for c in auto_approved:
                    if c["word"].lower() not in all_existing:
                        analyzer.emotion_dict.setdefault(c["inferred_emotion"], []).append(c["word"])
                        all_existing.add(c["word"].lower())
                        st.session_state.learned_history.append(c)
                        save_local_learned(c["word"], c["inferred_emotion"], c["confidence"])


                st.session_state.pending_words.extend(pending)
                st.session_state.pending_words = list({c["word"]: c for c in st.session_state.pending_words}.values())

                st.success(f"✅ Scanned! Discovered {len(new_candidates)} new words. Auto-approved: {len(auto_approved)}, Pending review: {len(pending)}")

                if auto_approved:
                    st.markdown("#### ✨ Auto-Approved Words")
                    for c in auto_approved[:15]:
                        color = EMOTION_COLORS.get(c["inferred_emotion"], "#999")
                        st.markdown(f"<span style='color:{color};'>●</span> **{c['word']}** → {c['inferred_emotion']} (confidence: {c['confidence']})", unsafe_allow_html=True)
        else:
            st.warning("Please enter some text to scan.")

    st.markdown("---")
    st.markdown("#### 📝 Pending Review Queue")

    if st.session_state.pending_words:
        for idx, c in enumerate(st.session_state.pending_words):
            with st.expander(f"🔤 {c['word']}  →  inferred: {c['inferred_emotion']}  (confidence: {c['confidence']})"):
                st.caption(f"Context: \"{c['context']}\"")
                st.caption(f"Frequency: {c['frequency']} | VADER compound: {c['vader_compound']}")
                col_e, col_f, col_g = st.columns([2,1,1])
                with col_e:
                    corrected_emo = st.selectbox("Assign emotion:",
                                                 list(analyzer.emotion_dict.keys()),
                                                 index=list(analyzer.emotion_dict.keys()).index(c["inferred_emotion"])
                                                 if c["inferred_emotion"] in analyzer.emotion_dict else 0,
                                                 key=f"emo_{idx}")
                with col_f:
                    if st.button("✅ Approve", key=f"approve_{idx}", use_container_width=True):
                        all_existing = set()
                        for words in analyzer.emotion_dict.values():
                            all_existing.update(w.lower() for w in words)
                        if c["word"].lower() not in all_existing:
                            analyzer.emotion_dict.setdefault(corrected_emo, []).append(c["word"])
                            c["inferred_emotion"] = corrected_emo
                            c["status"] = "approved"
                            st.session_state.learned_history.append(c)
                            save_local_learned(c["word"], corrected_emo, c["confidence"])

                            c["inferred_emotion"] = corrected_emo
                            c["status"] = "approved"
                            st.session_state.learned_history.append(c)
                        st.session_state.pending_words.pop(idx)
                        st.rerun()
                with col_g:
                    if st.button("❌ Reject", key=f"reject_{idx}", use_container_width=True):
                        st.session_state.pending_words.pop(idx)
                        st.rerun()
    else:
        st.info("No pending words. Analyze some speeches to discover new vocabulary.")

    st.markdown("#### 📚 Learning History")
    if st.session_state.learned_history:
        col_hist1, col_hist2 = st.columns([3, 1])
        with col_hist1:
            st.caption(f"Total: {len(st.session_state.learned_history)} words learned")
        with col_hist2:
            if st.button("🗑 Clear All History", use_container_width=True):
                st.session_state.learned_history = []
                st.rerun()

        hist_df = pd.DataFrame(st.session_state.learned_history)
        display_cols = ["word", "inferred_emotion", "confidence", "frequency", "status"]
        available_cols = [c for c in display_cols if c in hist_df.columns]
        st.dataframe(hist_df[available_cols], use_container_width=True, hide_index=True)

        st.markdown("##### Delete Single Entry")
        word_options = [f"{i + 1}. {item['word']} → {item['inferred_emotion']}"
                        for i, item in enumerate(st.session_state.learned_history)]
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            selected_idx = st.selectbox("Select entry to delete:",
                                        range(len(word_options)),
                                        format_func=lambda x: word_options[x],
                                        key="delete_hist_select")
        with col_del2:
            if st.button("🗑 Delete", use_container_width=True, key="delete_hist_btn"):
                removed = st.session_state.learned_history.pop(selected_idx)
                st.success(f"Deleted: {removed['word']}")
                st.rerun()
    else:
        st.info("No words learned yet. Analyze some speeches to discover new vocabulary.")

    st.markdown("---")
    st.markdown("#### 💾 Export Updated Lexicon")
    st.caption("Download the updated emotion_corpus.json to permanently save your learned words.")
    if st.button("📥 Export emotion_corpus.json", use_container_width=True):
        seen = set()
        deduped_dict = {}
        for emo, words in analyzer.emotion_dict.items():
            unique_words = []
            for w in words:
                if w.lower() not in seen:
                    seen.add(w.lower())
                    unique_words.append(w)
            deduped_dict[emo] = unique_words

        export_data = {
            "corpus_info": {
                "name": "Self-Learning English Emotion Lexicon",
                "version": "2.0",
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_words": sum(len(v) for v in deduped_dict.values()),
                "learned_words": len(st.session_state.learned_history)
            },
            "emotion_dict": deduped_dict,
            "structure_rule": BUILTIN_CORPUS["scene_rules"]
        }
        st.download_button("⬇ Download emotion_corpus.json",
                           data=json.dumps(export_data, indent=2, ensure_ascii=False).encode("utf-8"),
                           file_name="emotion_corpus.json",
                           mime="application/json",
                           use_container_width=True)

    st.markdown("---")

    st.markdown("---")
    st.markdown("#### ⚠ Reset Lexicon")
    st.warning("This will remove ALL learned words and restore the original built-in lexicon. This action cannot be undone.")
    col_reset1, col_reset2 = st.columns(2)
    with col_reset1:
        confirm_reset = st.checkbox("I understand, reset the lexicon")
    with col_reset2:
        if confirm_reset and st.button("🔄 Reset to Original", use_container_width=True, type="primary"):
            analyzer.emotion_dict = {emo: list(words) for emo, words in analyzer.original_dict.items()}
            if use_slang:
                for emo, words in SLANG_DICT.items():
                    existing = set(w.lower() for w in analyzer.emotion_dict.get(emo, []))
                    for w in words:
                        if w.lower() not in existing:
                            analyzer.emotion_dict.setdefault(emo, []).append(w)
            st.session_state.pending_words = []
            st.session_state.learned_history = []
            st.success("✅ Lexicon reset to original state!")
            st.rerun()

    st.markdown("#### ⚙ Learning Settings")
    col_h, col_i = st.columns(2)
    with col_h:
        auto_learn = st.checkbox("Auto-learn from every analysis", value=True,
                                 help="Automatically scan every speech analyzed in the Text Analysis tab for new words.")
    with col_i:
        min_word_len = st.number_input("Minimum word length to learn", 2, 10, 3)

st.markdown("---")
st.markdown('<p style="text-align:center;color:#5C4033;font-style:italic;font-size:12px;">❦ Speech Optimizer Pro · Classical Intelligence Edition · VADER + Slang + Acoustic ❦</p>', unsafe_allow_html=True)
