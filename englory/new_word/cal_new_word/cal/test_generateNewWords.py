from unittest import TestCase
from generate_result import GenerateNewWords


class TestGenerateNewWords(TestCase):
    def test_save_2_csv(self):
        generate_new_word = GenerateNewWords('localhost', 11112, 1)
        generate_new_word.set_output_dir('/home/wong/data/output')
        generate_new_word.save_2_csv()

    def test_save_2_db(self):
        generate_new_word = GenerateNewWords('localhost', 11112, 1)
        generate_new_word.set_db_info('mysql-server', 3306, 'root', '', 'recommendation', 'thesaurus')
        generate_new_word.save_2_db()
        generate_new_word.set_output_dir('/home/wong/data/output')
        generate_new_word.save_2_csv()
