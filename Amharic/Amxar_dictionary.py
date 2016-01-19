table = open('amxar_table.tsv','r',encoding = 'utf-8')
table2 = open('amxar_target.tsv','w',encoding = 'utf-8')
concord={}
new_table=[]
for line in table:
    line = line.strip('\n')
    line = line.split('\t')
    new_table.append(line)
for i in range(len(new_table)):                 # итерация по индексам, отвечающим за строки
    for j in range(len(new_table[i])):          # нашли столбцы
        if i!=0 and j!=0:
            concord[new_table[i][j]]= new_table[i][0]+new_table[0][j]

for k,v in concord.items():
    print (k + ' : ' + v)

table2.close()

        
    
