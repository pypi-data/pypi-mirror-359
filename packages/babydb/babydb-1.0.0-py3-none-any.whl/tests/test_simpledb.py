import unittest
from simpledb.core import SimpleDB

class TestSimpleDB(unittest.TestCase):
    def setUp(self):
        self.db = SimpleDB(db_file='test_database.json.gz', files_dir='test_files')

    def test_create_read(self):
        self.db.login("admin", "admin123")
        self.db.create("test1", '{"Name": "Test", "Age": 20, "Grade": 10, "Class": "A", "Subjects": ["Math"]}')
        result = self.db.read("test1")
        self.assertEqual(result, '{"Name": "Test", "Age": 20, "Grade": 10, "Class": "A", "Subjects": ["Math"]}')

    def test_find_fulltext(self):
        self.db.login("admin", "admin123")
        self.db.create("test2", '{"Name": "Test2", "Age": 21, "Grade": 11, "Class": "B", "Subjects": ["Math", "Science"]}')
        result = self.db.find('fulltext "Math Science"')
        self.assertIn("test2", result)

if __name__ == '__main__':
    unittest.main()