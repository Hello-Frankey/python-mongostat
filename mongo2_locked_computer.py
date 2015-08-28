class LockStatsInfo():
    'Class for lock statistic, which include namespace, read and write lock time.'

    def __init__(self, ns, read, write):
        self.ns = ns
        self.read = read
        self.write = write

    def total(self):
        return (self.read + self.write)


class LockStatsDiff():
    'Class for difference between two lock statistics.'

    def __init__(self, prev, current):
        self.ns = prev.ns
        self.read = current.read - prev.read
        self.write = current.write - prev.write


