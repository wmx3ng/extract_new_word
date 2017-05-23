from unittest import TestCase

from input_tokens import InputTokens


class TestInputTokens(TestCase):
    def test_resolve_text(self):
        input_token = InputTokens('/home/wong/data/output', 'localhost', 11112, 1)
        input_token.resolve_text()
        input_token.cal_new_word_ratio_with_batch()
