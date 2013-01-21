#-*- coding:utf-8 -*-

import tornado.database
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        db = tornado.database.Connection(host='localhost', database='blog', user='root')
        entries = db.query("select * from articles order by id desc;")
        self.render("index.html", entries = entries)


class EntryHandler(tornado.web.RequestHandler):

    def get(self, story_id):
        db = tornado.database.Connection(host='localhost', database='blog', user='root')
        entry = db.get("select * from articles where id=" + story_id)

        self.render("entry.html", entry=entry)


class NewPostHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("new.html")

    def post(self):
        db = tornado.database.Connection(host='localhost', database='blog', user='root')
        query = u"""
                insert into articles (title, subtitle, body, creation_date)
                values('%(TITLE)s', '%(SUBTITLE)s', '%(BODY)s', '%(CREATION_DATE)s');
                """ % {
                    'TITLE': self.get_argument('title'),
                    'SUBTITLE': self.get_argument('subtitle'),
                    'BODY': self.get_argument('body'),
                    'CREATION_DATE': self.get_argument('creation-date')
                }
        executed = db.execute(query)
        self.redirect('/story/%s' % executed)
        self.write("It works!!!")


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/story/([0-9]+)", EntryHandler),
    (r"/new", NewPostHandler)
])


if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
