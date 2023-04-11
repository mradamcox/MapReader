import json
import os
from typing import Union
from shapely.geometry import Polygon, Point, shape
from shapely.ops import unary_union
from .data_structures import Coordinate, GridBoundingBox
from .tile_loading import TileDownloader
from .tile_merging import TileMerger
from .downloader_utils import get_index_from_coordinate
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import shutil


class SheetDownloader:
    """
    A class to download map sheets using metadata.
    """

    def __init__(
        self,
        metadata_path: str,
        download_url: Union[str, list],
    ):
        self.polygons = False
        self.grid_bbs = False
        self.wfs_id_nos = False
        self.published_dates = False
        self.found_queries = []

        assert isinstance(
            metadata_path, str
        ), "[ERROR] Please pass metadata_path as string."

        if os.path.isfile(metadata_path):
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)
                self.features = self.metadata["features"]
                print(self.__str__())

        else:
            raise ValueError("[ERROR] Metadata file not found.")

        if isinstance(download_url, str):
            my_ts = [download_url]
        elif isinstance(download_url, list):
            my_ts = download_url
        else:
            raise ValueError(
                "[ERROR] Please pass ``download_url`` as string or list of strings."
            )

        self.tile_server = my_ts

    def __str__(self) -> str:
        info = f"[INFO] Metadata file has {self.__len__()} item(s)."
        return info

    def __len__(self) -> int:
        return len(self.features)

    def get_polygons(self):
        for i, feature in enumerate(self.features):
            polygon = shape(feature["geometry"])
            map_name = feature["properties"]["IMAGE"]
            if len(polygon.geoms) != 1:
                f"[WARNING] Multiple geometries found in map {map_name}. Using first instance."
            feature["polygon"] = polygon.geoms[0]

        self.polygons = True

    def get_grid_bb(self, zoom_level: int = 14) -> None:
        if not self.polygons:
            self.get_polygons()

        for i, feature in enumerate(self.features):
            polygon = feature["polygon"]
            min_x, min_y, max_x, max_y = polygon.bounds

            start = Coordinate(min_y, max_x)  # (lat, lon)
            end = Coordinate(max_y, min_x)  # (lat, lon)

            start_idx = get_index_from_coordinate(start, zoom_level)
            end_idx = get_index_from_coordinate(end, zoom_level)
            grid_bb = GridBoundingBox(start_idx, end_idx)

            feature["grid_bb"] = grid_bb

        self.grid_bbs = True

    def extract_wfs_id_nos(self) -> None:
        for i, feature in enumerate(self.features):
            wfs_id = feature["id"]
            wfs_id_no = wfs_id.split(sep=".")[-1]

            feature["wfs_id_no"] = eval(wfs_id_no)

        self.wfs_id_nos = True

    def extract_published_dates(self) -> None:
        for i, feature in enumerate(self.features):
            wfs_title = feature["properties"]["WFS_TITLE"]
            published_date = re.findall(
                r"Published.*[\D]([\d]+)", wfs_title, flags=re.IGNORECASE
            )
            if len(published_date) > 0:
                feature["properties"]["published_date"] = eval(published_date[0])
                if len(published_date) != 1:
                    map_name = feature["properties"]["IMAGE"]
                    print(
                        f"[WARNING] Multiple published dates detected in {map_name}. Using first date."
                    )
            else:
                feature["properties"]["published_date"] = []
                map_name = feature["properties"]["IMAGE"]
                print(f"[WARNING] No published date detected in {map_name}.")

        self.published_dates = True

    def get_minmax_latlon(self):
        polygon_list = []
        for i, feature in enumerate(self.features):
            polygon = feature["polygon"]
            polygon_list.append(polygon)

        merged_polygon = unary_union(polygon_list)
        self.merged_polygon = merged_polygon

        min_x, min_y, max_x, max_y = merged_polygon.bounds
        print(
            f"[INFO] Min lat: {min_y}, max lat: {max_y} \n\
[INFO] Min lon: {min_x}, max lon: {max_x}"
        )

    def hist_published_dates(self):
        if not self.published_dates:
            self.extract_published_dates()

        published_dates = [
            feature["properties"]["published_date"] for feature in self.features
        ]
        min_date = min(published_dates)
        max_date = max(published_dates)
        date_range = max_date - min_date
        print(min_date, max_date, date_range)

        plt.hist(published_dates, bins=date_range, range=(min_date, max_date))
        plt.locator_params(integer=True)
        plt.xticks(size=14)
        plt.yticks(size=14)
        plt.xlabel("Published date", size=18)
        plt.ylabel("Counts", size=18)
        plt.show()

    def plot_metadata_on_map(
        self,
        map_extent: Union[str, list, tuple, None] = None,
        add_text: bool = True,
    ):
        plt.figure(figsize=[15, 15])
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution="10m", color="black", linewidth=1)

        if isinstance(map_extent, str):
            if map_extent in ["uk", "UK", "United Kingdom"]:
                extent = [-8.08999993, 1.81388127, 49.8338702, 60.95000002]
                ax.set_extent(extent)
            else:
                raise NotImplementedError(
                    '[ERROR] Currently only "UK" is implemented. \
Try passing coordinates (min_x, max_x, min_y, max_y) instead or leave blank to auto-set map extent.'
                )

        elif isinstance(map_extent, (list, tuple)):
            ax.set_extent(map_extent)
        else:
            pass

        if add_text:
            if not self.wfs_id_nos:
                self.extract_wfs_id_nos()

        for i, feature in enumerate(self.features):
            text_id = feature["wfs_id_no"]
            coords = np.array(feature["geometry"]["coordinates"][0][0])

            # Plot coordinates
            plt.plot(
                coords[:, 0],
                coords[:, 1],
                c="r",
                alpha=0.5,
                transform=ccrs.Geodetic(),
            )

            if add_text:
                plt.text(
                    np.mean(coords[:, 0]) - 0.15,
                    np.mean(coords[:, 1]) - 0.05,
                    f"{text_id}",
                    color="r",
                )

        plt.show()

    def _initialise_downloader(self):
        self.downloader = TileDownloader(self.tile_server)

    def _initialise_merger(self, path_save: str):
        self.merger = TileMerger(output_folder=path_save, show_progress=False)

    def _download_map(self, feature: dict):
        map_name = str("map_" + feature["properties"]["IMAGE"])
        self.downloader.download_tiles(feature["grid_bb"])
        self.merger.merge(feature["grid_bb"], map_name)
        print(f'[INFO] Downloaded "{map_name}.png"')
        shutil.rmtree("_tile_cache/")

    def _save_metadata(self, feature: dict):
        map_name = str("map_" + feature["properties"]["IMAGE"] + ".png")
        map_url = str(feature["properties"]["IMAGEURL"])
        coords = feature["geometry"]["coordinates"][0][0]

        if not self.published_dates:
            self.extract_published_dates()

        published_date = feature["properties"]["published_date"]
        grid_bb = feature["grid_bb"]

        return [map_name, map_url, coords, published_date, grid_bb]

    def _create_metadata_df(self, metadata_to_save: list, out_filepath):
        metadata_df = pd.DataFrame(
            metadata_to_save,
            columns=["name", "url", "coordinates", "published_date", "grid_bb"],
        )
        exists = True if os.path.exists(out_filepath) else False
        metadata_df.to_csv(out_filepath, sep="|", mode="a", header=not exists)

    def query_map_sheets_by_wfs_ids(
        self,
        wfs_ids: Union[list, int],
        append: bool = False,
    ) -> None:
        if not self.wfs_id_nos:
            self.extract_wfs_id_nos()

        if isinstance(wfs_ids, list):
            requested_maps = wfs_ids
        elif isinstance(wfs_ids, int):
            requested_maps = [wfs_ids]
        else:
            raise ValueError(
                "[ERROR] Please pass ``wfs_ids`` as int or list of ints. \
\
If you would like to donwload all your map sheets try ``.download_all_map_sheets()`` \
or, if you would like to download map sheets using a polygon try ``.download_map_sheets_by_polygon()``"
            )

        if not append:
            self.found_queries = []  # reset each time

        for feature in self.features:
            wfs_id_no = feature["wfs_id_no"]

            if wfs_id_no in requested_maps:
                self.found_queries.append(feature)

    def query_map_sheets_by_polygon(
        self, polygon: Polygon, mode: str = "within", append: bool = False
    ) -> None:
        assert isinstance(
            polygon, Polygon
        ), "[ERROR] Please pass polygon as shapely.geometry.Polygon object.\n\
[HINT] Use ``create_polygon_from_latlons()`` to create polygon."

        assert mode in [
            "within",
            "intersects",
        ], '[ERROR] Please use ``mode="within"`` or ``mode="intersects"``.'

        if not self.polygons:
            self.get_polygons()

        if not append:
            self.found_queries = []  # reset each time

        for feature in self.features:
            map_polygon = feature["polygon"]

            if mode == "within":
                if map_polygon.within(polygon):
                    self.found_queries.append(feature)
            elif mode == "intersects":
                if map_polygon.intersects(polygon):
                    self.found_queries.append(feature)

    def query_map_sheets_by_coordinates(
        self, coords: tuple, append: bool = False
    ) -> None:
        assert isinstance(
            coords, tuple
        ), "[ERROR] Please pass coords as a tuple in the form (x,y)."

        coords = Point(coords)

        if not self.polygons:
            self.get_polygons()

        if not append:
            self.found_queries = []  # reset each time

        for feature in self.features:
            map_polygon = feature["polygon"]

            if map_polygon.contains(coords):
                self.found_queries.append(feature)

    def print_found_queries(self) -> None:
        if not self.polygons:
            self.get_polygons()

        if len(self.found_queries) == 0:
            print("[INFO] No query results found/saved.")
        else:
            divider = 14 * "="
            print(f"{divider}\nQuery results:\n{divider}")
            for feature in self.found_queries:
                map_url = feature["properties"]["IMAGEURL"]
                map_bounds = feature["polygon"].bounds
                print(f"URL:     \t{map_url}")
                print(f"coordinates:  \t{map_bounds}")
                print(20 * "-")

    def download_all_map_sheets(
        self, path_save: str = "./maps/", metadata_path="metadata.csv"
    ) -> None:
        if not self.grid_bbs:
            raise ValueError("[ERROR] Please first run ``get_grid_bb()``")

        self._initialise_downloader()
        self._initialise_merger(path_save)

        metadata_to_save = []
        for feature in self.features:
            self._download_map(feature)
            metadata_to_save.append(self._save_metadata(feature))

        metadata_path = "{}{}".format(path_save, metadata_path)
        self._create_metadata_df(metadata_to_save, metadata_path)

    def download_map_sheets_by_wfs_ids(
        self,
        wfs_ids: Union[list, int],
        path_save: str = "./maps/",
        metadata_path="metadata.csv",
    ) -> None:
        """
        Note
        -----
        Download by wfs ids as shown on plot_metadata_on_map - not by sheet no.
        """

        if not self.wfs_id_nos:
            self.extract_wfs_id_nos()

        if isinstance(wfs_ids, list):
            requested_maps = wfs_ids
        elif isinstance(wfs_ids, int):
            requested_maps = [wfs_ids]
        else:
            raise ValueError(
                "[ERROR] Please pass ``wfs_ids`` as int or list of ints. \
\
If you would like to donwload all your map sheets try ``.download_all_map_sheets()`` \
or, if you would like to download map sheets using a polygon try ``.download_map_sheets_by_polygon()``"
            )

        if not self.grid_bbs:
            raise ValueError("[ERROR] Please first run ``get_grid_bb()``")

        self._initialise_downloader()
        self._initialise_merger(path_save)

        metadata_to_save = []
        for feature in self.features:
            wfs_id_no = feature["wfs_id_no"]
            if wfs_id_no in requested_maps:
                self._download_map(feature)
                metadata_to_save.append(self._save_metadata(feature))

        metadata_path = "{}{}".format(path_save, metadata_path)
        self._create_metadata_df(metadata_to_save, metadata_path)

    def download_map_sheets_by_polygon(
        self,
        polygon: Polygon,
        path_save: str = "./maps/",
        metadata_path="metadata.csv",
        mode: str = "within",
    ) -> None:
        """
        If mode="within" - will get all individual map sheets which are completely with polygon
        If mode="intersects" - will get all individual map sheets which overlap with polygon

        Note
        -----
        Use ``create_polygon_from_latlons()`` to create polygon.
        """

        assert isinstance(
            polygon, Polygon
        ), "[ERROR] Please pass polygon as shapely.geometry.Polygon object.\n\
[HINT] Use ``create_polygon_from_latlons()`` to create polygon."

        assert mode in [
            "within",
            "intersects",
        ], '[ERROR] Please use ``mode="within"`` or ``mode="intersects"``.'

        if not self.grid_bbs:
            raise ValueError("[ERROR] Please first run ``get_grid_bb()``")

        self._initialise_downloader()
        self._initialise_merger(path_save)

        metadata_to_save = []
        for feature in self.features:
            requested = False
            map_polygon = feature["polygon"]

            if mode == "within":
                if map_polygon.within(polygon):
                    requested = True
            elif mode == "intersects":
                if map_polygon.intersects(polygon):
                    requested = True

            if requested == True:
                self._download_map(feature)
                metadata_to_save.append(self._save_metadata(feature))

        metadata_path = "{}{}".format(path_save, metadata_path)
        self._create_metadata_df(metadata_to_save, metadata_path)

    def download_map_sheets_by_coordinates(
        self, coords: tuple, path_save: str = "./maps/", metadata_path="metadata.csv"
    ) -> None:
        """
        Download any map whose polygon contains with these coordinates.
        Coordinates are (x,y)

        """

        assert isinstance(
            coords, tuple
        ), "[ERROR] Please pass coords as a tuple in the form (x,y)."

        coords = Point(coords)

        if not self.grid_bbs:
            raise ValueError("[ERROR] Please first run ``get_grid_bb()``")

        self._initialise_downloader()
        self._initialise_merger(path_save)

        metadata_to_save = []
        for feature in self.features:
            map_polygon = feature["polygon"]

            if map_polygon.contains(coords):
                self._download_map(feature)
                metadata_to_save.append(self._save_metadata(feature))

        metadata_path = "{}{}".format(path_save, metadata_path)
        self._create_metadata_df(metadata_to_save, metadata_path)

    def download_map_sheets_by_queries(
        self,
        path_save: str = "./maps/",
        metadata_path="metadata.csv",
    ) -> None:
        if not self.grid_bbs:
            raise ValueError("[ERROR] Please first run ``get_grid_bb()``")

        self._initialise_downloader()
        self._initialise_merger(path_save)

        metadata_to_save = []
        for feature in self.found_queries:
            self._download_map(feature)
            metadata_to_save.append(self._save_metadata(feature))

        metadata_path = "{}{}".format(path_save, metadata_path)
        self._create_metadata_df(metadata_to_save, metadata_path)
