<div align="center">
    <br>
    <p align="center">
    <h1>MapReader</h1>
    </p>
    <h2>A computer vision pipeline for analyzing and exploring images and maps at scale</h2>
</div>
 
<p align="center">
    <a href="https://github.com/Living-with-machines/MapReader/workflows/Continuous%20integration/badge.svg">
        <img alt="Continuous integration badge" src="https://github.com/Living-with-machines/MapReader/workflows/Continuous%20integration/badge.svg">
    </a>
    <a href="https://mybinder.org/v2/gh/Living-with-machines/MapReader/main?labpath=examples%2Fquick_start%2Fquick_start.ipynb">
        <img alt="Binder" src="https://mybinder.org/badge_logo.svg">
    </a>
    <a href="https://github.com/Living-with-machines/MapReader/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <br/>
</p>

## Gallery

<div align="center">

| **classification_one_inch_maps_001**<br><a href="https://github.com/Living-with-machines/MapReader/tree/main/examples/maps/classification_one_inch_maps_001"><img src="figs/tutorial_classification_one_inch_maps_001.png" alt="tutorial for classification_one_inch_maps_001" style="height:200px;"></a><br><sup>Tutorial: train/fine-tune PyTorch CV classifiers on <ins>historical maps</ins>. Fig shows the rail infrastructure around London as predicted by a MapReader CV model.</sup> | **classification_plant_phenotype**<br><a href="https://github.com/Living-with-machines/MapReader/tree/main/examples/non-maps/classification_plant_phenotype"><img src="figs/tutorial_classification_plant_phenotype.png" alt="tutorial for classification_plant_phenotype" style="height:200px;"></a><br><sup>Tutorial: train/fine-tune PyTorch CV classifiers on <ins>plant patches</ins> in images (plant phenotyping example).</sup> |
|:---:|:---:|
| **classification_mnist**<br><a href="https://github.com/Living-with-machines/MapReader/tree/main/examples/non-maps/classification_mnist"><img src="figs/tutorial_classification_mnist.png" alt="tutorial for classification_mnist" style="height:130px;"></a><br><sup>Tutorial: train/fine-tune PyTorch CV classifiers on <ins>MNIST</ins>.</sup> | |
</div>

# What is MapReader?

MapReader is an end-to-end computer vision (CV) pipeline for analyzing and exploring large collections of images and maps. 

MapReader was originally developed to analyze large historical maps (hence the name). However, MapReader is **general** enough to be applicable in both <ins>non-map images</ins> and <ins>maps</ins> and in a wide variety of domains. 

See [Gallery](#gallery) for some examples, and refer to each tutorial/example in [use cases](#use-cases) sections for more details on how MapReader can help and its relevant functionalities.

Generally, MapReader has two main components: preprocessing/annotation and training/inference:

<p align="center">
  <img src="./figs/MapReader_pipeline.png" 
        alt="MapReader pipeline" width="70%" align="center">
</p>

It provides a set of tools to:

- **load** images/maps stored locally or **retrieve** maps via web-servers (e.g., tileservers which can be used to retrieve maps from OpenStreetMap (OSM), the National Library of Scotland (NLS), or elsewhere). :warning: Refer to the [credits and re-use terms](#credits-and-re-use-terms) section if you are using digitized maps or metadata provided by NLS. 
- **preprocess** images/maps (e.g., divide them into patches, resampling the images, removing borders outside the neatline or reprojecting the map).
- annotate images/maps or their patches (i.e. slices of an image/map) using an **interactive annotation tool**.
- **train, fine-tune, and evaluate** various CV models.
- **predict** labels (i.e., model inference) on large sets of images/maps.
- Other functionalities include:
    - various **plotting tools** using, e.g., *matplotlib*, *cartopy*, *Google Earth*, and [kepler.gl](https://kepler.gl/).
    - compute mean/standard-deviation **pixel intensity** of image patches.

Table of contents
-----------------

- [Gallery](#gallery)
- [What is MapReader?](#what-is-mapreader)
- [Installation and setup](#installation)
  - [Set up a conda environment](#set-up-a-conda-environment)
  - [Method 1: pip](#method-1)
  - [Method 2: source code (for developers)](#method-2)
- [Use cases](#use-cases)
- [How to cite MapReader](#how-to-cite-mapreader)
- [Credits and re-use terms](#credits-and-re-use-terms)
  - [Digitized maps](#digitized-maps): MapReader can retrieve maps from NLS via tileserver. Read the re-use terms in this section.
  - [Metadata](#metadata): the metadata files are stored at [mapreader/persistent_data](https://github.com/Living-with-machines/MapReader/tree/main/mapreader/persistent_data). Read the re-use terms in this section.
  - [Acknowledgements](#acknowledgements)

## Installation

### Set up a conda environment

We strongly recommend installation via Anaconda:

* Refer to [Anaconda website and follow the instructions](https://docs.anaconda.com/anaconda/install/).

* Create a new environment for `mapreader` called `mr_py38`:

```bash
conda create -n mr_py38 python=3.8
```

* Activate the environment:

```bash
conda activate mr_py38
```

### Method 1

* Install `mapreader`:

```bash
pip install git+https://github.com/Living-with-machines/MapReader.git
```

and to work with maps:

```bash
pip install 'git+https://github.com/Living-with-machines/MapReader.git#egg=MapReader[maps]'
```

* ⚠️ On *Windows*, you might need to do:

```bash
# activate the environment
conda activate mr_py38

# install rasterio and fiona manually
conda install -c conda-forge rasterio=1.2.10
conda install -c conda-forge fiona=1.8.20

# install git
conda install git

# install MapReader
pip install git+https://github.com/Living-with-machines/MapReader.git

# open Jupyter Notebook (if you want to test/work with the notebooks in "examples" directory)
cd /path/to/MapReader 
jupyter notebook
```

* We have provided some [Jupyter Notebooks to show how different components in MapReader can be run](https://github.com/Living-with-machines/MapReader/tree/main/examples). To allow the newly created `mr_py38` environment to show up in the notebooks:

```bash
python -m ipykernel install --user --name mr_py38 --display-name "Python (mr_py38)"
```

* Continue with the [Tutorials](#table-of-contents)!

### Method 2

* Clone `mapreader` source code:

```bash
git clone https://github.com/Living-with-machines/MapReader.git 
```

* Install:

```bash
cd /path/to/MapReader
pip install -v -e .
```

and to work with maps:

```bash
cd /path/to/MapReader
pip install -e ."[maps]"
```

* Adding a `ipython` kernel to use in the [Tutorials](#table-of-contents)

```bash
python -m ipykernel install --user --name "<name-of-your-kernel>" --display-name "<Python (my kernel)>"
```
* Continue with the [Tutorials](#table-of-contents)!

## Use cases

[Tutorials](https://github.com/Living-with-machines/MapReader/tree/main/examples) are organized in Jupyter Notebooks as follows:
  - [Non-map images](https://github.com/Living-with-machines/MapReader/tree/main/examples/non-maps):
      - [classification_plant_phenotype](https://github.com/Living-with-machines/MapReader/tree/main/examples/non-maps/classification_plant_phenotype)
        * **Goal:** train/fine-tune PyTorch CV classifiers on plant patches in images (plant phenotyping example).
        * **Dataset:** Example images taken from the openly accessible `CVPPP2014_LSV_training_data` dataset available from https://www.plant-phenotyping.org/datasets-download. 
        * **Data access:** locally stored
        * **Annotations** are done on plant patches (i.e., slices of each plant image).
        * **Classifier:** train/fine-tuned PyTorch CV models.
      - [classification_mnist](https://github.com/Living-with-machines/MapReader/tree/main/examples/non-maps/classification_mnist)
        * **Goal:** train/fine-tune PyTorch CV classifiers on MNIST.
        * **Dataset:** Example images taken from http://yann.lecun.com/exdb/mnist/. 
        * **Data access:** locally stored
        * **Annotations** are done on MNIST (NOT patches/slices of MNIST images).
        * **Classifier:** train/fine-tuned PyTorch CV models.
  - [Maps](https://github.com/Living-with-machines/MapReader/tree/main/examples/maps):
      - [classification_one_inch_maps_001](https://github.com/Living-with-machines/MapReader/tree/main/examples/maps/classification_one_inch_maps_001)
        * **Goal:** train/fine-tune PyTorch CV classifiers on historical maps.
        * **Dataset:** from National Library of Scotland: [OS one-inch, 2nd edition layer](https://mapseries-tilesets.s3.amazonaws.com/1inch_2nd_ed/index.html).
        * **Data access:** tileserver
        * **Annotations** are done on map patches (i.e., slices of each map).
        * **Classifier:** train/fine-tuned PyTorch CV models.


## How to cite MapReader

Please consider acknowledging MapReader if it helps you to obtain results and figures for publications or presentations, by citing:

Link: https://arxiv.org/abs/2111.15592

```text
Kasra Hosseini, Daniel C. S. Wilson, Kaspar Beelen and Katherine McDonough (2021), MapReader: A Computer Vision Pipeline for the Semantic Exploration of Maps at Scale, arXiv:2111.15592.
```

and in BibTeX:

```bibtex
@misc{hosseini2021mapreader,
      title={MapReader: A Computer Vision Pipeline for the Semantic Exploration of Maps at Scale}, 
      author={Kasra Hosseini and Daniel C. S. Wilson and Kaspar Beelen and Katherine McDonough},
      year={2021},
      eprint={2111.15592},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```

## Credits and re-use terms 

### Digitized maps

MapReader can retrieve maps from NLS (National Library of Scotland) via webservers. For all the digitized maps (retrieved or locally stored), please note the re-use terms:

:warning: Use of the digitised maps for commercial purposes is currently restricted by contract. Use of these digitised maps for non-commercial purposes is permitted under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) (CC-BY-NC-SA) licence. Please refer to https://maps.nls.uk/copyright.html#exceptions-os for details on copyright and re-use license.

### Metadata

We have provided some metadata files in `mapreader/persistent_data`. For all these file, please note the re-use terms:

:warning: Use of the metadata for commercial purposes is currently restricted by contract. Use of this metadata for non-commercial purposes is permitted under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) (CC-BY-NC-SA) licence. Please refer to https://maps.nls.uk/copyright.html#exceptions-os for details on copyright and re-use license.

### Acknowledgements

This work was supported by Living with Machines (AHRC grant AH/S01179X/1) and The Alan Turing Institute (EPSRC grant EP/N510129/1). 
Living with Machines, funded by the UK Research and Innovation (UKRI) Strategic Priority Fund, is a multidisciplinary collaboration delivered by the Arts and Humanities Research Council (AHRC), with The Alan Turing Institute, the British Library and the Universities of Cambridge, East Anglia, Exeter, and Queen Mary University of London.
