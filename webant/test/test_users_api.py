from unittest import TestCase
import json

from webant import create_app
from conf.defaults import get_def_conf
from nose.tools import eq_


class TestUsersApiNoDb(TestCase):
    '''those tests express the behavior when no USERS_DATABASE is supplied'''
    def setUp(self):
        conf = get_def_conf()
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


class TestUsersApiWithDb(TestCase):
    '''those tests express the behavior when users are enabled'''
    def setUp(self):
        conf = get_def_conf()
        conf['USERS_DATABASE'] = 'sqlite:///:memory:'
        self.app = create_app(conf)
        self.wtc = self.app.test_client()

    def tearDown(self):
        pass

    def test_login_pages(self):
        eq_(self.wtc.get('/login').status_code, 200)
        res = self.wtc.get('/logout')
        eq_(res.status_code, 400)
        assert 'not logged' in res.data

    def test_admin(self):
        res = self.wtc.get('/api/v1/users/1')
        eq_(res.status_code, 200)
        eq_(json.loads(res.data)['data']['name'], 'admin')
        eq_(json.loads(res.data)['data']['id'], 1)

    def test_no_group(self):
        res = self.wtc.get('/api/v1/groups/1')
        eq_(res.status_code, 200)
        eq_(json.loads(res.data)['data']['name'], 'admins')
        eq_(json.loads(res.data)['data']['id'], 1)

    def test_everyone_can_delete(self):
        '''sad but true: everyone can delete everyone else'''
        res = self.wtc.delete('/api/v1/users/1')
        eq_(res.status_code, 200)
        res = self.wtc.get('/api/v1/users/1')
        eq_(res.status_code, 404)
