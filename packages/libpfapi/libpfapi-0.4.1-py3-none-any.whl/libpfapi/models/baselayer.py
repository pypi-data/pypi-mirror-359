import os
import time
from enum import Enum

from . import base


class LayerType(Enum):
    BASE_LAYER = "BaseLayer"
    BASE_LAYER_V2 = "BaseLayerV2"
    BASE_LAYER_RAW_FILE = "BaseLayerRawFile"


class BaseLayer(base.Model):
    """
        Pathfinder BaseLayer.

        A BaseLayer in pathfinder is treated as the Basic source of
        information.

        Different BaseLayers can be created and are accessible only to memebers
        of the company. Projects are created from those sources of information.

        Any :class:`libpfapi.models.layer` in a given
        :class:`libpfapi.models.project` should have an associated BaseLayer.

        :ivar id: Identifier for this BaseLayer in the server
        :ivar baselayer_class: Plain raw class name coming from the server
        :ivar feature_count: For vector layers (not WFSs) how many features are in the BaseLayer
        :ivar ltype: Raw layer time (use the properties functions instead)
        :ivar ~.name: Name of this BaseLayer
    """
    def __init__(self, api=None):
        self.pdefaults = {
            'id': None,
            'baselayer_class': None,
            'feature_count': None,
            'ltype': None,
            'name': None,
            'description': None,
            'owner_name': None,
        }
        self.__pload_items = []
        super(BaseLayer, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            setattr(self, k, v)

    def set_name(self, name):
        """
            Set a new name for this BaseLayer.
        """
        self.name = name
        self.__pload_items.append("name")

    def set_description(self, desc):
        """
            Set a new description for this BaseLayer.
        """
        self.description = desc
        self.__pload_items.append("description")

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new BaseLayer instance from a JSON dictionary.

            Mostly to be created from API calls.
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)
        return result

    @classmethod
    def new_from_file(cls, local_filepath, api=None, name=None, description=None):
        """
            Create a new BaseLayer from a file in your system.

            :param local_filepath: Path in the FileSystem to a Vector or Raster
                dataset file.
            :type local_filepath: String
            :param api: Api to perform the proper calls to create the BaseLayer.
            :type api: :class:`~libpfapi.api.API`
            :param name: Optional Name for the new BaseLayer, if not provided
                it will generate a default one
            :type name: string
            :param description: Optional description for this imported BaseLayer
                                if not provided it will be left with a default
                                description
            :type description: string
            :return: Tuple with BaseLayer and Task
            :rtype: (:class:`~libpfapi.models.BaseLayer`, :class:`~libpfapi.task.Task`)
        """
        fname, ext = os.path.splitext(os.path.basename(local_filepath))
        fname_in_server = "{}/{}{}".format(str(int(time.time())), fname, ext)

        # Get an URL to upload to
        upload_struct = api.generate_upload_url(fname_in_server)

        # Upload the file to the given URL
        api.upload_file_from_generated_url(upload_struct, local_filepath)

        if not name:
            name = fname_in_server
        if not description:
            description = "file {}, with size {}".format(
                fname_in_server,
                os.path.getsize(local_filepath))

        # All new files are baselayer v2
        return api.post_baselayerfile_v2(name=name, description=description, file=fname_in_server)

    def update_with_file(local_filepath, api=None):
        """
            Given this existing BaseLayer, push a new File as the source for the data.

            This will simply upload a new file and point the BaseLayer to this
            new file while simultaneously triggering a task
        """

        fname, ext = os.path.splitext(os.path.basename(local_filepath))
        fname_in_server = "{}/{}{}".format(str(int(time.time())), fname, ext)

        # Get an URL to upload to
        upload_struct = api.generate_upload_url(fname_in_server)

        # Upload the file to the given URL
        api.upload_file_from_generated_url(upload_struct, local_filepath)

        if not name:
            name = fname_in_server


        if self.baselayer_class is None or self.baselayer_class == LayerType.BASE_LAYER.value:
            self._api.post_baselayerfile(self.id)
        elif self.baselayer_class == LayerType.BASE_LAYER_V2.value:
            self._api.post_baselayerfile_v2(self.id)
        else:
            raise NotImplementedError("unimplemented for {}".format(self.baselayer_class))

    def delete(self):
        """
            Delete this BaseLayer from the server. This action does not
            delete :class:`~libpfapi.models.layer.Layer` instances in the
            server. Those instances will be orphans and actions requiring
            the BaseLayer will fail (for example filters and attribute
            queries)

            .. warning::
                This action is not reversible. Once deleted there is
                no way to recover

            :raises PFAPIException: If the server responds with an error
        """
        if self.baselayer_class is None or self.baselayer_class == LayerType.BASE_LAYER.value:
            self._api.delete_baselayer_file(self.id)
        elif self.baselayer_class == LayerType.BASE_LAYER_V2.value:
            self._api.delete_baselayer_file_v2(self.id)
        else:
            raise NotImplementedError("unimplemented for {}".format(self.baselayer_class))

    @property
    def is_vector(self):
        """
            :return: True If layer represents a Vector layer
        """
        return self.ltype == 'VEC'

    @property
    def is_raster(self):
        """
            :return: True If layer represents a Vector layer
        """
        return self.ltype == 'RST'

    @property
    def type(self):
        """
            Returns the type of the baselayer from the following list:
            [file-raster, file-vector, wfs]
        """
        if self.baselayer_class == 'BaseLayer':
            if self.ltype == 'RST':
                return 'file-raster'
            else:
                return 'file-vector'

        if self.baselayer_class == 'BaseLayerWFS':
            return 'wfs'

    @property
    def attributes(self):
        """
            returns list of attributes for this baselayer
        """
        raise NotImplementedError()

    @property
    def attribute_values(self):
        """
            returns a list of valid attribute values for this baselayer
        """
        raise NotImplementedError()

    def get_features_at_point(self, point):
        """
            Function to retrieve matching features at a given point
        """
        raise NotImplementedError()

    def get_changes_from_server(self):
        """
            Update this BasLayer instance with the latest information
            from the server.
        """
        # TODO. This looks terrible, but we switch by the different
        # kinds of BaseLayer classes, and the default matcher
        # when it's undefined will be FILE (to work nicely
        # with users uploading files)
        if self.baselayer_class is None or self.baselayer_class == LayerType.BASE_LAYER.value:
            nbl = self._api.get_baselayer_file(self.id)
        elif self.baselayer_class == LayerType.BASE_LAYER_V2.value:
            nbl = self._api.get_baselayer_file_v2(self.id)
        else:
            raise NotImplementedError("unimplemented for {}".format(self.baselayer_class))

        self._raw = nbl._raw
        self._parse_from_dict(nbl._raw)

    def push_changes_to_server(self):
        """
            Update this BaseLayer in the server with performed modifications.

            :return: a Task instance. Since patching a Layer might
                     trigger a preprocessing that needs to finis
                     before retrieving the new data.
                     Task might be None if no task was started in
                     the server.
            :rtype: :class:`~libpfapi.task.Task`
        """
        payload = {k: getattr(self, k) for k in set(self.__pload_items)}
        if self.baselayer_class is None or self.baselayer_class == LayerType.BASE_LAYER.value:
            self._api.patch_baselayer_file(self.id, **payload)
        elif self.baselayer_class == LayerType.BASE_LAYER_V2.value:
            nbl = self._api.patch_baselayer_file_v2(self.id)
        else:
            raise NotImplementedError("unimplemented for {}".format(self.baselayer_class))
        self.__pload_items = []

    def __repr__(self):
        return "BLayer ({}): {}. {}.".format(self.id, self.name, self.ltype)
