import re
import os

"""Counts weighted levenshtein distance between every pair of lexemes 
from two dictionaries (txt-files) for the part of speech given"""

def load_lexemes(lex_file):
    N = {}
    file = open(lex_file, 'r', encoding='utf-8-sig').read()
    lexemes = re.findall('-lexeme *\n((?: [^\r\n]*\n)+)', file, flags=re.DOTALL)
    print("Load lexemes from", lex_file)
    print(len(lexemes))
    
    for lex in lexemes:
        mLex = re.search(' lex: *([^\r\n ]+)', lex, flags=re.DOTALL)
        if mLex is None:
            continue
        lemma = mLex.group(1)

        mStem = re.search(' stem: *([^\r\n ]+)', lex, flags=re.DOTALL)
        if mStem is None:
            continue
        stem = mStem.group(1)
        
        mTrans = re.search(' trans_ru: *([^\r\n\d]+)\n', lex, flags=re.DOTALL)
        if mTrans is None:
            continue
        trans_ru = mTrans.group(1)
        N[lemma] = [stem, trans_ru]
        
    return N

"""
def short_load_lexemes(lex_file):
    N = {}
    file = open (lex_file, 'r', encoding='utf-8-sig').read()
    lexemes = re.findall(u'-lexeme *\n((?: [^\r\n]*\n)+)', file, flags=re.DOTALL)
    print("Load lexemes from", lex_file)
    print(len(lexemes))
    
    for lex in lexemes:
        mLex = re.search(u' lex: *([^\r\n ]+)', lex, flags=re.DOTALL)
        if mLex is None:
            continue
        lemma = mLex.group(1)

        mStem = re.search(u' stem: *([^\r\n ]+)', lex, flags=re.DOTALL)
        if mStem is None:
            continue
        stem = mStem.group(1)
        
        mTrans = re.search(u' trans_ru: *([^\r\n\d]+)\n', lex, flags=re.DOTALL)
        if mTrans is None:
            continue
        trans_ru = mTrans.group(1)
        N[lemma] = [stem, trans_ru]
        
    return N"""


def distance(a, b):
    # Calculates the Levenshtein distance between a and b.
    n, m = len(a), len(b)
    # Costs for phonological regularities (Kpv, Udm): cost
    d = {('ӧ','о'): 0.2,
         ('ӧ','э'): 0.2,
         ('а','о'): 0.2,
         ('у','а'): 0.2,
         
         ('ӧ','е'): 0.4,       
         ('а','я'): 0.4,
         ('е','о'): 0.4,
         ('в','л'): 0.4,
                  
         ('о','у'): 0.6,  
         ('я','и'): 0.6,
         ('е','ё'): 0.6,
         ('б','в'): 0.6,
         
         ('ш','ж'): 0.8,         
         ('ч','ц'): 0.8}
    
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n 
                
    current_row = range(n+1) # Keep current and previous row, not entire matrix
       
    for i in range(1, m+1):        
        previous_row, current_row = current_row, [i]+[0]*n
        for j in range(1,n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if a[j-1] != b[i-1] :
                try:
                    change+= d [(a[j-1], b[i-1])]
                except KeyError:
                    change +=1    
            current_row[j] = min(add, delete, change)
    return current_row[n]


def compare(komi_D, udmurt_D, part_of_speech):
    outfile='dicts/'+part_of_speech+'_crossdict.csv'
    # Set bounds for Levenstein distance depending on word length
    dictlen = {2: 0.6,
               3: 1,
               4: 1.2,
               5: 2,
               6: 2.2,
               7: 2.4,
               8: 2.4,
               9: 2.6,
               10: 2.6}
    
    for komi_w in komi_D.keys():
        f = open(outfile, 'a', encoding='utf-8-sig' )   
        filter_match = open('dicts/'+part_of_speech+'_filter_match.csv','a',encoding='utf-8-sig')        
        n = 0
        
        for udmurt_w in udmurt_D.keys():
            
            # Filter: remove words with length difference more than 2
            komi_len, udmurt_len = len(komi_w), len(udmurt_w)            
            if komi_len - udmurt_len > 2 or udmurt_len - komi_len > 2:
                continue

            # Filter: remove words that have similar form and translation 
            komi_tr1, udm_tr1 = [], []            
            for i in komi_D[komi_w][1].split(' '):
                if '.' in i: continue
                else: komi_tr1.append(i)                
            komi_tr = ' '.join(komi_tr1)

            for i in udmurt_D[udmurt_w][1].split(' '):
                if '.' in i: continue
                else: udm_tr1.append(i)
            udm_tr = ' '.join(udm_tr1)
           
            if komi_w == udmurt_w and komi_tr == udm_tr:
                filter_match.write(u'\t'.join([komi_w, komi_D[komi_w][1], udmurt_w, udmurt_D[udmurt_w][1]])+'\n')
                break
                        
            dist = distance(komi_D[komi_w][0], udmurt_D[udmurt_w][0])
            try:
                if dist <= dictlen[komi_len]:
                    f.write(u'\t'.join([komi_w, udmurt_w, komi_D[komi_w][1], udmurt_D[udmurt_w][1], str(komi_len), str(udmurt_len), str(dist)])+'\n')

            # If length of the lexeme is out of the dictionary
            except KeyError: 
                if komi_len > 10 and dist < 2.6:
                    f.write(u'\t'.join([komi_w, udmurt_w, komi_D[komi_w][1], udmurt_D[udmurt_w][1], str(komi_len), str(udmurt_len), str(dist)])+'\n')
           
        f.close()
        filter_match.close()    
        
def count_levenshtein_distance(part_of_speech):
    if os.access('../dicts/udmurt', os.F_OK) == 'False' or os.access('../dicts/udmurt', os.F_OK) == 'False':
        print('There is not enough dictionaries to compare.')
        
    udm_D = load_lexemes('../dicts/udmurt/udm_lexemes_'+part_of_speech+'.txt')
    komi_D = load_lexemes('../dicts/komi/komi_lexemes_'+part_of_speech+'.txt')
    compare(komi_D, udm_D, part_of_speech)
