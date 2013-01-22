#-*- coding:utf-8 -*-

import tornado.database
import tornado.ioloop
import tornado.web
import tornado.httpclient

# from MySQLdb.connections import AsyncConnection

from adisp import process
from adb import Database

class BaseHandler(tornado.web.RequestHandler):

    adb = Database(
                   driver="MySQLdb",
                   host='localhost',
                   database='blog',
                   user='root',
                   password='',
                   num_threads=3,
                   tx_connection_pool_size=2,
                   queue_timeout=0.001)

    db = tornado.database.Connection(
                   host='localhost',
                   database='blog',
                   user='root')


class MainHandler(BaseHandler):

    # @tornado.web.asynchronous
    # def get(self):
    #     self.entries = self.adb.async_query("select * from articles order by id desc;",
    #                                    self.query_done)
    #     # client = tornado.httpclient.AsyncHTTPClient()
    #     # client.fetch("http://localhost:8888/story/1", self.query_done)

    # def query_done(self, *stuff):
    #     # self.finish(self.render("index.html", entries = stuff[0]))
    #     self.write('success!!')
    #     self.finish()


    @process
    @tornado.web.asynchronous
    def get(self):
        entries = yield self.adb.runQuery("select * from articles order by id desc;")
        self.render("index.html", entries = entries)


class EntryHandler(BaseHandler):

    @process
    @tornado.web.asynchronous
    def get(self, story_id):
        entry = yield self.adb.runQuery("select * from articles where id=" + story_id)
        self.render("entry.html", entry=entry[0])


class NewPostHandler(BaseHandler):

    def get(self):
        self.render("new.html")

    @process
    @tornado.web.asynchronous
    def post(self):
        query = u"""
                insert into articles (title, subtitle, body, creation_date)
                values('%(TITLE)s', '%(SUBTITLE)s', '%(BODY)s', '%(CREATION_DATE)s');
                """ % {
                    'TITLE': self.get_argument('title'),
                    'SUBTITLE': self.get_argument('subtitle'),
                    'BODY': self.get_argument('body'),
                    'CREATION_DATE': self.get_argument('creation-date')
                }
        executed = yield self.adb.runOperation(query)
        import pdb; pdb.set_trace()
        self.redirect('/story/%s' % executed)


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/story/([0-9]+)", EntryHandler),
    (r"/new", NewPostHandler)
])


if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
