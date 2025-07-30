from test_utils import *


def test_constant():

    @Commentor("<return>")
    def target():
        x = 2
        print(x == 2)

    asserteq_or_print(target(), '''
    def target():
        x = 2
        print(x == 2)
        """
        True : x == 2
        None : print(x == 2)
        """
''')


def test_if():

    @Commentor("<return>")
    def target():
        x = 2
        if x > 3:
            x = 2 * x
            y = 1
        elif x > 2:
            x = 4 * x
            y = 2
        elif x > 3:
            x = 4 * x
            y = 3
        else:
            x = 8 * x
            y = 5
    
    asserteq_or_print(target(), '''
    def target():
        x = 2
        if x > 3:  # False
            x = 2 * x  # skipped
            y = 1  # skipped
            
        elif x > 2:  # False
            x = 4 * x  # skipped
            y = 2  # skipped
            
        elif x > 3:  # False
            x = 4 * x  # skipped
            y = 3  # skipped
            
        else:    # True
            x = 8 * x
            """
            2 : x
            16 : 8 * x
            ----------
            16 : x
            """

            y = 5

''')


def test_for():
    
    with closing(StringIO()) as f:
        @Commentor(f, _exit=False, check=False)
        def target():
            odds = []
            # return only odd numbers - 1,3,5,7,9
            for x in range(10):
                # Check if x is even
                if x % 2 == 0:
                    continue
                odds.append(x)
            return odds
        
        assert target() == [1, 3, 5, 7, 9]
        asserteq_or_print(f.getvalue(), '''
        def target():
            odds = []
            for x in range(10):
                
                if x % 2 == 0:  # False
                    continue  # skipped
                    
                odds.append(x)
                """
                [1, 3, 5, 7] : odds
                9 : x
                None : odds.append(x)
                """

            return odds
            """
            [1, 3, 5, 7, 9] : odds
            """
''')
        
        
