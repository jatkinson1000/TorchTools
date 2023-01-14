"""Two-dimensional convolutional encoder moder."""
from typing import List

from torch.nn import Sequential


from torch_tools.models._blocks_2d import DownBlock, DoubleConvBlock
from torch_tools.models._argument_processing import (
    process_num_feats,
    process_str_arg,
    process_negative_slope_arg,
)

# pylint: disable=too-many-arguments


class Encoder2d(Sequential):
    """Encoder model for image-like inputs.

    Parameters
    ----------
    in_chans : int
        The number of input channels the encoder should take.
    start_features : int
        The number of features the first conv block should produce.
    num_blocks : int
        The number of downsampling blocks in the encoder.
    pool_style : str
        The type of pooling to use in downsampling (`"avg"` or `"max"`).
    lr_slope : float
        The negative slope argument to use in the `LeakyReLU`s.

    """

    def __init__(
        self,
        in_chans: int,
        start_features: int,
        num_blocks: int,
        pool_style: str,
        lr_slope: float,
    ):
        """Build `Encoder`."""
        super().__init__(
            DoubleConvBlock(
                process_num_feats(in_chans),
                process_num_feats(start_features),
                process_negative_slope_arg(lr_slope),
            ),
            *self._get_blocks(
                process_num_feats(start_features),
                process_num_feats(num_blocks),
                process_str_arg(pool_style),
                process_negative_slope_arg(lr_slope),
            )
        )

    def _get_blocks(
        self,
        in_chans: int,
        num_blocks,
        pool_style: str,
        lr_slope: float,
    ) -> List[DownBlock]:
        """Get the encoding layers in a sequential.

        Parameters
        ----------
        in_chans : int
            The number of input channels.
        num_blocks : int
            The number of blocks in the encoder.
        pool_style : str
            The pool style to use when downsampling.
        lr_slope : float
            The negative slope to use in the leak relu layers.

        Returns
        -------
        List[DownBlock]
            A list of the model's blocks.

        """
        chans = in_chans
        blocks = []
        for _ in range(num_blocks - 1):
            blocks.append(DownBlock(chans, chans * 2, pool_style, lr_slope))
            chans *= 2
        return blocks
