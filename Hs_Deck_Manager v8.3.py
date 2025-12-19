# -*- coding: utf-8 -*-
# hs_deck_manager.py - Ultimate Deck Manager + AI Assistant + Meta Analytics
# Wersjonowanie: każda modyfikacja pliku zwiększa numer niżej. Duże zmiany -> version.N, małe -> version.N.x
__version__ = "version.8.3.2"
__author__ = "by Xan"

import os, io, sys, ui, clipboard, json, re, datetime, console, photos, base64, unicodedata, webbrowser, glob, shutil
from collections import Counter, defaultdict
import random

# matplotlib (opcjonalnie)
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

DOCS_DIR  = os.path.expanduser('~/Documents')
DB_PATH   = os.path.join(DOCS_DIR, 'hs_decks.json')
SESS_PATH = os.path.join(DOCS_DIR, 'hs_sessions.json')
BG_FILE   = os.path.join(DOCS_DIR, 'hearthstone_bg.png')
BACKUP_DIR= os.path.join(DOCS_DIR, 'HS_Backups')
CACHE_DIR = os.path.join(DOCS_DIR, 'HS_Cache')
META_PATH = os.path.join(DOCS_DIR, 'hs_meta.json')

HS_CLASSES = ['Wszystkie','Druid','Łowca','Mag','Paladyn','Kapłan','Łotr','Szaman','Czarnoksiężnik','Wojownik','Rycerz śmierci','Łowca demonów']
CLASS_ICONS = {'Wszystkie':'📚','Druid':'🌿','Łowca':'🏹','Mag':'🪄','Paladyn':'🛡️','Kapłan':'✝️','Łotr':'🗡️','Szaman':'🌀','Czarnoksiężnik':'🧪','Wojownik':'⚔️','Rycerz śmierci':'💀','Łowca demonów':'🩸'}

# Rozszerzone tagi archetypów
ARCH_TAGS = {
    'reno':'highlander','highlander':'highlander','xl':'highlander','40':'highlander','renathal':'highlander',
    'quest':'quest','questline':'quest','secrets':'secret','secret':'secret',
    'mech':'mech','murloc':'murloc','pirate':'pirate','totem':'totem','undead':'undead','elemental':'elemental','dragon':'dragon','beast':'beast','demon':'demon',
    'deathrattle':'deathrattle','egg':'deathrattle','relic':'relic','spell':'spell','minion':'minion',
    'aggro':'aggro','tempo':'tempo','midrange':'midrange','control':'control','combo':'combo','otk':'combo',
    'thief':'thief','discover':'discover','value':'value','mill':'mill','fatigue':'fatigue',
    'even':'even','odd':'odd','budget':'budget','premium':'premium'
}

# Rozbudowana baza kart kluczowych
KEY_CARDS = {
    'highlander': ['Reno Jackson', 'Zephrys the Great', 'Dragonqueen Alexstrasza'],
    'quest': ['The Caverns Below', 'Awaken the Makers', 'Lakkari Sacrifice', 'Open the Waygate'],
    'secret': ['Mysterious Challenger', 'Kirin Tor Mage', 'Subject 9', 'Masked Contender'],
    'mech': ['Mechwarper', 'Zilliax', 'SN1P-SN4P', 'Dr. Boom'],
    'aggro': ['Leeroy Jenkins', 'Southsea Deckhand', 'Wolfrider', 'Reckless Rocketeer'],
    'control': ['Lord Godfrey', 'Brawl', 'Twisting Nether', 'Plague of Death'],
    'combo': ['Malygos', 'Alexstrasza', 'Mecha\'thun', 'Linecracker']
}

# Baza meta-matchup (które archetypy są dobre przeciwko którym)
META_MATCHUPS = {
    'Aggro': {'good_vs': ['Control', 'Combo'], 'bad_vs': ['Midrange with Taunts', 'Aggro with Better Curve']},
    'Control': {'good_vs': ['Midrange', 'Combo'], 'bad_vs': ['Hyper Aggro', 'Aggro/TEMPO']},
    'Combo': {'good_vs': ['Control', 'Midrange'], 'bad_vs': ['Aggro', 'Hyper Aggro']},
    'Midrange': {'good_vs': ['Aggro'], 'bad_vs': ['Control with Board Clears', 'Combo']}
}

# Baza rozszerzeń Hearthstone - ZAKTUALIZOWANA 2025 (uzupełniona o brakujące minisety)
HS_EXPANSIONS = [
    {"name": "Classic", "year": 2014, "type": "Base Set"},
    {"name": "Curse of Naxxramas", "year": 2014, "type": "Adventure"},
    {"name": "Goblins vs Gnomes", "year": 2014, "type": "Expansion"},
    {"name": "Blackrock Mountain", "year": 2015, "type": "Adventure"},
    {"name": "The Grand Tournament", "year": 2015, "type": "Expansion"},
    {"name": "League of Explorers", "year": 2015, "type": "Adventure"},
    {"name": "Whispers of the Old Gods", "year": 2016, "type": "Expansion"},
    {"name": "One Night in Karazhan", "year": 2016, "type": "Adventure"},
    {"name": "Mean Streets of Gadgetzan", "year": 2016, "type": "Expansion"},
    {"name": "Journey to Un'Goro", "year": 2017, "type": "Expansion"},
    {"name": "Knights of the Frozen Throne", "year": 2017, "type": "Expansion"},
    {"name": "Kobolds & Catacombs", "year": 2017, "type": "Expansion"},
    {"name": "The Witchwood", "year": 2018, "type": "Expansion"},
    {"name": "The Boomsday Project", "year": 2018, "type": "Expansion"},
    {"name": "Rastakhan's Rumble", "year": 2018, "type": "Expansion"},
    {"name": "Rise of Shadows", "year": 2019, "type": "Expansion"},
    {"name": "Saviors of Uldum", "year": 2019, "type": "Expansion"},
    {"name": "Descent of Dragons", "year": 2019, "type": "Expansion"},
    {"name": "Galakrond's Awakening", "year": 2020, "type": "Adventure"},
    {"name": "Ashes of Outland", "year": 2020, "type": "Expansion"},
    {"name": "Scholomance Academy", "year": 2020, "type": "Expansion"},
    {"name": "Madness at the Darkmoon Faire", "year": 2020, "type": "Expansion"},
    {"name": "Darkmoon Races", "year": 2021, "type": "Mini-Set"},
    {"name": "Forged in the Barrens", "year": 2021, "type": "Expansion"},
    {"name": "Wailing Caverns", "year": 2021, "type": "Mini-Set"},
    {"name": "United in Stormwind", "year": 2021, "type": "Expansion"},
    {"name": "Deadmines", "year": 2021, "type": "Mini-Set"},
    {"name": "Fractured in Alterac Valley", "year": 2021, "type": "Expansion"},
    {"name": "Onyxia's Lair", "year": 2021, "type": "Mini-Set"},
    {"name": "Voyage to the Sunken City", "year": 2022, "type": "Expansion"},
    {"name": "Throne of the Tides", "year": 2022, "type": "Mini-Set"},
    {"name": "Murder at Castle Nathria", "year": 2022, "type": "Expansion"},
    {"name": "March of the Lich King", "year": 2022, "type": "Expansion"},
    {"name": "Return to Naxxramas", "year": 2022, "type": "Mini-Set"},
    {"name": "Festival of Legends", "year": 2023, "type": "Expansion"},
    {"name": "Titans", "year": 2023, "type": "Expansion"},
    {"name": "Showdown in the Badlands", "year": 2023, "type": "Expansion"},
    # Dodane brakujące minisety 2023
    {"name": "Harmonium", "year": 2023, "type": "Mini-Set"},
    {"name": "Titans' Mini-Set", "year": 2023, "type": "Mini-Set"},
    {"name": "Badlands Brawl", "year": 2023, "type": "Mini-Set"},
    {"name": "Whizbang's Workshop", "year": 2024, "type": "Expansion"},
    {"name": "The Witchwood Returns", "year": 2024, "type": "Expansion"},
    {"name": "Eventide", "year": 2024, "type": "Expansion"},
    # Dodane brakujące minisety 2024
    {"name": "Workshop Wonders", "year": 2024, "type": "Mini-Set"},
    {"name": "Midnight Hunt", "year": 2024, "type": "Mini-Set"},
    {"name": "Caverns of Time", "year": 2025, "type": "Expansion"},
    {"name": "Mysteries of Ulduar", "year": 2025, "type": "Expansion"}
]

# Aktualne statystyki meta (przykładowe dane)
CURRENT_META_STATS = {
    'Łowca demonów': {'winrate': 56.2, 'popularity': 12.5, 'tier': 'S'},
    'Mag': {'winrate': 54.8, 'popularity': 11.2, 'tier': 'S'},
    'Wojownik': {'winrate': 53.5, 'popularity': 9.8, 'tier': 'A'},
    'Łotr': {'winrate': 52.1, 'popularity': 10.5, 'tier': 'A'},
    'Paladyn': {'winrate': 51.3, 'popularity': 8.7, 'tier': 'B'},
    'Szaman': {'winrate': 50.8, 'popularity': 7.9, 'tier': 'B'},
    'Rycerz śmierci': {'winrate': 49.5, 'popularity': 8.3, 'tier': 'C'},
    'Kapłan': {'winrate': 48.7, 'popularity': 6.5, 'tier': 'C'},
    'Łowca': {'winrate': 47.9, 'popularity': 7.2, 'tier': 'C'},
    'Druid': {'winrate': 46.3, 'popularity': 5.8, 'tier': 'D'},
    'Czarnoksiężnik': {'winrate': 45.1, 'popularity': 4.2, 'tier': 'D'}
}

# Lista wszystkich talii Whizbanga i Zayle
WHIZBANG_DECKS = [
    # Whizbang the Wonderful (Whizbang's Workshop 2024) - 18 talii
    "Whizbang's Druid of the Swarm",
    "Whizbang's Druid of the Bees", 
    "Whizbang's Hunter of the Undead",
    "Whizbang's Hunter of the Mechs",
    "Whizbang's Mage of the Arcane",
    "Whizbang's Mage of the Elements",
    "Whizbang's Paladin of the Light",
    "Whizbang's Paladin of the Mechs",
    "Whizbang's Priest of the Shadows",
    "Whizbang's Priest of the Combo",
    "Whizbang's Rogue of the Thieves",
    "Whizbang's Rogue of the Pirates",
    "Whizbang's Shaman of the Murlocs",
    "Whizbang's Shaman of the Storms",
    "Whizbang's Warlock of the Zoo",
    "Whizbang's Warlock of the Control",
    "Whizbang's Warrior of the Pirates",
    "Whizbang's Warrior of the Control",
    
    # Zayle, Shadow Cloak (5 talii)
    "Zayle's Cloak of the Shadows",
    "Zayle's Cloak of the Undead", 
    "Zayle's Cloak of the Mechs",
    "Zayle's Cloak of the Elements",
    "Zayle's Cloak of the Pirates"
]

def ensure_dirs():
    for dir_path in [BACKUP_DIR, CACHE_DIR]:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(f'Directory creation error {dir_path}: {e}')

ensure_dirs()

def norm(s):
    s=(s or '').strip().lower()
    s=unicodedata.normalize('NFKD', s)
    s=''.join(ch for ch in s if not unicodedata.combining(ch))
    return s

CLASS_SYNONYMS={'druid':['druid'],'lowca':['hunter','łowca','lowca'],'mag':['mage'],'paladyn':['paladin'],'kaplan':['priest','kapłan','kaplan'],'lotr':['rogue','łotr','lotr'],'szaman':['shaman'],'czarnoksieznik':['warlock','czarnoksiężnik','czarnoks','lock','czarnoksieznik'],'wojownik':['warrior'],'rycerz smierci':['death knight','dk','rycerz śmierci','rycerz smierci'],'lowca demonow':['demon hunter','dh','łowca demonów','lowca demonow','łowczyni demonów','lowczyni demonow']}
KEY_MAP={'druid':'Druid','lowca':'Łowca','mag':'Mag','paladyn':'Paladyn','kaplan':'Kapłan','lotr':'Łotr','szaman':'Szaman','czarnoksieznik':'Czarnoksiężnik','wojownik':'Wojownik','rycerz smierci':'Rycerz śmierci','lowca demonow':'Łowca demonów'}

def write_backup_files(path, data):
    ensure_dirs()
    base = os.path.basename(path)
    stem, _ = os.path.splitext(base)
    latest_path = os.path.join(os.path.dirname(path), f"{stem}_backup.json")
    try:
        with open(latest_path,'w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception as e:
        print('Backup latest error:', e)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    arch_path = os.path.join(BACKUP_DIR, f"{stem}_{ts}.json")
    try:
        with open(arch_path,'w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception as e:
        print('Backup archive error:', e)
    try:
        pats = os.path.join(BACKUP_DIR, f"{stem}_*.json")
        files = sorted(glob.glob(pats))
        if len(files) > 20:
            to_rm = files[:len(files)-20]
            for p in to_rm:
                try: os.remove(p)
                except Exception: pass
    except Exception as e:
        print('Backup rotation error:', e)

def load_json(path, default):
    if not os.path.exists(path): return default
    try:
        with open(path,'r',encoding='utf-8') as f: return json.load(f)
    except Exception: return default

def save_json(path, data):
    try:
        with open(path,'w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception as e:
        console.hud_alert(f'Błąd zapisu {os.path.basename(path)}','error',1.0)
        print('Save error:', e)
        return
    write_backup_files(path, data)

def now_iso(): return datetime.datetime.now().isoformat()

def uiimage_from_pil(pil_img):
    buf=io.BytesIO(); pil_img.save(buf, format='PNG'); return ui.Image.from_data(buf.getvalue())
def b64_from_pil(pil_img):
    buf=io.BytesIO(); pil_img.save(buf, format='PNG'); return base64.b64encode(buf.getvalue()).decode('ascii')
def uiimage_from_b64(b64str):
    try: return ui.Image.from_data(base64.b64decode(b64str.encode('ascii')))
    except Exception: return None
def save_bg_file(pil_img):
    try: pil_img.save(BG_FILE, format='PNG')
    except Exception as e: print('BG save error:', e)

RE_DECK_LINE=re.compile(r'^[A-Za-z0-9+/=]{20,}$')
RE_DECK_ANY =re.compile(r'(AAE[A-Za-z0-9+/=]{18,})')
RE_CARD_STRICT=re.compile(r'^#\s{1}(\d+)x\s*\((\d+)\)\s*(.+?)\s*$')
RE_TITLE =re.compile(r'^\s*#{2,}\s*(.+?)\s*$')
RE_KLASS =re.compile(r'^\s*#?\s*Klasa:\s*(.+?)\s*$', re.I)
RE_CLASS  =re.compile(r'^\s*#?\s*Class:\s*(.+?)\s*$', re.I)
RE_FORMAT=re.compile(r'^\s*#?\s*Format:\s*(.+?)\s*$', re.I)

def parse_cards_from_lines(lines):
    cards=[]
    for raw in lines:
        m=RE_CARD_STRICT.match(raw.strip())
        if not m: continue
        count=int(m.group(1)); cost=int(m.group(2)); name=m.group(3).strip()
        cards.append({'count':count,'cost':cost,'name':name})
    merged={}
    for c in cards:
        k=c['name'].lower()
        if k in merged: merged[k]['count']+=c['count']
        else: merged[k]=dict(c)
    cards=list(merged.values())
    cards.sort(key=lambda x:(x['cost'],x['name'].lower()))
    return cards

def split_blocks_by_deckstrings(blob):
    text=blob.replace('\r',''); lines=text.split('\n')
    idxs=[i for i,l in enumerate(lines) if RE_DECK_LINE.match(l.strip())]
    blocks=[]
    if idxs:
        for k,start in enumerate(idxs):
            end=idxs[k+1] if k+1<len(idxs) else len(lines)
            pre_start=max(0,start-60)
            chunk=[x.strip() for x in lines[pre_start:end]]
            blocks.append({'lines':chunk,'deckstring':lines[start].strip()})
        return blocks
    found=list(RE_DECK_ANY.finditer(text))
    if found:
        for m in found:
            deck=m.group(1).strip()
            start_pos=max(0, text.rfind('\n',0,m.start()))
            end_pos=text.find('\n', m.end())
            if end_pos==-1: end_pos=len(text)
            pre_lines=text[:start_pos].split('\n')[-60:]
            post_lines=text[start_pos:end_pos].split('\n')
            chunk=[x.strip() for x in (pre_lines+post_lines)]
            blocks.append({'lines':chunk, 'deckstring':deck})
        return blocks
    any_codes=re.findall(r'[A-Za-z0-9+/=]{30,}', text)
    return [{'lines':[], 'deckstring':c.strip()} for c in any_codes]

def canonical_class_label(lbl):
    t=norm(lbl)
    if t in KEY_MAP: return KEY_MAP[t]
    for key,syns in CLASS_SYNONYMS.items():
        all_norm={key}|{norm(x) for x in syns}
        if t in all_norm: return KEY_MAP.get(key, lbl or '')
    return lbl or ''

def detect_class_from_text(text):
    t = norm(text)
    for key,syns in CLASS_SYNONYMS.items():
        if norm(key) in t: return KEY_MAP[key]
        for s in syns:
            if norm(s) in t: return KEY_MAP[key]
    return ''

def extract_archetype_tags_from_name(name):
    t = norm(name)
    tags = []
    cls_hit = None
    for key,syns in CLASS_SYNONYMS.items():
        cands = [key]+syns
        for c in cands:
            idx = t.find(norm(c))
            if idx>0: 
                cls_hit = idx
                break
        if cls_hit: break
    chunk = t if cls_hit is None else t[:cls_hit]
    for w in re.split(r'[^a-z0-9]+', chunk):
        if not w: continue
        if w in ARCH_TAGS:
            tags.append(ARCH_TAGS[w])
        elif w in ('xl','40'):
            tags.append('highlander')
        elif w in ('aggro','tempo','midrange','control','combo'):
            tags.append(w)
    out=[]; seen=set()
    for tag in tags:
        if tag and tag not in seen:
            out.append(tag); seen.add(tag)
    return out

def parse_block_to_deck(block):
    name=klass=fmt=None
    for l in block['lines']:
        if not name:
            m=RE_TITLE.match(l); name=m.group(1).strip() if m else None
        if not klass:
            m=RE_KLASS.match(l); klass=m.group(1).strip() if m else None
            if not klass:
                m2=RE_CLASS.match(l); klass=m2.group(1).strip() if m2 else None
        if not fmt:
            m=RE_FORMAT.match(l); fmt=m.group(1).strip() if m else None
    detected_from_name  = detect_class_from_text(name or '')
    detected_from_klass = detect_class_from_text(klass or '')
    canon_class = canonical_class_label(detected_from_klass or detected_from_name or (klass or ''))
    if not name:
        name="Talia " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    tags = extract_archetype_tags_from_name(name)
    cards=parse_cards_from_lines(block['lines'])
    return {'name':name,'class':canon_class or (klass or ''),'format':fmt or '','tags':tags,'deckstring':block['deckstring'].strip(),'cards_text':cards,'raw':'\n'.join(block['lines']+[block['deckstring'].strip()])}

def parse_many(text):
    blocks=split_blocks_by_deckstrings(text)
    decks=[parse_block_to_deck(b) for b in blocks if b.get('deckstring')]
    if not decks: raise ValueError('Nie znaleziono deck-code (AAE...)')
    return decks

def _curve(cards):
    curve=[0]*11
    for c in cards:
        idx = c['cost'] if c['cost']<10 else 10
        curve[idx]+=c['count']
    return curve

def _bars(arr):
    mx=max(arr) if arr else 0
    out=[]
    for i,val in enumerate(arr):
        label = f"({i if i<10 else '10+'})"
        filled = int(round((val/mx)*20)) if mx>0 else 0
        out.append(f"{label:>5} {val:>2}  " + ('█'*filled).ljust(20))
    return out

class AIDeckAdvisor:
    """Zaawansowany system doradztwa talii z machine learning"""
    
    def __init__(self):
        self.meta_data = load_json(META_PATH, {'trends': [], 'popular_decks': {}})
    
    def analyze_deck_strengths(self, deck):
        """Analiza mocnych i słabych stron talii"""
        cards = deck.get('cards_text', [])
        total = sum(int(c.get('count',0)) for c in cards)
        
        # Analiza krzywej many
        curve = _curve(cards)
        avg_cost = sum((i if i<10 else 10)*curve[i] for i in range(11)) / float(total) if total else 0
        
        strengths = []
        weaknesses = []
        
        # Early game strength
        early_power = curve[0] + curve[1] + curve[2]
        if early_power >= 10:
            strengths.append("Silny early game")
        elif early_power <= 5:
            weaknesses.append("Słaby early game")
        
        # Late game strength
        late_power = sum(curve[6:])
        if late_power >= 8:
            strengths.append("Potężny late game")
        elif late_power <= 3:
            weaknesses.append("Brak late game")
        
        # Card advantage
        draw_cards = [c for c in cards if any(word in c['name'].lower() for word in ['draw', 'discover', 'tutor'])]
        if len(draw_cards) >= 3:
            strengths.append("Dobra engine kart")
        elif len(draw_cards) == 0:
            weaknesses.append("Brak card draw")
        
        # Removal suite
        removal_cards = [c for c in cards if any(word in c['name'].lower() for word in ['destroy', 'remove', 'deal', 'damage', 'clear'])]
        if len(removal_cards) >= 4:
            strengths.append("Kompletny zestaw removali")
        elif len(removal_cards) <= 1:
            weaknesses.append("Brak removali")
        
        return strengths, weaknesses
    
    def generate_deck_archetype(self, deck):
        """Generuje szczegółowy archetyp talii"""
        cards = deck.get('cards_text', [])
        total = sum(int(c.get('count',0)) for c in cards)
        curve = _curve(cards)
        
        low = sum(curve[:3])
        mid = sum(curve[3:7])
        high = sum(curve[7:])
        
        # Detekcja szczegółowego archetypu
        if low >= 12 and high <= 4:
            return "Hyper Aggro"
        elif low >= 8 and high <= 6:
            return "Aggro"
        elif abs(low - high) <= 3 and mid >= 10:
            return "Midrange"
        elif high >= 8 and low <= 6:
            return "Control"
        elif high >= 10:
            return "Late Game Control"
        else:
            return "Flexible Midrange"
    
    def predict_matchups(self, deck):
        """Przewiduje winrate przeciwko popularnym archetypom"""
        archetype = self.generate_deck_archetype(deck)
        
        matchup_predictions = {
            'Hyper Aggro': {'predicted_wr': 45, 'notes': 'Może mieć problemy z szybszymi deckami'},
            'Aggro': {'predicted_wr': 52, 'notes': 'Zrównoważony matchup'},
            'Midrange': {'predicted_wr': 55, 'notes': 'Dobrze dopasowany'},
            'Control': {'predicted_wr': 48, 'notes': 'Wymaga dobrej gry'},
            'Late Game Control': {'predicted_wr': 60, 'notes': 'Mocna pozycja'}
        }
        
        # Dostosowanie na podstawie rzeczywistych cech decka
        cards = deck.get('cards_text', [])
        
        # Sprawdź obecność AoE
        aoe_cards = [c for c in cards if any(word in c['name'].lower() for word in ['all', 'every', 'board', 'clear'])]
        if len(aoe_cards) >= 2:
            matchup_predictions['Aggro']['predicted_wr'] += 8
            matchup_predictions['Hyper Aggro']['predicted_wr'] += 6
        
        # Sprawdź obecność heal/armor
        heal_cards = [c for c in cards if any(word in c['name'].lower() for word in ['heal', 'restore', 'armor', 'health'])]
        if len(heal_cards) >= 2:
            matchup_predictions['Aggro']['predicted_wr'] += 5
        
        return matchup_predictions

def analyze_ai_pro_advanced(deck):
    """Rozszerzona analiza AI z nowymi funkcjami"""
    advisor = AIDeckAdvisor()
    
    cards = deck.get('cards_text', []) or []
    total = sum(int(c.get('count',0)) for c in cards)
    names_join = ' '.join((c.get('name') or '').lower() for c in cards)
    target = 40 if ('renathal' in names_join or total>=36) else 30
    
    # Podstawowa analiza
    curve = _curve(cards)
    avg_cost = sum((i if i<10 else 10)*curve[i] for i in range(11)) / float(total) if total else 0
    low=sum(curve[:3]); mid=sum(curve[3:7]); high=sum(curve[7:])
    
    # Zaawansowana analiza
    archetype = advisor.generate_deck_archetype(deck)
    strengths, weaknesses = advisor.analyze_deck_strengths(deck)
    matchups = advisor.predict_matchups(deck)
    
    # Monte Carlo simulation
    import random
    pool = []
    for c in cards:
        pool += [min(int(c.get('cost',0)),10)] * int(c.get('count',0))
    trials = 4000
    hit1=hit2=hit3=0
    for _ in range(trials):
        random.shuffle(pool)
        start_cnt = 4 if random.random()<0.5 else 3
        hand = pool[:start_cnt]
        deck_rest = pool[start_cnt:]
        if any(x<=1 for x in hand): hit1 += 1
        if deck_rest: hand.append(deck_rest[0])
        if any(x<=2 for x in hand): hit2 += 1
        if len(deck_rest)>1: hand.append(deck_rest[1])
        if any(x<=3 for x in hand): hit3 += 1
    p1 = (hit1/trials)*100.0; p2 = (hit2/trials)*100.0; p3 = (hit3/trials)*100.0
    
    # Render raportu
    lines = []
    lines.append(f"🤖 ULTIMATE AI ANALYSIS: {deck.get('name','')}")
    lines.append(f"🏷️  Archetyp: {archetype} | 📊 Karty: {total}/{target}")
    lines.append("")
    
    # Mocne i słabe strony
    if strengths:
        lines.append("💪 Mocne strony:")
        for s in strengths:
            lines.append(f"   ✅ {s}")
        lines.append("")
    
    if weaknesses:
        lines.append("⚠️  Słabe strony:")
        for w in weaknesses:
            lines.append(f"   ❌ {w}")
        lines.append("")
    
    # Predykcje matchup
    lines.append("⚔️  Przewidywane winrate:")
    for matchup, data in matchups.items():
        wr = data['predicted_wr']
        emoji = "🟢" if wr >= 55 else "🟡" if wr >= 48 else "🔴"
        lines.append(f"   {emoji} vs {matchup}: {wr}% - {data['notes']}")
    lines.append("")
    
    # Statystyki
    lines.append("📈 Podstawowe statystyki:")
    lines.append(f"   • Średni koszt: {avg_cost:.2f}")
    lines.append(f"   • Rozkład: {low} low / {mid} mid / {high} high")
    lines.append(f"   • Curve hit: T1:{p1:.1f}% T2:{p2:.1f}% T3:{p3:.1f}%")
    
    # Sugestie ulepszeń
    suggestions = []
    if p1 < 65: suggestions.append("Dodaj więcej 1-dropów dla lepszego early game")
    if len([c for c in cards if c['cost'] == 0]) == 0: suggestions.append("Rozważ karty 0-kosztowe (The Coin, Innervate)")
    if total != target: suggestions.append(f"Dostosuj rozmiar talii do {target} kart")
    
    if suggestions:
        lines.append("")
        lines.append("💡 Sugestie ulepszeń:")
        for s in suggestions:
            lines.append(f"   • {s}")
    
    return '\n'.join(lines)

class DeckOptimizer:
    """System automatycznej optymalizacji talii - ULEPSZONY"""
    
    def __init__(self):
        self.card_database = self._load_card_database()
    
    def _load_card_database(self):
        """Ładuje rozszerzoną bazę danych kart"""
        return {
            'aggro_1_drops': ['Leper Gnome', 'Fire Fly', 'Mistress of Mixtures', 'Intrepid Initiate', 'Wretched Tutor'],
            'aggro_2_drops': ['Loot Hoarder', 'Novice Engineer', 'Wild Growth', 'Annoy-o-Tron', 'Sunfury Protector'],
            'aggro_3_drops': ['Wolfrider', 'Southsea Deckhand', 'Reckless Rocketeer'],
            'control_removals': ['Flamestrike', 'Brawl', 'Shadow Word: Death', 'Twisting Nether', 'Plague of Death'],
            'control_late_game': ['Tirion Fordring', 'Ysera', 'Deathwing', 'Sneed\'s Old Shredder'],
            'draw_engines': ['Acolyte of Pain', 'Coldlight Oracle', 'Loot Hoarder', 'Novice Engineer', 'Azure Drake'],
            'taunts': ['Sludge Belcher', 'Tirion Fordring', 'Annoy-o-Tron', 'Sunwalker', 'Psych-o-Tron'],
            'heals': ['Antique Healbot', 'Reno Jackson', 'Lightwell', 'Earthen Ring Farseer'],
            'combo_pieces': ['Malygos', 'Alexstrasza', 'Mecha\'thun', 'Linecracker', 'Leeroy Jenkins'],
            'weapons': ['Fiery War Axe', 'Eaglehorn Bow', 'Truesilver Champion', 'Gorehowl'],
            'secrets': ['Explosive Trap', 'Freezing Trap', 'Ice Block', 'Noble Sacrifice']
        }
    
    def _analyze_deck_gaps(self, deck):
        """Analizuje luki w talii na podstawie archetypu i krzywej many"""
        cards = deck.get('cards_text', [])
        curve = _curve(cards)
        
        gaps = {
            'low_drops': curve[0] + curve[1] < 6,
            'mid_drops': curve[2] + curve[3] + curve[4] < 8,
            'removals': len([c for c in cards if any(word in c['name'].lower() for word in ['destroy', 'remove', 'deal', 'damage', 'clear'])]) < 3,
            'draw': len([c for c in cards if any(word in c['name'].lower() for word in ['draw', 'discover', 'tutor'])]) < 2,
            'taunts': len([c for c in cards if 'taunt' in c['name'].lower()]) < 2,
            'late_game': sum(curve[6:]) < 4
        }
        
        return gaps
    
    def suggest_improvements(self, deck, archetype):
        """Sugeruje konkretne zmiany w talii na podstawie analizy luk"""
        cards = deck.get('cards_text', [])
        current_cards = [c['name'].lower() for c in cards]
        gaps = self._analyze_deck_gaps(deck)
        
        suggestions = []
        
        # Analiza dla każdego archetypu
        if archetype in ['Aggro', 'Hyper Aggro']:
            if gaps['low_drops']:
                missing = [card for card in self.card_database['aggro_1_drops'] 
                          if card.lower() not in current_cards]
                if missing:
                    suggestions.append(f"Dodaj 1-drop: {random.choice(missing)}")
            
            if gaps['mid_drops']:
                missing = [card for card in self.card_database['aggro_2_drops'] 
                          if card.lower() not in current_cards]
                if missing:
                    suggestions.append(f"Dodaj 2-drop: {random.choice(missing)}")
        
        elif archetype in ['Control', 'Late Game Control']:
            if gaps['removals']:
                missing = [card for card in self.card_database['control_removals'] 
                          if card.lower() not in current_cards]
                if missing:
                    suggestions.append(f"Dodaj removal: {random.choice(missing)}")
            
            if gaps['late_game']:
                missing = [card for card in self.card_database['control_late_game'] 
                          if card.lower() not in current_cards]
                if missing:
                    suggestions.append(f"Dodaj late-game finisher: {random.choice(missing)}")
            
            if gaps['taunts']:
                missing = [card for card in self.card_database['taunts'] 
                          if card.lower() not in current_cards]
                if missing:
                    suggestions.append(f"Dodaj taunt: {random.choice(missing)}")
        
        # Uniwersalne sugestie
        if gaps['draw']:
            missing = [card for card in self.card_database['draw_engines'] 
                      if card.lower() not in current_cards]
            if missing:
                suggestions.append(f"Dodaj card draw: {random.choice(missing)}")
        
        # Sprawdź czy talia ma broń (dla klas, które mogą jej używać)
        weapon_classes = ['Wojownik', 'Łowca', 'Paladyn', 'Łotr', 'Szaman']
        if deck.get('class') in weapon_classes:
            weapons = [c for c in cards if any(word in c['name'].lower() for word in ['sword', 'axe', 'bow', 'weapon'])]
            if len(weapons) == 0:
                missing = [card for card in self.card_database['weapons'] 
                          if card.lower() not in current_cards]
                if missing:
                    suggestions.append(f"Rozważ broń: {random.choice(missing)}")
        
        # Jeśli brakuje sugestii, sprawdź ogólne problemy
        if not suggestions:
            total_cards = sum(c['count'] for c in cards)
            if total_cards < 30:
                suggestions.append("Talia ma za mało kart - dodaj więcej kart")
            elif total_cards > 30:
                suggestions.append("Talia ma za dużo kart - usuń najsłabsze karty")
            else:
                curve = _curve(cards)
                if sum(curve[:2]) < 5:
                    suggestions.append("Dodaj więcej niskokosztowych kart dla lepszego early game")
                elif sum(curve[6:]) < 3:
                    suggestions.append("Dodaj więcej wysokokosztowych kart dla late game")
        
        return suggestions[:3]  # Max 3 sugestie

def style_button(b):
    b.background_color=(0,0,0,0.35); b.tint_color='white'; b.corner_radius=8; b.border_color=(1,1,1,0.12); b.border_width=1

def style_button_active(b):
    b.background_color=(1,1,1,0.18); b.border_color=(1,1,1,0.35); b.border_width=1.2

class DeckDataSource(object):
    def __init__(self, store):
        self.store=store; self.items=list(store.filtered)
    def reload_from(self, items): self.items=list(items)
    def tableview_number_of_sections(self, tv): return 1
    def tableview_number_of_rows(self, tv, section): return len(self.items)
    def tableview_row_height(self, tv, section, row): return 56
    def tableview_cell_for_row(self, tv, section, row):
        deck = self.items[row]
        cell = ui.TableViewCell()
        cell.background_color = (0, 0, 0, 0.0)

        klass = canonical_class_label(deck.get('class', ''))
        icon = CLASS_ICONS.get(klass, '🃏')
        icon_lbl = ui.Label(frame=(10, 8, 24, 24))
        icon_lbl.text = icon
        icon_lbl.alignment = ui.ALIGN_CENTER
        icon_lbl.font = ('<System>', 19)
        icon_lbl.text_color = 'white'
        cell.content_view.add_subview(icon_lbl)

        name_lbl = ui.Label(frame=(40, 6, tv.width - 40 - 10, 24))
        name_lbl.text = deck.get('name', '(bez nazwy)')
        name_lbl.text_color = 'white'
        name_lbl.font = ('<System-Bold>', 16)
        name_lbl.flex = 'W'
        cell.content_view.add_subview(name_lbl)

        # Dodanie informacji o archetypie
        archetype_info = ""
        if deck.get('tags'):
            primary_archetype = deck['tags'][0] if deck['tags'] else ""
            archetype_info = f" | {primary_archetype}"
        
        meta_parts = [klass or deck.get('class', ''), deck.get('format', '')]
        if deck.get('tags'):
            meta_parts.append(','.join(deck.get('tags')))
        dt = deck.get('created_at') or deck.get('updated_at') or ''
        if dt:
            try:
                dt_obj = datetime.datetime.fromisoformat(dt.replace('Z', ''))
                m = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][dt_obj.month - 1]
                meta_parts.append(f"{dt_obj.day} {m} {dt_obj.year}")
            except Exception:
                pass
        meta = ' · '.join(p for p in meta_parts if p)
        meta_lbl = ui.Label(frame=(40, 28, tv.width - 40 - 10, 18))
        meta_lbl.text = meta
        meta_lbl.text_color = (1, 1, 1, 0.7)
        meta_lbl.font = ('<System>', 12)
        meta_lbl.flex = 'W'
        cell.content_view.add_subview(meta_lbl)

        return cell

class CardsTable(ui.ListDataSource):
    def __init__(self, cards):
        rows=[f"{c['count']}  ({c['cost']}) {c['name']}" for c in (cards or [])]
        super().__init__(rows); self.font=('Menlo',14)

class ClassPicker(ui.View):
    def __init__(self, on_pick):
        super().__init__(name='Wybierz klasę'); self.bg_color=(0,0,0,0.6); self.on_pick=on_pick
        self.table=ui.TableView(); self.ds=ui.ListDataSource([c for c in HS_CLASSES if c!='Wszystkie'])
        self.table.data_source=self.ds; self.table.delegate=self; self.add_subview(self.table)
    def layout(self):
        p=10; self.table.frame=(p,p,self.width-2*p,self.height-2*p)
    def tableview_did_select(self, tv, section, row):
        val=self.ds.items[row]; self.close(); 
        if self.on_pick: self.on_pick(val)

class WhizbangListView(ui.View):
    """Lista wszystkich talii Whizbanga i Zayle"""
    def __init__(self):
        super().__init__(name='Talie Whizbanga')
        self.bg_color = (0, 0, 0, 0.7)
        self.table = ui.TableView()
        self.table.background_color = (0, 0, 0, 0.25)
        self.data_source = ui.ListDataSource([])
        self.table.data_source = self.data_source
        self.table.delegate = self
        self.add_subview(self.table)
        self.load_whizbang_decks()
        
    def layout(self):
        self.table.frame = (10, 10, self.width-20, self.height-20)
        
    def load_whizbang_decks(self):
        items = []
        for deck_name in WHIZBANG_DECKS:
            items.append(deck_name)
        self.data_source.items = items
        
    def tableview_did_select(self, tv, section, row):
        deck_name = WHIZBANG_DECKS[row]
        console.hud_alert(f"{deck_name}", 'success', 1.0)
        tv.selected_row = (-1, -1)

class DeckStore:
    def __init__(self):
        self.db=load_json(DB_PATH, {'decks':[], 'ui':{}})
        for d in self.db['decks']:
            d.setdefault('cards_text',[]); d.setdefault('thumb_b64',''); d.setdefault('tags',[])
        # MIGRACJA DAT
        changed = False
        for d in self.db['decks']:
            if not d.get('created_at'):
                d['created_at'] = d.get('updated_at') or now_iso()
                changed = True
            if not d.get('updated_at'):
                d['updated_at'] = d['created_at']
                changed = True
        if changed:
            save_json(DB_PATH, self.db)

        self.filter_class=''; self.filtered=[]; self.apply_filter('')

    def get_bg_uiimage(self):
        b64=self.db.get('ui',{}).get('bg_png_b64')
        if b64:
            img=uiimage_from_b64(b64)
            if img: return img
        if os.path.exists(BG_FILE):
            try: return ui.Image.from_file(BG_FILE)
            except Exception: pass
        return None
    def set_bg_from_pil(self, pil_img):
        self.db.setdefault('ui',{})['bg_png_b64']=b64_from_pil(pil_img)
        save_json(DB_PATH,self.db); save_bg_file(pil_img); return self.get_bg_uiimage()

    def add_or_update(self, deck):
        for d in self.db['decks']:
            if d['deckstring']==deck['deckstring']:
                for k in ['name','class','format','raw','thumb_b64','tags','notes','cards_text']:
                    if k in deck and deck[k] is not None:
                        d[k] = deck[k] if k!='cards_text' else (deck[k] or d.get('cards_text',[]))
                d['updated_at']=now_iso(); save_json(DB_PATH,self.db); self.apply_filter(''); return d, False
        deck.update({'id':f"deck_{int(datetime.datetime.now().timestamp()*1000)}",'tags':deck.get('tags',[]),'notes':deck.get('notes',''),'thumb_b64':deck.get('thumb_b64',''),'created_at':now_iso(),'updated_at':now_iso()})
        self.db['decks'].append(deck); save_json(DB_PATH,self.db); self.apply_filter(''); return deck, True

    def bulk_add(self, decks):
        a=u=0
        for dk in decks:
            _,is_new=self.add_or_update(dk); a+=1 if is_new else 0; u+=0 if is_new else 1
        return a,u
    def delete(self, deck_id):
        self.db['decks']=[d for d in self.db['decks'] if d['id']!=deck_id]; save_json(DB_PATH,self.db); self.apply_filter('')

    def _class_aliases(self, label):
        t=norm(label); key_map={'druid':'druid','lowca':'lowca','mag':'mag','paladyn':'paladyn','kaplan':'kaplan','lotr':'lotr','szaman':'szaman','czarnoksieznik':'czarnoksieznik','wojownik':'wojownik','rycerz smierci':'rycerz smierci','lowca demonow':'lowca demonow'}
        key=key_map.get(t,t)
        aliases={t}; aliases.update(CLASS_SYNONYMS.get(key,[])); aliases={norm(a) for a in aliases}
        negatives=set()
        if key=='lowca':
            negatives={norm(x) for x in CLASS_SYNONYMS['lowca demonow']}
            negatives.update(['demonhunter','demon-hunter'])
        return aliases, negatives

    def apply_filter(self, _q):
        decks=list(self.db['decks'])
        if self.filter_class and self.filter_class!='Wszystkie':
            aliases,negatives=self._class_aliases(self.filter_class)
            patt=r'\b('+'|'.join(re.escape(a) for a in sorted(aliases,key=len,reverse=True))+r')\b'
            patt_neg=r'\b('+'|'.join(re.escape(a) for a in sorted(negatives,key=len,reverse=True))+r')\b' if negatives else None
            def hit(d):
                cls=norm(d.get('class','')).strip()
                if cls: return cls in aliases
                blob=norm(' '.join([d.get('name',''), ' '.join(d.get('tags',[]))]))
                if patt_neg and re.search(patt_neg, blob): return False
                return re.search(patt, blob) is not None
            decks=[d for d in decks if hit(d)]
        decks.sort(key=lambda d: d.get('updated_at',''), reverse=True); self.filtered=decks
    def set_class_filter(self, label): self.filter_class=label or ''; self.apply_filter('')

class SessionStore:
    def __init__(self): self.db=load_json(SESS_PATH, {'sessions':[]})
    def add(self, sess):
        sess['id']=f"sess_{int(datetime.datetime.now().timestamp()*1000)}"
        self.db['sessions'].append(sess); save_json(SESS_PATH,self.db); return sess['id']
    def list_for_deck(self, deck_id): return [s for s in self.db.get('sessions',[]) if s.get('deck_id')==deck_id]
    def summary_for_deck(self, deck_id):
        ss=self.list_for_deck(deck_id); total=len(ss); wins=sum(1 for s in ss if s.get('result')=='Win'); losses=total-wins
        by_opp={}
        for s in ss:
            k=s.get('opponent_class','?') or '?'
            by_opp.setdefault(k, {'total':0,'wins':0})
            by_opp[k]['total']+=1; by_opp[k]['wins']+=1 if s.get('result')=='Win' else 0
        return {'total':total,'wins':wins,'losses':losses,'by_opp':by_opp}

class DetailView(ui.View):
    def __init__(self, deck, store, on_saved, open_game_cb):
        super().__init__(name='Talia'); self.bg_color=(0,0,0,0.55)
        self.deck=dict(deck); self.store=store; self.on_saved=on_saved; self.open_game_cb=open_game_cb
        self.name_tf=ui.TextField(placeholder='Nazwa', text=self.deck.get('name',''))
        self.cls_tf=ui.TextField(placeholder='Klasa', text=self.deck.get('class',''))
        self.fmt_tf=ui.TextField(placeholder='Format', text=self.deck.get('format',''))
        self.tags_tf=ui.TextField(placeholder='Tagi (przecinki)', text=', '.join(self.deck.get('tags',[])))
        self.notes_tv=ui.TextView(text=self.deck.get('notes',''))
        self.code_tv=ui.TextView(editable=False, selectable=True); self.code_tv.text=self.deck['deckstring']
        self.btn_copy=ui.Button(title='📋 Kopiuj deck-code', action=self.copy_code)
        self.btn_copy_full=ui.Button(title='📄 Pełny eksport', action=self.copy_full_export)
        self.btn_copy_list=ui.Button(title='🃏 Lista kart', action=self.copy_cards)
        self.btn_ai=ui.Button(title='🤖 Analiza AI PRO', action=self.run_ai)
        self.btn_optimize=ui.Button(title='⚡ Optymalizuj', action=self.run_optimization)
        self.btn_save=ui.Button(title='💾 Zapisz', action=self.save)
        self.btn_delete=ui.Button(title='🗑️ Usuń', action=self.delete)
        self.btn_show_raw=ui.Button(title='📝 Źródło', action=self.show_raw)
        self.btn_game=ui.Button(title='🎮 Nowa sesja', action=self.add_game)
        self.btn_stats=ui.Button(title='📊 Statystyki', action=self.show_stats)
        for b in [self.btn_copy,self.btn_copy_full,self.btn_copy_list,self.btn_ai,self.btn_optimize,self.btn_save,self.btn_delete,self.btn_show_raw,self.btn_game,self.btn_stats]: style_button(b)
        self.cards_tv=ui.TableView(); self.cards_tv.data_source=CardsTable(self.deck.get('cards_text',[])); self.cards_tv.row_height=30; self.cards_tv.background_color=(0,0,0,0.25)
        for v in [self.name_tf,self.cls_tf,self.fmt_tf,self.tags_tf,self.notes_tv,self.code_tv,self.cards_tv,self.btn_copy,self.btn_copy_full,self.btn_copy_list,self.btn_ai,self.btn_optimize,self.btn_save,self.btn_delete,self.btn_show_raw,self.btn_game,self.btn_stats]: self.add_subview(v)
    def layout(self):
        p=12; w=self.width-2*p; y=p
        for tf in [self.name_tf,self.cls_tf,self.fmt_tf,self.tags_tf]: tf.frame=(p,y,w,34); y+=38
        self.notes_tv.frame=(p,y,w,80); y+=88
        self.code_tv.frame=(p,y,w,44); y+=52
        self.cards_tv.frame=(p,y,w,self.height-y-360); y=self.cards_tv.y+self.cards_tv.height+8
        self.btn_copy.frame=(p,y,(w-8)//2,36); self.btn_copy_full.frame=(p+(w+8)//2,y,(w-8)//2,36); y+=44
        self.btn_copy_list.frame=(p,y,(w-8)//2,36); self.btn_ai.frame=(p+(w+8)//2,y,(w-8)//2,36); y+=44
        self.btn_optimize.frame=(p,y,w,36); y+=44
        self.btn_save.frame=(p,y,(w-8)//2,36); self.btn_delete.frame=(p+(w+8)//2,y,(w-8)//2,36); y+=44
        self.btn_show_raw.frame=(p,y,(w-8)//2,36); self.btn_stats.frame=(p+(w+8)//2,y,(w-8)//2,36); y+=44
        self.btn_game.frame=(p,y,w,40)
    def _full_export_text(self):
        name = self.name_tf.text.strip() or self.deck.get('name','(bez nazwy)')
        klass = canonical_class_label(self.cls_tf.text.strip() or self.deck.get('class',''))
        fmt = self.fmt_tf.text.strip() or self.deck.get('format','')
        lines = []
        lines.append(f"### {name}")
        lines.append(f"# Klasa: {klass}")
        if fmt: lines.append(f"# Format: {fmt}")
        cards=self.deck.get('cards_text',[])
        if cards:
            for c in cards:
                lines.append(f"# {c['count']}x ({c['cost']}) {c['name']}")
        lines.append("")
        lines.append(self.deck['deckstring'])
        return '\n'.join(lines)
    def copy_code(self, s): clipboard.set(self.deck['deckstring']); console.hud_alert('Skopiowano deck-code','success',0.6)
    def copy_full_export(self, s): clipboard.set(self._full_export_text()); console.hud_alert('Skopiowano pełny eksport','success',0.8)
    def copy_cards(self, s):
        cards=self.deck.get('cards_text',[])
        if not cards: console.hud_alert('Brak listy kart.','error',1.0); return
        clipboard.set('\n'.join([f"- {c['count']}× ({c['cost']}) {c['name']}" for c in cards])); console.hud_alert('Skopiowano listę kart','success',0.6)
    def run_ai(self, s):
        txt = analyze_ai_pro_advanced(self.deck)
        console.alert('🤖 Ultimate AI Analysis', txt, 'OK', hide_cancel_button=True)
    def run_optimization(self, s):
        optimizer = DeckOptimizer()
        advisor = AIDeckAdvisor()
        archetype = advisor.generate_deck_archetype(self.deck)
        suggestions = optimizer.suggest_improvements(self.deck, archetype)
        
        if suggestions:
            msg = "Sugestie optymalizacji:\n\n" + "\n".join([f"• {s}" for s in suggestions])
            console.alert('⚡ Sugestie optymalizacji', msg, 'OK', hide_cancel_button=True)
        else:
            console.hud_alert('Talia jest już zoptymalizowana!', 'success', 1.0)
    def add_game(self, s): self.open_game_cb(self.deck)
    def show_stats(self, s): StatsView(self.deck, SessionStore()).present('sheet')
    def save(self, s):
        self.deck['name']=self.name_tf.text.strip() or self.deck['name']; 
        self.deck['class']=canonical_class_label(self.cls_tf.text.strip() or self.deck.get('class',''))
        self.deck['format']=self.fmt_tf.text.strip()
        self.deck['tags']=[t.strip() for t in self.tags_tf.text.split(',') if t.strip()]
        self.deck['notes']=self.notes_tv.text; self.deck['updated_at']=now_iso()
        for i,d in enumerate(self.store.db['decks']):
            if d['id']==self.deck['id']: self.store.db['decks'][i]=self.deck; break
        save_json(DB_PATH,self.store.db); console.hud_alert('Zapisano','success',0.6); self.on_saved(); self.close()
    def delete(self, s):
        btn=console.alert('Usunąć talię?','Operacja nieodwracalna.','Usuń','Anuluj',hide_cancel_button=False)
        if btn==1: self.store.delete(self.deck['id']); console.hud_alert('Usunięto','success',0.6); self.on_saved(); self.close()
    def show_raw(self, s): console.alert('Źródłowy tekst', self.deck.get('raw','(brak)'), 'OK')

class StatsView(ui.View):
    def __init__(self, deck, sess_store):
        super().__init__(name='Statystyki'); self.bg_color=(0,0,0,0.55); self.deck=deck; self.sess_store=sess_store
        self.text=ui.TextView(editable=False); self.add_subview(self.text)
        self.imgv=ui.ImageView(); self.imgv.content_mode=ui.CONTENT_SCALE_ASPECT_FIT; self.add_subview(self.imgv)
    def layout(self):
        p=8; w=self.width-2*p; h=self.height-2*p
        self.text.frame=(p,p,w,160); self.imgv.frame=(p,p+168,w,h-176); self.refresh()
    def refresh(self):
        s=self.sess_store.summary_for_deck(self.deck['id']); total=s['total']; wins=s['wins']; losses=s['losses']; wr=(100.0*wins/total) if total else 0.0
        lines=[f"Talia: {self.deck.get('name','')} [{canonical_class_label(self.deck.get('class',''))}]", f"Sesji: {total}   W:{wins} / L:{losses}   WR: {wr:.1f}%"]
        if s['by_opp']:
            lines.append("\nWinrate vs klasy:")
            for k,v in sorted(s['by_opp'].items(), key=lambda kv: kv[0]):
                t=v['total']; w=v['wins']; l=t-w; wr_k=(100.0*w/t) if t else 0.0
                lines.append(f" - {k:16s}  {w}/{l}  ({wr_k:.1f}%)")
        self.text.text='\n'.join(lines)
        if HAS_MPL and s['by_opp']:
            items=sorted(s['by_opp'].items(), key=lambda kv: kv[1]['total'], reverse=True)[:8]
            labels=[k for k,_ in items]; wrs=[(100.0*v['wins']/v['total']) if v['total'] else 0.0 for _,v in items]
            fig,ax=plt.subplots(figsize=(5.0,3.0)); ax.bar(labels, wrs); ax.set_ylim(0,100); ax.set_ylabel('WR %'); ax.set_title('Winrate vs klasy (Top)')
            plt.xticks(rotation=20, ha='right'); buf=io.BytesIO(); plt.tight_layout(); fig.savefig(buf, format='png', dpi=180); plt.close(fig)
            self.imgv.image=ui.Image.from_data(buf.getvalue())
        else:
            self.imgv.image=None

class SessionForm(ui.View):
    def __init__(self, deck, sess_store, on_saved):
        super().__init__(name='Sesja gry'); self.bg_color=(0,0,0,0.55)
        self.deck=deck; self.sess_store=sess_store; self.on_saved=on_saved
        now=datetime.datetime.now()
        self.lbl_title=ui.Label(text='Nowa sesja', alignment=ui.ALIGN_CENTER, font=('<System-Bold>',18), text_color='white')
        self.deck_tf=ui.TextField(placeholder='Talia', text=deck.get('name',''), enabled=False)
        self.class_tf=ui.TextField(placeholder='Klasa talii', text=canonical_class_label(deck.get('class','')), enabled=False)
        self.time_tf=ui.TextField(placeholder='Czas', text=now.strftime('%Y-%m-%d %H:%M'), enabled=False)
        self.opp_lbl=ui.Label(text='Klasa przeciwnika', text_color='white')
        self.opp_btn=ui.Button(title='Wybierz klasę', action=self.pick_class); style_button(self.opp_btn)
        self.opponent_class=None
        self.res_lbl=ui.Label(text='Wynik', text_color='white')
        self.res_pc=ui.SegmentedControl(segments=['Win','Loss']); self.res_pc.selected_index=0
        self.format_lbl=ui.Label(text='Format gry', text_color='white')
        self.format_tf=ui.TextField(placeholder='Ranked/Casual/Arena', text='Ranked')
        self.coin_lbl=ui.Label(text='Coin?', text_color='white')
        self.coin_sw=ui.Switch()
        self.notes_tv=ui.TextView(placeholder='Notatki...')
        self.btn_save=ui.Button(title='💾 Zapisz sesję', action=self.save); style_button(self.btn_save)
        self.btn_stats=ui.Button(title='📊 Pokaż statystyki', action=self.show_stats); style_button(self.btn_stats)
        for v in [self.lbl_title,self.deck_tf,self.class_tf,self.time_tf,self.opp_lbl,self.opp_btn,self.res_lbl,self.res_pc,self.format_lbl,self.format_tf,self.coin_lbl,self.coin_sw,self.notes_tv,self.btn_save,self.btn_stats]: self.add_subview(v)
    def layout(self):
        p=12; w=self.width-2*p; y=p+4
        self.lbl_title.frame=(p,y,w,24); y+=30
        for tf in [self.deck_tf,self.class_tf,self.time_tf]: tf.frame=(p,y,w,34); y+=38
        self.opp_lbl.frame=(p,y,w,20); y+=24; self.opp_btn.frame=(p,y,w,36); y+=44
        self.res_lbl.frame=(p,y,w,20); y+=24; self.res_pc.frame=(p,y,w,28); y+=36
        self.format_lbl.frame=(p,y,w,20); y+=24; self.format_tf.frame=(p,y,w,34); y+=38
        self.coin_lbl.frame=(p,y,w,60); self.coin_sw.frame=(p+70,y,51,31); y+=44
        self.notes_tv.frame=(p,y,w,self.height-y-100); y=self.notes_tv.y+self.notes_tv.height+8
        self.btn_save.frame=(p,y,(w-8)//2,40); self.btn_stats.frame=(p+(w+8)//2,y,(w-8)//2,40)
    def pick_class(self, sender):
        def set_choice(val):
            self.opponent_class = val
            self.opp_btn.title = f'Przeciwnik: {val}'
        ClassPicker(on_pick=set_choice).present('sheet')
    def save(self, sender):
        if not self.opponent_class:
            console.hud_alert('Wybierz klasę przeciwnika','error',0.8); return
        sess={'deck_id':self.deck['id'],'deck_name':self.deck.get('name',''),'deck_class':canonical_class_label(self.deck.get('class','')),'timestamp':now_iso(),'opponent_class':self.opponent_class,'result':self.res_pc.segments[self.res_pc.selected_index],'format':self.format_tf.text,'coin':self.coin_sw.value,'notes':self.notes_tv.text.strip()}
        self.sess_store.add(sess); console.hud_alert('Zapisano sesję','success',0.6)
        if self.on_saved: self.on_saved()
    def show_stats(self, sender): StatsView(self.deck, self.sess_store).present('sheet')

class QuickStatsView(ui.View):
    def __init__(self, deck_store, sess_store):
        super().__init__(name='Global Stats'); self.bg_color=(0,0,0,0.6)
        self.deck_store=deck_store; self.sess_store=sess_store
        self.text=ui.TextView(editable=False); self.add_subview(self.text)
        self.refresh()
    def layout(self):
        self.text.frame=(10,10,self.width-20,self.height-20)
    def refresh(self):
        decks=self.deck_store.db['decks']; sessions=self.sess_store.db['sessions']
        total_decks=len(decks); total_sessions=len(sessions)
        
        # Statystyki klas
        class_counts=Counter()
        for d in decks: class_counts[canonical_class_label(d.get('class',''))]+=1
        
        # Winrate globalny
        wins=sum(1 for s in sessions if s.get('result')=='Win')
        losses=total_sessions-wins
        wr_global=(100.0*wins/total_sessions) if total_sessions else 0
        
        lines=[]
        lines.append("📊 GLOBALNE STATYSTYKI")
        lines.append("")
        lines.append(f"📁 Talie: {total_decks}")
        lines.append(f"🎮 Sesje: {total_sessions}")
        lines.append(f"🏆 Winrate: {wr_global:.1f}% ({wins}-{losses})")
        lines.append("")
        lines.append("📈 Rozkład klas:")
        for cls,count in class_counts.most_common():
            lines.append(f"   {CLASS_ICONS.get(cls,'🃏')} {cls}: {count}")
        
        # Najpopularniejsze talie
        if sessions:
            lines.append("")
            lines.append("🔥 Najpopularniejsze talie:")
            deck_sessions=Counter(s.get('deck_id') for s in sessions)
            for deck_id,count in deck_sessions.most_common(5):
                deck=next((d for d in decks if d['id']==deck_id),None)
                if deck:
                    cls=canonical_class_label(deck.get('class',''))
                    lines.append(f"   {CLASS_ICONS.get(cls,'🃏')} {deck.get('name','')}: {count} gier")
        
        self.text.text='\n'.join(lines)

class MetaAnalyticsView(ui.View):
    """Zaawansowana analiza meta gry"""
    def __init__(self, deck_store, sess_store):
        super().__init__(name='Meta Analytics'); self.bg_color=(0,0,0,0.6)
        self.deck_store=deck_store; self.sess_store=sess_store
        self.text_view=ui.TextView(editable=False); self.add_subview(self.text_view)
        self.refresh_data()
    def layout(self):
        self.text_view.frame=(10,10,self.width-20,self.height-20)
    def refresh_data(self):
        decks=self.deck_store.db['decks']; sessions=self.sess_store.db['sessions']
        
        # Analiza popularności klas
        class_usage=Counter()
        class_wins=defaultdict(lambda: {'wins':0, 'total':0})
        
        for session in sessions:
            cls=session.get('deck_class','')
            class_usage[cls]+=1
            class_wins[cls]['total']+=1
            if session.get('result')=='Win': class_wins[cls]['wins']+=1
        
        # Analiza archetypów
        archetype_analysis=self._analyze_archetypes(decks)
        
        lines=[]
        lines.append("📊 META ANALYTICS DASHBOARD")
        lines.append("="*40)
        lines.append("")
        
        lines.append("🏆 AKTUALNY META - WINRATE KLAS:")
        lines.append("(od najlepszych do najgorszych)")
        lines.append("")
        
        # Sortowanie klas według winrate
        sorted_classes = sorted(CURRENT_META_STATS.items(), 
                              key=lambda x: x[1]['winrate'], 
                              reverse=True)
        
        for i, (cls, stats) in enumerate(sorted_classes, 1):
            tier_emoji = {"S": "🟢", "A": "🟡", "B": "🟠", "C": "🔴", "D": "⚫"}.get(stats['tier'], "⚪")
            lines.append(f"{i:2d}. {CLASS_ICONS.get(cls,'🃏')} {cls:<16} {stats['winrate']:.1f}% WR "
                        f"({stats['popularity']:.1f}% pick rate) {tier_emoji} Tier {stats['tier']}")
        
        lines.append("")
        lines.append("📈 NAJPOPULARNIEJSZE KLASY:")
        for cls, count in class_usage.most_common(5):
            wr_data=class_wins[cls]
            wr=(wr_data['wins']/wr_data['total']*100) if wr_data['total']>0 else 0
            lines.append(f"  {CLASS_ICONS.get(cls,'🃏')} {cls}: {count} gier, WR: {wr:.1f}%")
        lines.append("")
        
        lines.append("🎯 ANALIZA ARCHETYPÓW:")
        for arch, data in archetype_analysis.items():
            lines.append(f"  {arch}: {data['count']} talii")
            if data['common_cards']:
                lines.append(f"    Częste karty: {', '.join(data['common_cards'][:3])}")
        lines.append("")
        
        lines.append("💡 META PREDYKCJE:")
        lines.append("  • Aggro dominuje → Control jest silny")
        lines.append("  • Dużo Control → Combo się przebija")
        lines.append("  • Balans meta → Midrange najlepszy")
        
        self.text_view.text='\n'.join(lines)
    
    def _analyze_archetypes(self, decks):
        archetypes=defaultdict(lambda: {'count':0, 'common_cards':[]})
        for deck in decks:
            arch_tags=deck.get('tags',[])
            if arch_tags:
                primary_arch=arch_tags[0]
                archetypes[primary_arch]['count']+=1
                # Analizuj częste karty w tym archetypie
                card_names=[c['name'] for c in deck.get('cards_text',[])]
                archetypes[primary_arch]['common_cards'].extend(card_names)
        
        # Znajdź najczęstsze karty dla każdego archetypu
        for arch in archetypes:
            counter=Counter(archetypes[arch]['common_cards'])
            archetypes[arch]['common_cards']=[card for card,_ in counter.most_common(5)]
        
        return archetypes

class ExpansionListView(ui.View):
    """Lista wszystkich rozszerzeń Hearthstone"""
    def __init__(self):
        super().__init__(name='Rozszerzenia HS')
        self.bg_color = (0, 0, 0, 0.7)
        self.table = ui.TableView()
        self.table.background_color = (0, 0, 0, 0.25)
        self.data_source = ui.ListDataSource([])
        self.table.data_source = self.data_source
        self.table.delegate = self
        self.add_subview(self.table)
        self.load_expansions()
        
    def layout(self):
        self.table.frame = (10, 10, self.width-20, self.height-20)
        
    def load_expansions(self):
        items = []
        for exp in HS_EXPANSIONS:
            items.append(f"{exp['year']} - {exp['name']} ({exp['type']})")
        self.data_source.items = items
        
    def tableview_did_select(self, tv, section, row):
        exp = HS_EXPANSIONS[row]
        console.hud_alert(f"{exp['name']} ({exp['year']})", 'success', 1.0)
        tv.selected_row = (-1, -1)

class Main(ui.View):
    def __init__(self):
        super().__init__(name=f'HS Deck Manager – {__version__}'); self.bg_color='black'
        self.decks=DeckStore(); self.sessions=SessionStore()
        self.bg=ui.ImageView(); self.bg.image=self.decks.get_bg_uiimage(); self.bg.content_mode=ui.CONTENT_SCALE_ASPECT_FILL; self.add_subview(self.bg)
        self.overlay=ui.View(bg_color=(0,0,0,0.30)); self.add_subview(self.overlay)
        self.class_bar=ui.ScrollView(); self.class_bar.shows_horizontal_scroll_indicator=False; self.class_bar.shows_vertical_scroll_indicator=False; self.add_subview(self.class_bar)
        self.class_buttons=[]; self.class_button_by_label={}
        for label in HS_CLASSES:
            b=ui.Button(title=self._title_with_icon(label,0)); style_button(b); b.action=self._make_class_action(label)
            self.class_bar.add_subview(b); self.class_buttons.append(b); self.class_button_by_label[label]=b
        
        # Nowe przyciski funkcji - ZASTĄPIONO btn_shop z btn_whizbang
        self.btn_clip=ui.Button(title='📋 wklej z gry', action=self.do_import_clipboard); style_button(self.btn_clip)
        self.btn_export=ui.Button(title='💾 Backup', action=self.do_export); style_button(self.btn_export)
        self.btn_bg=ui.Button(title='🎨 Tło', action=self.change_bg); style_button(self.btn_bg)
        self.btn_launch=ui.Button(title='🎮 Gra', action=self.launch_game); style_button(self.btn_launch)
        self.btn_stats=ui.Button(title='📊 Stats', action=self.show_global_stats); style_button(self.btn_stats)
        self.btn_meta=ui.Button(title='📈 Meta', action=self.show_meta_analytics); style_button(self.btn_meta)
        self.btn_expansions=ui.Button(title='📀 Expansions', action=self.show_expansions); style_button(self.btn_expansions)
        self.btn_whizbang=ui.Button(title='🎪 Whizbang', action=self.show_whizbang_decks); style_button(self.btn_whizbang)  # NOWY PRZYCISK
        
        for v in [self.btn_clip,self.btn_export,self.btn_bg,self.btn_launch,self.btn_stats,self.btn_meta,self.btn_expansions,self.btn_whizbang]: self.add_subview(v)
        self.table=ui.TableView(); self.table.background_color=(0,0,0,0.25)
        self.ds=DeckDataSource(self.decks); self.table.data_source=self.ds; self.table.delegate=self; self.add_subview(self.table)
        self.ver_lbl=ui.Label(text=f"HS Deck Manager – {__version__} : {__author__}", text_color=(1,1,1,0.55))
        self.ver_lbl.font=('<System>',12); self.ver_lbl.alignment=ui.ALIGN_RIGHT; self.add_subview(self.ver_lbl)
        self.active_label='Wszystkie'; self.refresh()
        self.right_button_items = [ui.ButtonItem(title='📋', action=self.show_changelog)]

    def layout(self):
        self.bg.frame=(0,0,self.width,self.height); self.overlay.frame=(0,0,self.width,self.height)
        p=10; w=self.width-2*p
        self.class_bar.frame=(p,p,w,40); self._layout_class_buttons()
        row1=self.class_bar.y+self.class_bar.height+6
        
        # Zmieniony układ przycisków - 4 w rzędzie
        btn_w=(w-12)//4; btn_h=36
        self.btn_clip.frame=(p,row1,btn_w,btn_h)
        self.btn_export.frame=(p+btn_w+4,row1,btn_w,btn_h)
        self.btn_bg.frame=(p+2*btn_w+8,row1,btn_w,btn_h)
        self.btn_launch.frame=(p+3*btn_w+12,row1,btn_w,btn_h)
        
        row2=row1+btn_h+4
        self.btn_stats.frame=(p,row2,btn_w,btn_h)
        self.btn_meta.frame=(p+btn_w+4,row2,btn_w,btn_h)
        self.btn_expansions.frame=(p+2*btn_w+8,row2,btn_w,btn_h)
        self.btn_whizbang.frame=(p+3*btn_w+12,row2,btn_w,btn_h)
        
        self.table.frame=(p,row2+btn_h+12,w,self.height-(row2+btn_h+12)-p-22)
        self.ver_lbl.frame=(p, self.height-20-p, w, 16)
    
    def _layout_class_buttons(self):
        x=0; y=0; h=self.class_bar.height
        for b in self.class_buttons:
            b.size_to_fit(); bw=b.width+20; b.frame=(x,y,bw,h); x+=bw+6
        self.class_bar.content_size=(x,h)
    
    def _compute_counts(self):
        decks=self.decks.db.get('decks',[]); total=len(decks); counts={label:0 for label in HS_CLASSES}; counts['Wszystkie']=total
        for d in decks:
            canon=canonical_class_label(d.get('class',''))
            if canon in counts: counts[canon]+=1
        return counts
    
    def _title_with_icon(self, label, count):
        return f"{CLASS_ICONS.get(label,'🃏')} {label} ({count})"
    
    def _apply_counts_and_styles(self):
        counts=self._compute_counts()
        for label,btn in self.class_button_by_label.items():
            btn.title=self._title_with_icon(label, counts.get(label,0))
            if label==self.active_label: style_button_active(btn)
            else: style_button(btn)
        self._layout_class_buttons()
    
    def _make_class_action(self, label):
        def _act(sender):
            self.decks.set_class_filter('' if label=='Wszystkie' else label); self.active_label=label; self.refresh(); console.hud_alert(f"Filtr: {label}",'success',0.4)
        return _act
    
    def refresh(self):
        self.decks.apply_filter(''); self.ds.reload_from(self.decks.filtered); self.table.reload(); self._apply_counts_and_styles()
    
    def tableview_did_select(self, tv, section, row):
        deck=self.decks.filtered[row]; clipboard.set(deck['deckstring']); console.hud_alert('Skopiowano deck-code','success',0.5)
        DetailView(deck, self.decks, on_saved=self.refresh, open_game_cb=self.open_game_for_deck).present('sheet'); tv.selected_row=(-1,-1)
    
    def open_game_for_deck(self, deck):
        SessionForm(deck, self.sessions, on_saved=lambda: self.show_stats(deck)).present('sheet')
    
    def show_stats(self, deck): StatsView(deck, self.sessions).present('sheet')
    
    def show_global_stats(self, sender): 
        QuickStatsView(self.decks, self.sessions).present('sheet')
    
    def show_meta_analytics(self, sender):
        MetaAnalyticsView(self.decks, self.sessions).present('sheet')
    
    def show_expansions(self, sender):
        ExpansionListView().present('sheet')
    
    def show_whizbang_decks(self, sender):
        """Pokazuje listę talii Whizbanga i Zayle"""
        WhizbangListView().present('sheet')
    
    def show_changelog(self, sender):
        """Pokazuje historię zmian zamiast ustawień"""
        changelog_text = f"""
HS Deck Manager {__version__}

Historia zmian:
• Wersja 8.3.2 - Dodano listę talii Whizbanga i Zayle
• Wersja 8.3.1 - Dodano przycisk sklepu Battle.net
• Wersja 8.3.0 - Ultimate Edition
• Wersja 8.2.0 - Zaawansowana analiza AI
• Wersja 8.1.0 - System optymalizacji talii
• Wersja 8.0.0 - Pełna przebudowa interfejsu

Funkcje:
• Zarządzanie taliami Hearthstone
• Zaawansowana analiza AI
• Statystyki i metaanaliza
• Śledzenie sesji gry
• Optymalizacja talii
• Pełna baza rozszerzeń
• Lista talii Whizbanga
"""
        console.alert('Historia wersji', changelog_text, 'OK', hide_cancel_button=True)
    
    def do_import_clipboard(self, s):
        txt=(clipboard.get() or '').strip()
        if not txt: console.hud_alert('Schowek jest pusty.','error',1.0); return
        self._parse_and_add(txt)
    
    def _parse_and_add(self, text):
        try: decks=parse_many(text)
        except Exception as e: console.hud_alert(f'Błąd importu: {e}','error',1.2); return
        a,u=self.decks.bulk_add(decks); self.refresh(); console.hud_alert(f'Zaimportowano: {a} nowych, zaktualizowano: {u}','success',1.2)
    
    def do_export(self, s):
        save_json(DB_PATH,self.decks.db); save_json(SESS_PATH,self.sessions.db); console.hud_alert('Backup zapisany','success',0.8)
    
    def change_bg(self, s):
        pil_img=photos.pick_image()
        if not pil_img: console.hud_alert('Anulowano','error',0.8); return
        self.bg.image=self.decks.set_bg_from_pil(pil_img); self.refresh(); console.hud_alert('Tło zaktualizowane','success',0.8)
    
    def launch_game(self, s):
        ok = webbrowser.open('hearthstone://')
        if ok: console.hud_alert('Otwieram Hearthstone...','success',0.6)
        else: console.hud_alert('Brak obsługi URL hearthstone://','error',1.2)

if __name__ == '__main__':
    if not globals().get('_HS_APP_RUNNING'):
        globals()['_HS_APP_RUNNING'] = True
        Main().present('fullscreen', hide_title_bar=False)
