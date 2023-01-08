"""A simple image encoder-decoder model."""

from torch.nn import Module, Conv2d

from torch import Tensor, set_grad_enabled

from torch_tools.models._encoder_2d import Encoder2d
from torch_tools.models._decoder_2d import Decoder2d
from torch_tools.models._blocks_2d import DoubleConvBlock

from torch_tools.models._argument_processing import process_num_feats

from torch_tools.misc import batch_spatial_dims_power_of_2

# pylint:disable=too-many-arguments


class EncoderDecoder2d(Module):
    """A simple encoder-decoder pair for image-like inputs.

    Parameters
    ----------
    in_chans : int
        The number of input channels.
    num_layers : int
        The number of layers in the encoder/decoder.
    features_start : int
        The number of features produced by the first conv block.
    lr_slope : float
        The negative slope to use in the `LeakReLU`s.
    pool_style : str
        The pool style to use in the downsampling blocks (`"avg"` or `"max"`).
    bilinear : bool
        Whether or not to upsample with bilinear interpolation (`True`) or
        `ConvTranspose2d` (`False`).

    """

    def __init__(
        self,
        in_chans: int,
        num_layers: int = 4,
        features_start: int = 64,
        lr_slope: float = 0.1,
        pool_style: str = "max",
        bilinear: bool = False,
    ):
        """Build `EncoderDecoder2d`."""
        super().__init__()

        self._in_conv = DoubleConvBlock(
            process_num_feats(in_chans),
            process_num_feats(features_start),
            lr_slope,
        )

        self._encoder = Encoder2d(
            features_start,
            num_layers - 1,
            pool_style,
            lr_slope,
        )

        self._decoder = Decoder2d(
            (2 ** (num_layers - 1)) * features_start,
            num_layers - 1,
            bilinear,
            lr_slope,
        )

        self._out_conv = Conv2d(
            in_channels=features_start,
            out_channels=in_chans,  # Return should have `in_chans` channels.
            kernel_size=1,
            stride=1,
        )

    def forward(
        self,
        batch: Tensor,
        frozen_encoder: bool = False,
        frozen_decoder: bool = False,
    ) -> Tensor:
        """Pass `batch` through the model.

        Parameters
        ----------
        batch : Tensor
            A mini-batch of inputs.
        frozen_encoder : bool
            Boolean switch controlling whether the encoder's gradients are
            enabled or disabled (usefull for transfer learning).
        frozen_decoder : bool
            Boolean switch controlling whether the decoder's gradients are
            enabled or disabled (usefull for transfer learning).

        Returns
        -------
        Tensor
            The result of passing `batch` through the model.

        """
        batch_spatial_dims_power_of_2(batch)

        with set_grad_enabled(not frozen_encoder):
            encoded = self._in_conv(batch)
            encoded = self._encoder(encoded)
        with set_grad_enabled(not frozen_decoder):
            decoded = self._decoder(encoded)
            decoded = self._out_conv(decoded)
        return decoded
