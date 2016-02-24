__author__ = 'abullik'
from lxml import html
from urllib.request import urlopen
import re, csv, os, shutil

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
    '''
    url = urlopen(url).read().decode()
    tree = html.fromstring(url)
    links = tree.xpath('//a/@href')
    cleared = []
    for i in range(len(links)):
        if not links[i].startswith('http:'):
            links[i] = 'http://www.belrab.ru' + links[i]
        if links[i].startswith('http://www.belrab.ru/rubriki') and links[i].find('/item/') != -1 \
                and not re.search('\?|#', links[i]):
            cleared.append(links[i])
    return cleared


def removedubl(list):                                # removes dublicates from the given list
    new_one = set(list)
    modified = [i for i in new_one]
    return modified


def metadata(url):
    '''
    The function crawls the given url
    and finds specific metadata for further
    creating of a table with the indicated data.
    The function returns a list with 23 slots
    containing different pieces of the data in
    question
    '''
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

def filefolder(url):
    '''
    The function crawls the given url,
    finds specific data, in particular, the
    article and some metadata, creates a file
    and writes the data to the file. Then the
    function creates a folder named after the
    year of the publication of the article and
    puts the file into another folder, named after
    the publication month, inside the previous one.
    If such file already exists in the path, the
    function removes the newly created one.
    '''
    page = url
    filename = re.findall('item/([\d\w-]*)', page)
    file = open(filename[0] + '.txt', 'w', encoding='utf-8')
    url = urlopen(url).read().decode()
    tree = html.fromstring(url)

    header = tree.find_class('me-inline')
    file.write('@ti ' + header[0].text_content().strip() + '\n')

    created = tree.find_class('itemDateCreated me-inline')
    date = created[0].text_content().strip().split()
    date[1] = months[date[1]]
    year = date[2]
    month = date[1].strip('.')
    date = "".join(date)
    file.write('@da ' + date + '\n')

    topic = re.findall('rubriki/(\w*)', page)
    file.write('@topic ' + topic[0] + '\n')

    file.write('@url ' + page + '\n' + '\n')

    introtext = tree.find_class('itemIntroText')
    file.write(introtext[0].text_content().strip() + '\n' + '\n')

    article = tree.find_class('itemFullText')
    file.write(article[0].text_content().strip())

    file.close()
    if not os.path.exists(year):
        os.makedirs(year)
    if not os.path.exists(year + '\\' + month):
        os.makedirs(year + '\\' + month)
    if not os.path.exists(year + '\\' + month + '\\' + filename[0] + '.txt'):
        shutil.move(filename[0] + '.txt', year + '\\' + month)
    else:
        os.remove(filename[0] + '.txt')

url = 'http://www.belrab.ru'
all_links = getlink(url)

for i in all_links:                                #iterates through the links found on the main page
    all_links += getlink(i)                        #and calls the function getlink for every link, removing
    all_links = removedubl(all_links)              #dublicates

for i, v in enumerate(all_links):                                   #creates a file containing a list of all the links
    linksfile.write(str(i + 1) + ': ' + str(v) + '\n')              #we are interested in from the website
linksfile.close()

writer.writerow(colnames)                                   #writes the list with the column names to the csv file
for i in all_links:                                         #and calls the function metadata for every link repeating
    writer.writerow(metadata(i))                            #the writing process for the generated lists of metadata
    filefolder(i)                                           #calls the function filefolder for every link

metatable.close()
