# TorchTools
Handy PyTorch models and utilities which should save you time.

This Python library contains a bunch of neural networks, implemented in PyTorch, and a generic `Dataset` class with useful features to help you get started with your deep-learning problem more quickly, and spend a lot less time engineering—and testing—the PyTorch-specific software you need. There is also the hope that you will write, and duplicate, less code by being able to easily set and modify these models' architectures at instantiation.

## Installation

To clone the repository (shouldn't work right now):
```bash
git clone https://github.com/jdenholm/TorchTools.git
```

To create the necessary conda environment:
```bash
cd /path/to/TorchTools/
conda env create -f requirements.conda.yaml
```

To install TorchTools:
```bash
conda activate torch-tools
pip install -e .
```

To run the tests:
```bash
pytest tests/
```


## Contents



### Models


---

#### Dense Network
Often people share code with simple perceptron-style networks where they have hard-coded the architecture—the number of layers, dropout probabilities and the number of input/output features, etc. Hard-coding these features is inelegant and doesn't allow one to easily modify the architecture.

`DenseNetwork` is a straightforward perceptron-style neural network that can be used for classification and regression. It is super-simple to use and instantiate.

For example:
```python
>>> from torch_tools.models import DenseNetwork

>>> DenseNetwork(in_feats=256,
                 out_feats=2,
                 hidden_sizes=(128, 64),
                 input_bnorm=True,
                 input_dropout=0.1,
                 hidden_dropout=0.25,
                 hidden_bnorm=True,
                 negative_slope=0.2)
DenseNetwork(
  (_input_block): InputBlock(
    (_fwd_seq): Sequential(
      (0): BatchNorm1d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
      (1): Dropout(p=0.1, inplace=False)
    )
  )
  (_dense_blocks): Sequential(
    (0): DenseBlock(
      (_fwd_seq): Sequential(
        (0): Linear(in_features=256, out_features=128, bias=True)
        (1): BatchNorm1d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        (2): Dropout(p=0.25, inplace=False)
        (3): LeakyReLU(negative_slope=0.2)
      )
    )
    (1): DenseBlock(
      (_fwd_seq): Sequential(
        (0): Linear(in_features=128, out_features=64, bias=True)
        (1): BatchNorm1d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        (2): Dropout(p=0.25, inplace=False)
        (3): LeakyReLU(negative_slope=0.2)
      )
    )
    (2): DenseBlock(
      (_fwd_seq): Sequential(
        (0): Linear(in_features=64, out_features=2, bias=True)
      )
    )
  )
)
```
The model is a subclass of `torch.nn.Module` and inherits the same functionality as other PyTorch modules.

---


#### Convolutional Network 2D


Torchvision's default models assume three-channel (RGB) images. To use a different number of channels, one has to overwrite the first convolutional layer, which results in ugly code that must be modified if you want to want to change architectures from, say, ResNet to VGG, etc. Furthermore, you may wish to experiment with the classification layer's architecture, which requires more ugly code to modify the default models. To circumvent this, you can use `ConvNet2d`.

`ConvNet2d` is a convolution neural network made of three parts: an encoder, an adaptive pooling layer and a `DenseNetwork` (which serves as a classification/regression head). The model can be customised in a modular fashion:

* Encoder: the encoder can be chosen with the optional argument `encoder_style`, which can be any of Torchvision's ResNet or VGG models (i.e. `"resnet18"`, `"vgg11"`, `"vgg_11_bn"` etc.).
* Pool: the adaptive pooling layer can be chosen with the `pool_style` optional argument. The options are `"avg"`, `"max"` and `"avg-max-concat"`. The former two options are simply adaptive average and max pooling layers, and the latter is a layer which concatenates the former two (thus doubling the number of features).
* `DenseNetwork`: the final part of the model is simply the dense network introduced in the previous section. The keyword arguments can be supplied by passing a dictionary to `dense_net_kwargs` optional argument.


For example, suppose we want an encoder in the style of Torchvision's VGG11 with batch normalisation, initialised with Torchvision's ImageNet pretrained weights, a pooling layer which concatenates the outputs of both the average and maximum adaptive pooling layers, a classifier with two hidden layers and a dropout probability of 0.25:

```python
>>> from torch_tools.models import ConvNet2d
>>> model = ConvNet2d(out_feats=512,
                      in_channels=3,
                      encoder_style="vgg11_bn",
                      pretrained=True,
                      pool_style="avg-max-concat",
                      dense_net_kwargs={"hidden_sizes": (1024, 1024), "hidden_dropout": 0.25})
>>> model
ConvNet2d(
  (_backbone): Sequential(
    (0): Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (2): ReLU(inplace=True)
    (3): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (4): Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (5): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (6): ReLU(inplace=True)
    (7): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (8): Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (9): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (10): ReLU(inplace=True)
    (11): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (12): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (13): ReLU(inplace=True)
    (14): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (15): Conv2d(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (16): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (17): ReLU(inplace=True)
    (18): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (19): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (20): ReLU(inplace=True)
    (21): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    (22): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (23): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (24): ReLU(inplace=True)
    (25): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
    (26): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    (27): ReLU(inplace=True)
    (28): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
  )
  (_pool): Sequential(
    (0): _ConcatMaxAvgPool2d(
      (_avg_pool): AdaptiveAvgPool2d(output_size=(7, 7))
      (_max_pool): AdaptiveMaxPool2d(output_size=(7, 7))
    )
    (1): Flatten(start_dim=1, end_dim=-1)
  )
  (_dense): DenseNetwork(
    (_input_block): InputBlock(
      (_fwd_seq): Sequential()
    )
    (_dense_blocks): Sequential(
      (0): DenseBlock(
        (_fwd_seq): Sequential(
          (0): Linear(in_features=50176, out_features=1024, bias=True)
          (1): Dropout(p=0.25, inplace=False)
          (2): LeakyReLU(negative_slope=0.2)
        )
      )
      (1): DenseBlock(
        (_fwd_seq): Sequential(
          (0): Linear(in_features=1024, out_features=1024, bias=True)
          (1): Dropout(p=0.25, inplace=False)
          (2): LeakyReLU(negative_slope=0.2)
        )
      )
      (2): DenseBlock(
        (_fwd_seq): Sequential(
          (0): Linear(in_features=1024, out_features=512, bias=True)
        )
      )
    )
  )
)
```
The model is again a subclass of `torch.nn.Module`. Another useful feature of
`ConvNet2d` if the ability to _freeze_ the encoder—that is to say, disable gradients in the encoder in order take full advantage of the pretrained weights (transfer learning). For example:
```python
>>> from torch import rand
>>> batch = rand(10, 3, 100, 100)
>>> # With the encoder frozen
>>> preds = model(batch, frozen_encoder=True)
>>> # Without the encoder frozen (default behaviour)
>>> preds = model(batch, frozen_encoder=False)
```

---


#### UNet—Semantic Segmentation
The `UNet` has become a classic model which, again, is often implemented with the architecture hard-coded. Having an easy-to-instantiate `UNet` with an easily-modifiable architecture is always handy, so we include one here.

Suppose we want a `UNet` that takes three-channel inputs, produces 16 output channels, has an initial convolution block which produces 64 features, has three layers in the U, uses max pooling (rather than average), used `ConvTranspose2d` layers to upsample (rather than bilinear interpolation) and has `LeakyReLU` layers with a slope of 0.2.

While this is quite a mouthful, it is incredibly easy to instantiate:

```python
>>> from torch_tools import UNet
>>> model = UNet(in_chans=3,
                 out_chans=16,
                 features_start=64,
                 num_layers=3,
                 pool_style="max",
                 bilinear=False,
                 lr_slope=0.2)
>>> model
UNet(
  (_in_conv): DoubleConvBlock(
    (conv1): ConvBlock(
      (_fwd): Sequential(
        (0): Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        (2): LeakyReLU(negative_slope=0.2)
      )
    )
    (conv2): ConvBlock(
      (_fwd): Sequential(
        (0): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        (2): LeakyReLU(negative_slope=0.2)
      )
    )
  )
  (_down_blocks): ModuleList(
    (0): DownBlock(
      (_pool): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
      (_conv): DoubleConvBlock(
        (conv1): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
        (conv2): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
      )
    )
    (1): DownBlock(
      (_pool): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
      (_conv): DoubleConvBlock(
        (conv1): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
        (conv2): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
      )
    )
  )
  (_up_blocks): ModuleList(
    (0): UNetUpBlock(
      (_upsample): Sequential(
        (0): Upsample(scale_factor=2.0, mode=bilinear)
        (1): Conv2d(256, 128, kernel_size=(1, 1), stride=(1, 1))
      )
      (_double_conv): DoubleConvBlock(
        (conv1): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(256, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
        (conv2): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
      )
    )
    (1): UNetUpBlock(
      (_upsample): Sequential(
        (0): Upsample(scale_factor=2.0, mode=bilinear)
        (1): Conv2d(128, 64, kernel_size=(1, 1), stride=(1, 1))
      )
      (_double_conv): DoubleConvBlock(
        (conv1): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(128, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
        (conv2): ConvBlock(
          (_fwd): Sequential(
            (0): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
            (2): LeakyReLU(negative_slope=0.2)
          )
        )
      )
    )
  )
  (_out_conv): Conv2d(64, 16, kernel_size=(1, 1), stride=(1, 1))
)

```

---


#### Encoder


---

#### Decoder

---


#### Encoder–Decoder model
This model is effectively a UNet without the skip connections. It can be used for segmentation and style transfer in the same way, however a roughly equivalent UNet will likely outperform it. That said, it carries the advantage that it requires less memory during training and inference, and is faster computationally.

---

#### Simple 2D convolution network
While we've already included a two-dimensional convolutional model, it uses default architectures from Torchvision's available VGG and ResNet models, which are pretty hefty and might be too "overpowered" for certain applications (say, to be used as a discriminator when training a GAN). To address this, we also include a simpler two-dimensional convolutional neural network which is a lot more lightweight and customisable.


### Datasets

#### DataSet