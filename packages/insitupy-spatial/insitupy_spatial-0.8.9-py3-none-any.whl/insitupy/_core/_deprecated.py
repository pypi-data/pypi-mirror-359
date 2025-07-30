from warnings import warn


### DEPRECATED INSITUDATA FUNCTIONS
def read_all(self, *args, **kwargs):
    warn("`read_all` is deprecated. Use `load_all` instead.", DeprecationWarning, stacklevel=2)

def read_annotations(self, *args, **kwargs):
    warn("`read_annotations` is deprecated. Use `load_annotations` instead.", DeprecationWarning, stacklevel=2)

def read_regions(self, *args, **kwargs):
    warn("`read_regions` is deprecated. Use `load_regions` instead.", DeprecationWarning, stacklevel=2)

def read_cells(self, *args, **kwargs):
    warn("`read_cells` is deprecated. Use `load_cells` instead.", DeprecationWarning, stacklevel=2)

def read_images(self, *args, **kwargs):
    warn("`read_images` is deprecated. Use `load_images` instead.", DeprecationWarning, stacklevel=2)

def read_transcripts(self, *args, **kwargs):
    warn("`read_transcripts` is deprecated. Use `load_transcripts` instead.", DeprecationWarning, stacklevel=2)

def read_xenium(self, *args, **kwargs):
    warn("`read_xenium` is deprecated. Use `read(mode='xenium')` instead.", DeprecationWarning, stacklevel=2)

def normalize_and_transform(self, *args, **kwargs):
    warn("`normalize_and_transform()` is deprecated. Use `insitupy.preprocessing.normalize_and_transform()` instead.", DeprecationWarning, stacklevel=2)

def reduce_dimensions(self, *args, **kwargs):
    warn("`reduce_dimensions()` is deprecated. Instead, use `insitupy.preprocessing.reduce_dimensions()` for dimensionality reduction and `insitupy.preprocessing.cluster_cells()` for clustering.", DeprecationWarning, stacklevel=2)

def plot_overview(self, *args, **kwargs):
    warn("`plot_overview()` is deprecated. Use `insitupy.plotting.plot_overview()` instead.", DeprecationWarning, stacklevel=2)

def save_current_colorlegend(self, *args, **kwargs):
    warn("`save_current_colorlegend()` is deprecated. Use `.save_colorlegends()` instead.", DeprecationWarning, stacklevel=2)

def add_alt(self, *args, **kwargs):
    warn("`add_alt()` is deprecated. Use `.cells.add_{}()` instead.", DeprecationWarning, stacklevel=2)

def add_baysor(self, *args, **kwargs):
    warn("`add_baysor()` is deprecated. Use `.cells.add_{}()` instead.", DeprecationWarning, stacklevel=2)

def store_geometries(self, *args, **kwargs):
    warn("`store_geometries()` is deprecated. Use `.cells.sync_geometries()` instead.", DeprecationWarning, stacklevel=2)