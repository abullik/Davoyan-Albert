georg = open('georgia.txt', 'r', encoding='UTF-8')
georgnew = open('target.txt', 'w', encoding='UTF-8')
letters = {
    'ა': 'ɑ',
    'ბ': 'b',
    'გ': 'g',
    'დ': 'd',
    'ე': 'ɛ',
    'ვ': 'v',
    'ზ': 'z',
    'ჱ': 'ɛj',
    'თ': 'tʰ',
    'ი': 'i',
    'კ': 'k\'',
    'ლ': 'l',
    'მ': 'm',
    'ნ': 'n',
    'ჲ': 'j',
    'ო': 'ɔ',
    'პ': 'p\'',
    'ჟ': 'ʒ',
    'რ': 'r',
    'ს': 's',
    'ტ': 't\'',
    'ჳ': 'wi',
    'უ': 'u',
    'ფ': 'pʰ',
    'ქ': 'kʰ',
    'ღ': 'ʁ',
    'ყ': 'q\'',
    'შ': 'ʃ',
    'ჩ': 'tʃ',
    'ც': 'ts',
    'ძ': 'dz',
    'წ': 'tsʼ',
    'ჭ': 'tʃʼ',
    'ხ': 'χ',
    'ჴ': 'q',
    'ჯ': 'dʒ',
    'ჰ': 'h',
    'ჵ': 'hɔɛ'
}

for line in georg:
    for i in line:
        if i in letters:
            line = line.replace(i, letters[i])
    georgnew.write(line)

georg.close()
georgnew.close()
