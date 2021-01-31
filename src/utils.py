from functools import partial

import pyproj
import numpy as np
import scipy.ndimage as nd
from shapely.geometry import Point
from shapely.ops import transform


class GoogleEarthEngineDownloadError(Exception):
    """Indicates an error occurred whilst downloading image from GEE"""
    def __init__(self, message):
        self.error_message = message

    def __str__(self):
        return f'gee>> download failed! message: {self.error_message}'


def area_of_interest(lat, lon, km):
    """
    Generate a buffer around a location (lat, long). Returns
    the geometry corresponding to its spatial envelope.
    """
    proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(lat, lon).buffer(km * 1000)
    aoi = transform(project, buf).exterior.envelope
    xmin, ymin, xmax, ymax = [round(coord, 3) for coord in aoi.bounds]
    return [xmin, ymin, xmax, ymax]


def fill(data):
    """
    Replace the value of invalid 'data' cells - NaNs
    by the value of the nearest valid data cell.
    """
    ind = nd.distance_transform_edt(np.isnan(data), return_distances=False, return_indices=True)
    return data[tuple(ind)]
