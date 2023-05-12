from mapreader.load.images import MapImages
from mapreader.load.loader import loader
from mapreader.load.loader import load_patches

from mapreader.download import azure_access
from mapreader.download.tileserver_access import TileServer

from mapreader.learn.load_annotations import AnnotationsLoader
from mapreader.learn.datasets import PatchDataset
from mapreader.learn.datasets import patchContextDataset
from mapreader.learn.classifier import classifier
from mapreader.learn.classifier_context import classifierContext
from mapreader.learn import custom_models

from mapreader.process import process

from . import _version

__version__ = _version.get_versions()["version"]

from mapreader.load import geo_utils
