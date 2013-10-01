class MockMySQLConnection():

    def __init__(self):
        self._cursor = MockMySQLCursor()
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True

class MockMySQLCursor():

    def __init__(self):
        self.queries = []
        self.return_vals = {}

    def execute(self, *args):
        query = args[0]
        arguments = []
        if len(args) > 1:
            arguments = args[1]
        index = 0
        while (query.find('%s') != -1):
            query = query.replace('%s', str(arguments[index]), 1)
            index += 1
        self.queries.append(query)
        if (query in self.return_vals):
            return self.return_vals[query]
        return None