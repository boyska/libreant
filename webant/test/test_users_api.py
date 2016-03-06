from unittest import TestCase

from webant import create_app
from conf.defaults import get_def_conf
from nose.tools import eq_


class TestUsersApiNoDb(TestCase):
    '''those tests express the behavior when no USERS_DATABASE is supplied'''
    def setUp(self):
        conf = get_def_conf()
        print(conf)
        self.app = create_app(conf)
        self.wtc = self.app.test_client()

    def tearDown(self):
        pass

    def test_no_login(self):
        eq_(self.wtc.get('/login').status_code, 404)
        eq_(self.wtc.get('/logout').status_code, 404)

    def test_no_user(self):
        res = self.wtc.get('/api/v1/users/1')
        eq_(res.status_code, 500)

    def test_no_group(self):
        res = self.wtc.get('/api/v1/groups/1')
        eq_(res.status_code, 500)
