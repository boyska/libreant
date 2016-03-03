from unittest import TestCase

from webant import create_app
from conf.defaults import get_def_conf
from nose.tools import eq_


class TestWebAdd(TestCase):
    def setUp(self):
        conf = get_def_conf()
        conf['ES_INDEXNAME'] = 'test-book'
        self.app = create_app(conf)
        self.wtc = self.app.test_client()

    def tearDown(self):
        es = self.app.archivant._db.es
        if es.indices.exists('test-book'):
            es.indices.delete('test-book')

    def test_get_add(self):
        eq_(self.wtc.get('/add').status_code, 200)

    def test_do_add(self):
        rv = self.wtc.post('/add',
                      data=dict(
                          _language='en',
                          field_title='I am a canary',
                      ), follow_redirects=True)
        eq_(rv.status_code, 200)
        assert 'I am a canary' in rv.data
