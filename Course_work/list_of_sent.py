
# coding: utf-8

# Запись предложений, где встречается глагол (verb), в файл, имя которого мы указываем в filename.

# In[2]:

import pandas as pd
def findsent(verb, table, filename):
    from time import time
    start = time()
    
    sentlist = open(filename, 'a',encoding='utf-8')
    for index, row in table[table.lemma == verb].iterrows():
        begin = index - row['word_num'] + 1
        end = index + 1
        while table['gramm'].loc[end] != 'SENT':
            end += 1
        for i in range(begin, end + 1):
            #if data['link'].loc[i] == 'PUNC' or pd.isnull(data['link'].loc[i]):
            #    sentlist.write(data['token'].loc[i])
            #else:
            if table['token'].loc[i] == '\t':
                sentlist.write('\"')
            else:
                sentlist.write(' ' + table['token'].loc[i])
        sentlist.write('\n')
    sentlist.close()
    print('Processing time: {}'.format((time() - start) / 60))


# In[3]:
import os
for doc in os.listdir(".\corpora"):
    doc = pd.read_csv(".\corpora\\" + doc,delimiter='\t',header=0,encoding='utf-8')
    findsent('идти', doc, 'list_of_sent.txt')

