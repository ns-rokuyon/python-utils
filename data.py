# coding: utf-8
import os
import random
import collections
from glob import glob

class Sample(object):
    def __init__(self, path, label=None, group=None):
        self.path = os.path.abspath(path)
        self.label = label
        self.group = group

    def __repr__(self):
        return 'Sample(path={}, label={}, group={})'.format(
                self.path, self.label, self.group)

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other


class Dataset(object):
    def __init__(self, directory):
        self.directory = directory
        self.labels = [os.path.basename(d) for d in 
                       sorted([d for d in glob(os.path.join(self.directory, '*'))
                               if not d.startswith('.') 
                               and not d.startswith('_') 
                               and os.path.isdir(d)])]
        self.data = {}
        for l in self.labels:
            _files = [Sample(f, label=l) for f in 
                      glob(os.path.join(self.directory, l, '*')) 
                      if os.path.isfile(f)]
            self.data[l] = _files

    def __getitem__(self, key):
        return self.data[key]

    def __getattr__(self, name):
        return getattr(self.data, name)

    def keys(self):
        return self.labels

    def group(self, g):
        return {k: [d for d in ds if d.group == g] for k, ds in self.data.items()}

    def trainset(self):
        return self.group('train')

    def valset(self):
        return self.group('val')

    def testset(self):
        return self.group('test')

    def random_split(self, pers=None, shuffle=True):
        G = collections.namedtuple('GroupSplitNum', 
                ('train', 'val', 'test'))
        gpers = G(0.8, 0.1, 0.1) if pers is None else G(*pers)
        for l in self.labels:
            random.shuffle(self.data[l])

            n = len(self.data[l])
            train_n = int(gpers.train * n)
            val_n = int(gpers.val * n)
            test_n = train_n - val_n

            for s in self.data[l][0:train_n]:
                s.group = 'train'
            for s in self.data[l][train_n:train_n+val_n]:
                s.group = 'val'
            for s in self.data[l][train_n+val_n:]:
                s.group = 'test'

    def savelist(self, savedir, group, listtype='list'):
        groupdata = self.group(group)
        savefile = os.path.join(savedir, '{}.{}'.format(group, listtype))
        if os.path.exists(savefile):
            return False

        seps = {'list': ' ', 'csv': ',', 'tsv': '\t'}
        sep = seps.get(listtype)

        if not sep:
            return False

        with open(savefile, 'w') as fp:
            for label, data in groupdata.items():
                for d in data:
                    row = '{}{}{}\n'.format(d, sep, label)
                    fp.write(row)
