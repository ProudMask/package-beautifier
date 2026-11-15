import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from main import LookupFailed, check_package_existence, normalize_name, suggest_names


class NameTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_name(' My__Analytics.X '), 'my-analytics-x')
        for name in ('', '-name', 'name.', 'a/b', 'مرحبا', 'name\nother'):
            with self.assertRaises(ValueError):
                normalize_name(name)

    def test_seed_and_uniqueness(self):
        self.assertEqual(suggest_names('demo', seed=42), suggest_names('demo', seed=42))
        self.assertEqual(len(set(suggest_names('demo', 8, 42))), 8)
        for count in (0, 9, True):
            with self.assertRaises(ValueError):
                suggest_names('demo', count)

    @patch('main.urlopen')
    def test_found(self, open_url):
        open_url.return_value = io.BytesIO(json.dumps({'info': {'name': 'My_Analytics'}}).encode())
        self.assertTrue(check_package_existence('my-analytics'))
        self.assertEqual(open_url.call_args.kwargs['timeout'], 10)

    @patch('main.urlopen')
    def test_http_errors(self, open_url):
        open_url.side_effect = HTTPError('https://example.test', 404, 'missing', {}, None)
        self.assertFalse(check_package_existence('demo'))
        for status in (429, 500):
            open_url.side_effect = HTTPError('https://example.test', status, 'failed', {}, None)
            with self.assertRaises(LookupFailed):
                check_package_existence('demo')

    @patch('main.urlopen')
    def test_network_failure(self, open_url):
        for error in (URLError('failure'), TimeoutError('timeout')):
            open_url.side_effect = error
            with self.assertRaises(LookupFailed):
                check_package_existence('demo')

    @patch('main.urlopen')
    def test_invalid_metadata(self, open_url):
        for payload in (b'not-json', b'{}', b'{"info":{"name":"other"}}'):
            open_url.return_value = io.BytesIO(payload)
            with self.assertRaises(LookupFailed):
                check_package_existence('demo')

    def test_offline_cli(self):
        result = subprocess.run([sys.executable, 'main.py', 'demo', '--seed', '42', '--offline'], capture_output=True, text=True, check=True, timeout=10)
        report = json.loads(result.stdout)
        self.assertTrue(all(item['status'] == 'not_checked' for item in [report['query'], *report['suggestions']]))


if __name__ == '__main__':
    unittest.main()
