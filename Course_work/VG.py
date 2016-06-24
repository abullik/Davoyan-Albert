
class VerbGovernment:
    
    def __init__(self, verb, table=None):
        self.verb = verb
        if table != None:
            self.table = table
        self.possible_preps = []
        self.examples = dict()
        self.configs = []
        
    
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

    def get_config(self, tags, tokens, pmi_preps):
        config = []
        case = ''
        has_numeral = False
        for (tag, token) in zip(tags, tokens):
            if tag == '' or tag[0] in 'RAI' or tag[0] == 'V' and tag[2] in 'mpg':
                continue
            elif tag[0] in 'S' and token not in pmi_preps:
                case = self.get_case(tag)                                  #сохраняем падеж
            elif tag[0] == 'S' and token in pmi_preps:
                config.append(token)
            elif tag[0] == 'C':
                config.append(tag[0])
            elif tag[0] in 'V':
                config.append(tag[0])
                case = ''
                has_numeral = False
            elif tag[0] in 'NPM':
                if tag[0] == 'M':
                    num_case = self.get_case(tag)
                    has_numeral = True
                if tag[0] in 'NP' and self.get_case(tag) == case:        #удаляем, т.к. входит в предложную группу, такой же падеж
                    continue
                #удаляем указательные местоимение, т.к. такой же падеж, как и у сущ. перед ним
                if len(config) != 0 and config[-1][0] == 'P' and tag[0] == 'N' and config[-1][1] == self.get_case(tag):
                    config[-1] = 'N' + self.get_case(tag)
                new_case = num_case if tag[0] == 'N' and has_numeral else self.get_case(tag)
                #если предыдущий тэг не такой же, то записываем 
                if (len(config) == 0 or config[-1] != (tag[0] + new_case)):
                    config.append(tag[0] + new_case)
                case = ''
        
        result = []
        conj = False
        is_verb = False
        for i in range(0, len(config)):
            if config[i][0] == 'M':
                result.append('S' + config[i][1])
                continue
            if conj and is_verb and config[i] == 'V':
                break
            if config[i] == 'C':
                conj = True
                continue
            if config[i] == 'V':
                is_verb = True
            if not (config[i - 1][0] in 'S'  and config[i] == 'Ng') or i == 0:
                if config[i][0] in 'PN':
                    config[i] = 'S' + config[i][1]
                if config[i] != 'Sn':
                    result.append(config[i])
                    

        for tag in tags[::-1]:
            if tag and tag in ['что', 'как','чтобы','когда']:
                result.append(tag)
            elif tag and tag not in ['что', 'как','чтобы', 'когда']:
                break

        return ['Sn'] + result

    def combiner(self, config_str):
        import re
        if 'V' in config_str:
            config_str.remove('V')
        if 'Sn' in config_str:
            config_str.remove('Sn')

        config = []
        prep = ''
        for tag in config_str:
            if config != [] and tag in config:
                continue
            if re.search('[а-я]', tag):
                prep = tag + ' '
                continue
            config.append(prep + tag)
            prep = ''

        if 'Sa' in config:
            config.remove('Sa')
            result = ['Sn', 'V', 'Sa']
        else:
            result = ['Sn', 'V']

        result = result + sorted(config)
        final_result = []
        for i in range(len(result)):
            if i == 0 or not(result[i] in 'SgV' and result[i-1] == 'Sa'):
                final_result.append(result[i])
        return final_result

    def extractor(self, verb, table):
        import re

        # global examples
        
        sentence_id = 0
        for index, _ in table[table.lemma == self.verb].iterrows():
            if table['gramm'].loc[index][2] not in 'mpgn':
                tags  = [''] * 11
                tokens = [''] * 11
                tags[5] = table['gramm'].loc[index]
                tokens[5] = table['token'].loc[index]
                words = 0
                left = 1
                change_gen_left, change_gen_right = False, False
                if table['lemma'].loc[index - 1] == 'не' and index >= 1:
                    left += 1
                    change_gen_left, change_gen_right = True, True
                while table['lemma'].loc[index - left] not in [',','-',':','.','!','?',';'] and self.table['POS'].loc[index - left] != 'C' and words < 5 and index - left >= 0:
                    if re.search('\w', table['token'].loc[index-left]):
                        words += 1
                        tags[5 - words] = table['gramm'].loc[index-left]
                        tokens[5 - words] = table['token'].loc[index-left]
                        if tags[5 - words][0] in 'PN' and self.get_case(tags[5 - words]) == 'g' and change_gen_left:
                            change_gen_left = False
                            if tags[5 - words][0] == 'N':
                                tags[5 - words] = tags[5 - words][:4] + 'a' + tags[5 - words][5:]
                            else:
                                tags[5 - words] = tags[5 - words][:5] + 'a' + tags[5 - words][6:]
                    left += 1

                right = 1
                words = 0
                while table['lemma'].loc[index + right] not in [',','-',':','.','!','?',';'] and (self.table['POS'].loc[index + right - 1] != 'V' or right == 1) and words < 5 and index + right < len(table):
                    if re.search('\w', table['token'].loc[index+right]):
                        words += 1
                        tags[5 + words] = table['gramm'].loc[index + right]
                        tokens[5 + words] = table['token'].loc[index + right]
                        if tags[5 + words][0] in 'NP' and self.get_case(tags[5 + words]) == 'g' and change_gen_right:
                            change_gen_right = False
                            if tags[5 + words][0] == 'N':
                                tags[5 + words] = tags[5 + words][:4] + 'a' + tags[5 + words][5:]
                            else:
                                tags[5 + words] = tags[5 + words][:5] + 'a' + tags[5 + words][6:]
                    right +=1

                if table['gramm'].loc[index + right] == ',' and words < 5 and table['gramm'].loc[index + right + 1] in ['что', 'как','чтобы', 'когда']:
                    tags[6 + words] = table['lemma'].loc[index + right + 1]
                    tokens[6 + words] = table['token'].loc[index + right + 1]

                current_config = self.combiner(self.get_config(tags, tokens, self.possible_preps))
                if 'S-' not in current_config:
                    self.configs.append(current_config)
                    config_str = ' '.join(current_config)
                    if (config_str not in self.examples or len(self.examples[config_str]) < 3) and sentence_id != table.sent_id.loc[index]:
                        sentence_id = table.sent_id.loc[index]
                        self.examples[config_str] = self.examples.get(config_str, []) + [self.get_sent(table, sentence_id)]
                    

        print('Пожалуйста, подождите...')
#         return configs
    
   
    
    def get_sent(self, table, sent_num):
        
        result = ' '.join(table[table.sent_id == sent_num].token)
        result = result.replace('\t', '\"')
        for punc in ['.', ',', '!', '?', ':', ';',')','(']:
            if punc == '(':
                result = result.replace(punc + ' ', punc)
            else:
                result = result.replace(' ' + punc, punc)
        return result
        
    def government(self):
        import pandas as pd
        
        import random, statistics
        config_freq = {}

        for i in self.configs:
            config_str = ' '.join(i)
            config_freq[config_str] = config_freq.get(config_str, 0) + 1

        med = statistics.median(config_freq.values())
        average = statistics.mean([i for i in config_freq.values() if i > med])
        
        final_result = []
        
        for chain in sorted(config_freq, key=config_freq.get, reverse=True):
            final_result.append((chain, config_freq[chain], self.examples[chain]))
            if config_freq[chain] < average:
                break
        return final_result

    def changeTable(self, new_table):
        self.table = new_table
        if not self.possible_preps:
            self.possible_preps = self.pmi_preps()
        self.extractor(self.verb, self.table)

import pandas as pd
verb = input('Введите глагол:')
configs = VerbGovernment(verb)

for num in range(1, 5):
    document = pd.read_csv('.\corpora\corpus-i-part' + str(num) + '.txt', delimiter='\t', header=0)
    configs.changeTable(document)
answer = configs.government()
for row in answer:
    print('\n', row[0], row[1], '\n', '\n'.join(row[2]), '\n')

