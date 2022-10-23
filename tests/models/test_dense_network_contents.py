"""Test the contents of `torch-tools.models.DenseNetwork`."""

from torch.nn import Dropout, BatchNorm1d

from torch_tools.models import DenseNetwork


# pylint: disable=protected-access


def test_full_input_block_contents():
    """Test contents of input block with `BatchNorm1d` and `Dropout`."""
    model = DenseNetwork(
        in_feats=10,
        out_feats=2,
        input_bnorm=True,
        input_dropout=0.25,
    )

    in_block = model._input_block

    # There should be two layers in the input block
    assert len(in_block._fwd_seq) == 2, "Expected two layers in input block."

    # The first layer in the input block should be BatchNorm1d
    msg = "First layer should be BatchNorm1d."
    assert isinstance(in_block._fwd_seq[0], BatchNorm1d), msg

    # The second layer in the input block should be Dropout.
    msg = "Second layer should be Dropout"
    assert isinstance(in_block._fwd_seq[1], Dropout), msg


def test_input_block_contents_with_batchnorm_only():
    """Test contents of input block when user asks for batchnorm only.

    Notes
    -----
    By setting the argument `input_dropout=0.0`, we exclude the dropout
    layer.

    """
    model = DenseNetwork(
        in_feats=10,
        out_feats=2,
        input_bnorm=True,
        input_dropout=0.0,
    )

    in_block = model._input_block

    # There should only be one layer in the input block
    assert len(in_block._fwd_seq) == 1, "Expected one layer in input block."

    # The only layer in input block should be a BatchNorm1d
    msg = "First layer should be BatchNorm1d"
    assert isinstance(in_block._fwd_seq[0], BatchNorm1d), msg


def test_input_block_contents_with_dropout_only():
    """Test the contents of input block when user asks for dropout only.

    Notes
    -----
    To ask for input dropout only, we set `input_bnorm=False`.

    """
    model = DenseNetwork(
        in_feats=10,
        out_feats=2,
        input_bnorm=False,
        input_dropout=0.25,
    )

    in_block = model._input_block

    # There should only be one layer in the input block
    assert len(in_block._fwd_seq) == 1, "Expected one layer in input block."

    # The only layer in input block should be a Dropout
    msg = "First layer should be BatchNorm1d"
    assert isinstance(in_block._fwd_seq[0], Dropout), msg


def test_input_batchnorm_number_of_feats_assignment():
    """Test the input batchnorm layer is assigned correct number of feats."""
    msg = "Unexpected number of batchnorm features."
    model = DenseNetwork(123, 2, input_bnorm=True)
    assert model._input_block._fwd_seq[0].num_features == 123, msg

    msg = "Unexpected number of batchnorm features."
    model = DenseNetwork(321, 2, input_bnorm=True)
    assert model._input_block._fwd_seq[0].num_features == 321, msg


def test_input_block_dropout_probability_assignment():
    """Test the dropout probability in input block is correctly assigned."""
    model = DenseNetwork(
        in_feats=10, out_feats=2, input_bnorm=True, input_dropout=0.123456
    )
    input_dropout_prob = model._input_block._fwd_seq[1].p
    assert input_dropout_prob == 0.123456, "Dropout prob incorrectly assigned."

    model = DenseNetwork(
        in_feats=10, out_feats=2, input_bnorm=True, input_dropout=0.654321
    )
    input_dropout_prob = model._input_block._fwd_seq[1].p
    assert input_dropout_prob == 0.654321, "Dropout prob incorrectly assigned."


def test_number_of_dense_blocks_with_no_hidden_layers():
    """Test the number of dense blocks in `DenseNetwork`."""
    # With no hidden layers (hidden_sizes=None), the model should only have
    # one dense block.
    model = DenseNetwork(in_feats=10, out_feats=2, hidden_sizes=None)

    dense_blocks = model._dense_blocks
    msg = "Should only be one dense block when no hidden layers are requested."
    assert len(dense_blocks) == 1, msg


def test_number_of_hidden_blocks_with_one_hidden_layer():
    """Test the number of dense blocks with one hidden layer."""
    model = DenseNetwork(in_feats=10, out_feats=2, hidden_sizes=((5,)))

    # There should be two dense blocks if we ask for one hidden layer.
    # `print(model)` if that seems confusing.

    dense_blocks = model._dense_blocks
    msg = "Should be two dense blocks when one hidden layer is requested."
    assert len(dense_blocks) == 2, msg


def test_number_of_dense_blocks_with_seven_hidden_layers():
    """Test the numer of dense blocks with seven hidden layers."""
    model = DenseNetwork(in_feats=10, out_feats=2, hidden_sizes=(7 * (10,)))

    # There should be 8 dense block when 7 hidden layers are requested
    dense_blocks = model._dense_blocks
    msg = "Should be 8 dense blocks when you ask for 7 hidden layers."
    assert len(dense_blocks) == 8, msg


def test_linear_layer_sizes_in_dense_blocks_with_no_hidden_layers():
    """Test the feature dimensions in the linear layers with hidden layers."""
    # Test with no hidden layers
    model = DenseNetwork(10, 2, hidden_sizes=None)
    dense_blocks = model._dense_blocks
    msg = "The linear layer should have 10 input features."
    assert dense_blocks[0]._fwd_seq[0].in_features == 10, msg

    msg = "The linear layer should have 2 output features."
    assert dense_blocks[0]._fwd_seq[0].out_features == 2, msg


def test_linear_layer_sizes_in_dense_blocks_with_hidden_layers():
    """Test the feature dimensions in the linear layers with hidden layers."""
    # Test with hidden layers
    in_feats, out_feats = 128, 2
    hidden_sizes = (64, 32, 16, 8, 16, 32, 64)
    model = DenseNetwork(in_feats, out_feats, hidden_sizes=hidden_sizes)

    in_sizes = iter((in_feats,) + hidden_sizes)
    out_sizes = iter(hidden_sizes + (out_feats,))
    for _, module in model._dense_blocks.named_children():

        msg = "Unexpected number of input features in linear layer."
        assert module._fwd_seq[0].in_features == next(in_sizes), msg

        msg = "Unexpected number of output features in linear layer."
        assert module._fwd_seq[0].out_features == next(out_sizes), msg
