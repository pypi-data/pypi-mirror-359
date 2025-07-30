"""
    Module containing the class for Scenario Handling.

    Scenario is the top-level handler for all configurations of a given Project.
    One Project can have multiple scenarios (limited by the user's account).

    In that sense, Pathfinder's model hierarchy works as follows::

        PROJECT
            CATEGORY1
                LAYER1
            CATEGORY2
                LAYER2
                LAYER3

    And Scenario provides a configuration for this sets of data::

        PROJECT        <--  SCENARIO (with ScenarioConfig)
            CATEGORY1  <--      CategoryConfig
                LAYER1 <--          LayerConfig
            CATEGORY2  <--      CategoryConfig
                LAYER2 <--          LayerConfig
                LAYER3 <--          LayerConfig

    This Scenario class encompasses both Pathfinder's Scenario and
    :class:`~libpfapi.models.scenarioconfig.ScenarioConfig` for ease of use.

    With a given configuration, a scenario can generate the different
    result models available:

        * :class:`libpfapi.models.rmap.ResistanceMap`
            Single result computed via
            :func:`libpfapi.models.scenario.Scenario.calculate_resistance_map`)
        * :class:`libpfapi.models.corridor.Corridor` (Single result)
            Single result computed via
            :func:`libpfapi.models.scenario.Scenario.calculate_corridor`)
        * :class:`libpfapi.models.scenariopath.ScenarioPath` (Multiple results)
            Multiple results computed via
            :func:`libpfapi.models.scenario.Scenario.calculate_paths`)

    Differing from :class:`~libpfapi.models.layer.Layer`, modifications of
    Scenario do not need to wait for any kind of task since it's only a set of
    configurations.  Tasks will be relevant when waiting for computing results.
    In that sense Scenario is a state in the server that will modify the
    computation outputs.

    for exmaple to change the routing algorithm and generate the new paths::

        from libpfapi.api import API

        a = API(mytoken)
        s = a.get_scenario(myscenarioid)

        s.set_routing_gilytics_fast()
        s.set_pylon_min_max_distances(40, 80)
        s.push_changes_to_server() # S already updated with latest changes in server

        s.calculate_paths()  # Paths will be calculated with the new configuration

    ---

"""

from . import base
from .scenarioconfig import ScenarioConfig
from .cost import CostModel
from libpfapi.exceptions import PFModelException

# Known Routing Models
ROUTING_FAST = 'GilyticsFastRouting'
ROUTING_ADVANCED = 'LionD8SinglePath'
ROUTING_ADVANCED_MULTI = 'LionD8MultiPath'
ROUTING_PYLON_SPOTTING = 'LionPylonSpottingOptimal'
ROUTING_PYLON_SPOTTING_MULTI = 'LionPylonSpottingMultiPath'
ROUTING_GENETIC = 'GeneticAlgorithm'


class Scenario(base.Model):
    """
        Pathfinder Scenario model

        An Scenario contains information on how to run a given
        :class:`~libpfapi.models.project`.  One
        :class:`~libpfapi.models.project` can be configured via different
        Scenarios
    """

    def __init__(self, api=None):

        self.internally_shared = False
        self.description = None
        self.name = None
        self.project_id = None
        self.intermediate_points = None
        self.config = None
        self.corridor_id = None
        self.pdefaults = {
            'id': None,
            'name': None,
            'description': None,
            'project_id': None,
            'project_name': None,
            'start_point': None,
            'end_point': None,
            'intermediate_points': None,
            'resistance_map_id': None,
            'corridor_id': None,
            'optimal_path': None,
            'config': None,
            'internally_shared': False,
            'owner_username': None,

            # TODO should probably deprecate those
            'heatmap_id': None,
            'resistance_alpha': 1.00,
            'corridor_alpha': 1.00,
            'heatmap_alpha': 1.00,
            'building_count': None,
        }

        self.__pload_items = []
        super(Scenario, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        properties = ["paths"]

        for k, v in ddict.items():
            if k in properties:
                # This is handled as a property and
                # has its own function.
                continue
            if k == 'config':
                v = ScenarioConfig.new_from_dict(v, api=self._api)
            if k == 'project':
                setattr(self, "project_id", v)
                continue

            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new project instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)
        return result

    @classmethod
    def new_scenario(cls, project, name='New', api=None, stype="CLASSIC"):
        """
            Create a new Scenario in the server

            :param project: Project to associate this scenario with
            :type project: :class:`~libpfapi.models.project.Project`:
            :param name: Name of the scenario
            :param api: Api connection
            :param stype: Classic, Multi, Multi-Child or Siting
        """
        return api.post_scenario(name, project.id, stype)

    def delete(self):
        """
            Delete this Scenario from the server

            .. warning::
                This action is not reversible. Once deleted there is
                no way to recover this scenario

            :raises PFAPIException: If the server responds with an error
        """
        self._api.delete_scenario(self.id)

    @property
    def resistance_map(self):
        """
            Returns an The instance of ResistanceMap calculated by this scenario

            :raises PFAPIException: If the server responds with an error
            :raises PFModelException: If there is no resistance map associated with this instance
        """
        if getattr(self, "resistance_map_id", None) is None:
            raise PFModelException('No resistance map available for scenario {}'.format(self.id))

        return self._api.get_resistance_map(self.resistance_map_id)

    @property
    def corridor(self):
        """
            Returns an The instance of Corridor calculated by this scenario

            :raises PFAPIException: If the server responds with an error
            :raises PFModelException: If there is no resistance map associated with this instance
        """
        if getattr(self, "corridor_id", None) is None:
            raise PFModelException('No corridor available for scenario {}'.format(self.id))

        return self._api.get_corridor(self.corridor_id)

    @property
    def paths(self):
        """
            Returns a list with all :class:`~libpfapi.models.scenariopath` related
            to this project and accessible by the user.

            :raises PFAPIException: If one of the paths could not be retrieved.
        """
        if "paths" not in self._raw:
            return []

        if "paths" in self.caches:
            return self.caches["paths"]

        self.caches["paths"] = []
        for path in self._raw.get("paths", []):
            pid = path.get("id", None)

            if not pid:
                continue

            spath = self._api.get_path(pid)
            self.caches["paths"].append(spath)

        return self.caches["paths"]

    @property
    def project(self):
        """
            Retrieve and return the project that this Scenario Configures

            :return: Project configured by this scenario
            :rtype: :class:`~libpfapi.models.project.Project`
            :raises PFAPIException: If any error was returned from the server
        """
        if self.caches.get("project", None) is not None:
            return self.caches.get("project")

        if getattr(self, "project_id", None) is None:
            raise PFModelException('Scenario instance not initialized with project_id')

        proj = self._api.get_project(self.project_id)
        self.caches["project"] = proj
        return proj

    def calculate_resistance_map(self):
        """
            Starts computing a new ResistanceMap for this scenario.

            :return: Task reference for the server computation
            :rtype: :class:`~libpfapi.task.Task`
            :raises PFAPIException: If any problem occurred in requesting the computation
        """
        rmap, tsk = self._api.post_scenario_calculate_rmap(self.id)
        self.resistance_map_id = rmap.id
        return tsk

    def set_name(self, name):
        """
            Set a new Name for this scenario
            :param name: new name
        """
        self.name = name
        self.__pload_items.append("name")

    def set_description(self, description):
        """
            Set a new Description for this scenario
            :param description: new description
        """
        self.description = description
        self.__pload_items.append("description")

    def set_internally_shared(self, value):
        """
            Set this scenario as internally_shared or private.  Internally
            shared scenarios can be loaded by anyone within the company with
            access to that project.

            :param value: True or False
            :ptype bool:
        """
        self.internally_shared = value
        self.__pload_items.append("internally_shared")

    def set_corridor_threshold_method(self, method):
        """
            Set the way in how the corridors should be computed, either by
            percentage or by percentile

            :param method: percentage or percentile
        """
        self.config.corridor_threshold_method = method
        self.__pload_items.append("config")

    def calculate_corridor(self, threshold=0.1):
        """
            Starts computing a new corridor for this scenario.

            :param threshold: Corridor threshold percentage (from 0 to 1)
            :return: Task reference for the server computation
            :rtype: :class:`~libpfapi.task.Task`
            :raises PFAPIException: If any problem ocurred in requesting the computation
        """
        cor, tsk = self._api.post_scenario_calculate_corridor(self.id, threshold)
        self.corridor_id = cor.id
        return tsk

    def calculate_paths(self):
        """
            Starts computing a routes for this scenario.

            It will compute everything according to the state of
            :class:`~libpfapi.models.scenarioconfig.ScenarioConfig`.

            Once finished, perform call
            :func:`~libpfapi.models.scenario.Scenario.get_changes_from_server`
            to retrieve the latest set of paths for this scenario. and
            :func:`~libpfapi.models.scenario.Scenario.paths`

            :return: Task reference for the server computation
            :rtype: :class:`~libpfapi.task.Task`
            :raises PFAPIException: If any problem ocurred in requesting the computation
        """
        scen, tsk = self._api.post_scenario_calculate_paths(self.id)
        return tsk

    def set_start_point(self, geojson_point=None):
        """
            Sets the start point for a scenario.
            If set to None (the default) computing will route using the
            defined Project start and end points


            :param geojson_point: String containing a single GeoJSON point
            :type geojson_point: string

            .. note::
                Example of valid input:
                {type: "Point", coordinates: [4.070011774461028, 50.61418252158475]}

            .. note::
                Point is expected in WGS84

            :return: None
        """
        self.start_point = geojson_point
        self.__pload_items.append('start_point')

    def set_end_point(self, geojson_point=None):
        """
            Sets the end point for a scenario.
            If set to None (the default) computing will route using the
            defined Project start and end points


            :param geojson_point: String containing a single GeoJSON point
            :type geojson_point: string

            .. note::
                Example of valid input:
                {type: "Point", coordinates: [4.070011774461028, 50.61418252158475]}

            .. note::
                Point is expected in WGS84

            :return: None
        """
        self.end_point = geojson_point
        self.__pload_items.append('end_point')

    def set_intermediate_points(self, geojson_points=None):
        """
            Sets the optional intermediate points for a scenario.
            If set to None (the default) computing will route using the
            defined Project start and end points


            :param geojson_points: String containing a GeoJSON Multipoint
            :type geojson_points: string

            .. note::
                Example of valid input:
                {type: "MultiPoint", coordinates: [[14.243965746976444, 45.69767384587274]]}

            .. note::
                Points are expected in WGS84

            :return: None
        """
        self.intermediate_points = geojson_points
        self.__pload_items.append('intermediate_points')

    def set_config_values(self, **kwargs):
        """
            Set config values directly by kwargs.

            Check :class:~libpfapi.models.scenarioconfig.ScenarioConfig` for
            valid known scenarioconfig values that will be sent to the server

            .. warning::
                You can potentially set incorrect values through this function
                so handle with care.

            Utility function open for changing values directly
            if there's no specific set function.::

                set_config_values(layer_min_resistance=3, layer_max_resistance=4)

            :param kwargs: Key value pairs to set
        """
        for k, v in kwargs.items():
            setattr(self.config, k, v)
        self.__pload_items.append("config")

    def set_min_max_resistances(self, minr, maxr):
        """
            Set the configured minimum and maximum resistances for
            this scenario

            :param minr: Value of maximum resistance allowed
            :param maxr: Value of minimum resistance allowed
        """
        self.config.layer_min_resistance = minr
        self.config.layer_max_resistance = maxr
        self.__pload_items.append("config")

    def set_mcda_distance_weight_factor(self, factor):
        """
            Set the distance weight factor for the
            :class:`libpfapi.models.rmap.ResistanceMap` Calculation

            :param factor: Factor between 0 and 1 for weighting the ResistanceMap
            :type: float
        """
        if factor < 0 or factor > 1:
            raise PFModelException("set_mcda_distance_weight_factor should be between 0 and 1")

        self.config.mcda_dist_weight_factor = factor
        self.__pload_items.append('config')

    def set_mcda_model_gilytics(self, model_name):
        self.config.mcda_class_model = 'GilyticsMCDA'
        self.__pload_items.append('config')

    def set_mcda_model_swiss(self, model_name):
        self.config.mcda_class_model = 'SwissMCDA'
        self.__pload_items.append('config')

    def set_mcda_model_maximum_value(self, model_name):
        self.config.mcda_class_model = 'SimpleAdditiveWeighting'
        self.__pload_items.append('config')

    def set_mcda_model_by_name(self, model_name):
        """
            Set the MCDA model to a known model_name in the server.

            This might be a custom name for a custom client so contact Gilytics
            for more information on how to set up specific models.

            The list of available models for this user are stated by the api
            on :func:`~libpfapi.api.API.get_capabilities`


            :param model_name: Model name (know by the server)
            :type: string
        """
        self.config.mcda_class_model = model_name
        self.__pload_items.append('config')

    def set_pylon_min_max_distances(self, mindist, maxdist):
        """
            Set this scenario limits for pylon distances
            :param mindist: Minimum distance in meters
            :param maxdist: maximum distance in meters

            :returns: Nothing

        """
        cfg = self.config
        cfg.pylon_min_m = mindist
        cfg.pylon_max_m = maxdist

        self.__pload_items.append("config")  # We're modifying this Scenario Config

    @property
    def enabled_cost_models(self):
        """
            Cost models enabled for this Scenario

            :return: List of strings with names of enabled cost models
        """
        return self.config.cost_models

    def get_cost_models(self, **kwargs):
        """
            Returns a list with all the Scenario cost models with the
            scenario-parameter global cost-model values loaded.

            If any global parameter is not initialized its value will be None
            (meaning the server is responsible of setting a default)

            :return: List of CostModel instances
            :rtype: :class:`~libpfapi.models.cost.CostModel`
        """
        cmodels = []
        for cm_name in self.enabled_cost_models:
            cm = CostModel(cm_name, api=self._api)
            cmodel_data = self.config.cost_data.get(cm_name, {})
            for param in cm.get_global_parameters():
                param.set_value(cmodel_data.get(param.name, ""))
            cmodels.append(cm)
        return cmodels

    def enable_cost_model_with_cmodel_instance(self, cmodel):
        """
            Configure this scenario global cost model parameters
            using an instantiated :class:`~libpfapi.models.cost.CostModel`

            :param cmodel: A fully loaded cost model instance
            :ptype: :class:`~libpfapi.models.cost.CostModel`
        """
        cmodel.configure_scenario(self)

    def enable_cost_model_by_name(self, cost_model, **kwargs):
        """
            Enable a custom existing cost model by its name. Each custom
            model might need different custo keyword arguments, in case
            of doubt contact Gilytics.

            :param cost_model: Cost model name to enable
            :ptype: string
            :param kwargs: pairs of key value for the model parameters
        """
        cmodels = self.config.cost_models
        cmodels.append(cost_model)
        cmodels = list(set(cmodels))
        self.config.cost_models = cmodels

        cmodel_data = self.config.cost_data.get(cost_model, {})
        cmodel_data.update(kwargs)
        self.config.cost_data[cost_model] = cmodel_data
        self.__pload_items.append('config')

    def disable_cost_model_by_cmodel_instance(self, cmodel):
        """
            Disable a custom existing cost model using an instantiated
            :class:`~libpfapi.models.cost.CostModel`
        """
        self.disable_cost_model_by_name(cmodel.cname)

    def disable_cost_model_by_name(self, cost_model):
        """
            Disable a custom existing cost model by its name.
        """
        try:
            self.config.cost_models.remove(cost_model)
            self.__pload_items.append('config')
        except ValueError:
            pass

    def set_routing_model_by_name(self, model_name, **kwargs):
        """
            Set the routing model to a known model_name in the server.

            This might be a custom name for a custom client so contact Gilytics
            for more information on how to set up specific models.

            The list of available models for this user are stated by the api
            on :func:`~libpfapi.api.API.get_capabilities`

            :param model_name: Model name (know by the server)
            :type: string
            :param kwargs: extra directly named parameter to set as ScenarioConfig
                           This is very prone to error and one must be sure of
                           the valid parameters. But it's also open to cover
                           possible situations that were not intended for this library
                           version
        """
        self.config.routing_model = model_name

        for k, v in kwargs.items():
            setattr(self.config, k, v)
            # Those parameters are considered dirty since any name can come
            # here.
            self.config.add_dirty_parameter(k)

        self.__pload_items.append('config')

    def set_routing_pathfinder_explore(self, angle_weight=None,
                                       edge_weight=None, between_points_allowed=None):
        """
            Set the routing algorithm to the Pathfinder explore algorithm Check
            `Pathfinder docs website <http://docs.gilytics.com>`_ For more
            information
            :raises PFAPIException: If the user can't set this algorithm
        """
        cfg = self.config
        self.config.routing_model = ROUTING_GENETIC

        if angle_weight is not None:
            cfg.angle_weight = angle_weight
        if between_points_allowed is not None:
            cfg.between_points_allowed = between_points_allowed
        if edge_weight is not None:
            cfg.edge_weight = edge_weight

        self.__pload_items.append('config')

    def set_routing_gilytics_fast(self):
        """
            Set the routing algorithm to the GilyticsFast algorithm

            Check `Pathfinder docs website <http://docs.gilytics.com>`_ For more information
        """
        cfg = self.config
        cfg.routing_model = ROUTING_FAST

        self.__pload_items.append("config")  # We're modifying this Scenario Config

    def set_routing_pylon_spotting(self, angle_cost_f=None, angle_weight=None,
                                   between_points_allowed=None, edge_weight=None,
                                   max_angle=None, max_direction_deviation=None):
        """
            Set the routing algorithm to the Routing Pylon Spotting alongside its
            set of configurations. All configurations are required

            Check `Pathfinder docs website <http://docs.gilytics.com>`_ For more information

            .. note::
                This changes only the local instance, don't forget to call
                :func:`~libpfapi.models.scenario.Scenario.push_changes_to_server`

        """
        # We just modify the config
        cfg = self.config
        cfg.routing_model = ROUTING_PYLON_SPOTTING
        if angle_cost_f is not None:
            cfg.angle_cost_function = angle_cost_f
        if angle_weight is not None:
            cfg.angle_weight = angle_weight
        if between_points_allowed is not None:
            cfg.between_points_allowed = between_points_allowed
        if edge_weight is not None:
            cfg.edge_weight = edge_weight
        if max_angle is not None:
            cfg.max_angle = max_angle
        if max_direction_deviation is not None:
            cfg.max_direction_deviation = max_direction_deviation

        self.__pload_items.append("config")  # We're modifying this Scenario Config

    def get_layerconfig(self, layer_id):
        """
            Given a Layer-id Retrieve the LayerConfig for this Scenario

            :param layer_id: Id of the Layer to retrieve config from
            :return: LayerConfiguration for this Layer on the provided scenario
            :rtype: :class:`~libpfapi.models.layerconfig.LayerConfig`
        """
        return self._api.get_scenario_layer_config(self.id, layer_id)

    def get_changes_from_server(self):
        """
            Update this Scenario instance with the latest information from
            the server.

            :raises PFAPIException: If any error occurred while connecting to the server
        """
        # TODO we accept this roundtrip since we want to update this
        # instance, but at the same time we like how api returns
        # model instances too. The overhead is not that terrible
        ns = self._api.get_scenario(self.id)
        self.invalidate_cache()
        self._raw = ns._raw
        self._parse_from_dict(ns._raw)

    def push_changes_to_server(self):
        """
            Update this Scenario in the server with performed
            modifications. Will push both the :class:`~libpfapi.modules.scenario.Scenario`
            and its related :class:`~libpfapi.modules.scenarioconfig.ScenarioConfig`.

            :return: No return
            :rtype: :class:`~libpfapi.task.Task`
            :raises PFAPIException: If any problem occurred while pushing changes
        """
        payload = {k: getattr(self, k) for k in set(self.__pload_items)}

        if 'config' in payload:
            nconf = self.config.push_changes_to_server()
            del payload['config']
            self.config = nconf  # Assign new scenarioconfig

        scen = self._api.patch_scenario(self.id, **payload)
        self._raw = scen._raw
        self._parse_from_dict(scen._raw)

        self.__pload_items = []

    def recursive_copy(self, s):
        """
            Performs a recursive copy in PF's server from another Scenario. It'll
            copy all values LayerConfigs, ScenarioConfigs, CategoryConfigs making
            the two scenarios the same.

            This instance is updated with the latest server information when the
            function finishes.

            :param s: Scenario to copy from
            :type: :class:`~libpfapi.models.scenario.Scenario`
            :raises PFAPIException: If any problem arised when posting to the server
        """
        self._api.post_scenario_copy(self.id, s.id)
        self.get_changes_from_server()

    def __repr__(self):
        return "Scenario ({}): {}".format(self.id, self.name)
