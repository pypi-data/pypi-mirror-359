from libpfapi.exceptions import PFModelException
from libpfapi.utils import get_binary_url


class Model(object):
    """
        A Base model object for all subclasses. Should not
        be used directly
    """

    def __init__(self, api=None):
        self.caches = None
        if not getattr(self, "pdefaults", None):
            self.pdefaults = {}

        for (param, default) in self.pdefaults.items():
            setattr(self, param, default)

        self._api = api
        self.invalidate_cache()

    @classmethod
    def new_from_dict(cls, data, api=None, **kwargs):
        """
            Create a new instance based on a JSON dict. Any kwargs should be
            supplied by the inherited, calling class.

            :param data: A dict with information
            :param api:
        """
        raise NotImplementedError

    def invalidate_cache(self):
        self.caches = {}

    def push_changes_to_server(self):
        raise NotImplementedError

    def get_changes_from_server(self):
        raise NotImplementedError


class RasterResultMixin(object):
    """
        Mixin for raster retrieval. ResistanceMap, Corridor..
    """
    API_F_NAME = 'get_resistance_map'

    def __get_binary_data(self, attribute, path=None):
        """
            Retrieve data from an attribute containing an URL.

            :param attribute: Resistance Map attribute to use as URL
            :param path: Optional file path where to store the file
            :return: Binary information or string to file path
            :raises PFModelException: If layer has no valid data

            .. note:
                This function retrieves the latest ResistanceMap information
                from the server to refresh temporal URLs to files. Will
                read this information as a binary dump
        """
        func = getattr(self._api, self.API_F_NAME)
        obj = func(self.id)
        url = getattr(obj, attribute, None)

        if url is None:
            raise PFModelException("No Geojson Data found for attribute %s".format(attribute))

        raw = get_binary_url(url)

        if path:
            with open(path, "wb") as f:
                f.write(raw)
            return path
        else:
            return raw

    def get_png_image(self, path=None):
        """
            Returns the binary PNG data representing this Raster result

            :param path: instead of returning raw PNG binary data, store
                         that result to a file

            :return: raw PNG binary data or string to path
            :raises PFModelException: If layer has no valid geojson data
        """
        return self.__get_binary_data("png_data", path)

    def get_tif_data(self, path=None):
        """
            Returns the binary tif data representing this Raster result

            :param path: instead of returning raw TIF binary data, store
                         that result to a file

            :return: raw TIF binary data or string to path
            :raises PFModelException: If layer has no valid geojson data
        """
        return self.__get_binary_data("tif_f", path)
