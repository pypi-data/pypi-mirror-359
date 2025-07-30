from test_utils import *


def test_function_def():

    @Commentor("<return>")
    def target():
        pass

    asserteq_or_print(target(), '''
    def target():
        pass
''')


def test_return():

    with closing(StringIO()) as f:

        @Commentor(f, _exit=False)
        def target():
            a = 1
            return a + 1

        assert target() == 2

        asserteq_or_print(
            f.getvalue(), '''
        def target():
            a = 1
            return a + 1
            """
            1 : a
            2 : a + 1
            """
''')




def test_args():

    @Commentor("<return>")
    def target(a, d=1, *b, c, k=1):
        return a + k

    asserteq_or_print(target(1, 2, 3, 4, c=5, k=2), '''
    def target(a, d=1, *b, c, k=1):
        """
        1 : a
        2 : d
        (3, 4) : b
        5 : c
        2 : k
        """

        return a + k
        """
        1 : a
        2 : k
        3 : a + k
        """
''')
