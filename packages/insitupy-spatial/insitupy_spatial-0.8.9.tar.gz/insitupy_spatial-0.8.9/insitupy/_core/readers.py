import os
from os.path import abspath
from pathlib import Path
from typing import Literal, Optional, Union
from uuid import uuid4
from warnings import warn

import dask.dataframe as dd
import pandas as pd
from parse import *

from insitupy import __version__
from insitupy._constants import ISPY_METADATA_FILE
from insitupy._core._xenium import (_read_binned_expression,
                                    _read_boundaries_from_xenium,
                                    _read_matrix_from_xenium,
                                    _restructure_transcripts_dataframe)
from insitupy._core.insitudata import InSituData
from insitupy._exceptions import InvalidXeniumDirectory
from insitupy.io.files import read_json
from insitupy.utils.utils import convert_to_list

from .._core.dataclasses import (AnnotationsData, CellData, ImageData,
                                 MultiCellData, RegionsData)


def read_xenium(
    path: Union[str, os.PathLike, Path],
    nuclei_type: Literal["focus", "mip", ""] = "mip",
    load_cell_segmentation_images: bool = True,
    verbose: bool = True,
    transcript_mode: Literal["pandas", "dask"] = "dask",
    restructure_transcripts: bool = False
    ) -> InSituData:
    """
    Reads `Xenium In Situ data <https://www.10xgenomics.com/support/software/xenium-onboard-analysis/latest>`__
    from the specified directory.

    Args:
        path (Union[str, os.PathLike, Path]): Path to the Xenium data bundle.
        nuclei_type (Literal["focus", "mip", ""], optional): Type of nuclei image to load. Defaults to "mip".
            If "mip" is unavailable, "focus" will be used as a fallback.
        load_cell_segmentation_images (bool, optional): Whether to load cell segmentation images. Defaults to True.
        verbose (bool, optional): Whether to print progress messages. Defaults to True.
        transcript_mode (Literal["pandas", "dask"], optional): Mode to load transcript data. Defaults to "dask".
            - "pandas": Loads the data into a pandas DataFrame.
            - "dask": Loads the data into a Dask DataFrame for larger datasets.
        restructure_transcripts (bool, optional): Whether to restructure the transcript data. Defaults to False.

    Returns:
        InSituData: An object containing the processed Xenium experiment data, including metadata, cells, images, and transcripts.

    Raises:
        InvalidXeniumDirectory: If the specified directory does not contain the required Xenium metadata file.
        FileNotFoundError: If the specified directory does not exist.
        ValueError: If an invalid value is provided for `transcript_mode`.

    Notes:
        - The function initializes an `InSituData` object with metadata and loads cell data, images, and transcripts.
        - For Xenium versions <2.0, the "mip" image is used if available; otherwise, the "focus" image is loaded.
        - Cell segmentation images are loaded if available and `load_cell_segmentation_images` is True.
        - Transcript data can be loaded using either pandas or Dask, depending on the `transcript_mode` parameter.
    """

    path = Path(path) # make sure the path is a pathlib path
    metadata_filename: str = "experiment.xenium"

    if not (path / metadata_filename).exists():
        raise InvalidXeniumDirectory(directory=path)

    # INITIALIZE INSITUDATA
    # initialize the metadata dict
    metadata = {}
    metadata["data"] = {}
    metadata["history"] = {}
    metadata["history"]["cells"] = []
    metadata["history"]["annotations"] = []
    metadata["history"]["regions"] = []

    # check if path exists
    if not path.is_dir():
        raise FileNotFoundError(f"No such directory found: {str(path)}")

    # save paths of this project in metadata
    metadata["path"] = abspath(path).replace("\\", "/")
    metadata["metadata_file"] = metadata_filename

    # read metadata
    metadata["method_params"] = read_json(path / metadata_filename)

    # get slide id and sample id from metadata
    slide_id = metadata["method_params"]["slide_id"]
    sample_id = metadata["method_params"]["region_name"]

    # initialize the uid section
    metadata["uids"] = [str(uuid4())]

    # add method
    metadata["method"] = "Xenium"

    data = InSituData(path=path,
                        metadata=metadata,
                        slide_id=slide_id,
                        sample_id=sample_id,
                        )

    # LOAD CELLS
    if verbose:
        print("Loading cells...", flush=True)
    pixel_size = data.metadata["method_params"]["pixel_size"]
    # read celldata
    matrix = _read_matrix_from_xenium(path=data.path)
    boundaries = _read_boundaries_from_xenium(path=data.path, pixel_size=pixel_size)
    data.cells = MultiCellData()
    cd = CellData(matrix=matrix, boundaries=boundaries)
    data.cells.add_celldata(cd=cd, key="main", is_main=True)


    # LOAD IMAGES
    if verbose:
        print("Loading images...", flush=True)
    nuclei_file_key = f"morphology_{nuclei_type}_filepath"

    # In v2.0 the "mip" image was removed due to better focusing of the machine.
    # For <v2.0 the function still tries to retrieve the "mip" image but in case this is not found
    # it will retrieve the "focus" image
    if nuclei_type == "mip" and nuclei_file_key not in data.metadata["method_params"]["images"].keys():

        nuclei_type = "focus"
        nuclei_file_key = f"morphology_{nuclei_type}_filepath"

    # if names == "nuclei":
    img_keys = [nuclei_file_key]
    img_names = ["nuclei"]

    # get path of image files
    img_files = [data.metadata["method_params"]["images"][k] for k in img_keys]

    if load_cell_segmentation_images:
        # get cell segmentation images if available
        if "morphology_focus/" in data.metadata["method_params"]["images"][nuclei_file_key]:
            seg_files = ["morphology_focus/morphology_focus_0001.ome.tif",
                            "morphology_focus/morphology_focus_0002.ome.tif",
                            "morphology_focus/morphology_focus_0003.ome.tif"
                            ]
            seg_names = ["cellseg1", "cellseg2", "cellseg3"]

            # check which segmentation files exist and append to image list
            seg_file_exists_list = [(data.path / f).is_file() for f in seg_files]
            #print(seg_file_exists_list)
            img_files += [f for f, exists in zip(seg_files, seg_file_exists_list) if exists]
            img_names += [n for n, exists in zip(seg_names, seg_file_exists_list) if exists]

    # create imageData object
    img_paths = [data.path / elem for elem in img_files]

    if data.images is None:
        data.images = ImageData(img_paths, img_names)
    else:
        for im, n in zip(img_paths, img_names):
            data.images.add_image(im, n, overwrite=False, verbose=True)

    # LOAD TRANSCRIPTS
    transcript_filename = "transcripts.parquet"
    if verbose:
        print("Loading transcripts...", flush=True)

    if transcript_mode == "pandas":
        transcript_dataframe = pd.read_parquet(data.path / transcript_filename)

        if restructure_transcripts:
            data.transcripts = _restructure_transcripts_dataframe(transcript_dataframe)
        else:
            data.transcripts = transcript_dataframe
    elif transcript_mode == "dask":
        # Load the transcript data using Dask
        data.transcripts = dd.read_parquet(data.path / transcript_filename)
    else:
        raise ValueError(f"Invalid value for `transcript_mode`: {transcript_mode}")

    return data
