import csv, requests
metatable = open('metatable.csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(
    metatable,
    quoting=csv.QUOTE_NONE,
    escapechar='',
    quotechar='',
    delimiter='\t')
col_names = [
    'Full Name', 'Sex', 'VK_id', 'Birth Date', 'Relation', 'Languages'
]

search_url = 'https://api.vk.com/method/users.search'
search_params = {
    'access_token':
    '14ff99154e15b92963e63900e2e874af6365ac0788f7ca03b79097a009b263ca6433b0b4793f4da2bae01',
    'count': 200,
    'city': 1396,  #г. Белокуриха - 1396
    'country': 1,
    'fields': 'bdate, sex, occupation, relation, personal'
}

find_users = requests.get(
    search_url,
    params=search_params)  #находим 200 человек из города Белокуриха

data = find_users.json()

fields = {
    'first_name': 0,
    'last_name': 0,
    'sex': 1,
    'uid': 2,
    'bdate': 3,
    'relation': 4,
    'langs': 5
}

for i in range(1, len(data['response'])):
    metadata = [''] * 6
    for feature in data['response'][
            i]:  #ищем интересующие нас социологические данные по пользователям
        if feature in fields.keys():
            metadata[fields[feature]] += ' ' + str(data['response'][i][
                feature])
            metadata[fields[feature]] = metadata[fields[feature]].strip()
        if feature == 'personal':
            try:
                metadata[fields['langs']] = data['response'][i][feature][
                    'langs']
            except:
                pass
    writer.writerow(metadata)  #записываем данные в таблицу

    target_id = data['response'][i]['uid']
    wall_url = 'https://api.vk.com/method/wall.get'
    wall_params = {'owner_id': target_id, 'count': 100, 'filter': 'owner'}
    get_wall = requests.get(
        wall_url,
        params=wall_params)  #выкачиваем записи со стены пользователя через id
    posts = get_wall.json()
    with open(
            'VK_Belokurikha\Posts_of_' + str(target_id) + '.txt',
            'a',
            encoding='utf-8') as current_file:  #записываем посты в файлы
        try:
            for post in posts['response'][1:]:
                post['text'] = post['text'].replace('<br>', '\n')
                current_file.write(post['text'] + '\n')
        except:
            pass

metatable.close()
