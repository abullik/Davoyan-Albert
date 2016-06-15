import os
os.system('python2 WikiExtractor.py -o kywiki kywiki.xml')

def cleaning(path):
    all_in_one = []
    for root, dirs, files in os.walk(path):
        for file in files:
            with open(root + '/' + file, 'r',encoding='utf-8') as text:
                for line in text:
                    if '<doc' in line or '</doc>' in line or 'MediaWiki' in line:
                        continue
                    else:
                        all_in_one += line.split()
    return all_in_one
            
wiki = cleaning('./kywiki/AA')

import string, re, csv
freq_dict = dict()
for token in wiki:
    if re.search('[0-9\uf02d]', token):
        continue
    token = token.strip(string.punctuation + '–«»—•”“'+ '&lt;br&gt')
    if len(token) != 0:
        token = token.lower()
        freq_dict[token] = freq_dict.get(token, 0) + 1

sorted_dict = sorted(freq_dict.items(), key= lambda x:x[1], reverse=True)
      
with open('list_of_freq.tsv', 'w', encoding='utf-8') as result:
    writer = csv.writer(result, delimiter='\t')
    writer = writer.writerows(sorted_dict)

