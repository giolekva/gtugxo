import os

from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app

import game as game_manager


class NewGameHandler(webapp.RequestHandler):
    def get(self):
        board = game_manager.New()
        game_manager.Save(board)
        self.redirect('/game/%s' % board.Id())


class GameHandler(webapp.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(GameHandler, self).__init__(*args, **kwargs)

    def get(self):
        if self._Prepare():
            self.Handle()

    def post(self):
        if self._Prepare():
            self.Handle()

    def Handle(self):
        raise Error('Unimplemented')

    def _Prepare(self):
        user = users.get_current_user()
        if user:
            self._user = user.user_id()
        else:
            self.redirect(users.create_login_url(self.request.path))
            return False

        self._id = self._GetGameId()
        if self._id:
            self._board = game_manager.Load(self._id)
        else:
            self._board = None
        return True

    def _GetGameId(self):
        id = self.request.get('id')
        if id:
            return id

        tmp = self.request.path.split('/')
        if len(tmp) == 3 and tmp[1] == 'game':
            return tmp[2]

    def _RenderTemplate(self, template_name, context):
        path = os.path.join(os.path.dirname(__file__), template_name)
        self.response.out.write(template.render(path, context))


class JoinGameHandler(GameHandler):
    def Handle(self):
        if self._board and self._board.Join(self._user):
            game_manager.Save(self._board)
            channel_token = channel.create_channel(
                '%s__%s' % (self._board.Id(), self._user))
            self._RenderTemplate('game.html', {
                    'board_id': self._board.Id(),
                    'channel_token': channel_token,
                    'logout_url': users.create_logout_url('/')})
        else:
            self.error(403)


class MoveHandler(GameHandler):
    def Handle(self):
        x = int(self.request.get('x', -1))
        y = int(self.request.get('y', -1))
        if x == -1 or y == -1:
            self.error(403)
            return

        if self._board.Move(self._user, x, y):
            game_manager.Save(self._board)
            oponent = self._board.GetOponent(self._user)
            channel.send_message(
                '%s__%s' % (self._board.Id(), oponent),
                '{"move": {"x": %d, "y": %d}}' % (x, y))
            self.response.headers.add_header(
                'Content-Type', 'application/json')
            self.response.out.write('{"winner": %d}' %
                                    self._board.Winner())
        else:
            self.error(403)


def main():
    run_wsgi_app(webapp.WSGIApplication([
                ('/', NewGameHandler),
                ('/game/.*', JoinGameHandler),
                ('/move?.*', MoveHandler)]))


if __name__ == "__main__":
    main()
