
import functools as ft
import os
import shutil
from datetime import datetime
from numbers import Number
from os.path import abspath
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union
from uuid import uuid4
from warnings import warn

import dask.dataframe as dd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from geopandas import GeoDataFrame
from parse import *
from pyarrow import ArrowInvalid
from scipy.sparse import issparse
from shapely import Point
from tqdm import tqdm

import insitupy._core._config as _config
from insitupy import WITH_NAPARI, __version__
from insitupy._constants import (CACHE, ISPY_METADATA_FILE, LOAD_FUNCS,
                                 MODALITIES, MODALITIES_COLOR_DICT)
from insitupy._core._checks import _check_geometry_symbol_and_layer
from insitupy._core._layers import _create_points_layer
from insitupy._core._save import (_save_annotations, _save_cells, _save_images,
                                  _save_regions, _save_transcripts)
from insitupy._core._utils import _get_cell_layer
from insitupy._core.dataclasses import (AnnotationsData, CellData, ImageData,
                                        MultiCellData, RegionsData)
from insitupy._exceptions import (InSituDataMissingObject,
                                  InSituDataRepeatedCropError,
                                  ModalityNotFoundError)
from insitupy._textformat import textformat as tf
from insitupy._warnings import NoProjectLoadWarning
from insitupy.images.utils import _get_contrast_limits, create_img_pyramid
from insitupy.io.files import (check_overwrite_and_remove_if_true, read_json,
                               write_dict_to_json)
from insitupy.io.io import read_multicelldata, read_shapesdata
from insitupy.utils.geo import fast_query_points_within_polygon
from insitupy.utils.utils import (_crop_transcripts,
                                  convert_napari_shape_to_polygon_or_line,
                                  convert_to_list)

# optional packages that are not always installed
if WITH_NAPARI:
    import napari
    from napari.layers import Layer, Points, Shapes

    #from napari.layers.shapes.shapes import Shapes
    from ._layers import _add_geometries_as_layer
    from ._widgets import _initialize_widgets, add_new_geometries_widget


class InSituData:
    """
    InSituData class for managing and analyzing spatially resolved transcriptomics data.

    .. figure:: ../_static/img/insitudata_overview.svg
       :width: 500px
       :align: right
       :class: dark-light

    It provides methods for loading, saving, visualizing, and manipulating various modalities
    of data, such as images, cells, annotations, regions, and transcripts.

    Attributes:
        images (ImageData): Image data associated with the object.
        cells (MultiCellData): Cell data associated with the object.
        annotations (AnnotationsData): Annotation data associated with the object.
        regions (RegionsData): Region data associated with the object.
        transcripts (pd.DataFrame): Transcript data associated with the object.

        path (Union[str, os.PathLike, Path]): Path to the data directory.
        metadata (dict): Metadata associated with the InSituData object.
        slide_id (str): Identifier for the slide.
        sample_id (str): Identifier for the sample.
        from_insitudata (bool): Indicates whether the object was loaded from an InSituData project.

        viewer (napari.Viewer): Napari viewer for visualizing the data.
        quicksave_dir (Path): *Experimental feature!* Directory for quicksave operations.

    Methods:
        __init__(path, metadata, slide_id, sample_id, from_insitudata):
            Initializes an InSituData object.
        __repr__():
            Returns a string representation of the object.
        assign_geometries(geometry_type, keys, add_masks, add_to_obs, overwrite, cells_layer):
            Assigns geometries (annotations or regions) to the cell data.
        assign_annotations(keys, add_masks, overwrite):
            Assigns annotations to the cell data.
        assign_regions(keys, add_masks, overwrite):
            Assigns regions to the cell data.
        copy(keep_path):
            Creates a deep copy of the InSituData object.
        crop(region_tuple, xlim, ylim, inplace, verbose):
            Crops the data based on the provided parameters.
        plot_dimred(save):
            Plots dimensionality reduction results.
        load_all(skip, verbose):
            Loads all available modalities.
        load_annotations(verbose):
            Loads annotation data.
        import_annotations(files, keys, scale_factor, verbose):
            Imports annotation data from external files.
        load_regions(verbose):
            Loads region data.
        import_regions(files, keys, scale_factor, verbose):
            Imports region data from external files.
        load_cells(verbose):
            Loads cell data.
        load_images(names, overwrite, verbose):
            Loads image data.
        load_transcripts(verbose, mode):
            Loads transcript data.
        read(path):
            Reads an InSituData object from a specified folder.
        saveas(path, overwrite, zip_output, images_as_zarr, zarr_zipped, images_max_resolution, verbose):
            Saves the InSituData object to a specified path.
        save(path, zarr_zipped, verbose, keep_history):
            Saves the InSituData object to its current path or a specified path.
        save_colorlegends(savepath, from_canvas, max_per_col):
            Saves color legends from the viewer.
        quicksave(note):
            *Experimental feature!* Saves a quick snapshot of the annotations.
        list_quicksaves():
            *Experimental feature!* Lists all available quicksaves.
        load_quicksave(uid):
            *Experimental feature!* Loads a quicksave by its unique identifier.
        show(keys, cells_layer, point_size, scalebar, unit, grayscale_colormap, return_viewer, widgets_max_width):
            Visualizes the data using a napari viewer.
        store_geometries(name_pattern, uid_col):
            Extracts geometric layers from the viewer and stores them as annotations or regions.
        reload(skip, verbose):
            Reloads the loaded modalities.
        get_loaded_modalities():
            Returns a list of currently loaded modalities.
        remove_history(verbose):
            Removes the history of saved modalities.
        remove_modality(modality):
            Removes a specific modality from the object.

    """

    # import deprecated functions
    from ._deprecated import (add_alt, add_baysor, normalize_and_transform,
                              read_all, read_annotations, read_cells,
                              read_images, read_regions, read_transcripts,
                              reduce_dimensions, save_current_colorlegend,
                              store_geometries)

    def __init__(self,
                 path: Union[str, os.PathLike, Path] = None,
                 metadata: dict = None,
                 slide_id: str = None,
                 sample_id: str = None,
                #  from_insitudata: bool = None,
                 ):
        """
        """
        # metadata
        if path is not None:
            self._path = Path(path)
        else:
            self._path = None
        self._metadata = metadata
        self._slide_id = slide_id
        self._sample_id = sample_id
        # self._from_insitudata = from_insitudata

        # modalities
        self._images = None
        self._cells = None
        self._annotations = None
        self._transcripts = None
        self._regions = None

        # other
        self._viewer = None
        self._quicksave_dir = None

    def __repr__(self):
        if self._metadata is None:
            method = "unknown"
        else:
            try:
                method = self._metadata["method"]
            except KeyError:
                method = "unknown"

        if self._path is not None:
            self._path = self._path.resolve()

        # check if all modalities are empty
        is_empty = np.all([elem is None for elem in [self._images, self._cells, self._annotations, self._transcripts, self._regions]])

        # if is_empty:
        #     repr = f"{tf.Bold+tf.Red}InSituData{tf.ResetAll}\nEmpty"
        # else:
        repr = (
            f"{tf.Bold+tf.Red}InSituData{tf.ResetAll}\n"
            f"{tf.Bold}Method:{tf.ResetAll}\t\t{method}\n"
            f"{tf.Bold}Slide ID:{tf.ResetAll}\t{self._slide_id}\n"
            f"{tf.Bold}Sample ID:{tf.ResetAll}\t{self._sample_id}\n"
            f"{tf.Bold}Path:{tf.ResetAll}\t\t{self._path}\n"
        )

        if self._metadata is not None:
            if "metadata_file" in self._metadata:
                mfile = self._metadata["metadata_file"]
            else:
                mfile = None
        else:
            mfile = None

        repr += f"{tf.Bold}Metadata file:{tf.ResetAll}\t{mfile}"

        if is_empty:
            repr += "\n\nNo modalities loaded."
        else:
            if self._images is not None:
                images_repr = self._images.__repr__()
                repr = (
                    repr + f"\n{tf.SPACER+tf.RARROWHEAD+MODALITIES_COLOR_DICT['images']+tf.Bold} images{tf.ResetAll}\n{tf.SPACER}   " + images_repr.replace("\n", f"\n{tf.SPACER}   ")
                )

            if self._cells is not None:
                cells_repr = self._cells.__repr__()
                repr = (
                    repr + f"\n{tf.SPACER+tf.RARROWHEAD+MODALITIES_COLOR_DICT['cells']+tf.Bold} cells{tf.ResetAll}\n{tf.SPACER}   " + cells_repr.replace("\n", f"\n{tf.SPACER}   ")
                )

            if self._transcripts is not None:
                trans_repr = f"DataFrame with shape {self._transcripts.shape[0]} x {self._transcripts.shape[1]}"

                repr = (
                    repr + f"\n{tf.SPACER+tf.RARROWHEAD+MODALITIES_COLOR_DICT['transcripts']+tf.Bold} transcripts{tf.ResetAll}\n{tf.SPACER}   " + trans_repr
                )

            if self._annotations is not None:
                annot_repr = self._annotations.__repr__()
                repr = (
                    repr + f"\n{tf.SPACER+tf.RARROWHEAD+MODALITIES_COLOR_DICT['annotations']+tf.Bold} annotations{tf.ResetAll}\n{tf.SPACER}   " + annot_repr.replace("\n", f"\n{tf.SPACER}   ")
                )

            if self._regions is not None:
                region_repr = self._regions.__repr__()
                repr = (
                    repr + f"\n{tf.SPACER+tf.RARROWHEAD+MODALITIES_COLOR_DICT['regions']+tf.Bold} regions{tf.ResetAll}\n{tf.SPACER}   " + region_repr.replace("\n", f"\n{tf.SPACER}   ")
                )
        return repr


    @property
    def path(self):
        """Return save path of the InSituData object.
        Returns:
            str: Save path.
        """
        return self._path

    @property
    def metadata(self):
        """Return metadata of the InSituData object.
        Returns:
            dict: Metadata.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: dict):
        self._metadata = metadata

    @property
    def slide_id(self):
        """Return slide id of the InSituData object.
        Returns:
            str: Slide id.
        """
        return self._slide_id

    @property
    def sample_id(self):
        """Return sample id of the InSituData object.
        Returns:
            str: Sample id.
        """
        return self._sample_id

    @property
    def from_insitudata(self):
        if self._path is not None:
            if Path(self._path).exists():
                return True
            else:
                print(f"Path {str(self._path)} does not exist.")
                return False
        else:
            return False

    @property
    def images(self):
        """Return images of the InSituData object.
        Returns:
            insitupy._core.dataclasses.ImageData: Images.
        """
        return self._images

    @images.setter
    def images(self, images: ImageData):
        self._images = images

    @images.deleter
    def images(self):
        self._images = None

    @property
    def cells(self):
        """Return cell data of the InSituData object.
        Returns:
            insitupy._core.dataclasses.MultiCellData: Cell data.
        """
        return self._cells

    @cells.setter
    def cells(self, value: MultiCellData):
        self._cells = value

    @cells.deleter
    def cells(self):
        self._cells = None

    @property
    def transcripts(self):
        """Return transcripts of the InSituData object.
        Returns:
            pd.DataFrame: Transcripts.
        """
        return self._transcripts

    @transcripts.setter
    def transcripts(self, value: dd.DataFrame):
        if isinstance(value, dd.DataFrame):
            self._transcripts = value
        else:
            raise ValueError(f"Value must be of type dask.dataframe.DataFrame, but got {type(value)} instead.")

    @transcripts.deleter
    def transcripts(self):
        self._transcripts = None

    @property
    def viewer(self):
        """Return viewer of the InSituData object.
        """
        return self._viewer

    @viewer.setter
    def viewer(self, value):
        self._viewer = value

    @viewer.deleter
    def viewer(self):
        self._viewer = None

    @property
    def annotations(self):
        """Return annotations of the InSituData object.
        Returns:
            insitupy._core.dataclasses.AnnotationsData: Annotations.
        """
        return self._annotations

    @annotations.setter
    def annotations(self, value: AnnotationsData):
        if isinstance(value, AnnotationsData):
            self._annotations = value
        else:
            raise ValueError(f"Value must be of type AnnotationsData, but got {type(value)} instead.")

    @annotations.deleter
    def annotations(self):
        self._annotations = None

    @property
    def regions(self):
        """Return regions of the InSituData object.
        Returns:
            insitupy._core.dataclasses.RegionsData: Regions.
        """
        return self._regions

    @regions.setter
    def regions(self, value: RegionsData):
        if isinstance(value, RegionsData):
            self._regions = value
        else:
            raise ValueError(f"Value must be of type RegionsData, but got {type(value)} instead.")

    @regions.deleter
    def regions(self):
        self._regions = None

    def assign_geometries(self,
                          geometry_type: Literal["annotations", "regions"],
                          keys: Union[str, Literal["all"]] = "all",
                          add_masks: bool = False,
                          add_to_obs: bool = False,
                          overwrite: bool = True,
                          cells_layer: str = None
                          ):
        '''
        Function to assign geometries (annotations or regions) to the anndata object in
        InSituData.cells[layer].matrix. Assignment information is added to the DataFrame in `.obs`.
        '''
        # assert that prerequisites are met
        try:
            geom_attr = getattr(self, geometry_type)
        except AttributeError:
            raise ModalityNotFoundError(modality=geometry_type)

        # get the right cells layer
        celldata, cells_layer_name = _get_cell_layer(
            cells=self.cells, cells_layer=cells_layer,
            verbose=True, return_layer_name=True
            )
        name = f".cells['{cells_layer_name}']"

        if keys == "all":
            keys = geom_attr.metadata.keys()

        # make sure annotation keys are a list
        keys = convert_to_list(keys)

        # convert coordinates into shapely Point objects
        x = celldata.matrix.obsm["spatial"][:, 0]
        y = celldata.matrix.obsm["spatial"][:, 1]
        cells = gpd.points_from_xy(x, y)
        cells = gpd.GeoSeries(cells)

        # iterate through annotation keys
        for key in keys:
            print(f"Assigning key '{key}'...")
            # extract pandas dataframe of current key
            geom_df = geom_attr[key]

            # make sure the geom names do not contain any ampersand string (' % '),
            # since this would interfere with the downstream analysis
            if geom_df["name"].str.contains(' & ').any():
                raise ValueError(
                    f"The {geometry_type} with key '{key}' contains names with the ampersand string ' & '. "
                    f"This is not allowed as it would interfere with downstream analysis."
                    )

            # get unique list of annotation names
            geom_names = geom_df.name.unique()

            # initiate dataframe as dictionary
            data = {}

            # iterate through names
            for n in tqdm(geom_names):
                polygons = geom_df[geom_df["name"] == n]["geometry"].tolist()

                #in_poly = [poly.contains(cells) for poly in polygons]
                in_poly = [fast_query_points_within_polygon(poly, cells) for poly in polygons]

                # check if points were in any of the polygons
                in_poly_res = np.array(in_poly).any(axis=0)

                # collect results
                data[n] = in_poly_res

            # convert into pandas dataframe
            data = pd.DataFrame(data)
            data.index = celldata.matrix.obs_names

            # transform data into one column
            column_to_add = [" & ".join(geom_names[row.values]) if np.any(row.values) else "unassigned" for _, row in data.iterrows()]

            if add_to_obs:
                # create annotation from annotation masks
                col_name = f"{geometry_type}-{key}"
                data[col_name] = column_to_add
                if col_name in celldata.matrix.obs:
                    if overwrite:
                        celldata.matrix.obs.drop(col_name, axis=1, inplace=True)
                        print(f'Existing column "{col_name}" is overwritten.', flush=True)
                        add = True
                    else:
                        warn(f'Column "{col_name}" exists already in `{name}.matrix.obs`. Assignment of key "{key}" was skipped. To force assignment, select `overwrite=True`.')
                        add = False
                else:
                    add = True

                if add:
                    if add_masks:
                        celldata.matrix.obs = pd.merge(left=celldata.matrix.obs, right=data, left_index=True, right_index=True)
                    else:
                        celldata.matrix.obs = pd.merge(left=celldata.matrix.obs, right=data.iloc[:, -1], left_index=True, right_index=True)

                    # save that the current key was analyzed
                    geom_attr.metadata[key]["analyzed"] = tf.TICK
            else:
                # add to obsm
                obsm_keys = celldata.matrix.obsm.keys()
                if geometry_type not in obsm_keys:
                    # add empty pandas dataframe with obs_names as index
                    celldata.matrix.obsm[geometry_type] = pd.DataFrame(index=celldata.matrix.obs_names)

                celldata.matrix.obsm[geometry_type][key] = column_to_add

                # save that the current key was analyzed
                geom_attr.metadata[key]["analyzed"] = tf.TICK

                print(f"Added results to `{name}.matrix.obsm['{geometry_type}']", flush=True)


    def assign_annotations(
        self,
        keys: Union[str, Literal["all"]] = "all",
        cells_layers: Optional[Union[List[str], str]] = None,
        add_masks: bool = False,
        overwrite: bool = True
    ):
        if cells_layers is None:
            layers_list = self._cells.get_all_keys()
        else:
            layers_list = convert_to_list(cells_layers)

        for l in layers_list:
            self.assign_geometries(
                geometry_type="annotations",
                keys=keys,
                add_masks=add_masks,
                overwrite=overwrite,
                cells_layer=l
            )

    def assign_regions(
        self,
        keys: Union[str, Literal["all"]] = "all",
        cells_layers: Optional[Union[List[str], str]] = None,
        add_masks: bool = False,
        overwrite: bool = True
    ):
        if cells_layers is None:
            layers_list = self._cells.get_all_keys()
        else:
            layers_list = convert_to_list(cells_layers)

        for l in layers_list:
            self.assign_geometries(
                geometry_type="regions",
                keys=keys,
                add_masks=add_masks,
                overwrite=overwrite,
                cells_layer=l
            )

    def copy(self, keep_path: bool = False):
        '''
        Function to generate a deep copy of the InSituData object.
        '''
        from copy import deepcopy
        had_viewer = False
        if self._viewer is not None:
            # make copy of viewer to add it later again
            had_viewer = True
            viewer_copy = self._viewer.copy()

            # remove viewer because there is otherwise a error during deepcopy
            self.viewer = None

        # make copy
        self_copy = deepcopy(self)

        if not keep_path:
            self_copy._path = None
            self_copy.metadata["path"] = None

        # add viewer again to original object if necessary
        if had_viewer:
            self._viewer = viewer_copy

        return self_copy

    def crop(self,
             region_tuple: Optional[Tuple[str, str]] = None,
             xlim: Optional[Tuple[int, int]] = None,
             ylim: Optional[Tuple[int, int]] = None,
             inplace: bool = False,
             verbose: bool = False
            ):
        """
        Crop the data based on the provided parameters.

        Args:
            region_tuple (Optional[Tuple[str, str]]): A tuple specifying the region to crop.
            xlim (Optional[Tuple[int, int]]): The x-axis limits for cropping.
            ylim (Optional[Tuple[int, int]]): The y-axis limits for cropping.
            inplace (bool): If True, modify the data in place. Otherwise, return a new cropped data.

        Raises:
            ValueError: If none of region_tuple, layer_name, or xlim/ylim are provided.
        """
        # check if the changes are supposed to be made in place or not
        if inplace:
            _self = self
        else:
            _self = self.copy()

        # if layer_name is None and region_tuple is None and (xlim is None or ylim is None):
        #     raise ValueError("At least one of shape_layer, region_tuple, or xlim/ylim must be provided.")
        if region_tuple is None:
            if xlim is None or ylim is None:
                raise ValueError("If shape is None, both xlim and ylim must not be None.")

            # make sure there are no negative values in the limits
            xlim = tuple(np.clip(xlim, a_min=0, a_max=None))
            ylim = tuple(np.clip(ylim, a_min=0, a_max=None))
            shape = None
        else:
            # extract regions dataframe
            region_key = region_tuple[0]
            region_name = region_tuple[1]
            region_df = self._regions[region_key]

            # extract geometry
            print(region_name)
            shape = region_df[region_df["name"] == region_name]["geometry"].item()
            #use_shape = True

            # extract x and y limits from the geometry
            minx, miny, maxx, maxy = shape.bounds # (minx, miny, maxx, maxy)
            xlim = (minx, maxx)
            ylim = (miny, maxy)

        try:
            # if the object was previously cropped, check if the current window is identical with the previous one
            if np.all([elem in _self.metadata["method_params"].keys() for elem in ["cropping_xlim", "cropping_ylim"]]):
                # test whether the limits are identical
                if (xlim == _self.metadata["method_params"]["cropping_xlim"]) & (ylim == _self.metadata["method_params"]["cropping_ylim"]):
                    raise InSituDataRepeatedCropError(xlim, ylim)
        except TypeError:
            pass

        if _self.cells is not None:
            _self.cells.crop(
                shape=shape,
                xlim=xlim, ylim=ylim,
                inplace=True, verbose=False
            )

        if _self.transcripts is not None:
            _self.transcripts = _crop_transcripts(
                transcript_df=_self.transcripts,
                shape=shape,
                xlim=xlim, ylim=ylim, verbose=verbose
            )

        if self._images is not None:
            _self.images.crop(xlim=xlim, ylim=ylim, inplace=True)

        if self._annotations is not None:

            _self.annotations.crop(
                shape=shape,
                xlim=tuple([elem for elem in xlim]),
                ylim=tuple([elem for elem in ylim]),
                verbose=verbose, inplace=True
                )

        if self._regions is not None:
            _self.regions.crop(
                shape=shape,
                xlim=tuple([elem for elem in xlim]),
                ylim=tuple([elem for elem in ylim]),
                verbose=verbose, inplace=True
            )

        if _self.metadata is not None:
            # add information about cropping to metadata
            if "cropping_history" not in _self.metadata:
                _self.metadata["cropping_history"] = {}
                _self.metadata["cropping_history"]["xlim"] = []
                _self.metadata["cropping_history"]["ylim"] = []
            _self.metadata["cropping_history"]["xlim"].append(tuple([int(elem) for elem in xlim]))
            _self.metadata["cropping_history"]["ylim"].append(tuple([int(elem) for elem in ylim]))

            # add new uid to uid history
            _self.metadata["uids"].append(str(uuid4()))

            # empty current data and data history entry in metadata
            _self.metadata["data"] = {}
            for k in _self.metadata["history"].keys():
                _self.metadata["history"][k] = []

        if inplace:
            if self._viewer is not None:
                del _self.viewer # delete viewer
        else:
            return _self

    # def add_alt(self,
    #             celldata_to_add: CellData,
    #             key_to_add: str
    #             ) -> None:
    #     # check if the current self has already an alt object and add a empty one if not
    #     #alt_attr_name = "alt"
    #     #try:
    #     #    alt_attr = getattr(self, alt_attr_name)
    #     #except AttributeError:
    #     #    setattr(self, alt_attr_name, {})
    #     #    alt_attr = getattr(self, alt_attr_name)

    #     if self._cells is None:
    #         self._cells = MultiCellData()

    #     # add the celldata to the given key
    #     self._cells.add_celldata(cd=celldata_to_add, key=key_to_add)

    # def add_baysor(self,
    #                path: Union[str, os.PathLike, Path],
    #                read_transcripts: bool = False,
    #                key_to_add: str = "baysor",
    #                pixel_size: Number = 1 # the pixel size is usually 1 since baysor runs on the µm coordinates
    #                ):

    #     # # convert to pathlib path
    #     path = Path(path)

    #     # read baysor data
    #     celldata = read_baysor_cells(baysor_output=path, pixel_size=pixel_size)

    #     # add celldata to alt attribute
    #     self.add_alt(celldata_to_add=celldata, key_to_add=key_to_add)

    #     if read_transcripts:
    #         #trans_attr_name = "transcripts"
    #         if self._transcripts is None:
    #             print("No transcript layer found. Addition of Baysor transcript data is skipped.", flush=True)
    #         else:
    #             trans_attr = self._transcripts
    #             # read baysor transcripts
    #             baysor_results = read_baysor_transcripts(baysor_output=path)
    #             baysor_results = baysor_results[["cell"]]

    #             # merge transcripts with existing transcripts
    #             baysor_results.columns = pd.MultiIndex.from_tuples([("cell_id", key_to_add)])
    #             trans_attr = pd.merge(left=trans_attr,
    #                                 right=baysor_results,
    #                                 left_index=True,
    #                                 right_index=True
    #                                 )

    #             # add resulting dataframe to InSituData
    #             self._transcripts = trans_attr


    def plot_dimred(self, save: Optional[str] = None):
        '''
        Read dimensionality reduction plots.
        '''
        # construct paths
        analysis_path = self._path / "analysis"
        umap_file = analysis_path / "umap" / "gene_expression_2_components" / "projection.csv"
        pca_file = analysis_path / "pca" / "gene_expression_10_components" / "projection.csv"
        cluster_file = analysis_path / "clustering" / "gene_expression_graphclust" / "clusters.csv"


        # read data
        umap_data = pd.read_csv(umap_file)
        pca_data = pd.read_csv(pca_file)
        cluster_data = pd.read_csv(cluster_file)

        # merge dimred data with clustering data
        data = ft.reduce(lambda left, right: pd.merge(left, right, on='Barcode'), [umap_data, pca_data.iloc[:, :3], cluster_data])
        data["Cluster"] = data["Cluster"].astype('category')

        # plot
        nrows = 1
        ncols = 2
        fig, axs = plt.subplots(nrows, ncols, figsize=(8*ncols, 6*nrows))
        sns.scatterplot(data=data, x="PC-1", y="PC-2", hue="Cluster", palette="tab20", ax=axs[0])
        sns.scatterplot(data=data, x="UMAP-1", y="UMAP-2", hue="Cluster", palette="tab20", ax=axs[1])
        if save is not None:
            plt.savefig(save)
        plt.show()

    def load_all(self,
                 skip: Optional[str] = None,
                 verbose: bool = False
                 ):
        # # extract read functions
        # read_funcs = [elem for elem in dir(self) if elem.startswith("load_")]
        # read_funcs = [elem for elem in read_funcs if elem not in ["load_all", "load_quicksave"]]

        for f in LOAD_FUNCS:
            if skip is None or skip not in f:
                func = getattr(self, f)
                try:
                    func(verbose=verbose)
                except ModalityNotFoundError as err:
                    if verbose:
                        print(err)

    def load_annotations(self, verbose: bool = False):
        if verbose:
            print("Loading annotations...", flush=True)
        try:
            p = self._metadata["data"]["annotations"]
        except KeyError:
            if verbose:
                raise ModalityNotFoundError(modality="annotations")
        else:
            self._annotations = read_shapesdata(path=self._path / p, mode="annotations")


    def import_annotations(self,
                           files: Optional[Union[str, os.PathLike, Path]],
                           keys: Optional[str],
                           scale_factor: Number, # µm/pixel - can be used to convert the pixel coordinates into µm coordinates
                           verbose: bool = False
                           ):
        if verbose:
            print("Importing annotations...", flush=True)

        # add annotations object
        files = convert_to_list(files)
        keys = convert_to_list(keys)

        if len(files) != len(keys):
            raise ValueError("Length of files and keys must be the same.")

        if self._annotations is None:
            self._annotations = AnnotationsData()

        for key, file in zip(keys, files):
            # read annotation and store in dictionary
            self._annotations.add_data(
                data=file,
                key=key,
                scale_factor=scale_factor
                )

        #self._remove_empty_modalities()

    def load_regions(self, verbose: bool = False):
        if verbose:
            print("Loading regions...", flush=True)
        try:
            p = self._metadata["data"]["regions"]
        except KeyError:
            if verbose:
                raise ModalityNotFoundError(modality="regions")
        else:
            self._regions = read_shapesdata(path=self._path / p, mode="regions")

    def import_regions(self,
                    files: Optional[Union[str, os.PathLike, Path]],
                    keys: Optional[str],
                    scale_factor: Number, # µm/pixel - used to convert the pixel coordinates into µm coordinates
                    verbose: bool = False
                    ):
        if verbose:
            print("Importing regions...", flush=True)

        # add regions object
        files = convert_to_list(files)
        keys = convert_to_list(keys)

        if len(files) != len(keys):
            raise ValueError("Length of files and keys must be the same.")


        if self._regions is None:
            self._regions = RegionsData()

        for key, file in zip(keys, files):
            # read annotation and store in dictionary
            self._regions.add_data(data=file,
                                key=key,
                                scale_factor=scale_factor
                                )

        #self._remove_empty_modalities()


    def load_cells(self, verbose: bool = False):
        if verbose:
            print("Loading cells...", flush=True)

        if self.from_insitudata:
            try:
                cells_path = self._metadata["data"]["cells"]
            except KeyError:
                if verbose:
                    raise ModalityNotFoundError(modality="cells")
            else:
                self._cells = read_multicelldata(path=self._path / cells_path)
        else:
            NoProjectLoadWarning()

    def load_images(self,
                    names: Union[Literal["all", "nuclei"], str] = "all", # here a specific image can be chosen
                    overwrite: bool = False,
                    verbose: bool = False
                    ):
        # load image into ImageData object
        if verbose:
            print("Loading images...", flush=True)

        if self.from_insitudata:
            # check if matrix data is stored in this InSituData
            try:
                images_dict = self._metadata["data"]["images"]
            except KeyError:
                if verbose:
                    raise ModalityNotFoundError(modality="images")
            else:
                if names == "all":
                    img_names = list(images_dict.keys())
                else:
                    img_names = convert_to_list(names)

                # get file paths and names
                img_files = [v for k,v in images_dict.items() if k in img_names]
                img_names = [k for k,v in images_dict.items() if k in img_names]

                # create imageData object
                img_paths = [self._path / elem for elem in img_files]

                if self._images is None:
                    self._images = ImageData(img_paths, img_names)
                else:
                    for im, n in zip(img_paths, img_names):
                        self._images.add_image(im, n, overwrite=overwrite, verbose=verbose)

        else:
            NoProjectLoadWarning()

    def load_transcripts(self,
                        verbose: bool = False,
                        mode: Literal["pandas", "dask"] = "dask",
                        ):
        # read transcripts
        if verbose:
            print("Loading transcripts...", flush=True)

        if self.from_insitudata:
            # check if transcript data is stored in this InSituData
            try:
                transcripts_path = self._metadata["data"]["transcripts"]
            except KeyError:
                if verbose:
                    raise ModalityNotFoundError(modality="transcripts")
            else:
                if mode == "pandas":
                    self._transcripts = pd.read_parquet(self._path / transcripts_path)
                elif mode == "dask":
                    # Load the transcript data using Dask
                    try:
                        self._transcripts = dd.read_parquet(self._path / transcripts_path)
                    except ArrowInvalid:
                        parquet_files = list(Path(self._path / transcripts_path).glob("part*.parquet"))
                        self._transcripts = dd.read_parquet(parquet_files)

                else:
                    raise ValueError(f"Invalid value for `mode`: {mode}")


        else:
            NoProjectLoadWarning()

    @classmethod
    def read(cls, path: Union[str, os.PathLike, Path]):
        """Read an InSituData object from a specified folder.

        Args:
            path (Union[str, os.PathLike, Path]): The path to the folder where data is saved.

        Returns:
            InSituData: A new InSituData object with the loaded data.
        """
        path = Path(path) # make sure the path is a pathlib path

        assert (path / ISPY_METADATA_FILE).exists(), "No insitupy metadata file found."
        # read InSituData metadata
        insitupy_metadata_file = path / ISPY_METADATA_FILE
        metadata = read_json(insitupy_metadata_file)

        # retrieve slide_id and sample_id
        slide_id = metadata["slide_id"]
        sample_id = metadata["sample_id"]

        # save paths of this project in metadata
        metadata["path"] = abspath(path).replace("\\", "/")
        metadata["metadata_file"] = ISPY_METADATA_FILE

        data = cls(path=path,
                   metadata=metadata,
                   slide_id=slide_id,
                   sample_id=sample_id,
                   #from_insitudata=True
                   )
        return data


    def saveas(self,
            path: Union[str, os.PathLike, Path],
            overwrite: bool = False,
            zip_output: bool = False,
            images_as_zarr: bool = True,
            zarr_zipped: bool = False,
            images_max_resolution: Optional[Number] = None, # in µm per pixel
            verbose: bool = True
            ):
        '''
        Function to save the InSituData object.

        Args:
            path: Path to save the data to.
        '''
        # check if the path already exists
        path = Path(path)

        # check overwrite
        check_overwrite_and_remove_if_true(path=path, overwrite=overwrite)

        if zip_output:
            zippath = path / (path.stem + ".zip")
            check_overwrite_and_remove_if_true(path=zippath, overwrite=overwrite)

        print(f"Saving data to {str(path)}") if verbose else None

        # create output directory if it does not exist yet
        path.mkdir(parents=True, exist_ok=True)

        # store basic information about experiment
        self._metadata["slide_id"] = self._slide_id
        self._metadata["sample_id"] = self._sample_id

        # clean old entries in data metadata
        self._metadata["data"] = {}

        # save images
        if self._images is not None:
            images = self._images
            _save_images(
                imagedata=images,
                path=path,
                metadata=self._metadata,
                images_as_zarr=images_as_zarr,
                zipped=zarr_zipped,
                max_resolution=images_max_resolution,
                verbose=False
                )

        # save cells
        if self._cells is not None:
            cells = self._cells
            _save_cells(
                cells=cells,
                path=path,
                metadata=self._metadata,
                boundaries_zipped=zarr_zipped,
                max_resolution_boundaries=images_max_resolution
            )

        # save transcripts
        if self._transcripts is not None:
            transcripts = self._transcripts
            _save_transcripts(
                transcripts=transcripts,
                path=path,
                metadata=self._metadata
                )

        # save annotations
        if self._annotations is not None:
            annotations = self._annotations
            _save_annotations(
                annotations=annotations,
                path=path,
                metadata=self._metadata
            )

        # save regions
        if self._regions is not None:
            regions = self._regions
            _save_regions(
                regions=regions,
                path=path,
                metadata=self._metadata
            )

        # save version of InSituPy
        self._metadata["version"] = __version__

        if "method_params" in self._metadata:
            # move method_param key to end of metadata
            self._metadata["method_params"] = self._metadata.pop("method_params")

        # write Xeniumdata metadata to json file
        xd_metadata_path = path / ISPY_METADATA_FILE
        write_dict_to_json(dictionary=self._metadata, file=xd_metadata_path)

        # Optionally: zip the resulting directory
        if zip_output:
            shutil.make_archive(path, 'zip', path, verbose=False)
            shutil.rmtree(path) # delete directory

        # # change path to the new one
        # self._path = path.resolve()

        # # reload the modalities
        # self.reload(verbose=False)

        print("Saved.") if verbose else None

    def save(self,
             path: Optional[Union[str, os.PathLike, Path]] = None,
             zarr_zipped: bool = False,
             verbose: bool = True,
             keep_history: bool = False
             ):

        # check path
        if path is not None:
            path = Path(path)
        else:
            if self.from_insitudata:
                #path = Path(self._metadata["path"])
                path = self.path
            else:
                warn(
                    f"Data is not linked to an InSituPy project folder (link can be lost by copy for example). "
                    f"Use `saveas()` instead to save the data to a new project folder."
                    )
                return

        if path.exists():
            if verbose:
                print(f"Saving to existing path: {str(path)}", flush=True)

            # check if path is a valid directory
            if not path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {str(path)}")

            # check if the folder is a InSituPy project
            metadata_file = path / ISPY_METADATA_FILE

            if metadata_file.exists():
                # read metadata file and check uid
                project_meta = read_json(metadata_file)

                # check uid
                project_uid = project_meta["uids"][-1]  # [-1] to select latest uid
                current_uid = self._metadata["uids"][-1]
                if current_uid == project_uid:
                    self._update_to_existing_project(path=path,
                                                     zarr_zipped=zarr_zipped,
                                                     verbose=verbose
                                                     )

                    # reload the modalities
                    self.reload(verbose=False, skip=["transcripts", "images"])

                    if not keep_history:
                        self.remove_history(verbose=False)
                else:
                    warn(
                        f"UID of current object {current_uid} not identical with UID in project path {path}: {project_uid}.\n"
                        f"Project is neither saved nor updated. Try `saveas()` instead to save the data to a new project folder. "
                        f"A reason for this could be the data has been cropped in the meantime."
                    )
            else:
                warn(
                    f"No `.ispy` metadata file in {path}. Directory is probably no valid InSituPy project. "
                    f"Use `saveas()` instead to save the data to a new InSituPy project."
                    )


        else:
            if verbose:
                print(f"Saving to new path: {str(path)}", flush=True)

            # save to the respective directory
            self.saveas(path=path)

    def save_colorlegends(
        self,
        savepath: Optional[Union[str, os.PathLike, Path]] = None,
        from_canvas: bool = False,
        max_per_col: int = 10
        ):
        from insitupy.plotting.plots import plot_colorlegend

        if from_canvas:
            # Check if static_canvas exists
            if not hasattr(_config, 'static_canvas'):
                print("Warning: 'static_canvas' attribute not found in config. "
                    "Please display data in the napari viewer using '.show()' first.")
                return

            try:
                # Save the figure to a PDF file
                _config.static_canvas.figure.savefig(savepath)
                print(f"Figure saved as {savepath}")
            except RuntimeError as e:
                if 'FigureCanvasQTAgg has been deleted' in str(e):
                    print("Warning: The color legend has been deleted and cannot be saved.")
                else:
                    raise  # Re-raise the exception if it's a different error
        else:
            if not hasattr(self, "viewer"):
                raise ValueError("No viewer attribute found. Open a napari viewer with `.show()`.")

            selected_layers = self.viewer.layers.selection
            for layer in selected_layers:
                if savepath is None:
                    savepath = Path(f"figures/colorlegend-{layer.name}.pdf")
                plot_colorlegend(
                    viewer=self.viewer,
                    mapping=None,
                    layer_name=layer.name,
                    max_per_col=max_per_col,
                    savepath=savepath
                    )

    def _update_to_existing_project(self,
                                    path: Optional[Union[str, os.PathLike, Path]],
                                    zarr_zipped: bool = False,
                                    verbose: bool = True
                                    ):
        if verbose:
            print(f"Updating project in {path}")

        # save cells
        if self._cells is not None:
            cells = self._cells
            if verbose:
                print("\tUpdating cells...", flush=True)
            _save_cells(
                cells=cells,
                path=path,
                metadata=self._metadata,
                boundaries_zipped=zarr_zipped,
                overwrite=True
            )


        # save annotations
        if self._annotations is not None:
            annotations = self._annotations
            if verbose:
                print("\tUpdating annotations...", flush=True)
            _save_annotations(
                annotations=annotations,
                path=path,
                metadata=self._metadata
            )

        # save regions
        if self._regions is not None:
            regions = self._regions
            if verbose:
                print("\tUpdating regions...", flush=True)
            _save_regions(
                regions=regions,
                path=path,
                metadata=self._metadata
            )

        # save version of InSituPy
        self._metadata["version"] = __version__

        if "method_params" in self._metadata:
            # move method_params key to end of metadata
            self._metadata["method_params"] = self._metadata.pop("method_params")

        # write Xeniumdata metadata to json file
        xd_metadata_path = path / ISPY_METADATA_FILE
        write_dict_to_json(dictionary=self._metadata, file=xd_metadata_path)

        if verbose:
            print("Saved.")


    def quicksave(self,
                  note: Optional[str] = None
                  ):
        # create quicksave directory if it does not exist already
        self._quicksave_dir = CACHE / "quicksaves"
        self._quicksave_dir.mkdir(parents=True, exist_ok=True)

        # save annotations
        if self._annotations is None:
            print("No annotations found. Quicksave skipped.", flush=True)
        else:
            annotations = self._annotations
            # create filename
            current_datetime = datetime.now().strftime("%y%m%d_%H-%M-%S")
            slide_id = self._slide_id
            sample_id = self._sample_id
            uid = str(uuid4())[:8]

            # create output directory
            outname = f"{slide_id}__{sample_id}__{current_datetime}__{uid}"
            outdir = self._quicksave_dir / outname

            _save_annotations(
                annotations=annotations,
                path=outdir,
                metadata=None
            )

            if note is not None:
                with open(outdir / "note.txt", "w") as notefile:
                    notefile.write(note)

            # # # zip the output
            # shutil.make_archive(outdir, format='zip', root_dir=outdir, verbose=False)
            # shutil.rmtree(outdir) # delete directory


    def list_quicksaves(self):
        pattern = "{slide_id}__{sample_id}__{savetime}__{uid}"

        # collect results
        res = {
            "slide_id": [],
            "sample_id": [],
            "savetime": [],
            "uid": [],
            "note": []
        }
        for d in self._quicksave_dir.glob("*"):
            parse_res = parse(pattern, d.stem).named
            for key, value in parse_res.items():
                res[key].append(value)

            notepath = d / "note.txt"
            if notepath.exists():
                with open(notepath, "r") as notefile:
                    res["note"].append(notefile.read())
            else:
                res["note"].append("")

        # create and return dataframe
        return pd.DataFrame(res)

    def load_quicksave(self,
                       uid: str
                       ):
        # find files with the uid
        files = list(self._quicksave_dir.glob(f"*{uid}*"))

        if len(files) == 1:
            ad = read_shapesdata(files[0] / "annotations", mode="annotations")
        elif len(files) == 0:
            print(f"No quicksave with uid '{uid}' found. Use `.list_quicksaves()` to list all available quicksaves.")
        else:
            raise ValueError(f"More than one quicksave with uid '{uid}' found.")

        # add annotations to existing annotations attribute or add a new one
        if self._annotations is None:
            self._annotations = AnnotationsData()
        else:
            annotations = self._annotations
            for k in ad.metadata.keys():
                annotations.add_data(ad[k], k, verbose=True)


    def show(self,
        keys: Optional[str] = None,
        cells_layer: Optional[str] = None,
        point_size: int = 8,
        scalebar: bool = True,
        unit: str = "µm",
        grayscale_colormap: List[str] = ["red", "green", "cyan", "magenta", "yellow", "gray"],
        return_viewer: bool = False,
        widgets_max_width: int = 500
        ):

        # create viewer
        self._viewer = napari.Viewer(title=f"{self._slide_id}: {self._sample_id}")

        if self._images is None:
            warn("No attribute `.images` found.")
        else:
            images_attr = self._images
            n_images = len(images_attr.metadata)
            n_grayscales = 0 # number of grayscale images
            for i, (img_name, img_metadata) in enumerate(images_attr.metadata.items()):
            #for i, img_name in enumerate(image_keys):
                img = images_attr[img_name]
                is_visible = False if i < n_images - 1 else True # only last image is set visible
                pixel_size = img_metadata['pixel_size']

                # check if the current image is RGB
                is_rgb = self._images.metadata[img_name]["rgb"]

                if is_rgb:
                    cmap = None  # default value of cmap
                    blending = "translucent_no_depth"  # set blending mode
                else:
                    if img_name == "nuclei":
                        cmap = "blue"
                    else:
                        cmap = grayscale_colormap[n_grayscales]
                        n_grayscales += 1
                    blending = "additive"  # set blending mode


                if not isinstance(img, list):
                    # create image pyramid for lazy loading
                    img_pyramid = create_img_pyramid(img=img, nsubres=6)
                else:
                    img_pyramid = img

                # infer contrast limits
                contrast_limits = _get_contrast_limits(img_pyramid)

                if contrast_limits[1] == 0:
                    warn("The maximum value of the image is 0. Is the image really completely empty?")
                    contrast_limits = (0, 255)

                # add img pyramid to napari viewer
                self._viewer.add_image(
                        img_pyramid,
                        name=img_name,
                        colormap=cmap,
                        blending=blending,
                        rgb=is_rgb,
                        contrast_limits=contrast_limits,
                        scale=(pixel_size, pixel_size),
                        visible=is_visible
                    )

        # optionally: add cells as points
        if keys is not None:
            if self._cells is None:
                raise InSituDataMissingObject("cells")
            else:
                celldata = _get_cell_layer(cells=self.cells, cells_layer=cells_layer)
                # convert keys to list
                keys = convert_to_list(keys)

                # get point coordinates
                points = np.flip(celldata.matrix.obsm["spatial"].copy(), axis=1) # switch x and y (napari uses [row,column])
                #points *= pixel_size # convert to length unit (e.g. µm)

                # get expression matrix
                if issparse(celldata.matrix.X):
                    X = celldata.matrix.X.toarray()
                else:
                    X = celldata.matrix.X

                for i, k in enumerate(keys):
                    #pvis = False if i < len(keys) - 1 else True # only last image is set visible
                    # get expression values
                    if k in celldata.matrix.obs.columns:
                        color_value = celldata.matrix.obs[k].values

                    else:
                        geneid = celldata.matrix.var_names.get_loc(k)
                        color_value = X[:, geneid]

                    # extract names of cells
                    cell_names = celldata.matrix.obs_names.values

                    # create points layer
                    layer = _create_points_layer(
                        points=points,
                        color_values=color_value,
                        name=k,
                        point_names=cell_names,
                        point_size=point_size,
                        visible=True
                    )

                    # add layer programmatically - does not work for all types of layers
                    # see: https://forum.image.sc/t/add-layerdatatuple-to-napari-viewer-programmatically/69878
                    self._viewer.add_layer(Layer.create(*layer))

        # WIDGETS
        if self._cells is None:
            # add annotation widget to napari
            add_geom_widget = add_new_geometries_widget()
            add_geom_widget.max_height = 120
            add_geom_widget.max_width = widgets_max_width
            self._viewer.window.add_dock_widget(add_geom_widget, name="Add geometries", area="right")
        else:
            celldata = self._cells
            # initialize the widgets
            show_points_widget, locate_cells_widget, show_geometries_widget, show_boundaries_widget, select_data, filter_cells_widget = _initialize_widgets(xdata=self)

            # add widgets to napari window
            if select_data is not None:
                self._viewer.window.add_dock_widget(select_data, name="Select data", area="right")
                select_data.max_height = 50
                select_data.max_width = widgets_max_width

            if show_points_widget is not None:
                self.viewer.window.add_dock_widget(show_points_widget, name="Show data", area="right")
                show_points_widget.max_height = 170
                show_points_widget.max_width = widgets_max_width

            if show_boundaries_widget is not None:
                self._viewer.window.add_dock_widget(show_boundaries_widget, name="Show boundaries", area="right")
                #show_boundaries_widget.max_height = 80
                show_boundaries_widget.max_width = widgets_max_width

            if locate_cells_widget is not None:
                self._viewer.window.add_dock_widget(locate_cells_widget, name="Navigate to cell", area="right", tabify=True)
                #locate_cells_widget.max_height = 130
                locate_cells_widget.max_width = widgets_max_width

            if filter_cells_widget is not None:
                self.viewer.window.add_dock_widget(filter_cells_widget, name="Filter cells", area="right", tabify=True)
                filter_cells_widget.max_height = 150
                show_points_widget.max_width = widgets_max_width

            # add annotation widget to napari
            add_geom_widget = add_new_geometries_widget()
            #annot_widget.max_height = 100
            add_geom_widget.max_width = widgets_max_width
            self._viewer.window.add_dock_widget(add_geom_widget, name="Add geometries", area="right", tabify=False, #add_vertical_stretch=True
                                                )

            # if show_region_widget is not None:
            #     self.viewer.window.add_dock_widget(show_region_widget, name="Show regions", area="right")
            #     show_region_widget.max_height = 100
            #     show_region_widget.max_width = widgets_max_width

            if show_geometries_widget is not None:
                self._viewer.window.add_dock_widget(show_geometries_widget, name="Show geometries", area="right", tabify=True)
                show_geometries_widget.max_width = widgets_max_width

        # EVENTS
        # Assign function to an layer addition event
        def _update_uid(event):
            if event is not None:
                layer = event.source
                if event.action == "added":
                    if 'uid' in layer.properties:
                        layer.properties['uid'][-1] = str(uuid4())
                    else:
                        layer.properties['uid'] = np.array([str(uuid4())], dtype='object')

                # elif event.action == "removed":
                #     pass
                # else:
                #     raise ValueError(f"Unexpected value '{event.action}' for `event.action`. Expected 'add' or 'remove'.")

        # Assign the function to data of all existing layers
        for layer in self._viewer.layers:
            if isinstance(layer, Shapes) or isinstance(layer, Points):
                layer.events.data.connect(_update_uid)

        # Connect the function to the data of existing shapes and points layers in the viewer
        def connect_to_all_shapes_layers(event):
            layer = event.source[event.index]
            if event is not None:
                if isinstance(layer, Shapes) or isinstance(layer, Points):
                    layer.events.data.connect(_update_uid)

        # Connect the function to any new layers added to the viewer
        self._viewer.layers.events.inserted.connect(connect_to_all_shapes_layers)

        # add color legend widget
        import insitupy._core._config as _config
        from insitupy._core._config import init_colorlegend_canvas
        init_colorlegend_canvas()
        self._viewer.window.add_dock_widget(_config.static_canvas, area='left', name='Color legend')

        # NAPARI SETTINGS
        if scalebar:
            # add scale bar
            self._viewer.scale_bar.visible = True
            self._viewer.scale_bar.unit = unit

        napari.run()
        if return_viewer:
            return self._viewer

    def sync_geometries(self):
        name_pattern = "{type_symbol} {class_name} ({annot_key})"

        if self._viewer is not None:
            viewer = self._viewer
        else:
            print("Use `.show()` first to open a napari viewer.")

        # iterate through layers and save them as annotation or region if they meet requirements
        layers = viewer.layers
        for layer in layers:
            if isinstance(layer, Shapes) or isinstance(layer, Points):
                name_parsed = parse(name_pattern, layer.name)
                if name_parsed is not None:
                    type_symbol = name_parsed.named["type_symbol"]
                    annot_key = name_parsed.named["annot_key"]
                    class_name = name_parsed.named["class_name"]

                    checks_passed, object_type = _check_geometry_symbol_and_layer(
                        layer=layer, type_symbol=type_symbol
                    )

                    if checks_passed:
                        if object_type == "annotation":
                            # if the InSituData object does not have an annotations attribute, initialize it
                            if self.annotations is None:
                                self.annotations = AnnotationsData() # initialize empty object

                            shapesdata = self.annotations
                        else:
                            # if the InSituData object does not have an regions attribute, initialize it
                            if self.regions is None:
                                self.regions = RegionsData() # initialize empty object

                            shapesdata = self.regions

                        # import all geometries from viewer into InSituData
                        self._store_geometries(
                            layer=layer,
                            shapesdata=shapesdata,
                            object_type=object_type,
                            annot_key=annot_key,
                            class_name=class_name
                        )

                        # remove entries in InSituData that are not present in viewer
                        current_ids = layer.properties['uid'] # get ids from current layer
                        geom_df = shapesdata[annot_key]
                        ids_stored = geom_df[geom_df["name"] == class_name].index

                        # filter geom_df and keep only those entries that are also present in viewer
                        mask = ~ids_stored.isin(current_ids)
                        ids_to_remove = ids_stored[mask]
                        n_removed = np.sum(mask)
                        geom_df.drop(
                            ids_to_remove,
                            inplace=True
                            )

                        if n_removed > 0:
                            if n_removed > 1:
                                object_str = object_type + "s"
                            else:
                                object_str = object_type

                            print(f"Removed {n_removed} {object_str} with key {annot_key} and class {class_name}.")

    def _store_geometries(
        self,
        layer,
        shapesdata,
        object_type: str,
        annot_key: str,
        class_name: str,
        uid_col: str = "id"
        ):
        # extract shapes coordinates and colors
        layer_data = layer.data
        scale = layer.scale

        if isinstance(layer, Points):
            colors = layer.border_color.tolist()
        else:
            colors = layer.edge_color.tolist()

        if isinstance(layer, Shapes):
            # extract shape types
            shape_types = layer.shape_type
            # build annotation GeoDataFrame
            geom_df = {
                uid_col: layer.properties["uid"],
                "objectType": object_type,
                "geometry": [convert_napari_shape_to_polygon_or_line(napari_shape_data=ar, shape_type=st) for ar, st in zip(layer_data, shape_types)],
                "name": class_name,
                "color": [[int(elem[e]*255) for e in range(3)] for elem in colors],
            }

        elif isinstance(layer, Points):
            # build annotation GeoDataFrame
            geom_df = {
                uid_col: layer.properties["uid"],
                "objectType": object_type,
                "geometry": [Point(d[1], d[0]) for d in layer_data],  # switch x/y
                "name": class_name,
                "color": [[int(elem[e]*255) for e in range(3)] for elem in colors],
            }

        # generate GeoDataFrame
        geom_df = GeoDataFrame(geom_df, geometry="geometry")

        # add annotations
        shapesdata.add_data(
            data=geom_df,
            key=annot_key,
            verbose=True,
            scale_factor=scale[0]
            )

        # if object_type == "region":
        #     # add regions
        #     self.regions.add_data(
        #         data=geom_df,
        #         key=annot_key,
        #         verbose=True,
        #         scale_factor=scale[0]
        #         )
        # else:
        #     # add annotations
        #     self.annotations.add_data(
        #         data=geom_df,
        #         key=annot_key,
        #         verbose=True,
        #         scale_factor=scale[0]
        #         )



    # def sync_geometries(
    #     self
    # ):
    #     # store all geometries from viewer
    #     self.store_geometries()

    #     # remove non-matching entries


    # def plot_expr_along_obs_val(
    #     self,
    #     keys: str,
    #     obs_val: str,
    #     cells_layer: Optional[str] = None,
    #     groupby: Optional[str] = None,
    #     method: Literal["lowess", "loess"] = 'loess',
    #     stderr: bool = False,
    #     savepath=None,
    #     return_data=False,
    #     **kwargs
    #     ):
    #     # retrieve anndata object from InSituData
    #     celldata = _get_cell_layer(cells=self.cells, cells_layer=cells_layer, verbose=True)
    #     adata = celldata.matrix

    #     results = expr_along_obs_val(
    #         adata=adata,
    #         keys=keys,
    #         obs_val=obs_val,
    #         groupby=groupby,
    #         method=method,
    #         stderr=stderr,
    #         savepath=savepath,
    #         return_data=return_data,
    #         **kwargs
    #         )

    #     if return_data:
    #         return results

    def reload(
        self,
        skip: Optional[List] = None,
        verbose: bool = True
        ):
        data_meta = self._metadata["data"]
        loaded_modalities = [elem for elem in self.get_loaded_modalities() if elem in data_meta]

        if skip is not None:
            # remove the modalities which are supposed to be skipped during reload
            skip = convert_to_list(skip)
            for s in skip:
                try:
                    loaded_modalities.remove(s)
                except ValueError:
                    pass

        if len(loaded_modalities) > 0:
            print(f"Reloading following modalities: {', '.join(loaded_modalities)}") if verbose else None
            for cm in loaded_modalities:
                func = getattr(self, f"load_{cm}")
                func(verbose=verbose)
        else:
            print("No modalities with existing save path found. Consider saving the data with `saveas()` first.")

    def get_modality(self, modality: str):
        return getattr(self, modality)

    def get_loaded_modalities(self):
        loaded_modalities = [m for m in MODALITIES if getattr(self, m) is not None]
        return loaded_modalities

    def remove_history(self,
                       verbose: bool = True
                       ):

        for cat in ["annotations", "cells", "regions"]:
            dirs_to_remove = []
            #if hasattr(self, cat):
            files = sorted((self._path / cat).glob("*"))
            if len(files) > 1:
                dirs_to_remove = files[:-1]

                for d in dirs_to_remove:
                    shutil.rmtree(d)

                print(f"Removed {len(dirs_to_remove)} entries from '.{cat}'.") if verbose else None
            else:
                print(f"No history found for '{cat}'.") if verbose else None

    def remove_modality(self,
                        modality: str
                        ):
        if hasattr(self, modality):
            # delete attribute from InSituData object
            delattr(self, modality)

            # delete metadata
            self.metadata["data"].pop(modality, None) # returns None if key does not exist

        else:
            print(f"No modality '{modality}' found. Nothing removed.")
