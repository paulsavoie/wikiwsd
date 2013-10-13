# -*- coding: utf-8 -*-
'''
This file contains the code which allows to easily evaluate
the database of the disambiguation library - by executing
it, a command-line interface is presented to the user to
enter the necessary configuration values

Author: Paul Laufer
Date: Jun 2013

'''

from wsd.evaluation import Evaluator
from wsd.evaluation import SampleReader
import sys
import os
import time
import logging

LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
SAMPLE_FILE = 'samples.xml'

'''requests the required values from the user through the command-line
and starts the evaluation process
'''
def evaluate():
    print '-' * 80
    print '- This is the interactive evaluation program'
    print '-' * 80 + '\n'

    choice = -1
    while choice < 1 or choice > 2:
        print 'Would you like to'
        print '\t(1)  read samples from the wiki dump file'
        print '\t(2)  evaluate the samples'

        choice = raw_input('Please enter your choice: ')
        try:
            choice = int(choice)
        except:
            pass

    print

    if choice == 1: # read samples

        path = 'not existing'
        while not os.path.exists(path):
            path = raw_input('Please enter the path to the wikipedia dump file (.xml): ').strip()

        numSamples = 0
        while numSamples <= 0:
            new_numSamples = raw_input('Select the number of samples to use for evaluation (10): ').strip()
            if len(new_numSamples) == 0:
                numSamples = 10
            else:
                try:
                    numSamples = 0
                    numSamples = int(new_numSamples)
                except:
                    pass

        answer = ''
        while answer != 'y' and answer != 'n' and answer != 'yes' and answer != 'no':
            answer = raw_input('This step will require up to several minutes depending on how many items are parsed. Do you want to continue? (y/n): ').strip().lower()
        print
        if answer[0] == 'y':
            logging.basicConfig(filename='evaluation-1.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
            print 'Starting to read %d samples from %s...' % (numSamples, path)
            reader = SampleReader(path, numSamples, output=SAMPLE_FILE)
            time.clock()
            reader.read()
            total = round(time.clock())
            minutes = total / 60
            seconds = total % 60
            print 'Finished after %d minutes and %d seconds' % (minutes, seconds)
            print 'Finished reader samples'
        else:
            print 'Aborting!'

    else: # evaluate samples

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

            answer = ''
            while answer != 'y' and answer != 'n' and answer != 'yes' and answer != 'no':
                answer = raw_input('This step will require up to an hour to perform. Do you want to continue? (y/n): ').strip().lower()
            print
            if answer[0] == 'y':
                logging.basicConfig(filename='evaluation-2.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
                print 'Starting evaluation %s:%s...' % (host, port)
                evaluation = Evaluator(SAMPLE_FILE)
                time.clock()
                result = evaluation.run()
                total = round(time.clock())
                minutes = total / 60
                seconds = total % 60
                print 'Finished after %d minutes and %d seconds' % (minutes, seconds)
                print 'Evaluation done! - precision: %d%%, recall: %d%%' % (round(result['precision']*100), round(result['recall']*100))
            else:
                print 'Aborting!'


if __name__ == '__main__':
    evaluate()