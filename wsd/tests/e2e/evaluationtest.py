import logging
import time
import os
import difflib
from wsd.evaluation import Evaluator

class EvaluationTest():

    def test_evaluation_alkane(self):
        path = './wsd/tests/data/alkane.json'
        log_path = './tmp/evaluation-alkane.log'
        logging_format = '%(levelname)s:\t%(message)s'
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format=logging_format, filemode='w+')
        #evaluator = EvaluatorOld(path)
        evaluator = Evaluator('./wsd/tests/data/alkane.xml')
        start = time.clock()
        percentage = evaluator.run()
        seconds = round(time.clock() - start)

        success = True

        # evaluate log
        # read and delete log file
        flog = open(log_path, 'r')
        log = flog.readlines()
        flog.close()
        
        fref = open('./wsd/tests/data/alkane-reference.log', 'r')
        reference_log = fref.readlines()
        fref.close()

        diff = difflib.ndiff(reference_log, log)
        diff_ok = True
        lines_diff = 0
        for line in diff:
            if len(line) > 0 and line[0] != ' ':
                # ignore cumulative seconds with 0.0 relevance
                if line[:34] != '- INFO:\t\tcumulative 2nd (0.000000)' and line[:34] != '+ INFO:\t\tcumulative 2nd (0.000000)':
                    if diff_ok:
                        print 'ERROR: the log file is not how expected (see %s):' % (log_path)
                    diff_ok = False
                    #print line.strip('\n')
                    if line[0] == '-' or line[0] == '?':
                        lines_diff += 1

        if lines_diff != 0:
            print '------ %d lines are different' % (lines_diff)

        if diff_ok == False:
            success = False
        else:
            os.unlink(log_path)

        # evaluate percentage
        if round(percentage*100) != 84:
            print 'ERROR: percentage was expected to be 84, was %d' % round(percentage*100)
            success = False

        print 'Test finished - took %02d:%02d' % (seconds / 60, seconds % 60)

        return success