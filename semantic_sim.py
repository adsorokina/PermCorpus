import urllib.request
from urllib.parse import quote
import string
import pymorphy2


def sem_sim(w1,w2):
    url = 'http://rusvectores.org/ruwikiruscorpora/{0}__{1}/api/similarity/'.format(quote(w1),quote(w2))
    response = urllib.request.urlopen(url) 
    text = response.read().decode('utf-8-sig')
    return (text.split('\t')[0])

def count_ss(part_of_speech):
    crossdict = part_of_speech+ '_crossdict.csv'
    fi = open(crossdict, 'r', encoding='utf-8-sig').readlines()
    stopwords = ['и', 'а', 'без', 'в',
                 'к', 'до', 'о', 'от', 'по']
    morph = pymorphy2.MorphAnalyzer()
    
    for line in fi:
        try:
            fo = open(crossdict.replace('.', '_ss.'), 'a', encoding='utf-8-sig')
            l = line.split('\t')
            ktr = l[2].replace(',:();|',' ').replace('\s{2,}', ' '),
            utr = l[3].replace(',:();|',' ').replace('\s{2,}', ' ')

            ktrwords = []
            utrwords = []
            if ' ' in ktr:
                for w in ktr.split(' '):                
                    if '.' in w: continue
                    elif w in stopwords: continue
                    ktrwords.append(morph.parse(w)[0].normal_form.replace('ё','е'))
            else:
                ktrwords.append(morph.parse(ktr)[0].normal_form.replace('ё','е'))
                    
            if ' ' in utr:
                for w in utr.split(' '):                
                    if '.' in w: continue
                    elif w in stopwords: continue
                    utrwords.append(morph.parse(w)[0].normal_form.replace('ё','е'))
            else:
                utrwords.append(morph.parse(utr)[0].normal_form.replace('ё','е'))

            if len(utrwords) == 0 or len(ktrwords) == 0: continue
            
            ss = []
            for kw in ktrwords:
                for uw in utrwords:
                    se_si = sem_sim(kw, uw)
                    if se_si == "Unknown":
                        se_si = 0
                    ss.append(float(se_si))
            
        except urllib.error.HTTPError:
            print('HTTPError at linе:', line)
            continue
        
        fo.write(line.strip('\n')+'\t'+str(max(ss))+'\n')
        fo.close()
        


