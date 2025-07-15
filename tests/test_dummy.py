import unittest

class DummyTest(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main()
