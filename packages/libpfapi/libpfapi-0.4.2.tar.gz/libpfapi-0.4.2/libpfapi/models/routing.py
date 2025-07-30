"""
    Routing Model Parameters used for routing models.

    Routing Models are, by definition, Read-Only. They are used only to
    describe the model.
    The Routing Model Parameters, describe the model too, but we use their in-memory
    representation to store values that we'll use to send to the server.
"""
from . import base
from libpfapi.exceptions import PFModelException


class ModelParameter(base.Model):
    """
        Routing Model Parameters
    """
    def __init__(self, api=None):
        self._raw = None
        self._value = None
        self.pdefaults = {
            "name": "",
            "label": "",
            "category": "",
            "description": "",
            "TYPE_STR": "",
            "required": False,
            "default": None,
            "id_type": "",
            "ui_format_hint": "",
            "unit": "",
        }

        self.__pload_items = []
        super(ModelParameter, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Create a new instance based on a JSON dict. Any kwargs should be
            supplied by the inherited, calling class.
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)
        return result

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
        return str

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
    def value(self):
        return getattr(self, '_value', None)

    def set_value(self, value):
        """
            Set a value for this parameter which can be used to send to the server
            later on.

            :param value: An appropriate value according to type
            :ptype: the return :py:attr:`~libpfapi.models.routing.ModelParameter.type`
        """
        caster = self.python_type
        try:
            self._value = caster(value)
        except Exception as e:
            print(e)
            raise PFModelException("Invalid value {} for type {}".format(value, self.type))

    def __repr__(self):
        return "RoutingModelParam ({}:{})".format(self.name, self.type)


class RoutingModel(base.Model):
    """
        Pathfinder Routing Model
    """
    def __init__(self, api=None):

        self.parameters = None
        self.pdefaults = {
            "class_name": "",
            "label": "",
            "html_doc": "",
            "parameters": [],
        }

        self.__pload_items = []
        super(RoutingModel, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Create a new instance based on a JSON dict. Any kwargs should be
            supplied by the inherited, calling class.
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)
        return result

    def load_parameter_values_from_sconfig(self, sconfig):
        """
            Loads all parameter values from the ScenarioConfig for this RoutingModel

            :sconfig: ScenarioConfig instance
        """
        if not self.parameters:
            self.parameters = self._api.get_routing_model_parameters(self.class_name)

        if self.class_name in sconfig.routing_params:
            sc_params = sconfig.routing_params[self.class_name]
            for param in self.parameters:
                if param.name in sc_params:
                    param.set_value(sc_params[param.name])
        else:
            error_msg = "The given ScenarioConfig does not have values for this RoutingModel"
            raise PFModelException(error_msg)

    def get_parameter(self, param_name):
        """
            Return a parameter matching the param_name received.
            Raises an exception if it does not exist.
        """
        for param in self.parameters:
            if param_name == param.name:
                return param

        raise PFModelException(f"Parameter {param_name} does not exist")
