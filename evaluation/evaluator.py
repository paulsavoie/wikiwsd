import logging

class Evaluator():

    def __init__(self, inputFile, db_host='localhost', db_port=27017):
        self._input_path = inputFile
        self._db_host = db_host
        self._db_port = db_port

    def run(self):
        return 0.0