"""
Module contains the single class :class:`libpfapi.models.layer.Layer` aimed at
handling the Project's different Layers:

Layer should be worked locally by setting the different attributes using the
appropriate functions and finally pushing the changes to the server.  All
changes are performed to the local instance until otherwise specified

for example::

    from libpfapi.api import API
    a = API(mytoken)
    lay = a.get_layer(33)  # Get Layer 33 from server

    lay.set_buffer_rings([10])  # Sets a buffer of 10

At this point, the :class:`~libpfapi.models.layer.Layer` instance is only
modified locally, to send the changes to the server one must call the function
:func:`~libpfapi.models.layer.Layer.push_changes_to_server` which returns a
:class:`~libpfapi.task.Task` instance to keep track of the progress, retrieving
the Layer updates with
:func:`~libpfapi.models.layer.Layer.get_changes_from_server`

A full flow of a Layer modification would need pushing and acknowledging
changes to the api server::

    from libpfapi.api import API
    a = API(mytoken)
    lay = a.get_layer(33)  # Get Layer 33 from server

    lay.set_buffer_rings([10])  # Sets a buffer of 10
    task = lay.push_changes_to_server()
    task.wait_till_finished()  # Block thread until finished
    lay.get_changes_from_server()  #Upload the layer instance with the server data

    if lay.has_errors:  # Check if any errors occurred and act accordingly
        print(lay.error_msg)
        return
"""
from pathlib import Path

from libpfapi.exceptions import PFModelException
from libpfapi.utils import get_binary_url, get_json_url
from . import base
from .category import Category


class Layer(base.Model):
    """
        Pathfinder Project Layer

        :ivar id: Identifier for this Layer in the server
        :ivar original_data_vector_f: Url for GeoJson
            (use :func:`~libpfapi.models.layer.Layer.get_geojson_original` instead)
        :ivar processed_data_vector_f: Url for GeoJson
            (use :func:`~libpfapi.models.layer.Layer.get_geojson_processed` instead)
        :ivar buffer_settings: Raw buffer data from the server (modify via functions
                               :func:`~libpfapi.models.layer.Layer.set_buffer_rings`)
        :ivar has_errors: Boolean representing possible errors with this Layer
                          ocurred during preprocessing
        :ivar error_msg: if has_errors is true, string with the error description
        :ivar baselayer_filter: Raw filter for vector Layer (modify via functions)
        :ivar ltype: Raw layer type from server (use properties instead
                     :func:`~libpfapi.models.layer.Layer.is_vector`,
                     :func:`~libpfapi.models.layer.Layer.is_raster`)

    """
    def __init__(self, api=None):
        self.baselayer_filter = None
        self.full_preprocess = None
        self.buffer_settings = None
        self.name = None
        self.ltype = 'VEC'
        self.pdefaults = {
            'id': None,
            'original_data_vector_f': None,
            'name': None,
            'buffer_settings': None,
            'is_processed': False,
            'has_errors': False,
            'error_msg': "",
            'workspace_name': None,
            'baselayer_filter': None,
            'ltype': 'VEC',
            'packed_data_f': None,
        }

        self.__pload_items = []
        super(Layer, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            if k == 'category':
                # TODO review this! It seems we get category with an
                #  id sometimes and sometimes as an int. We should
                #  agree on how
                if isinstance(v, dict):
                    v = Category.new_from_dict(v, api=self._api)
                else:
                    v = Category.new_from_dict({"id": v}, api=self._api)
            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new Layer instance from a JSON dictionary. To be used
            with raw returns from the server
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)

        return result

    @classmethod
    def new_from_base_layer(cls, baselayer, category, buffer_rings=[], name=None, api=None):
        """
            Create a new Layer in the server from an existing BaseLayer
            to an existing category

            :param baselayer: BaseLayer to create the Layer from
            :param category: Category to assign the Layer to
            :param buffer_rings: Set of integers to generate buffers during preprocessing
            :param name: New name for this Layer
            :param api: Api to assign and perform appropriate REST calls

            :return: Layer and Task instances. Once Task finishes Layer instance
                     should be `refreshed` to obtain the latest data from the server.
            :rtype: (:class:`~libpfapi.models.layer.Layer`, :class:`~libpfapi.task.Task`)
        """
        result = cls(api)

        # Proper reference to original baselayer
        result.baselayer_id = baselayer.id
        result.baselayer_class = baselayer.baselayer_class

        # New Layer name
        result.name = name

        # Reference to category where this layer will reside
        result.category = category.id

        # Buffer settings for this bl
        result.buffer_settings = {
                "ring_widths": buffer_rings,
                "resistance_factors": [100]*len(buffer_rings)
        }

        pload_items = ["baselayer_id", "baselayer_class", "category", "buffer_settings", "name"]
        payload = {k: getattr(result, k) for k in pload_items}

        layer, task = api.post_layer(**payload)
        result.id = layer.id  # We assign the new Layer Id
        return layer, task

    def delete(self):
        """
            Delete this Layer from the server

            .. warning::
                This action is not reversible. Once deleted there is
                no way to recover

            :raises PFAPIException: If the server responds with an error
        """
        self._api.delete_layer(self.id)

    @property
    def is_raster(self):
        """
            :return: True If layer represents a Raster layer
        """
        return self.ltype == 'RST'

    @property
    def is_vector(self):
        """
            :return: True If layer represents a Vector layer
        """
        return self.ltype == 'VEC'

    @property
    def is_multiring(self):
        """
            :return: True if Layer is Vector with multiple rings
        """
        return self.ltype == 'VEC' and len(self.buffer_settings.get('ring_widths', [])) > 1

    @property
    def is_filtered(self):
        """
            :return: True if the current Layer has filtered data from its Base Dataset
        """
        return self.baselayer_filter is not None

    @property
    def number_of_rings(self):
        """
            :return: Total number of rings for the Layer
        """
        return len(self.buffer_settings["ring_widths"])

    def __get_geojson_data(self, attribute, path=None):
        """
            Retrieve data from an attribute containing a URL.

            :param attribute: Layer attribute to use as URL
            :param path: Optional file path where to store the file
            :return: Parsed GeoJSON file or string to path
            :raises PFModelException: If layer has no valid geojson data

            .. note:
                This function retrieves the Layer information to get
                a temporal URL to access the GeoJSON. And reads it
                in Memory unless a path is specified
        """
        nlay = self._api.get_layer(self.id)
        url = getattr(nlay, attribute, None)

        if url is None:
            raise PFModelException("No Geojson Data found for attribute %s".format(attribute))

        if path:
            raw = get_json_url(url, raw=True)
            with open(path, "wb") as f:
                f.write(raw)
            return path

        return get_json_url(url)

    def __get_packed_data(self, attribute, path=None):
        """
            Retrieve packed original data file for this Layer.

            .. note:
                Returns original data file zipped.

            :param path: It returns the packed data file and
                         stores the file into the given path
            :return: data file zipped (and the path if given)
            :raises PFModelException: If layer has no valid data
        """
        nlay = self._api.get_layer(self.id)
        url = getattr(nlay, attribute, None)

        if url is None:
            raise PFModelException("No packed data found for attribute %s".format(attribute))

        if path:
            path = Path(path)
            if path.suffix:
                path = path.with_suffix(".zip")
            else:
                path = path / (self.name + ".zip")

            try:
                with path.open("wb") as f:
                    zip_file = get_binary_url(url)
                    f.write(zip_file)
            except FileNotFoundError:
                raise PFModelException("The provided file path has not found")

            return zip_file, str(path)

        return get_binary_url(url)

    def get_geojson_processed(self, path=None):
        """
            Retrieve GeoJson processed data for this Layer.

            .. note:
                Returns GeoJSON geometry, not a Valid GeoJSON file.
                this geometry should be treated as such and added
                to a given GeoJSON file if necessary


            :param path: Instead of returning a GeoJSON dictionary
                         store file to path

            :return: Parsed GeoJSON file or string to path
            :raises PFModelException: If layer has no valid geojson data
        """
        if self.is_raster:
            raise PFModelException("Raster Layers do not hold GeoJson data")

        return self.__get_geojson_data("processed_data_vector_f", path)

    def get_geojson_original(self, path=None):
        """
            Retrieve GeoJson original data for this Layer.

            .. note:
                Returns GeoJSON geometry, not a Valid GeoJSON file.
                this geometry should be treated as such and added
                to a given GeoJSON file if necessary

            :param path: Instead of returning a GeoJSON dictionary
                         store file to path
            :return: Parsed GeoJSON file or string to path
            :raises PFModelException: If layer has no valid geojson data
        """
        if self.is_raster:
            raise PFModelException("Raster Layers do not have GeoJsons")

        return self.__get_geojson_data("original_data_vector_f", path)

    def get_packed_data_file(self, path=None):
        """
            Retrieve packed original data file for this Layer.

            .. note:
                Returns packed data file zipped.

            :param path: Instead of returning the packed data file,
                         stores file to the given path
            :return: original data file zipped.
            :raises PFModelException: If layer has no valid data
        """
        return self.__get_packed_data("packed_data_f", path)

    def set_buffer_rings(self, rings):
        """
            Set new buffer rings for this layer.

            :param rings: A list of integers representing Layer's increasing ring width in meters

            .. note::
                default factors are added too although not needed
        """
        self.buffer_settings = {
                "ring_widths": rings,
                "resistance_factors": [100]*len(rings)
        }
        self.__pload_items.extend(["buffer_settings"])

    def force_process_layer(self):
        """
            Force a Task when updating the server via
            :func:`~libpfapi.models.layer.Layer.push_changes_to_server`.

            .. note:
                Some changes to a Layer do not need force a re-processing
                of the layer. If this function is called, a preprocessing
                task will be always generated.

            :return: None
        """
        self.full_preprocess = True
        self.__pload_items.append("full_preprocess")

    def set_name(self, name):
        """
            Set a new name for this Layer.
        """
        self.name = name
        self.__pload_items.append("name")

    def set_baselayer_filter(self, filter_strict):
        """
            Set a Filter to this Layer. (Filters not provided by this API version)

            See `Pathfinder documentation
            <https://docs.gilytics.com/en/whatsNew.html?highlight=filter#filter-data-by-attribute>`_
            for more information

            .. note:
                Not Implemented
        """
        raise NotImplementedError

    def get_data_ranges(self):
        """
            Return the minimum and maximum value for this Layer Raster.

            .. note::
                This can be used for both rasters and vectors, although in
                general it only makes sense for rasters.
        """
        return self._api.get_layer_ranges(self.id)

    def get_config(self, scenario_id):
        """
            Retrieve a proper
            :class:`~libpfapi.models.layerconfig.LayerConfiguration` object for
            this layer on a given :class:`~libpfapi.models.scenario.Scenario`.

            :param scenario_id: Id of the Scenario to retrieve the config from.
            :return: LayerConfiguration for this Layer on the provided scenario
            :rtype: :class:`~libpfapi.models.layerconfig.LayerConfig`
        """
        return self._api.get_scenario_layer_config(scenario_id, self.id)

    def get_changes_from_server(self):
        """
            Update this Layer instance with the latest information from
            the server.
        """
        # TODO we accept this roundtrip since we want to update this
        #  instance, but at the same time we like how api returns
        #  modelinstances too. The overhead is not that terrible
        nlay = self._api.get_layer(self.id)
        self._raw = nlay._raw
        self._parse_from_dict(nlay._raw)

    def push_changes_to_server(self):
        """
            Update this Layer in the server with performed modifications.

            :return: a Task instance. Since patching a Layer might
                     trigger a preprocessing that needs to finis
                     before retrieving the new data.
                     Task might be None if no task was started in
                     the server.
            :rtype: :class:`~libpfapi.task.Task`
        """
        payload = {k: getattr(self, k) for k in set(self.__pload_items)}
        _, task = self._api.patch_layer(self.id, **payload)
        self.__pload_items = []
        return task

    def __repr__(self):
        return "Layer ({}): {}. {}. MRING:{}".format(
            self.id, self.name, self.ltype, self.is_multiring)
