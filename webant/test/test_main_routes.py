from unittest import TestCase

from webant import create_app
from conf.defaults import get_def_conf
from nose.tools import eq_


class TestMainRoutes(TestCase):
    def setUp(self):
        self.wtc = create_app(get_def_conf()).test_client()

    def test_home(self):
        eq_(self.wtc.get('/').status_code, 200)

    def test_get_add(self):
        eq_(self.wtc.get('/add').status_code, 200)

    def test_empty_search(self):
        eq_(self.wtc.get('/search?q=*').status_code, 200)

    def test_descr(self):
        eq_(self.wtc.get('/description.xml').status_code, 200)

    def test_recents(self):
        eq_(self.wtc.get('/recents').status_code, 200)
