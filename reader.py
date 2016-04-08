# coding: utf-8
import csv

class DataReader(object):
    def __init__(self, filepath):
        self.filepath = filepath
        
    def __call__(self, *args, **kwargs):
        return self.read(*args, **kwargs)

    def read(self, head=None):
        with open(self.filepath, 'r') as fp:
            for i, line in enumerate(fp):
                yield line
                if head is not None and i > head:
                    break


class CSVReader(DataReader):
    def __init__(self, csvfile, columns=None, header=False):
        super(CSVReader, self).__init__(csvfile)
        self.columns = columns
        self.header = header

    def read(self, head=None):
        with open(self.filepath, 'r') as fp:
            csvf = csv.reader(fp)
            if self.header and not isinstance(self.columns, list):
                self.columns = next(csvf)

            for i, line in enumerate(csvf):
                yield line
                if head is not None and i > head:
                    break

