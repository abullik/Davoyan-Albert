import xml.etree.ElementTree as ET
tree = ET.parse('stal.xml')
root = tree.getroot()
text = []
for line in root.iter('se'):
    if 'lang' in line.attrib:
        continue
    text.append(line.text)

dictionary = dict()
with open('cedict_ts.u8', 'r', encoding='utf-8') as chinese:
    for line in chinese:
        if line[0] == '#':
            continue
        line = line.split()
        dictionary[line[1]] = dictionary.get(line[1], []) + [' '.join(line[2:])]

def parse_sent(sent, dictionary):
    result = []
    seq = ''
    for c in sent:
        if c not in dictionary and len(c) == 1:
            if seq != '':
                result.append((seq, dictionary[seq]))
                seq = ''
            result.append(c)
        else:    
            seq += c
            if seq not in dictionary:
                result.append((seq[:-1], dictionary[seq[:-1]]))
                seq = seq[-1]
    return result

def write_to_xml(parsed, filename):
    
    import re
    import xml.etree.ElementTree as ET
    html = ET.Element('html')
    ET.SubElement(html, None).text = '\n'
    head = ET.SubElement(html, 'head')
    ET.SubElement(head, None).text = '\n'
    ET.SubElement(html, None).text = '\n'
    body = ET.SubElement(html, 'body')
    ET.SubElement(body, None).tail = '\n'
    se = ET.SubElement(body, 'se')
    ET.SubElement(se, None).text = '\n'
    for i in parsed:
        if len(i) == 1:
            ET.SubElement(se, None).tail = i
            continue
        w = ET.SubElement(se, 'w')
        for j in i[1]:
            transcr = re.findall('^(\[[\w:\s]+\])', j)[0].strip('[]')
            sem = re.findall('(/.*/)', j)[0].strip('/')
            sem = sem.replace('/', ', ')
            ET.SubElement(w, 'ana', lex=i[0], transcr=transcr, sem=sem)
        ET.SubElement(se, None).tail = '\n'
        ET.SubElement(w, None).text = i[0]
    ET.SubElement(body, None).tail = '\n'
    ET.SubElement(html, None).tail = '\n'
    
    ET.ElementTree(html).write(filename, encoding='utf-8', xml_declaration=True, short_empty_elements=False)

sent_no = 1
for i in text:
    sentence = parse_sent(i, dictionary)
    write_to_xml(sentence, 'chinese_sentences/Sentence' + str(count) +'.xml')
    sent_no += 1

