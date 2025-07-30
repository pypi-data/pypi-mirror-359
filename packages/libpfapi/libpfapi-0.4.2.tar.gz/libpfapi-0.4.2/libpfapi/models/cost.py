"""
    Module containing utility functions to handle different cost models

    Cost models are not treated directly but assigned to each possible
    :class:`~libpfapi.models.scenario.Scenario` and affect the results
    of :class:`~libpfapi.models.scenariopath.ScenarioPath`.

    The classes in this module aid in the listing and preparing of
    the different cost-model parameters
"""
from . import base
from libpfapi.exceptions import PFModelException


class CModelParameter(base.Model):
    """
        A single definition of a cost model parameter
    """

    @classmethod
    def param_type_to_python_type(cls, ptype):
        if ptype == 'INT':
            return int
        if ptype == 'FLOAT':
            return float
        if ptype == 'ARRAY':
            return list
        if ptype == 'BOOL':
            return bool

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Create a new instance based on a JSON dict. Any kwargs should be
            supplied by the inherited, calling class.
        """
        result = cls(api)
        result._raw = ddict
        return result

    @property
    def type(self):
        """
            Return the string type of this parameter
        """
        return self._raw.get('TYPE_STR', None)

    @property
    def python_type(self):
        """
            Return the python type class for this parameter
        """
        return self.param_type_to_python_type(self.type)

    @property
    def required(self):
        """
            Return true or false to know if this
            parameter is required
        """
        return self._raw.get('required', False)

    @property
    def child(self):
        """
            Specific case for ListParameters that might
            need a specification of a child

            :return: ChildParameter instance or None
            :rtype: :class:`~libpfapi.models.cost.CModelParameter`
        """
        child = self._raw.get('child_param', None)

        if child:
            return CModelParameter.new_from_dict(child)

        return None

    @property
    def name(self):
        """
            Name of this parameter, used to reference
            the value in the server.
        """
        return self._raw.get('name', False)

    @property
    def description(self):
        """
            Human-readable description for the cost parameter
        """
        return self._raw.get('description', False)

    @property
    def value(self):
        return getattr(self, '_value', None)

    def set_value(self, value):
        """
            Set a value for this parameter which can be used to send to the server
            later on.

            :param value: An appropriate value according to type
            :ptype: the return :py:attr:`~libpfapi.models.cost.CModelParameter.type`
        """
        caster = self.python_type
        try:
            self._value = caster(value)
        except Exception as e:
            print(e)
            # raise PFModelException(f"Invalid value {value} for type {self.type}")

    def __repr__(self):
        return "CMParam ({}:{})".format(self.name, self.type)


class CostModel(base.Model):
    """
        Pathfinder Cost Model

        A cost model contains information on which parameters
        are required to configure an scenario to run a specific
        cost model on each path generation.

        Each cost model is defined by two set of parameters, global
        and Layer. Global parameters are set once for each scenario
        while Layer parameters are explicitly set for each LayerConfig.
    """

    # We keep an in memory copy of the model definitions to avoid
    # continuous calls to the server for the same model descriptions
    MODEL_CACHES = {}

    def __init__(self, class_name, api=None):
        """
            Initialize a new cost_model with a given class name.

            Valid cost models for a user are described in
            :func:`~libpfapi.api.API.get_capabilities`
        """
        self.cname = class_name
        super(CostModel, self).__init__(api)

    def _get_cache_global_params(self):
        """
            Loads parameters in cache if not already loaded and return
            the list of raw global parameters
        """
        if getattr(self, "g_params", None):
            return self.g_params

        if self.cname not in self.MODEL_CACHES:
            self.MODEL_CACHES[self.cname] = self._api.get_cost_model_parameters(self.cname)

        params = self.MODEL_CACHES[self.cname].get("global_p", [])
        self.g_params = [CModelParameter.new_from_dict(pdict, api=self._api) for pdict in params]

        return self.g_params

    def _get_cache_local_params(self):
        """
            Loads parameters in cache if not already loaded and return
            the list of raw local parameters
        """
        if getattr(self, "l_params", None):
            return self.l_params

        if self.cname not in self.MODEL_CACHES:
            self.MODEL_CACHES[self.cname] = self._api.get_cost_model_parameters(self.cname)

        params = self.MODEL_CACHES[self.cname].get("layer_p", [])
        self.l_params = [CModelParameter.new_from_dict(pdict, api=self._api) for pdict in params]

        return self.l_params

    @classmethod
    def clear_parameter_cache(cls):
        """
            Clear Parameter Cache.

            To avoid lots of hits to the server the CostModels are cached in
            Memory. If a refresh is needed simply clear the cache calling this
            function
        """
        cls.MODEL_CACHES = {}

    def get_global_parameters(self):
        """
            Return a list of global parameters for this Cost Model.

            :return: List of global parameters
            :rtype: list of `~libpfapi.models.costs.CModelParameter`
        """
        return self._get_cache_global_params()

    def get_global_parameter(self, name):
        """
            Get a global parameter by name.

            :return: Parameter with the given name. None if it does no exist
            :rtype: `~libpfapi.models.costs.CModelParameter`
        """
        params = self._get_cache_global_params()
        return next((p for p in params if p.name == name), None)

    def get_layer_parameters(self):
        """
            Return a list of layer parameters for this Cost Model.

            :return: List of Layer parameters
            :rtype: list of `~libpfapi.models.costs.CModelParameter`
        """
        return self._get_cache_local_params()

    def get_layer_parameter(self, name):
        """
            Get a layer parameter by name.

            :return: Parameter with the given name. None if it does no exist
            :rtype: `~libpfapi.models.costs.CModelParameter`
        """
        params = self._get_cache_local_params()
        return next((p for p in params if p.name == name), None)

    def configure_scenario(self, scenario):
        """
            Configure a given scenario with this cost model parameters
        """
        gparam_values_dict = {p.name: p.value for p in self.g_params if p.value is not None}
        scenario.enable_cost_model_by_name(self.cname, **gparam_values_dict)

    def configure_layerconfig(self, lconf):
        """
            Configure a given layer config with this cost nodel layer parameters
        """
        lparam_values_dict = {p.name: p.value for p in self.l_params if p.value is not None}
        lconf.set_cost_model_by_name(self.cname, **lparam_values_dict)

    def read_globals_from_scenario(self, scenario):
        """
            Load this cost model with values from a Scenario

            :param scenario: Scenario with already loaded data
            :ptype: :class:`~libpfapi.models.scenario.Scenario`
        """
        raise NotImplementedError

    def read_lparams_from_layerconfig(self, lconf):
        """
            Load this cost model with the values from a LayerConfig

            :param lconf: LayerConfig with already loaded data
            :ptype: :class:`~libpfapi.models.layerconfig.LayerConfig`
        """
        raise NotImplementedError

    @property
    def name(self):
        return self.cname
