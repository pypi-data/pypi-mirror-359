"""
    ResistanceMap module provides the ResistanceMap class to access results
    from the server.

    To generate new resistance-maps you should use the
    :class:`~libpfapi.models.scenario.Scenario` instead
"""

from . import base


class ResistanceMap(base.Model, base.RasterResultMixin):
    """
        Resistance Map result

        :ivar id: Id of the ResistanceMap in the server
        :ivar is_processed: Does this ResistanceMap model holds data
        :ivar png_bounds: Bounds in WGS84 of the provided PNG
    """
    # Function name for RasterResultMixin
    API_F_NAME = 'get_resistance_map'

    def __init__(self, api):
        self.pdefaults = {
                "id": None,
                # "scenario": None,
                "is_processed": None,
                "png_data": None,
                "tif_f": None,
                "png_bounds": None,
                "tms_tiles": None,
                }

        super(ResistanceMap, self).__init__(api)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new ResistanceMap from a JSON dictionary,
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
