__author__ = 'abullik'
from lxml import html
from urllib.request import urlopen
import csv

linksfile = open('links.txt', 'w')
colnames = ['path', 'author', 'sex', 'birthday', 'header', 'created', 'sphere',
            'genre_fi', 'type', 'topic', 'chronotop', 'style', 'audience_age', 'audience_level',
            'audience_size', 'source', 'publication', 'publisher', 'publ_year',
            'medium', 'country', 'region', 'language']

months = {'Январь': '.01.', 'Февраль': '.02.', 'Март': '.03.', 'Апрель': '.04.',
          'Май': '.05.', 'Июнь': '.06.', 'Июль': '.07.', 'Август': '.08.',
          'Сентябрь': '.09.', 'Октябрь': '.10.', 'Ноябрь': '.11.', 'Декабрь': '.12.'}

metatable = open('metatable.csv', 'w', encoding='utf-8')
writer = csv.writer(metatable, quoting=csv.QUOTE_NONE, escapechar='', quotechar='', delimiter='\t')


def getlink(url):
    '''
    The function crawls the given url, finds every link at
    the page and returns only the links that belong to different
    rubrics of articles and, more specifically, that
    contain the word 'item', i.e. the links leading to the articles
    :param url:
    :return:
    '''
    url = urlopen(url).read().decode()
    tree = html.fromstring(url)
    links = tree.xpath('//a/@href')
    cleared = []
    for i in range(len(links)):
        if not links[i].startswith('http:'):
            links[i] = 'http://www.belrab.ru' + links[i]
        if links[i].startswith('http://www.belrab.ru/rubriki') and links[i].find('/item/') != -1:
            cleared.append(links[i])
    return cleared


def removedubl(list):
    new_one = set(list)
    modified = [i for i in new_one]
    return modified


def metadata(url):
    page = url
    url = urlopen(url).read().decode()
    tree = html.fromstring(url)
    table = [''] * 23

    header = tree.find_class('me-inline')
    table[4] = header[0].text_content().strip()

    created = tree.find_class('itemDateCreated me-inline')
    date = created[0].text_content().strip().split()
    date[1] = months[date[1]]
    table[5] = "".join(date)

    table[6] = 'публицистика'
    table[11] = 'нейтральный'
    table[12] = 'н-возраст'
    table[13] = 'н-уровень'
    table[14] = 'районная'
    table[15] = page
    table[16] = 'Белорецкий рабочий'
    table[19] = 'газета'
    table[20] = 'Россия'
    table[21] = 'Белорецкий'
    table[22] = 'ru'
    return table


url = 'http://www.belrab.ru'
all_links = getlink(url)

for i in all_links:
    all_links += getlink(i)
    all_links = removedubl(all_links)
for i, v in enumerate(all_links):
    linksfile.write(str(i + 1) + ': ' + str(v) + '\n')
linksfile.close()

writer.writerow(colnames)
for i in all_links:
    writer.writerow(metadata(i))

metatable.close()
