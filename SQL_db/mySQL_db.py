
import mysql.connector, csv
cnx = mysql.connector.connect(host ='localhost', user='guest1', passwd='n76Je4=wx6H')

with open('metatable.csv', encoding='utf-8') as vk_table:
    reader = csv.reader(vk_table, delimiter='\t')
    cur = cnx.cursor()
    database = """create database guest1_ardavoyan"""
    cur.execute(database)
    change_db = """use guest1_ardavoyan"""
    cur.execute(change_db)
    table = """create table vk_people (
               Full_Name varchar(50),
               Sex char(1),
               VK_id varchar(15),
               Birth_date varchar(10),
               Relation char(1),
               Languages varchar(100))"""
    cur.execute(table)
    insert_query = ("insert into vk_people (Full_Name, Sex, VK_id, Birth_date, Relation, Languages) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
    for row in reader:
        data = tuple(row)
        cur.execute(insert_query, data)
        cnx.commit()
    cnx.close()


