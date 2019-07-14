'''
Reads command line arguments and calls the seeking function.
'''


from argparse import ArgumentParser
from db_operator import seek_book

parser = ArgumentParser()
parser.add_argument("-a", dest="author")
parser.add_argument("-n", dest="title")
parser.add_argument("-y", dest="bookdate")
args = vars(parser.parse_args())

seek_book(args)
