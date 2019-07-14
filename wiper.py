'''
Reads command line arguments and calls the deleting function.
'''


from argparse import ArgumentParser
from db_operator import deleter

parser = ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-n", dest="number")
group.add_argument("-a", dest="wipe", action="store_true")
args = vars(parser.parse_args())

deleter(args)
