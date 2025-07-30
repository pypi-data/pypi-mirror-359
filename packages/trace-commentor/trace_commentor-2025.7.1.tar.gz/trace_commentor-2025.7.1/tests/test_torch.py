import torch
import torch.nn as nn

from test_utils import *


def test_torch():

    @Commentor("<return>")
    def target():

        x = torch.ones(4, 5)
        for i in range(3):
            x = x[..., None, :]

        a = torch.randn(309, 110, 3)[:100]
        f = nn.Linear(3, 128)
        b = f(a.reshape(-1, 3)).reshape(-1, 110, 128)
        c = torch.concat((a, b), dim=-1)

        return c.flatten()

    asserteq_or_print(
        target(), '''
    def target():
        x = torch.ones(4, 5)
        """
        Tensor((4, 5), f32) : torch.ones(4, 5)
        ----------
        Tensor((4, 5), f32) : x
        """

        for i in range(3):
            
            x = x[..., None, :]
            """
            Tensor((4, 1, 1, 5), f32) : x
            Tensor((4, 1, 1, 1, 5), f32) : x[..., None, :]
            ----------
            Tensor((4, 1, 1, 1, 5), f32) : x
            """

        a = torch.randn(309, 110, 3)[:100]
        """
        Tensor((309, 110, 3), f32) : torch.randn(309, 110, 3)
        Tensor((100, 110, 3), f32) : torch.randn(309, 110, 3)[:100]
        ----------
        Tensor((100, 110, 3), f32) : a
        """

        f = nn.Linear(3, 128)
        """
        ----------
        """

        b = f(a.reshape(-1, 3)).reshape(-1, 110, 128)
        """
        Tensor((100, 110, 3), f32) : a
        Tensor((11000, 3), f32) : a.reshape(-1, 3)
        Tensor((11000, 128), f32) : f(a.reshape(-1, 3))
        Tensor((100, 110, 128), f32) : f(a.reshape(-1,  ... pe(-1, 110, 128)
        ----------
        Tensor((100, 110, 128), f32) : b
        """

        c = torch.concat((a, b), dim=-1)
        """
        Tensor((100, 110, 3), f32) : a
        Tensor((100, 110, 128), f32) : b
        Tensor((100, 110, 131), f32) : torch.concat((a, b), dim=-1)
        ----------
        Tensor((100, 110, 131), f32) : c
        """

        return c.flatten()
        """
        Tensor((100, 110, 131), f32) : c
        Tensor((1441000,), f32) : c.flatten()
        """
''')
