import re
original = open('irishforms.html', 'r', encoding='utf-8')
words = []
first_word = False
regular = '(.*?)'
for line in original:
    line = line.strip()
    if first_word:
        words += re.findall('^' + regular + '<', line, re.UNICODE)
        break
    if re.search('Forms:$', line, re.DOTALL):
        words += re.findall('<h3 headword_id=.*>' + regular + '</h3>', line,
                            re.UNICODE)
        first_word = True

all_forms = {}
all_forms[words[0]] = words[1] if len(words) == 2 else None

print(all_forms)
