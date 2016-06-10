
# coding: utf-8

# In[1]:

class VerbGovernment:
    
    def __init__(self, verb, table):
        self.verb = verb
        self.table = table
        self.examples = dict()
        self.possible_preps = self.pmi_preps()
        import pymorphy2
        self.morph = pymorphy2.MorphAnalyzer()
        
    def isProperName(self, word):
        bad_tags = ['Surn', 'Abbr', 'Name', 'Patr', 'Geox', 'Orgn', 'Trad']
        tags = self.morph.parse(word)
        for row in tags:
            for bad_tag in bad_tags:
                if {bad_tag} in row.tag:
                    return True
        return False
    
    def pmi_nouns(self):
        import math,statistics
        from time import time
        start = time()

        nouns = dict()
        for index, _ in self.table[self.table.lemma == self.verb].iterrows():
            if self.table['gramm'].loc[index][2] not in 'mpgn':
                words = 0
                left = 1
                while self.table['link'].loc[index - left] != 'PUNC' and words < 5:
                    words += 1 
                    current_word = self.table['lemma'].loc[index - left]
                    if self.table['POS'].loc[index - left] == 'N' and not self.isProperName(current_word):
                        nouns[current_word] = nouns.get(current_word, 0) + 1 
                    left +=1

                right = 1
                words = 0
                while self.table['link'].loc[index + right] != 'PUNC' and words < 5:
                    words += 1
                    current_word = self.table['lemma'].loc[index + right]
                    if self.table['POS'].loc[index + right] == 'N' and not self.isProperName(current_word):
                        nouns[current_word] = nouns.get(current_word, 0) + 1 
                    right +=1
        
        nouns_pmi = dict()
        words_number = len(self.table[(self.table['link'] != 'PUNC') & (self.table['head'] != 'PUNC')])
        verb_freq = len(self.table[self.table.lemma == self.verb]) / words_number
        margin = statistics.mean(nouns.values())

        for noun in nouns.keys():
            if nouns[noun] < margin:
                continue
            noun_freq = len(self.table[self.table.lemma == noun]) / words_number
            together_freq = nouns[noun] / words_number
            nouns_pmi[noun] = math.log(together_freq / (noun_freq * verb_freq))
            
        print('Calculation time: {}'.format((time() - start) / 60))
        return sorted(nouns_pmi, key=nouns_pmi.get, reverse=True)[:5]
        
        
    
    def pmi_preps(self):
        import math,statistics
        
        prepositions = dict()
        for index, _ in self.table[self.table.lemma == self.verb].iterrows():
            if self.table['gramm'].loc[index][2] not in 'mpgn':
                words = 0
                left = 1
                while self.table['link'].loc[index - left] != 'PUNC' and words < 5 and index - left >= 0:
                    words += 1 
                    current_word = self.table['lemma'].loc[index - left]
                    if self.table['POS'].loc[index - left] == 'S':
                        prepositions[current_word] = prepositions.get(current_word, 0) + 1 
                    left +=1

                right = 1
                words = 0
                while self.table['link'].loc[index + right] != 'PUNC' and words < 5 and index + right < len(self.table):
                    words += 1
                    current_word = self.table['lemma'].loc[index + right]
                    if self.table['POS'].loc[index + right] == 'S':
                        prepositions[current_word] = prepositions.get(current_word, 0) + 1 
                    right +=1

        prep_pmi = dict()
        words_number = len(self.table[(self.table['link'] != 'PUNC') & (self.table['head'] != 'PUNC')])
        verb_freq = len(self.table[self.table.lemma == self.verb]) / words_number
        margin = statistics.mean(prepositions.values())

        for prep in prepositions.keys():
            if prepositions[prep] < margin:
                continue
            prep_freq = len(self.table[self.table.lemma == prep]) / words_number
            together_freq = prepositions[prep] / words_number

            prep_pmi[prep] = math.log(together_freq / (prep_freq * verb_freq))

        return sorted(prep_pmi, key=prep_pmi.get, reverse=True)[:5]

    
    def get_case(self, tag):
        if tag[0] == 'S':
            return tag[3]
        elif tag[0] == 'N':
            return tag[4]
        elif tag[0] == 'P':
            return tag[5]
        elif tag[0] == 'M':
            return tag[-1]
        elif tag[0] == 'A':
            return tag[5]

    def get_config(self, tags, tokens, pmi_preps):
        config = []
        case = ''
        for (tag, token) in zip(tags, tokens):
            if tag == '' or tag[0] in 'RAI' or tag[0] == 'V' and tag[2] in 'mpg':
                continue
            elif tag[0] in 'S' and token not in pmi_preps:
                case = self.get_case(tag)
            elif tag[0] == 'S' and token in pmi_preps:
                config.append(token)
            elif tag[0] == 'C':
                config.append(tag[0])
            elif tag[0] in 'V':
                config.append(tag[0])
                case = ''
            elif tag[0] in 'NPM':
                if tag[0] in 'NP' and self.get_case(tag) == case:
                    continue
                if len(config) != 0 and config[-1][0] == 'P' and tag[0] == 'N' and config[-1][1] == self.get_case(tag):
                    config[-1] = 'N' + self.get_case(tag)
                if len(config) != 0 and config[-1][0] == 'M' and tag[0] == 'N' and self.get_case(tag) in 'ga':
                    config[-1] = 'N' + self.get_case(tag)
                elif (len(config) == 0 or config[-1] != (tag[0] + self.get_case(tag))):
                    config.append(tag[0] + self.get_case(tag))
                case = ''
        
        result = []
        conj = False
        is_verb = False
        for i in range(0, len(config)):
            if config[i][0] == 'M':
                continue
            if conj and is_verb and config[i] == 'V':
                break
            if config[i] == 'C':
                conj = True
                continue
            if config[i] == 'V':
                is_verb = True
            if not ((config[i - 1][0] == 'M' or config[i - 1][0] == 'S')  and config[i] == 'Ng') or i == 0:
                if config[i][0] in 'PN':
                    config[i] = 'S' + config[i][1]
                if config[i] != 'Sn':
                    result.append(config[i])

        for tag in tags[::-1]:
            if tag and tag in ['что', 'как','чтобы','когда']:
                result.append(tag)
            elif tag and tag not in ['что', 'как','чтобы', 'когда']:
                break

    #         if config[i] == 'C' and config[i-1][1] == config[i+1][1]:
    #             result.remove(config[i])
    #             result.remove(config[i+1])
        return ['Sn'] + result
    
    def extractor(self, verb, table):
        
        import csv
        from time import time
        start = time()

        configs = []

        global examples
        
        sentence_id = 0
        for index, _ in table[table.lemma == self.verb].iterrows():
            if table['gramm'].loc[index][2] not in 'mpgn':
                tags  = [''] * 11
                tokens = [''] * 11
                tags[5] = table['gramm'].loc[index]
                tokens[5] = table['token'].loc[index]
                words = 0
                left = 1
                change_gen = False
                skip_sentence = False
                if table['lemma'].loc[index - 1] == 'не' and index >= 1:
                    left += 1
                    change_gen = True
                while table['link'].loc[index - left] != 'PUNC' and words < 5 and index - left >= 0:
                    words += 1
                    tags[5 - words] = table['gramm'].loc[index-left]
                    tokens[5 - words] = table['token'].loc[index-left]

                    left += 1

                right = 1
                words = 0
                while table['link'].loc[index + right] != 'PUNC' and words < 5 and index + right < len(table):
                    words += 1
                    tags[5 + words] = table['gramm'].loc[index + right]
                    tokens[5 + words] = table['token'].loc[index + right]
                    if tags[5 + words][0] == 'N' and self.get_case(tags[5 + words]) == 'g' and change_gen:
                        change_gen = False
                        tags[5 + words] = tags[5 + words][:4] + 'a' + tags[5 + words][5:]
                    right +=1

                if table['gramm'].loc[index + right] == ',' and words < 5 and table['gramm'].loc[index + right + 1] in ['что', 'как','чтобы', 'когда']:
                    tags[6 + words] = table['lemma'].loc[index + right + 1]
                    tokens[6 + words] = table['token'].loc[index + right + 1]

                current_config = self.get_config(tags, tokens, self.possible_preps)
                configs.append(current_config)
                config_str = self.sort_args(' '.join(current_config))
                if (config_str not in self.examples or len(self.examples[config_str]) < 5) and sentence_id != table.sent_id.loc[index]:
                    self.examples[config_str] = self.examples.get(config_str, []) + [table.sent_id.loc[index]]
                    sentence_id = table.sent_id.loc[index]

        print('Sorry for making you wait for {}'.format(round((time() - start) / 60, 2)), 'minutes')
        return configs
    
   
    
    def get_sent(self, table, sent_num):
        
        result = ' '.join(table[table.sent_id == sent_num].token)
        result = result.replace('\t', '\"')
        for punc in ['.', ',', '!', '?', ':', ';',')']:
            result = result.replace(' ' + punc, punc)
        return result
    
    def sort_args(self, config):
        config = config.split()[1:]
        if len(config) >= 4:
            return 'Sn ' + ' '.join(config)
        config.remove('V')
        new_config = []
        for i in range(len(config)):
            if config[i] in self.possible_preps:
                continue
            elif i > 0 and config[i - 1] in self.possible_preps:
                new_config.append(config[i - 1] + ' ' + config[i])
            else:
                new_config.append(config[i])
            
        return ('Sn V ' + ' '.join(sorted(new_config))).strip()
        
    def government(self):
        import pandas as pd
        
#         frames = []
#         for i in range(1, 5):
#             frames.append(pd.read_csv('.\corpora\corpus-i-part' + str(i) + '.txt', delimiter='\t', header = 0))
#         table = pd.concat(frames)
        table = pd.read_csv('.\corpora\corpus-i-part1.txt',delimiter='\t',header=0)
        configs = self.extractor(self.verb, table)
        
        import random, statistics
        config_freq = {}

        for i in configs:
            config_str = self.sort_args(' '.join(i))
            config_freq[config_str] = config_freq.get(config_str, 0) + 1

        med = statistics.median(config_freq.values())
        average = statistics.mean([i for i in config_freq.values() if i > med])
        
        final_result = []
        
        for chain in sorted(config_freq, key=config_freq.get, reverse=True):
            final_result.append((chain, config_freq[chain], self.get_sent(table, random.choice(self.examples[chain]))))
            if config_freq[chain] < average:
                break
        return final_result
    


# In[2]:

import pandas as pd
document = pd.read_csv('.\corpora\corpus-i-part1.txt', delimiter='\t', header=0)


# In[3]:

najti = VerbGovernment('найти', document)


# In[4]:

idti = VerbGovernment('идти', document)


# In[5]:

vesti = VerbGovernment('вести', document)


# In[6]:

answer = najti.government()


# In[7]:

for row in answer:
    print('\n', row[0], row[1], '\n', row[2], '\n')


# In[8]:

najti.possible_preps


# In[9]:

vesti.pmi_nouns()

