import os
import unittest
import tempfile

import shorten
from shorten_utils import get_short_url_from_id, get_id_from_short_url


class ShortenTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, shorten.app.config['DATABASE'] = tempfile.mkstemp()
        shorten.app.config['TESTING'] = True
        self.app = shorten.app.test_client()
        shorten.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(shorten.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post(
            '/login',
            data={
                "username": username,
                "password": password,
            },
            follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        self.assertTrue('You were logged in' in rv.data)
        rv = self.logout()
        self.assertTrue('You were logged out' in rv.data)
        rv = self.login('adminx', 'default')
        self.assertTrue('Invalid username' in rv.data)
        rv = self.login('admin', 'defaultx')
        self.assertTrue('Invalid password' in rv.data)

    def test_db_empty(self):
        self.login('admin', 'default')
        rv = self.app.get('/show/')
        self.assertTrue('No entries here so far' in rv.data)

    def test_index_redirect(self):
        rv = self.app.get('/')
        self.assertTrue(rv.status_code == 302)
        self.assertTrue(rv.headers['Location'] == shorten.SITE_URL)

    def test_add_url(self):
        url = 'test'
        rv = self.app.get('/add/' + url)
        self.assertTrue(rv.status_code == 302)
        self.assertTrue(rv.headers['Location'] == shorten.SITE_URL)

        self.login('admin', 'default')

        url = 'www.google.com'
        short_url = get_short_url_from_id(0)
        rv = self.app.get('/add/' + url, follow_redirects=True)
        self.assertTrue('No entries here so far' not in rv.data)
        self.assertTrue('http://' + url in rv.data)
        self.assertTrue(short_url in rv.data)

    def test_add_url_via_form(self):
        url = 'test'
        rv = self.app.get('/add/' + url)
        self.assertTrue(rv.status_code == 302)
        self.assertTrue(rv.headers['Location'] == shorten.SITE_URL)

        self.login('admin', 'default')

        url = 'http://www.google.com'
        short_url = get_short_url_from_id(1)
        rv = self.app.post('/add/form/', data=dict(
            url=url), follow_redirects=True)
        self.assertTrue('No entries here so far' not in rv.data)
        self.assertTrue(url in rv.data)
        self.assertTrue(short_url in rv.data)

        url = 'www.bing.com'
        short_url = get_short_url_from_id(2)
        rv = self.app.post('/add/form/', data=dict(
            url=url), follow_redirects=True)
        self.assertTrue('http://' + url in rv.data)
        self.assertTrue(short_url in rv.data)

    def test_util_functions(self):
        id_number = 1
        short_url = get_short_url_from_id(id_number)
        self.assertEqual(
            get_short_url_from_id(id_number),
            get_short_url_from_id(get_id_from_short_url(short_url)),
        )
        self.assertEqual(
            get_id_from_short_url(short_url),
            get_id_from_short_url(get_short_url_from_id(id_number)),
        )


if __name__ == '__main__':
    unittest.main()
