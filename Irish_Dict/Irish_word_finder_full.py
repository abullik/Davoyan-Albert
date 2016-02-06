import re
original = open('edil.html','r', encoding = 'utf-8')

main_form, forms = [], [] # main_form for the word; forms for its forms
previous_line = ''
regular = '([^\<]+)'      # distinguishing all charactes except '<' (the beginning of a tag)

# searching forms
for line in original:
    line = line.strip()
    global_line = previous_line + line
    if not main_form:
        main_form = re.findall('<h3 headword_id=.*?>\s*' + regular, global_line, re.UNICODE)
    if not forms:
        forms = re.findall('Forms:\s*' + regular, global_line, re.UNICODE)
    previous_line = line

# forming the dictionary
all_forms = {main_form[0]: forms[0] if forms else None}
print(all_forms)