__author__ = 'abullik'
import os, glob
'''
The following loops find files
in the subfolders of the previously made
folders 2015 and 2016. They call mystem to
parse the files into different formats (xml
and plain text). The program also creates
new folders corresponding to the original files'
folders and puts the parsed into them.
'''

for file in glob.glob('*/*/*.txt'):
    stem = 'mystem.exe -cdig --format xml'
    output = file[:-3] + 'xml'
    output = os.path.join('xml', output)
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    os.system(stem + ' ' + file + ' ' + output)

for file in glob.glob('*/*/*.txt'):
    stem = 'mystem.exe -cdig'
    output = os.path.join('plaintext', file)
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    os.system(stem + ' ' + file + ' ' + output)
