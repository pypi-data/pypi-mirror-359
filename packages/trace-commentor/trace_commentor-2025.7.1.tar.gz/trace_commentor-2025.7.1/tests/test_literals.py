from test_utils import *


def test_constant():

    @Commentor("<return>")
    def target():
        1

    asserteq_or_print(target(), '''
    def target():
''')


def test_tuple():
    
    @Commentor("<return>")
    def target():
        a, b = 1, 2

    asserteq_or_print(target(), '''
    def target():
        a, b = 1, 2
        """
        ----------
        1 : a
        2 : b
        """
''')
