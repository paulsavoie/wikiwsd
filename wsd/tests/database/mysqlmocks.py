class MockMySQLConnection():

    def __init__(self):
        self._cursor = MockMySQLCursor()
        self.closed = False
        self._last_query = None
        self.commited = 0

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True

    def commit(self):
        self.commited += 1

class MockMySQLCursor():

    def __init__(self):
        self.queries = []
        self.return_vals = {}

    def execute(self, *args):
        query = args[0]
        params = []
        if len(args) > 1:
            params = args[1]
        index = 0
        while (query.find('%s') != -1):
            query = query.replace('%s', str(params[index]), 1)
            index += 1
        self.queries.append(query)
        self._last_query = query

    def executemany(self, query, params):
        for item in params:
            copy = query
            index = 0
            while(copy.find('%s') != -1):
                copy = copy.replace('%s', str(item[index]), 1)
                index += 1
            self.queries.append(copy)
            self._last_query = copy

    def fetchone(self):
        if (self._last_query in self.return_vals):
            return self.return_vals[self._last_query]
        return None

    def fetchall(self):
        if (self._last_query in self.return_vals):
            return self.return_vals[self._last_query]
        return None
