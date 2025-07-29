<img src="./gaia2.png" width="450px"></img>

## Gaia2 - Pytorch (wip)

Implementation of the [world model architecture](https://arxiv.org/abs/2503.20523) proposed for the domain of self driving out of Wayve

## Install

```bash
$ pip install gaia2-pytorch
```

## Usage

```python
import torch
from gaia2_pytorch import VideoTokenizer, Gaia2

video = torch.randn(1, 3, 10, 16, 16)

tokenizer = VideoTokenizer()

loss = tokenizer(video)
loss.backward()

gaia2 = Gaia2(tokenizer)

loss = gaia2(video)
loss.backward()

generated = gaia2.generate((10, 16, 16))
assert generated.shape == video.shape
```

## Contributing

```bash
$ pip install '.[test]'
```

Then add a test to `tests` and run the following

```bash
$ pytest tests
```

That's it

## Citations

```bibtex
@article{Russell2025GAIA2AC,
    title   = {GAIA-2: A Controllable Multi-View Generative World Model for Autonomous Driving},
    author  = {Lloyd Russell and Anthony Hu and Lorenzo Bertoni and George Fedoseev and Jamie Shotton and Elahe Arani and Gianluca Corrado},
    journal = {ArXiv},
    year    = {2025},
    volume  = {abs/2503.20523},
    url     = {https://api.semanticscholar.org/CorpusID:277321454}
}
```

```bibtex
@article{Rombach2021HighResolutionIS,
    title   = {High-Resolution Image Synthesis with Latent Diffusion Models},
    author  = {Robin Rombach and A. Blattmann and Dominik Lorenz and Patrick Esser and Bj{\"o}rn Ommer},
    journal = {2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    year    = {2021},
    pages   = {10674-10685},
    url     = {https://api.semanticscholar.org/CorpusID:245335280}
}
```

```bibtex
@article{Zhu2025FracConnectionsFE,
    title   = {Frac-Connections: Fractional Extension of Hyper-Connections},
    author  = {Defa Zhu and Hongzhi Huang and Jundong Zhou and Zihao Huang and Yutao Zeng and Banggu Wu and Qiyang Min and Xun Zhou},
    journal = {ArXiv},
    year    = {2025},
    volume  = {abs/2503.14125},
    url     = {https://api.semanticscholar.org/CorpusID:277104144}
}
```

```bibtex
@inproceedings{Huang2025TheGI,
    title   = {The GAN is dead; long live the GAN! A Modern GAN Baseline},
    author  = {Yiwen Huang and Aaron Gokaslan and Volodymyr Kuleshov and James Tompkin},
    year    = {2025},
    url     = {https://api.semanticscholar.org/CorpusID:275405495}
}
```

```bibtex
@inproceedings{Darcet2023VisionTN,
    title   = {Vision Transformers Need Registers},
    author  = {Timoth'ee Darcet and Maxime Oquab and Julien Mairal and Piotr Bojanowski},
    year    = {2023},
    url     = {https://api.semanticscholar.org/CorpusID:263134283}
}
```

```bibtex
@misc{chen2025deepcompressionautoencoderefficient,
    title   = {Deep Compression Autoencoder for Efficient High-Resolution Diffusion Models},
    author  = {Junyu Chen and Han Cai and Junsong Chen and Enze Xie and Shang Yang and Haotian Tang and Muyang Li and Yao Lu and Song Han},
    year    = {2025},
    eprint  = {2410.10733},
    archivePrefix = {arXiv},
    primaryClass = {cs.CV},
    url     = {https://arxiv.org/abs/2410.10733},
}
```
