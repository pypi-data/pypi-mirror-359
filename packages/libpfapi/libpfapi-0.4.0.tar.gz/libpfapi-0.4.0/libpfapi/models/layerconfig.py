from . import base
from .cost import CostModel
from libpfapi.exceptions import PFModelException


class LayerConfig(base.Model):
    """
        Pathfinder Scenario LayerConfig.

        Contains utilities to actually setup a LayerConfiguration
        for a given scenario in different modes.

        :ivar id: Unique identifier for this Layer Config
        :ivar layer_id: raw ID of the referenced layer (use
            :py:attr:`~libpfapi.models.layerconfig.LayerConfig.layer` instead)
        :ivar scenario_id: raw ID of the referenced Scenario (use
            :py:attr:`~libpfapi.models.layerconfig.LayerConfig.scenario` instead)
        :ivar resistance_value: raw resistance value (use
            :func:`~libpfapi.models.layerconfig.LayerConfig.set_mode_vector_av` to
            modify safely)
        :ivar layer_color: Unused
        :ivar rmode: Mode flag for this Layer (will be set automatically when
            using the `set_mode*` functions).
        :ivar rfactors: Raw resistance factors (DEPRECATED)
        :ivar rvalues: Raw resistance values for PR mode, (use
            :func:`~libpfapi.models.layerconfig.LayerConfig.set_mode_vector_pr`
            to set properly, and
            :py:attr:`~libpfapi.models.layerconfig.LayerConfig.pr_resistances`
            attribute to get the currently set values)
        :ivar rst_av: Raw configuration for raster AV mode. (use
            :func:`~libpfapi.models.layerconfig.LayerConfig.set_mode_raster_av`
            to modify and
            :func:`~libpfapi.models.layerconfig.LayerConfig.get_raster_av_mode_conf`
            to retrieve current values)
        :ivar rst_rng: Raw raster ranges configuration.
        :ivar rst_linear: Raw raster linear configuration.
        :ivar cost_data: Raw cost parameters configuration
        :ivar forbidden: Forbidden value (DEPRECATED, use
            :func:`~libpfapi.models.layerconfig.LayerConfig.set_mode_forbidden`)
        :ivar not_considered: Not Considered value (DEPRECATED, use
            :func:`~libpfapi.models.layerconfig.LayerConfig.set_mode_not_considered`)
    """
    def __init__(self, api=None):
        self.pdefaults = {
            'id': None,
            'layer_id': None,
            'scenario_id': None,
            'weight': None,
            'resistance_value': None,
            'layer_color': False,
            'rmode': None,
            'rfactors': None,
            'rvalues': None,
            'rst_av': None,
            'rst_rng': None,
            'rst_linear': None,
            'cost_data': {},
            'forbidden': False,
            'not_considered': False,
        }

        # Internal handling of what to POST on update
        self.__pload_items = []
        super(LayerConfig, self).__init__(api)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new LayerConfig instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict

        for k, v in ddict.items():
            if k == "scenario":
                # do not build a scenario, simply keep ID and
                # we can generate it if ever called
                setattr(result, "scenario_id", v)
                continue
            if k == "layer":
                # do not build a Layer, simply keep ID and
                # we can generate it if ever called
                setattr(result, "layer_id", v)
                continue

            setattr(result, k, v)

        return result

    @property
    def pr_resistances(self):
        """
            Return a pair of lists with the current setup of PR resistances.
            Might return None if never set

            :return: Resistances and Forbidden lists
            :rtype: (list, list)
        """
        rvals = getattr(self, "rvalues", {})
        forbiddens = rvals.get("forbidden", None)
        resistances = rvals.get("resistances", None)

        return resistances, forbiddens

    @property
    def layer(self):
        """
            Return the Layer that this instance is configuring

            :return: Layer pointed by this LayerConfig
            :rtype: :class:`~libpfapi.models.layer.Layer`
            :raises PFModelException: If there's no related layer
            :raises PFAPIException: If the layer is not accessible (Server error)
        """
        if self.caches.get("layer", None) is None:
            if self.layer_id is None:
                raise PFModelException("Instance not initialized")

            nlay = self._api.get_layer(self.layer_id)
            self.caches["layer"] = nlay

        return self.caches.get("layer", None)

    @property
    def scenario(self):
        """
            Return the Scenario related to this instance

            :return: Parent Scenario holding this LayerConfig
            :rtype: :class:`~libpfapi.models.scenario.Scenario`
            :raises PFModelException: If there's no related layer
            :raises PFAPIException: If the scenario is not accessible (server error)
        """
        if self.caches.get("scenario", None) is None:
            if self.scenario_id is None:
                raise PFModelException("Instance not initialized")
            scen = self._api.get_scenario(self.scenario_id)
            self.caches["scenario"] = scen
        return self.caches.get("scenario", None)

    def set_mode_forbidden(self):
        """
            Set LayerConfig to Forbidden mode.
        """
        self.rmode = 'FB'
        self.__pload_items.extend(["rmode"])

    def set_mode_not_considered(self):
        """
            Set LayerConfig to Not Considered mode
        """
        self.rmode = 'NC'
        self.__pload_items.extend(["rmode"])

    def set_mode_vector_av(self, rval, factors=[]):
        """
            Set LayerConfig to AV mode with a single resistance

            :param rval: Integer for Resistance value
            :param factors: In case of multiring, decaying factors (1..100) of each ring
        """
        self.rmode = 'AV'
        self.resistance_value = rval
        self.forbidden = False
        self.not_considered = False
        if factors:
            self.rfactors = {
                "resistance_factors": factors,
                "ring_ids": list(range(1, len(factors)+1))
            }
            self.__pload_items.extend(["rfactors"])

        self.__pload_items.extend(["rmode", "resistance_value", "rfactors",
                                   "forbidden", "not_considered"])

    def set_mode_vector_pr(self, rvals, forbidden=[]):
        """
            Set LayerConfig to PR with a list of resistances.

            Consistency between this LayerConfig and its Layer is not checked,
            this is left to the hands of the library user

            :param rval: List of integers for resistance values
            :param forbidden: List of Booleans for each ring (if not provided, all False)
        """
        assert isinstance(rvals, list), "Expected list as rvals"

        self.rmode = 'PR'
        self.forbidden = False
        self.not_considered = False

        if not forbidden:
            forbidden = [False] * len(rvals)

        self.rvalues = {
            "forbidden": forbidden,
            "resistance_values": rvals,
            "ring_ids": list(range(1, len(rvals)+1))
        }

        self.__pload_items.extend(["rmode", "rvalues",
                                   "forbidden", "not_considered"])

    def set_mode_raster_av(self, value_map, default_resistance):
        """
            Set LayerConfig to AV mode for rasters. According to a list
            of value transformations.

            :param value_map: Setting from raster_value to resistance value. Allows
                              a boolean value of False instead of a number value to
                              signal a forbidden for that raster value.
            :ptype: List of Pairs[[10,20], [5, 55], [6, False]]

            :param default_resistance: Resistance for any non mapped value
            :ptype: Number
        """
        self.rmode = 'AV'
        resistance_pairs = [(rst, res) for (rst, res) in value_map if res is not False]
        forbidden_values = [rst for (rst, res) in value_map if res is False]
        self.rst_av = {
            "default": default_resistance,
            "values": resistance_pairs,
            "forbidden": forbidden_values
        }

        self.__pload_items.extend(["rmode", "rst_av"])

    def get_raster_av_mode_conf(self):
        """
            Return the currently set raster AV resistances in two values,
            default and list of pairs. The list of pairs is either `(Number,
            Number)` for value translations or `(Number, False)` to set that
            value to Forbidden.

            :return: default resistance and list of pairs.
            :rtype: (Number, List of pairs)
        """
        if self.rst_av is None:
            return 0, []

        rpairs = self.rst_av.get("values", [])
        rforbid = self.rst_av.get("forbidden", [])
        default = self.rst_av.get("default", 0)

        rpairs = [[r, R] for r, R in rpairs]  # just ensure those are modifiable lists
        rpairs.extend([[fr, False] for fr in rforbid])
        sorted_pairs = sorted(rpairs)

        return default, sorted_pairs

    def set_mode_raster_linear(self, min_r, max_r, ndata_r):
        """
            Set LayerConfig to LINEAR mode for rasters. According to a given
            maximum and minimum value.

            :param min_r: minimum target resistance
            :param max_r: maximum target resistance
            :param ndata_r: Resistance value for nodata cells
        """
        self.rmode = 'LINEAR'
        self.rst_linear = {
            "max_r": max_r,
            "min_r": min_r,
            "ndata_r": ndata_r
        }

        self.__pload_items.extend(["rmode", "rst_linear"])

    def get_raster_linear_conf(self):
        """
            Return current configuration for the raster LINEAR mode.
            If any value is not set will return None

            :return: Min resistance, Max resistance, nodata resistance
            :rtype: tuple of length 3
        """
        return (self.rst_linear.get("min_r", None),
                self.rst_linear.get("max_r", None),
                self.rst_linear.get("ndata_r", None),
                )

    def set_mode_raster_ranges(self, value_map, default):
        """
            Set this LayerConfig to Ranges mode with a valid
            list of ranges. Each item of the range is composed
            of two numerical values, and a third value, either
            a number of False (to signify Forbidden)

            :param value_map: List of ranges
            :ptype: List of triplets [[NUM, NUM, NUM|False],..]
            :param default: Default resistances for cell values
                            not inside any range
        """
        self.rmode = 'RANGE'

        resistance_ranges = [(minv, maxv, res) for
                             (minv, maxv, res) in value_map
                             if res is not False]
        forbidden_values = [(minv, maxv) for
                            (minv, maxv, res) in value_map
                            if res is False]

        self.rst_rng = {
            "default": default,
            "forbidden": forbidden_values,
            "ranges": resistance_ranges
        }

        self.__pload_items.extend(["rmode", "rst_rng"])

    def get_raster_ranges_conf(self):
        """
            Return current set of raster ranges configuration as a pair with
            the default value and the list of triplets.

            The third value of the triplet can be either a number of
            the False boolean (Representing forbidden).

            :return: default + List of triplets
            :rtype: (Number, list of triplets)
        """
        if self.rst_rng is None:
            return 0, []

        rtriplets = self.rst_rng.get("ranges", [])
        rforbid = self.rst_rng.get("forbidden", [])
        default = self.rst_rng.get("default", 0)

        rtriplets = [[rmin, rmax, R] for rmin, rmax, R in rtriplets]  # just ensure those are modifiable lists
        rtriplets.extend([[fmin, fmax, False] for fmin, fmax in rforbid])
        sorted_triplets = sorted(rtriplets)

        return default, sorted_triplets

    def set_cost_model_with_cmodel_instance(self, cmodel):
        """
            Configure this Layer cost model parameters
            using an instantiated :class:`~libpfapi.models.cost.CostModel`

            :param cmode: A fully loaded cost model instance
            :ptype: :class:`~libpfapi.models.cost.CostModel`
        """
        cmodel.configure_layerconfig(self)

    def set_cost_model_by_name(self, cost_model, **kwargs):
        """
            Enable a custom existing cost model by its name. Each custom
            model might need different custo keyword arguments, in case
            of doubt contact Gilytics.

            :param cost_model: Cost model name to enable
            :ptype: string
            :param kwargs: pairs of key value for the model parameters
        """
        cmodel_data = self.cost_data.get(cost_model, {})
        cmodel_data.update(kwargs)
        self.cost_data[cost_model] = cmodel_data
        self.__pload_items.append('cost_data')

    def get_cost_models(self):
        """
            Returns a list with all the LayerConfig cost models
            loded with this layer's parameters.

            :return: List of CModelParameter instances
            :rtype: :class:`~libpfapi.models.cost.CModelParameter`
        """
        cmodels = []
        for cname, params in self.cost_data.items():
            cmodel = CostModel(cname, api=self._api)
            for lp in cmodel.get_layer_parameters():
                lp.set_value(self.cost_data[cname].get(lp.name, None))
            cmodels.append(cmodel)

        return cmodels

    def push_changes_to_server(self):
        """
            Update this LayerConfig in the server with performed
            modifications
        """
        payload = {k: getattr(self, k) for k in set(self.__pload_items)}
        self._api.patch_scenario_layer_config(self.id, **payload)
        self.__pload_items = []

    def __repr__(self):
        return "Lconf ({}) (S{} L{})".format(self.id, self.scenario_id, self.layer_id)
