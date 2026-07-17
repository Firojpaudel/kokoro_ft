import os
import sys
import re
import csv
from misaki import en

_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEPALI_SUFFIXES = {
    'हरूले': 'ɦʌruːleː',
    'हरूलाई': 'ɦʌruːlaːiː',
    'हरूको': 'ɦʌruːkoː',
    'हरूका': 'ɦʌruːkaː',
    'हरूमा': 'ɦʌruːmaː',
    'हरू': 'ɦʌruː',
    'लाई': 'laːiː',
    'ले': 'leː',
    'को': 'koː',
    'का': 'kaː',
    'की': 'kiː',
    'मा': 'maː',
    'बाट': 'baːʈʌ',
    'सँग': 'sʌŋɡʌ',
    'देखि': 'dekʰi',
    'समेत': 'sʌmeːt',
    'तिर': 'tiɾʌ',
    'भन्दा': 'bʰʌndaː',
    'द्वारा': 'dwaːraː',
    'ै': 'ai',
    'नै': 'nʌi',
    'पछि': 'pʌtsʰi',
    'पट्टि': 'pʌʈʈi',
    'ने': 'neː'
}

G2P_CONSONANTS = {
    'क': 'k', 'ख': 'kʰ', 'ग': 'ɡ', 'घ': 'ɡʰ', 'ङ': 'ŋ',
    'च': 'ts', 'छ': 'tsʰ', 'ज': 'dz', 'झ': 'dzʰ', 'ञ': 'n',
    'ट': 'ʈ', 'ठ': 'ʈʰ', 'ड': 'ɖ', 'ढ': 'ɖʰ', 'ण': 'n',
    'त': 't', 'थ': 'tʰ', 'द': 'd', 'ध': 'dʰ', 'न': 'n',
    'प': 'p', 'फ': 'pʰ', 'ब': 'b', 'भ': 'bʰ', 'म': 'm',
    'य': 'j', 'र': 'r', 'ल': 'l', 'व': 'w',
    'श': 's', 'ष': 's', 'स': 's', 'ह': 'h',  # Map ह to standard h
    'श्र': 'sr', 'क्ष': 'kʃ', 'त्र': 'tr', 'ज्ञ': 'ɡj'
}

G2P_VOWELS = {
    'अ': 'ʌ', 'आ': 'aː', 'इ': 'i', 'ई': 'iː', 'उ': 'u', 'ऊ': 'uː',
    'ऋ': 'ri', 'ए': 'eː', 'ऐ': 'ʌi', 'ओ': 'oː', 'औ': 'ʌu'
}

G2P_MATRAS = {
    'ा': 'aː', 'ि': 'i', 'ी': 'iː', 'ु': 'u', 'ू': 'uː',
    'ृ': 'ri', 'े': 'eː', 'ै': 'ʌi', 'ो': 'oː', 'ौ': 'ʌu'
}

def devanagari_to_ipa(word):
    word = word.replace('ज्ञ', 'ग्य्')
    ipa = []
    i = 0
    n = len(word)
    while i < n:
        char = word[i]
        
        if char in G2P_VOWELS:
            ipa.append(G2P_VOWELS[char])
            i += 1
            continue
            
        if char in G2P_CONSONANTS:
            base_ipa = G2P_CONSONANTS[char]
            has_halant = False
            has_matra = False
            matra_val = ''
            
            j = i + 1
            while j < n and word[j] == '्':
                has_halant = True
                j += 1
            
            if not has_halant and j < n and word[j] in G2P_MATRAS:
                has_matra = True
                matra_val = G2P_MATRAS[word[j]]
                i = j
                
            if has_halant:
                ipa.append(base_ipa)
                i = j - 1
            elif has_matra:
                ipa.append(base_ipa + matra_val)
            else:
                if i + 1 == n:
                    ipa.append(base_ipa)
                else:
                    ipa.append(base_ipa + 'ʌ')
            i += 1
            continue
            
        if char == 'ं':
            next_char = word[i + 1] if i + 1 < n else ''
            if next_char in 'पफबभम':
                ipa.append('m')
            elif next_char in 'कखगघङ':
                ipa.append('ŋ')
            else:
                ipa.append('n')
            i += 1
            continue
            
        if char == 'ँ':
            if ipa:
                ipa.append('̃')
            i += 1
            continue
            
        i += 1
    return "".join(ipa)

class NepaliHybridG2P:
    def __init__(self, dict_path=os.path.join(_repo_root, "data/dictionary_data.csv")):
        self.word_dict = {}
        self.en_g2p = en.G2P()
        
        print(f"Loading dictionary from {dict_path}...")
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter='$')
                next(reader, None)
                for row in reader:
                    if len(row) >= 6:
                        word = row[1].strip()
                        ipa = row[5].strip()
                        if ipa.startswith('/') and ipa.endswith('/'):
                            ipa = ipa[1:-1]
                        if word and ipa:
                            self.word_dict[word] = ipa
            print(f"Loaded {len(self.word_dict)} words from dictionary.")
        except Exception as e:
            print(f"Error loading dictionary: {e}")

    def clean_rule_ipa(self, ipa_str):
        # Map curly ɦ to standard h
        res = ipa_str.replace('ɦ', 'h')
        allowed_chars = set(" !\"(),.:;?AIOQSTWYabcdefhijklmnopqrstuvwxyzæçðøŋœɐɑɒɔɕɖəɚɛɜɟɡɣɤɥɨɪɯɰɲɳNHɸɹɻɽɾʁʂʃʈʊʋʌʎʒʔʝʣʤʥʦʧʨʰʲˈˌː̃βθχᵊᵝᵻ—“”…→↓↗↘ꭧ")
        res = "".join(c for c in res if c in allowed_chars)
        return res

    def strip_suffixes_recursive(self, word):
        if word in self.word_dict:
            return self.word_dict[word]
            
        for suffix in sorted(NEPALI_SUFFIXES.keys(), key=len, reverse=True):
            if word.endswith(suffix) and len(word) > len(suffix):
                root = word[:-len(suffix)]
                root_ipa = self.strip_suffixes_recursive(root)
                if root_ipa:
                    if root_ipa.endswith('ʌ'):
                        root_ipa = root_ipa[:-1]
                    # Clean up suffix IPA curly ɦ
                    suffix_ipa = NEPALI_SUFFIXES[suffix].replace('ɦ', 'h')
                    return root_ipa + suffix_ipa
        return None

    def convert_word(self, word):
        if re.match(r'^[\u0900-\u097F]+$', word):
            # A. Direct / Recursive suffix lookup
            res = self.strip_suffixes_recursive(word)
            if res:
                return self.clean_rule_ipa(res)
            
            # B. Fallback to custom Devanagari rules
            try:
                raw_phonemes = devanagari_to_ipa(word)
                return self.clean_rule_ipa(raw_phonemes)
            except Exception:
                return ""
        elif re.match(r'^[a-zA-Z\-_]+$', word):
            try:
                en_phonemes, _ = self.en_g2p(word)
                allowed_chars = set(" !\"(),.:;?AIOQSTWYabcdefhijklmnopqrstuvwxyzæçðøŋœɐɑɒɔɕɖəɚɛɜɟɡɣɤɥɨɪɯɰɲɳNHɸɹɻɽɾʁʂʃʈʊʋʌʎʒʔʝʣʤʥʦʧʨʰʲˈˌː̃βθχᵊᵝᵻ—“”…→↓↗↘ꭧ")
                clean_en = "".join(c for c in en_phonemes if c in allowed_chars)
                return clean_en
            except Exception:
                return word
        return word

    def __call__(self, text):
        tokens = re.findall(r'[\u0900-\u097F]+|[a-zA-Z\-_]+|[^\u0900-\u097F\sa-zA-Z\-_]+|\s+', text)
        result_phonemes = []
        for token in tokens:
            if re.match(r'^[\u0900-\u097F]+$', token) or re.match(r'^[a-zA-Z\-_]+$', token):
                ph = self.convert_word(token)
                if ph:
                    result_phonemes.append(ph)
            else:
                result_phonemes.append(token)
        return "".join(result_phonemes), None

# Test on the user's exact paragraph (replacing hyphen with space before parsing)
test_text = (
    "यो दिनचर्या कस्तो हुन्छ भने, बिहान उठ्ने बित्तिकै mobile मा notifications चेक गर्नै पर्छ । "
    "त्यसपछि एक कप तातो chiya नपिई त काम गर्नै जाँगर चल्दैन । आज अलि बढी नै workload छ, अनि "
    "deadlines पनि नजिकै आइसके । दिउँसो खाना खाएपछि अलि productive हुने कोसिस गर्छु, नत्र "
    "बेलुकासम्म धेरै कुरा pending बस्छ । बेलुका चाहिँ साथीहरूसँग भेटेर अलि बढी guff-gaff भयो भने "
    "मात्रै मन हल्का हुन्छ, अनि बल्ल relax गर्न पाइन्छ ।"
)

g2p = NepaliHybridG2P()
# Simulate normalizer's hyphen space replacement
normalized_text = test_text.replace('-', ' ')
ph, _ = g2p(normalized_text)
print("\nGenerated Phonemes:\n", ph)
