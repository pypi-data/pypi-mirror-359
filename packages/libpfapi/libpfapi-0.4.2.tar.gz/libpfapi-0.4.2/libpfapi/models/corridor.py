"""
    Corridor module provides the Corridor class to access results from the
    server.

    To generate new corridors you should use the
    :class:`~libpfapi.models.scenario.Scenario` instead
"""

from . import base


class Corridor(base.Model, base.RasterResultMixin):
    """
        Corridor result

        :ivar id: Id of the corridor in the server
        :ivar is_processed: Does this corridor model holds data
        :ivar png_bounds: Bounds in WGS84 of the provided PNG
        :ivar threshold: Which threshold was used to compute this corridor
    """
    # Function name for RasterResultMixin
    API_F_NAME = 'get_corridor'

    def __init__(self, api):
        self.pdefaults = {
            "id": None,
            "is_processed": None,
            "png_data": None,
            "tif_f": None,
            "png_bounds": None,
            "tms_tiles": None,
        }

        super(Corridor, self).__init__(api)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new project instance from a JSON dictionary,
            aimed at loading an instance from an API response.
        """
        result = cls(api)
        result._raw = ddict
        properties = ["scenario"]

        for k, v in ddict.items():
            if k in properties:
                continue
            setattr(result, k, v)

        return result
