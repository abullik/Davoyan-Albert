from lxml import etree


def xml_to_prs(xml_file, prs_file):
    input_file_xml = open(xml_file, 'r', encoding='utf-8')
    tree_xml = etree.parse(input_file_xml)
    root_xml = tree_xml.getroot()

    with open(prs_file, 'w', encoding='utf-8') as writer:
        writer.write(
            '#sentno\t#wordno\t#lang\t#graph\t#word\t#indexword\t#nvars\t#nlems\
                     \t#nvar\t#lem\t#trans\t#trans_ru\t#lex\t#gram\t#flex\t#punctl\t#punctr\t#sent_pos\n'
        )
        for sentno, sentence in enumerate(root_xml):
            for wordno, word in enumerate(sentence):
                word_list = []
                different_lex = []

                for lemma in word:
                    word_list.append(lemma)
                    if lemma.get('lex') not in different_lex:
                        different_lex.append(lemma.get('lex'))
                lemma = word[-1].tail.strip()
                punct = word.tail.strip()

                for tagno, tag in enumerate(word_list):
                    cap = 'cap' if tag.get('lex').istitle() else ''

                    gram = tag.get('gr').split(',')
                    lex = tag.get('gr').split(',')[0]
                    gram = ' '.join(gram[1:])
                    if tag.get('morph'):
                        gram += ' ' + tag.get('morph')

                    if wordno == 0:
                        sent_pos = 'bos'
                    elif wordno == len(sentence) - 1:
                        sent_pos = 'eos'
                    else:
                        sent_pos = ''

                    row = [
                        str(sentno + 1), str(wordno + 1), '', cap, lemma, '',
                        str(len(word)), str(len(different_lex)),
                        str(tagno + 1), tag.get('lex'), tag.get('trans'), '',
                        lex, gram, '', '', punct, sent_pos
                    ]
                    writer.write('\t'.join(row) + '\n')


def prs_to_xml(prs_file, xml_file):
    import csv
    file = open(prs_file, 'r', encoding='utf-8')
    input_file_prs = csv.reader(file, delimiter='\t')

    body = etree.Element('body')
    se = etree.Element('se')
    sentno = 0
    wordno = 0
    for row in input_file_prs:
        # Пропускаем мета
        if not row[0].isnumeric():
            continue

        if sentno != int(row[0]):
            sentno = int(row[0])
            if len(se):
                body.append(se)
            se = etree.Element('se')
            wordno = 0

        if wordno != int(row[1]):
            wordno = int(row[1])
            w = etree.Element('w')

        ana = etree.Element('ana')
        ana.attrib['lex'] = row[9]
        ana.attrib['trans'] = row[10]
        ana.attrib['gr'] = row[12] + ' ' + row[13]
        if row[6] == row[8]:
            ana.tail = row[4]

        w.append(ana)
        if row[6] == row[8]:
            w.tail = row[-2]
            se.append(w)

    output_file = open(xml_file, 'w', encoding='utf-8')
    output_file.write(
        etree.tostring(
            body, method='xml', pretty_print=True, encoding='utf-8').decode(
                'utf-8'))


import sys
if len(sys.argv) < 4:
    print('Вы ввели не все аргументы')
elif sys.argv[1] == 'xml_to_prs':
    xml_to_prs(sys.argv[2], sys.argv[3])
elif sys.argv[1] == 'prs_to_xml':
    prs_to_xml(sys.argv[2], sys.argv[3])
