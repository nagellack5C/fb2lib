from argparse import ArgumentParser
from db_operator import seek_book, fts_book

desc = '''
Поиск информации о книгах. Добавьте флаг -f для полнотекстового поиска
'''

parser = ArgumentParser(description=desc)
parser.add_argument("-a", dest="author", help="Имя автора")
parser.add_argument("-n", dest="title", help="Название книги")
parser.add_argument("-y", dest="bookdate", help="Дата издания")
parser.add_argument("-f", dest="fts", action="store_true",
                    help="Полнотекстовый поиск")
args = vars(parser.parse_args())

if not args["author"] and not args["title"] and not args["bookdate"]:
    print("Укажите хотя бы один аргумент")
else:
    seek_book(args)
    if args["fts"]:
        fts_book(args)
