# -*- coding: utf-8 -*-
'''
This file contains the code which allows to easily build
the database of the disambiguation library - by executing
it, a command-line interface is presented to the user to
enter the necessary configuration values

Author: Paul Laufer
Date: Jun 2013

'''

from wsd.creator import DBSetup, Creator
import sys
import os
import time
import logging

LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'

'''requests the configuration from the user through the command-line 
and starts the building process
'''
def build():
    print '-' * 80
    print '- This is the interactive build program which guides you'
    print '- through the build setup of the word sense disambugation'
    print '- module'
    print '-' * 80 + '\n'

    choice = -1
    while choice < 1 or choice > 4:
        print 'Would you like to'
        print '\t(1)  setup the database'
        print '\t(2)  prepare the database'
        print '\t(3)  create the disambiguation entries'
        print '\t(4)  learn the n-grams\n'

        choice = raw_input('Please enter your choice: ')
        try:
            choice = int(choice)
        except:
            pass

    print

    host = 'localhost'
    new_host = raw_input('Select the host of the MongoDB installation (localhost): ').strip()
    if len(new_host) != 0:
        host = new_host

    port = 0
    while port == 0:
        new_port = raw_input('Select the port of the MongoDB installation(27017): ').strip()
        if len(new_port) == 0:
            port = 27017
        else:
            try:
                port = 0
                port = int(new_port)
            except:
                pass

    if choice == 1: # setup the db
        answer = ''
        while answer != 'y' and answer != 'n' and answer != 'yes' and answer != 'no':
            answer = raw_input('This will erase all previous data from the database. Do you want to continue? (y/n): ').strip().lower()
        print
        if answer[0] == 'y':
            print 'Setting up database at %s:%s...' % (host, port)
            setup = DBSetup(host, port)
            setup.run()
            print 'Setup finished!'
        else:
            print 'Aborting!'

    elif choice == 2: # prepare the database
        path = 'not existing'
        while not os.path.exists(path):
            path = raw_input('Please enter the path to the wikipedia dump file (.xml): ').strip()
        answer = ''
        while answer != 'y' and answer != 'n' and answer != 'yes' and answer != 'no':
            answer = raw_input('This step will require several HOURS to perform. Do you want to continue? (y/n): ').strip().lower()
        print
        if answer[0] == 'y':
            logging.basicConfig(filename='preparation.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
            print 'Preparing database %s:%s...' % (host, port)
            setup = Creator(path, db_host=host, db_port=port, num_threads=8, max_queue_size=300, action='prepare')
            time.clock()
            setup.run()
            total = round(time.clock())
            minutes = total / 60
            seconds = total % 60
            print 'Finished after %d minutes and %02d seconds' % (minutes, seconds)
            print 'Preparation of database finished - detailed information can be found in preparation.log logfile!'
        else:
            print 'Aborting!'

    elif choice == 3: # create the disambiguation entries
        path = 'not existing'
        while not os.path.exists(path):
            path = raw_input('Please enter the path to the wikipedia dump file (.xml): ').strip()
        answer = ''
        while answer != 'y' and answer != 'n' and answer != 'yes' and answer != 'no':
            answer = raw_input('This step will require several DAYS to perform. Do you want to continue? (y/n): ').strip().lower()
        print
        if answer[0] == 'y':
            logging.basicConfig(filename='learning.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
            print 'Learning meanings %s:%s...' % (host, port)
            setup = Creator(path, db_host=host, db_port=port, num_threads=26, max_queue_size=300, action='learn')
            time.clock()
            setup.run()
            total = round(time.clock())
            minutes = total / 60
            seconds = total % 60
            print 'Finished after %d minutes and %d seconds' % (minutes, seconds)
            print 'Learning of disambiguations finished - find detailed information in "learning.log"'
        else:
            print 'Aborting!'

    else: # learn n-grams
        path = 'not existing'
        while not os.path.exists(path):
            path = raw_input('Please enter the path to the wikipedia dump file (.xml): ').strip()
        answer = ''
        while answer != 'y' and answer != 'n' and answer != 'yes' and answer != 'no':
            answer = raw_input('This step will require several DAYS to perform. Do you want to continue? (y/n): ').strip().lower()
        print
        if answer[0] == 'y':
            logging.basicConfig(filename='n-grams.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
            print 'Learning meanings %s:%s...' % (host, port)
            setup = Creator(path, db_host=host, db_port=port, num_threads=26, max_queue_size=300, action='ngrams')
            time.clock()
            setup.run()
            total = round(time.clock())
            minutes = total / 60
            seconds = total % 60
            print 'Finished after %d minutes and %d seconds' % (minutes, seconds)
            print 'Learning of n-grams finished - find detailed information in "n-grams.log"'
        else:
            print 'Aborting!'

if __name__ == '__main__':
    build()