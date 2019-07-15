from argparse import ArgumentParser
from db_operator import deleter

desc = '''
Удаление записи об одной книге или полное очищение БД.
'''

parser = ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-n", dest="number", help="Удалить книгу по номеру")
group.add_argument("-a", dest="wipe", action="store_true",
                   help="Удалить все книги")
args = vars(parser.parse_args())

deleter(args)
