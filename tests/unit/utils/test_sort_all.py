import pathlib
import tempfile
import unittest
import importlib.util


SCRIPT_PATH = pathlib.Path(__file__).parents[3] / 'scripts' / 'sort__all__.py'
SPEC = importlib.util.spec_from_file_location('sort_all', SCRIPT_PATH)
sort_all = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sort_all)


class SortAllTests(unittest.TestCase):
    def test_sorts_single_line_tuple_without_deleting_following_code(self):
        source = "__all__ = ('long_name', 'x', 'medium')\n\ndef sentinel():\n    return 'kept'\n"

        with tempfile.TemporaryDirectory() as directory:
            filepath = pathlib.Path(directory) / 'module.py'
            filepath.write_text(source)

            changed = sort_all.sort_all(filepath)

            self.assertTrue(changed)
            self.assertEqual(
                filepath.read_text(),
                "__all__ = ('x', 'medium', 'long_name')\n\ndef sentinel():\n    return 'kept'\n",
            )

    def test_does_not_rewrite_already_sorted_exports(self):
        source = "__all__ = ('x', 'long_name')\n"

        with tempfile.TemporaryDirectory() as directory:
            filepath = pathlib.Path(directory) / 'module.py'
            filepath.write_text(source)

            self.assertFalse(sort_all.sort_all(filepath))
            self.assertEqual(filepath.read_text(), source)

    def test_sorts_list_exports(self):
        source = "__all__ = ['long_name', 'x']\n"

        with tempfile.TemporaryDirectory() as directory:
            filepath = pathlib.Path(directory) / 'module.py'
            filepath.write_text(source)

            self.assertTrue(sort_all.sort_all(filepath))
            self.assertEqual(filepath.read_text(), "__all__ = ['x', 'long_name']\n")

    def test_returns_false_when_module_has_no_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            filepath = pathlib.Path(directory) / 'module.py'
            filepath.write_text('VALUE = 1\n')

            self.assertFalse(sort_all.sort_all(filepath))


if __name__ == '__main__':
    unittest.main()
