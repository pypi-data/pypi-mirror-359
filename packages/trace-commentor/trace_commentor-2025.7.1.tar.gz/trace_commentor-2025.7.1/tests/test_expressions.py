from trace_commentor import Commentor
from test_utils import asserteq_or_print


def test_binop():

    @Commentor("<return>")
    def target():
        1 + 1

    asserteq_or_print(
        target(), '''
    def target():
        1 + 1
        """
        2 : 1 + 1
        """
''')


def test_binop_cascade():

    @Commentor("<return>")
    def target():
        1 + 1 + 1

    asserteq_or_print(
        target(), '''
    def target():
        1 + 1 + 1
        """
        2 : 1 + 1
        3 : 1 + 1 + 1
        """
''')


def test_call_print():

    @Commentor("<return>")
    def target():
        print("This line will be printed.")

    asserteq_or_print(
        target(), '''
    def target():
        print('This line will be printed.')
        """
        None : print('This line will be printed.')
        """
''')
