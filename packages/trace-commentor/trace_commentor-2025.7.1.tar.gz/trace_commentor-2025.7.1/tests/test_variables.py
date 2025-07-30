from test_utils import *


def test_assign():

    @Commentor("<return>")
    def target():
        myint = 7
        print(myint)

    asserteq_or_print(
        target(), '''
    def target():
        myint = 7
        print(myint)
        """
        7 : myint
        None : print(myint)
        """
''')
