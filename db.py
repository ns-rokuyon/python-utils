# coding: utf-8
import sqlite3
import collections


class SQLite3(object):
    """
    sqlite3 wrapper
    """
    def __init__(self, dbpath, noload=False):
        self.dbpath = dbpath
        self.conn = None
        self.batch_count = 0
        self.table_names = {'sqlite_master'}
        if not noload:
            self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.dbpath)
        self.table_names |= set(self.tables())

    def tables(self):
        return [t.tbl_name for t in self.select('sqlite_master')]

    def _tablecheck(func):
        def f(self, table, *args, **kwargs):
            if not table in self.table_names:
                raise ValueError('Invalid table name = {}'.format(table))
            return func(self, table, *args, **kwargs)
        return f

    @_tablecheck
    def count(self, table, where=None):
        if where:
            wh = ' and '.join(['{} = {}'.format(k,v) for k,v in where.items()])
            sql = 'select count(*) from {} where {}'.format(table, wh)
        else:
            sql = 'select count(*) from {}'.format(table)
        cur = self.conn.execute(sql)
        return cur.fetchone()[0]

    @_tablecheck
    def insert(self, table, values, replace=True, batch=1):
        placeholder = ','.join(['?' for _ in values])
        if replace:
            sql = 'insert or replace into {} values ({})'.format(
                    table, placeholder)
        else:
            sql = 'insert into {} values ({})'.format(
                    table, placeholder)
        self.conn.execute(sql, values)
        self.batch_count += 1
        self.commit_batch(batch)

    @_tablecheck
    def select(self, table, where=None, limit=None):
        if where:
            wh = ' and '.join(['{} = {}'.format(k,v) for k,v in where.items()])
            sql = 'select * from {} where {}'.format(table, wh)
        else:
            sql = 'select * from {}'.format(table)

        if limit:
            sql = '{} limit {}'.format(sql, int(limit))

        cur = self.conn.execute(sql)
        cols = [ d[0] for d in cur.description ]

        Row = collections.namedtuple('Row', cols)

        for c in cur:
            row = Row._make(c)
            yield row

    def commit(self):
        self.conn.commit()
        self.batch_count = 0

    def commit_batch(self, batch):
        if self.batch_count >= batch:
            self.commit()
