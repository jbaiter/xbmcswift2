import os
import pickle
from xbmcswift2.storage import _Storage, TimedStorage
from unittest import TestCase
from datetime import timedelta
import time


def remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


class TestCache(TestCase):

    def test_pickle(self):
        filename = '/tmp/testdict.pickle'
        remove(filename)
        storage = _Storage(filename, file_format='pickle')

        storage['name'] = 'jon'
        storage.update({'answer': 42})
        storage.close()

        storage2 = _Storage(filename, file_format='pickle')
        self.assertEqual(storage, storage2)
        self.assertEqual(2, len(storage2.items()))
        self.assertTrue('name' in storage2.keys())
        self.assertTrue('answer' in storage2.keys())
        self.assertEqual('jon', storage2.pop('name'))
        self.assertEqual(42, storage2['answer'])

        remove(filename)

    def test_csv(self):
        filename = '/tmp/testdict.csv'
        remove(filename)
        storage = _Storage(filename, file_format='csv')

        storage['name'] = 'jon'
        storage.update({'answer': '42'})
        storage.close()

        storage2 = _Storage(filename, file_format='csv')
        self.assertEqual(sorted(storage.items()), sorted(storage2.items()))
        self.assertEqual(2, len(storage2.items()))
        self.assertTrue('name' in storage2.keys())
        self.assertTrue('answer' in storage2.keys())
        self.assertEqual('jon', storage2.pop('name'))
        self.assertEqual('42', storage2['answer'])

        remove(filename)

    def test_json(self):
        filename = '/tmp/testdict.json'
        remove(filename)
        storage = _Storage(filename, file_format='json')

        storage['name'] = 'jon'
        storage.update({'answer': '42'})
        storage.close()

        storage2 = _Storage(filename, file_format='json')
        self.assertEqual(sorted(storage.items()), sorted(storage2.items()))
        self.assertEqual(2, len(storage2.items()))
        self.assertTrue('name' in storage2.keys())
        self.assertTrue('answer' in storage2.keys())
        self.assertEqual('jon', storage2.pop('name'))
        self.assertEqual('42', storage2['answer'])

        remove(filename)


class TestTimedStorage(TestCase):

    def test_pickle(self):
        filename = '/tmp/testdict.pickle'
        remove(filename)
        storage = TimedStorage(filename, file_format='pickle', TTL=timedelta(hours=1))
        storage['name'] = 'jon'
        storage.update({'answer': 42})
        storage.close()

        # Reopen
        storage2 = TimedStorage(filename, file_format='pickle', TTL=timedelta(hours=1))
        self.assertEqual(sorted(storage.items()), sorted(storage2.items()))

        # Reopen again but with a one second TTL which will be expired
        time.sleep(2)
        storage3 = TimedStorage(filename, file_format='pickle', TTL=timedelta(seconds=1))
        self.assertEqual([], sorted(storage3.items()))
        storage3.close()

        # Ensure the expired dict was synced
        storage4 = TimedStorage(filename, file_format='pickle', TTL=timedelta(hours=1))
        self.assertEqual(sorted(storage3.items()), sorted(storage4.items()))


class Test_Storage(TestCase):

    def test_clear(self):
        filename = '/tmp/testclear.json'
        storage = _Storage(filename, file_format='json')
        storage['name'] = 'jon'
        storage.sync()

        # dict with single value is now saved to disk
        with open(filename) as inp:
            self.assertEqual(inp.read(), '{"name":"jon"}')

        # now clear the dict, it should sync to disk.
        storage.clear()
        with open(filename) as inp:
            self.assertEqual(inp.read(), '{}')
            
    def test_dict_compatibility(self):
        """Test that the _Storage class fully implements dict()"""
        filename = '/tmp/testdict1.json'
        storage1 = _Storage(filename, file_format='json')
        storage2 = _Storage(filename.replace('1','2'), file_format='json')
        storage1['key'] = 'abc'
        self.assertEqual(storage1, storage1, '%s is equal to itself' % dict(storage1))
        self.assertNotEqual(storage1, storage2, '%s & %s are not equal' % (dict(storage1), dict(storage2)))
        self.assertGreater(storage1, storage2, '%s > %s' % (dict(storage1), dict(storage2)))
        self.assertLess(storage2, storage1, '%s < %s' % (dict(storage1), dict(storage2)))
        self.assertEqual(len(storage1),1)
        self.assertEqual(len(storage2),0)
        self.assertTrue(bool(storage1), 'non-empty objects test True')
        self.assertFalse(bool(storage2), 'empty objects test False')
        self.assertTrue(storage1.has_key('key'))
        self.assertFalse(storage1.has_key('non-key'))

        
        