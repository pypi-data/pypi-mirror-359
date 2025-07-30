import logging

import requests

from .exceptions import PFAPIException
from .models import (BaseLayer, Capabilities, Category, Corridor, Layer,
                     LayerConfig, ModelParameter, Project, ResistanceMap,
                     RoutingModel, Scenario, ScenarioConfig, ScenarioPath,
                     UserProfile)
from .task import Task
from .utils import _check_status_code_raise_error, get_url_call_response

logging.basicConfig(level=logging.INFO)


class API:
    """
        Base api class handling all connections

        .. danger::
            Not meant to be worked directly with except in specific
            cases where the :class:`libpfapi.models` do not provide
            the required functionality.
    """
    def __init__(self, token=None, url=None, log_level=None):
        """
            :param token: Token to connect to the server
            :param url: Base URL that the instance will connect to
            :param log_level: Set the desired log level
        """
        self.token = token
        self.url = "https://pathfinder.gilytics.com"

        # Allow setting other urls
        if url:
            self.url = url.rstrip("/")

        self.baseapiurl = self.url + '/api/v1'
        self.headers = {'authorization': 'Token {}'.format(self.token)}

        if log_level:
            logging.getLogger().setLevel(log_level)

    def get_version(self):
        """
            Return server version from the version endpoint

            :return: Version string if reported by the server
                     None otherwise
        """
        url = "{}/api/version".format(self.url)
        return get_url_call_response(url, self.headers)["version"]

    #
    # PROJECT
    #
    def get_projects(self):
        """
            Retrieve a list of the accessible projects per user. Projects are
            not fully loaded with all information at this point. You need to
            perform a call to the function
            :func:`libpfapi.models.project.Project.get_changes_from_server` to
            fill up more detailed project information.

            :return: All the projects accessible by the user
            :rtype: A list of :class:`~libpfapi.models.project`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/projects/".format(self.baseapiurl)
        res = get_url_call_response(url, self.headers)
        return [Project.new_from_dict(pdata, api=self) for pdata in res]

    def get_project(self, project_id):
        """
            Retrieve a single project from its id

            :param project_id: Pathfinder project ID
            :return: The project with that assigned id
            :rtype: :class:`~libpfapi.models.project`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/projects/{}/".format(self.baseapiurl, project_id)
        res = get_url_call_response(url, self.headers)
        return Project.new_from_dict(res, api=self)

    def delete_project(self, project_id):
        """
            Delete a single project from its id

            :param project_id: Pathfinder project ID
            :raises PFAPIException: If the project could not be deleted
        """
        url = "{}/projects/{}/".format(self.baseapiurl, project_id)
        logging.info("DELETE %s", url)

        ret = requests.delete(url, headers=self.headers)
        _check_status_code_raise_error(ret)

    def post_project(self, **kwargs):
        """
            Post a new project to the server.

            :return: the newly created Project
            :rtype: :class:`~libpfapi.models.project`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/projects/".format(self.baseapiurl)
        logging.info("POST %s %s", url, kwargs)

        ret = requests.post(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        return Project.new_from_dict(ret.json(), api=self)

    def patch_project(self, project_id, **kwargs):
        """
            Patch Project changes to server

            :param project_id: Id of the project to modify
            :return: A new instance with the modified project
            :rtype: :class:`~libpfapi.models.project`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/projects/{}/".format(self.baseapiurl, project_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        return Project.new_from_dict(ret.json(), api=self)

    def post_project_post_create_task(self, project_id, gen_dem_slope=False, gen_thumbnail=False):
        """
            Post project task

            :param project_id: ID of the project
            :param gen_dem_slope: Boolean to generate DEM/SLOPE layers
            :param gen_thumbnail: Boolean to generate thumbnail

            :return: Task reference. Once task is finished, refreshing
                     the Project instance is necessary.
                     Or None if the task instance was not created.
            :rtype: :class:`libpfapi.task.Task`
            :raises PFAPIException: For any server side error message
        """
        url = "{}/projects/{}/post_create_task/".format(self.baseapiurl, project_id)
        logging.info("POST {}".format(url))
        dpload = {
            "demslope": gen_dem_slope,
            "thumbnail": gen_thumbnail,
        }
        ret = requests.post(url, data=dpload, headers=self.headers)
        _check_status_code_raise_error(ret)
        tid = ret.json().get("process_key", None)
        if tid:
            return Task(tid, api=self)

    def get_project_layers(self, project_id):
        """
            Retrieve layers for a given project

            :param project_id: Pathfinder project ID

            :return: All the Layers related to the given project id
            :rtype: A list of :class:`~libpfapi.models.layer`

            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/projects/{}/layers".format(self.baseapiurl, project_id)
        res = get_url_call_response(url, self.headers)
        return [Layer.new_from_dict(ldata, api=self) for ldata in res]

    #
    # SCENARIO
    #
    def get_scenario(self, scenario_id):
        """
            Retrieve a single scenario from its id

            :param scenario_id: Pathfinder scenario ID
            :return: The Scenario with the given ID
            :rtype: :class:`~libpfapi.models.scenario`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenarios/{}/".format(self.baseapiurl, scenario_id)
        res = get_url_call_response(url, self.headers)
        return Scenario.new_from_dict(res, api=self)

    def get_scenarios(self):
        """
            Retrieve a list of the scenarios owned by this user

            :return: Scenarios owned by this user
            :rtype: A list of :class:`~libpfapi.models.scenario`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenarios/".format(self.baseapiurl)
        res = get_url_call_response(url, self.headers)
        return [Scenario.new_from_dict(sdata, api=self) for sdata in res]

    def post_scenario(self, name, project_id, stype="CLASSIC"):
        """
            Create a new Scenario in the server

            :param name: New name for this scenario
            :param project_id: Project to tie the scenario to
            :param stype: Classic, Multi, Multi-Child or Siting
            :return: Newly created scenario in the server
            :rtype: :class:`~libpfapi.models.scenario.Scenario`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenarios/".format(self.baseapiurl)
        pload = {
            "name": name,
            "project": project_id,
            "type": stype,
        }
        logging.info("POST {} {}".format(url, pload))
        ret = requests.post(url, headers=self.headers, json=pload)
        _check_status_code_raise_error(ret)
        return Scenario.new_from_dict(ret.json(), api=self)

    def patch_scenario(self, scenario_id, **kwargs):
        """
            Modifying an existing Scenario with new changes.

            .. note:
                you can call this endpoint incorrectly and have
                 no results. It's recommended to use the Layer class.

            :return: Scenario instance
            :rtype: :class:`~libpfapi.models.scenario.Scenario`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenarios/{}/".format(self.baseapiurl, scenario_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        return Scenario.new_from_dict(ret.json(), api=self)

    def delete_scenario(self, scenario_id):
        """
            Delete a single scenario from its id

            :param scenario_id: Pathfinder scenario ID
            :raises PFAPIException: If the scenario could not be deleted
        """
        url = "{}/scenarios/{}/".format(self.baseapiurl, scenario_id)
        logging.info("DELETE %s", url)

        ret = requests.delete(url, headers=self.headers)
        _check_status_code_raise_error(ret)

    def get_internally_shared_scenarios(self, project_id):
        """
            Retrieve a list of Public (read only) Scenarios for this project

            :return: Scenarios accesible by this user on this project
            :rtype: A list of :class:`~libpfapi.models.scenario.Scenario`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/projects/{}/internally-shared-scenarios".format(self.baseapiurl, project_id)
        res = get_url_call_response(url, self.headers)
        return [Scenario.new_from_dict(sdata, api=self) for sdata in res]

    def post_scenario_copy(self, base_scenario_id, import_scenario_id):
        """
            Copy one scenario on top of another recursively, so they
            generate the same kind of results

            :param base_scenario_id: Scenario id to copy to
            :param import_scenario_id: scenario id to copy from
            :return: None
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenarios/copy/".format(self.baseapiurl)
        pload = {"base_scenario_id": base_scenario_id,
                 "import_scenario_id": import_scenario_id}
        logging.info("POST {} {}".format(url, pload))
        ret = requests.post(url, headers=self.headers, json=pload)
        _check_status_code_raise_error(ret)

    #
    # CALCULATE RESISTANCE MAP, CORRIDOR AND PATHS
    #
    def post_scenario_calculate_rmap(self, scenario_id):
        """
            Start computation of the resistance map for a given scenario.

            :param scenario_id: ID of the scenario to compute the resistance map
            :return: Empty Resistance Map instance, alongisde Task reference. Once
                     task is finished, refreshing the ResistanceMap instance is
                     necessary.
            :rtype: (:class:`~libpfapi.models.rmap.ResistanceMap` ,
                     :class:`libpfapi.task.Task`)
            :raises PFAPIException: For any server side error message
        """
        url = "{}/scenarios/{}/calculate-resistance-map/".format(self.baseapiurl, scenario_id)
        logging.info("POST {}".format(url))
        ret = requests.post(url, headers=self.headers)
        _check_status_code_raise_error(ret)
        if isinstance(ret.json(), list):
            json_res = ret.json()[0]
        else:
            json_res = ret.json()
        rid = json_res["id"]
        tid = json_res["task_id"]
        rmap = ResistanceMap.new_from_dict({"id": rid}, api=self)
        tsk = Task(tid, api=self)
        return rmap, tsk

    def post_scenario_calculate_corridor(self, scenario_id, threshold=0.1):
        """
            Start computation of the corridor for a given scenario.

            :param scenario_id: ID of the scenario to compute the resistance map
            :param threshold: Corridor threshold percentage (between 0 and 1)
            :return: Empty Resistance Map instance, alongside Task reference. Once
                     task is finished, refreshing the ResistanceMap instance is
                     necessary.
            :rtype: tuple (:class:`~libpfapi.models.corridor.Corridor` ,
                     :class:`libpfapi.task.Task`)
            :raises PFAPIException: For any server side error message
        """
        url = "{}/scenarios/{}/calculate-corridor/".format(self.baseapiurl, scenario_id)
        pload = {"corridor_threshold": threshold}
        logging.info("POST {} {}".format(url, pload))
        ret = requests.post(url, headers=self.headers, json=pload)
        _check_status_code_raise_error(ret)
        if isinstance(ret.json(), list):
            json_res = ret.json()[0]
        else:
            json_res = ret.json()
        rid = json_res["id"]
        tid = json_res["task_id"]
        cor = Corridor.new_from_dict({"id": rid}, api=self)
        tsk = Task(tid, api=self)
        return cor, tsk

    def post_scenario_calculate_paths(self, scenario_id):
        """
            Start computation of the routing for a given scenario.

            :param scenario_id: ID of the scenario to compute the resistance map
            :return: Empty :class:`~libpfapi.models.scenario.Scenario` instance,
                     alongisde Task reference. Once task is finished, refreshing the
                     :class:`~libpfapi.models.scenario.Scenario` instance will obtain
                     the latest paths.
            :rtype: (:class:`~libpfapi.models.scenario.Scenario` ,
                     :class:`libpfapi.task.Task`)
            :raises PFAPIException: For any server side error message
        """
        url = "{}/scenarios/{}/calculate-paths/".format(self.baseapiurl, scenario_id)
        logging.info("POST {}".format(url))
        ret = requests.post(url, headers=self.headers)
        _check_status_code_raise_error(ret)
        if isinstance(ret.json(), list):
            json_res = ret.json()[0]
        else:
            json_res = ret.json()
        sid = json_res["id"]
        tid = json_res["task_id"]
        rmap = Scenario.new_from_dict({"id": sid}, api=self)
        tsk = Task(tid, api=self)
        return rmap, tsk

    #
    # CATEGORY
    #
    def post_category(self, **kwargs):
        """
            Post a new category to the server.

            :return: The newly created category
            :rtype: :class:`~libpfapi.models.category.Category`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/categories/".format(self.baseapiurl)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.post(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        return Category.new_from_dict(ret.json(), api=self)

    def delete_category(self, category_id):
        """
            Delete a single category from its category_id

            :param category_id: Pathfinder category ID
            :raises PFAPIException: If the category could not be deleted
        """
        url = "{}/categories/{}/".format(self.baseapiurl, category_id)
        logging.info("DELETE %s", url)
        ret = requests.delete(url, headers=self.headers)
        _check_status_code_raise_error(ret)

    #
    # SCENARIO CONFIG
    #
    def patch_scenario_config(self, scenarioconfig_id, **kwargs):
        """
            Modifying an existing Scenario Config with new changes.

            .. note:
                you can call this endpoint incorrectly and have
                 no results. It's recommended tu use the Layer class.

            :return: raw scenarioconfig JSON
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenario-configs/{}/".format(self.baseapiurl, scenarioconfig_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        return ScenarioConfig.new_from_dict(ret.json(), api=self)

    def get_scenario_layer_config(self, scenario_id, layer_id):
        """
            Retrieve a Layer with a config entry for a given
            scenario

            # TODO: this endpoint is very Pathfinder-ui focused,
               maybe we actually need a simpler one that returns
               the proper Config directly (without layer shenanigans)

            :param scenario_id: Pathfinder scenario ID
            :param layer_id: Pathfinder layer ID
            :return: LayerConfig for the scenario and the layer
            :rtype: instance of :class:`~libpfapi.models.layerconfig`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenarios/{}/layer/{}/".format(self.baseapiurl, scenario_id, layer_id)
        res = get_url_call_response(url, self.headers)
        return LayerConfig.new_from_dict(res['config'], api=self)

    def patch_scenario_layer_config(self, layer_config_id, **kwargs):
        """
            Patch the given kwargs to a scenario LayerConfig.
            If no exception is raised, data was properly updated in the server

            :param layer_config_id: Which LayerConfig to patch
            :param kwargs: each named argument updates the value of a given attribute
            :raises PFAPIException: If the response is not an HTTP OK response
            :return: No return provided
        """
        url = "{}/layer-configs/{}/".format(self.baseapiurl, layer_config_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)

    #
    # LAYER
    #
    def get_layer(self, layer_id):
        """
            Retrieve information from a given Layer

            :return: The Layer with the given id
            :rtype: :class:`~libpfapi.models.layer`

            :raises PFAPIException: If the response is not an HTTP OK response

        """
        url = "{}/layers/{}/".format(self.baseapiurl, layer_id)
        res = get_url_call_response(url, self.headers)
        return Layer.new_from_dict(res, api=self)

    def post_layer(self, **kwargs):
        """
            Post Layer creates a new Layer in the system. The minimum
            payload will be determined by the callee.

            .. note: you can call this endpoint incorrectly

            :return: Layer instance of the newly created layer and Task
                     instance to follow the preprocessing progress.

                     Once preprocessing is finished you should update
                     the Layer instace from the server
            :rtype: (:class:`~libpfapi.models.layer`, :class:`~libpfapi.task.Task`)

            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/layers/".format(self.baseapiurl)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.post(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        lid = ret.json()["layer_id"]
        tid = ret.json()["process_key"]
        lay = Layer.new_from_dict({"id": lid}, api=self)
        tsk = Task(tid, api=self)
        return (lay, tsk)

    def patch_layer(self, layer_id, **kwargs):
        """
            Modifying an existing Layer with new changes.

            .. note:
                you can call this endpoint incorrectly and have
                no results. It's recommended tu use the Layer class.

            :return: Layer instance of the newly created layer and Task
                     instance to follow the preprocessing progress.

                     Once preprocessing is finished you should update
                     the Layer instace from the server.

                     PATCHING might return a None Task, so double
                     check the output.

            :rtype: (:class:`~libpfapi.models.layer`, :class:`~libpfapi.task.Task`)
                    or None in any of the cases

            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/layers/{}/".format(self.baseapiurl, layer_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)
        lid = ret.json().get("layer_id", None)
        tid = ret.json().get("process_key", None)
        lay = tsk = None

        if lid:
            lay = Layer.new_from_dict({"id": lid}, api=self)
        if tid:
            tsk = Task(tid, api=self)

        return (lay, tsk)

    def delete_layer(self, layer_id):
        """
            Delete a single layer from its id

            :param layer_id: Pathfinder layer ID
            :raises PFAPIException: If the layer could not be deleted
        """
        url = "{}/layers/{}/".format(self.baseapiurl, layer_id)
        logging.info("DELETE %s", url)

        ret = requests.delete(url, headers=self.headers)
        _check_status_code_raise_error(ret)

    def get_layer_ranges(self, layer_id):
        """
            Retrieve raster ranges of a given layer. Works for
            any kind of layer although only makes sense
            for raster ones

            :return: tuple with the minimum and maximum values (min, max)
            :rtype: (int, int)
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/layers/{}/data_range/".format(self.baseapiurl, layer_id)
        res = get_url_call_response(url, self.headers)
        return res.get('min', None), res.get('max', None)

    #
    # RESISTANCE MAP, CORRIDOR, PATHS
    #
    def get_resistance_map(self, rmap_id):
        """
            Retrieve a given resistance map

            :param rmap_id: Resistance map id
            :return: The resistance map with the assigned ID
            :rtype: :class:`~libpfapi.models.rmap.ResistanceMap`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/resistance-maps/{}/".format(self.baseapiurl, rmap_id)
        res = get_url_call_response(url, self.headers)
        return ResistanceMap.new_from_dict(res, api=self)

    def get_corridor(self, corridor_id):
        """
            Retrieve a given corridor

            :param corridor_id: Corridor id
            :return: The Corridor with the assigned id
            :rtype: :class:`~libpfapi.models.corridor.Corridor`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/corridors/{}/".format(self.baseapiurl, corridor_id)
        res = get_url_call_response(url, self.headers)
        return Corridor.new_from_dict(res, api=self)

    def post_scenariopath_recompute_costs(self, path_id):
        """
            Petition a re-calculation task for the cost_models of a path id

            :param path_id: integer identifying a path
            :return: The task associated with the processing of the given file
            :rtype: :class:`~libpfapi.task.Task`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenario-paths/{}/recalculate-costs/".format(self.baseapiurl, path_id)
        logging.info("GET %s", url)

        ret = requests.post(url, headers=self.headers)
        _check_status_code_raise_error(ret)
        return Task(ret.json()["process_key"], api=self)

    def get_path(self, path_id):
        """
            Retrieve a path from it's id

            :param path_id: integer identifying a path
            :return: The scenariopath with the given ID
            :rtype: :class:`~libpfapi.models.scenariopath.ScenarioPath`

            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/scenario-paths/{}/".format(self.baseapiurl, path_id)
        res = get_url_call_response(url, self.headers)
        return ScenarioPath.new_from_dict(res, api=self)

    #
    # FILES
    #
    def generate_upload_url(self, filename):
        """
            Generate a new Upload URL to send a filename to. It returns a
            temporary url where the system can POST a File.

            :param filename: Filename to store
            :return: A Json structure with url and a possible 'fields'
                     parameter that provides extra information to authenticate and
                     upload
        """
        url = "{}/repository/upload/generate-url/{}/".format(self.url, filename)
        return get_url_call_response(url, self.headers)

    def upload_file_from_generated_url(self, presigned_post, local_filepath):
        """
            Generate a new Upload URL to send a filename to. It returns a
            temporary url where the system can POST a File.

            :param presigned_post: Post information to upload data to a server
                                   presigned URL
            :param local_filepath: Local File path to upload to pathfinder
            :return: True if file was upload correctly
            :raises: Error exception if any problem ocurred
        """
        fp = open(local_filepath, 'rb')
        files = {'file': fp}

        ret = requests.post(presigned_post["url"],
                            data=presigned_post.get("fields", {}),
                            files=files)
        _check_status_code_raise_error(ret)
        return True

    def upload_file_as_single_baselayer(self, fpath, name=None):
        """
            Given a filepath on the filesystem upload that file as a new
            BaseLayer using the single BaseLayer approach. Fpath must contain a
            single Layer to be uploaded (zip file with a single shape, single
            geopackage, geojson etc...)

            .. deprecated:: 0.4.0
                Version 0.4 onwards favour the use of
                :func:`~libpfapi.models.baselayer.BaseLayer.NewFromFile` the function
                remains available for the time being but will be removed or stop
                working altogether int the near future.

            :param fpath: valid path to a filesystem file.
            :param name: New name for this baselayer
            :return: The task associated with the processing of the given file
            :rtype: (:class:`~libpfapi.baselayer.BaseLayer`, :class:`~libpfapi.task.Task`)
            :raises PFAPIException: If the response is not an HTTP OK response

        """
        url = "{}/repository/import-single-layer".format(self.url)
        logging.info("POST %s", url)

        fh = open(fpath, "rb")
        fpload = {"file": fh}
        dpload = {"store": "default"}
        if name is not None:
            dpload["name"] = name

        ret = requests.post(url, files=fpload,
                            data=dpload,
                            headers=self.headers)
        fh.close()

        _check_status_code_raise_error(ret)
        data = ret.json()
        dpload["id"] = data["baselayer_id"]

        blay = BaseLayer.new_from_dict(dpload, api=self)
        tsk = Task(data["process_key"], api=self)
        return [blay, tsk]

    def upload_file_as_baselayer(self, fpath):
        """
            Given a filepath on the filesystem upload
            that file as a new BaseLayer.

            .. deprecated:: 0.4.0
                Version 0.4 onwards favour the use of
                :func:`~libpfapi.models.baselayer.BaseLayer.NewFromFile` the function
                remains available for the time being but will be removed or stop
                working altogether int the near future.


            :param fpath: valid path to a filesystem file.
            :return: The task associated with the processing of the given file
            :rtype: :class:`~libpfapi.task.Task`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/repository/import-layer".format(self.url)
        logging.info("POST %s", url)

        test_file = open(fpath, "rb")
        pload = {"file": test_file}

        ret = requests.post(url, files=pload,
                            data={"store": "default"},
                            headers=self.headers)
        test_file.close()

        _check_status_code_raise_error(ret)
        return Task(ret.json()["process_key"], api=self)

    #
    # BASELAYER
    #
    def get_baselayer_file(self, bl_id):
        """
            Retrieve a file BaseLayer (of type file) from the server.

            :return: The BaseLayer (file) with the given id
            :rtype: :class:`~libpfapi.models.BaseLayer`

            :raises PFAPIException: If the response is not an HTTP OK response

        """
        url = "{}/repository/api/v1/baselayer-file/{}/".format(self.url, bl_id)
        res = get_url_call_response(url, self.headers)
        return BaseLayer.new_from_dict(res, api=self)

    def get_baselayer_file_v2(self, bl_id):
        """
            Retrieve a file BaseLayer (of type file) from the server.

            :return: The BaseLayer (file) with the given id
            :rtype: :class:`~libpfapi.models.BaseLayer`

            :raises PFAPIException: If the response is not an HTTP OK response

        """
        url = "{}/repository/api/v1/baselayer-file-v2/{}/".format(self.url, bl_id)
        res = get_url_call_response(url, self.headers)
        return BaseLayer.new_from_dict(res, api=self)

    def patch_baselayer_file(self, bl_id, **kwargs):
        """
            Patch the given kwargs to a BaseLayer, This can mainly include
            name and description as most of the other attributes of a BaseLayer
            are read only
            If no exception is raised, data was properly updated in the server

            :param bl_id: Which BaseLayer file to patch
            :param kwargs: each named argument updates the value of a given attribute
            :raises PFAPIException: If the response is not an HTTP OK response
            :return: No return provided
        """
        url = "{}/repository/api/v1/baselayer-file/{}/".format(self.url, bl_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)

    def patch_baselayer_file_v2(self, bl_id, **kwargs):
        """
            Patch the given kwargs to a BaseLayer, This can mainly include
            name and description as most of the other attributes of a BaseLayer
            are read only
            If no exception is raised, data was properly updated in the server

            :param bl_id: Which BaseLayer file to patch
            :param kwargs: each named argument updates the value of a given attribute
            :raises PFAPIException: If the response is not an HTTP OK response
            :return: No return provided
        """
        url = "{}/repository/api/v1/baselayer-file/{}/".format(self.url, bl_id)
        logging.info("PATCH %s %s", url, kwargs)

        ret = requests.patch(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)

    def post_baselayerfile(self, **kwargs):
        """
            Post the base metadata to generate a BaseLayer from, in this case
            it's a matter of setting up at least the proper file reference
            in the system and then queue a processing task.

            .. note: you can call this endpoint incorrectly

            :return: BaseLayer instance of the newly created BaseLayer and Task
                     instance to follow the preprocessing progress.

                     Once preprocessing is finished you should update
                     the Layer instace from the server
            :rtype: (:class:`~libpfapi.models.BaseLayer`, :class:`~libpfapi.task.Task`)

            :raises PFAPIException: If the response is not an HTTP OK response
        """
        raise DeprecationWarning("Posting of BaseLayerV1 is deprecated")
        url = "{}/repository/api/v1/baselayer-file/".format(self.url)
        logging.info("POST %s %s", url, kwargs)

        ret = requests.post(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)

        blid = ret.json()["baselayer_id"]
        tid = ret.json()["process_key"]
        bl = BaseLayer.new_from_dict({"id": blid}, api=self)
        tsk = Task(tid, api=self)

        return (bl, tsk)

    def post_baselayerfile_v2(self, **kwargs):
        """
            Post the base metadata to generate a BaseLayer from, in this case
            it's a matter of setting up at least the proper file reference
            in the system and then queue a processing task.

            .. note: you can call this endpoint incorrectly

            :return: BaseLayer instance of the newly created BaseLayer and Task
                     instance to follow the preprocessing progress.

                     Once preprocessing is finished you should update
                     the Layer instace from the server
            :rtype: (:class:`~libpfapi.models.BaseLayer`, :class:`~libpfapi.task.Task`)

            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/repository/api/v1/baselayer-file-v2/".format(self.url)
        logging.info("POST %s %s", url, kwargs)

        ret = requests.post(url, headers=self.headers, json=kwargs)
        _check_status_code_raise_error(ret)

        blid = ret.json()["baselayer_id"]
        tid = ret.json()["process_key"]
        bl = BaseLayer.new_from_dict({"id": blid}, api=self)
        tsk = Task(tid, api=self)

        return (bl, tsk)

    def get_base_datasets(self):
        """
            Returns a list of base datasets accessible by the user

            :return: List of base datasets accessible by this user
            :rtype: list of :class:`~libpfapi.baselayer.BaseLayer`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/repository/api/v1/baselayers/".format(self.url)
        res = get_url_call_response(url, self.headers)
        return [BaseLayer.new_from_dict(d, api=self) for d in res]

    def delete_baselayer_file(self, baselayer_id):
        """
            Delete a single BaseLayer from its baselayer_id

            :param baselayer_id: Pathfinder BaseLayer ID
            :raises PFAPIException: If the baselayer could not be deleted
        """
        url = "{}/repository/api/v1/baselayer-file/{}/".format(self.url, baselayer_id)
        logging.info("DELETE %s", url)

        ret = requests.delete(url, headers=self.headers)
        _check_status_code_raise_error(ret)

    def delete_baselayer_file_v2(self, baselayer_id):
        """
            Delete a single BaseLayer from its baselayer_id

            :param baselayer_id: Pathfinder BaseLayer ID
            :raises PFAPIException: If the baselayer could not be deleted
        """
        url = "{}/repository/api/v1/baselayer-file/{}/".format(self.url, baselayer_id)
        logging.info("DELETE %s", url)

        ret = requests.delete(url, headers=self.headers)
        _check_status_code_raise_error(ret)

    def get_base_datasets_within_project(self, project_id):
        """
            Returns a list of base datasets accessible by the user and
            intersecting the given project_id

            :return: List of base datasets accessible by this user
            :rtype: list of :class:`~libpfapi.baselayer.BaseLayer`
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/repository/api/v1/list-layers/{}/".format(self.url, project_id)
        res = get_url_call_response(url, self.headers)
        return [BaseLayer.new_from_dict(d, api=self) for d in res]

    #
    # TASK
    #
    def get_progress(self, task_id):
        """
            Checks current progress of a remote task

            :return: dictionary with details, state and task_id
            :rtype: dict
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/get_progress/{}/".format(self.baseapiurl, task_id)
        return get_url_call_response(url, self.headers)

    def cancel_task(self, task_id):
        """
            Sends a signal to the server to try to cancel a remote task

            :param task_id: ID of task to be canceled
            :raises PFAPIException: If the response is not an HTTP OK response
        """
        url = "{}/tasks/terminate".format(self.baseapiurl)
        pload = {"task_id": task_id}
        logging.info("POST %s %s", url, str(pload))

        ret = requests.post(url,
                            data=pload,
                            headers=self.headers)
        _check_status_code_raise_error(ret)

    #
    # COST
    #
    def get_cost_model_parameters(self, cmodel):
        """
            Return a list of parameters for the given cost model, as
            a set of two lists:

            global_p -> global parameters
            layer_p -> layer parameters

            :return: List of parameters for this cost_model
            :rtype: dict
        """
        url = "{}/costs/model/list_parameters/{}/".format(self.url, cmodel)
        return get_url_call_response(url, self.headers)

    #
    # USER, TOKEN, CAPABILITIES
    #
    def get_account_info(self):
        """
            Retrieve account information for the current token

            :return: Dictionary with information on this account
            :rtype: dict
        """
        url = "{}/users/user-profile/".format(self.url)
        res = get_url_call_response(url, self.headers)[0]
        user_profile = UserProfile.new_from_dict(res, api=self)
        user_profile.load_capabilities()
        return user_profile

    def get_token(self, user, password):
        """
            Generate and receive a new token. Token is automatically
            assigned to the api instance

            :param user: Username
            :param password: password
        """
        url = "{}/api-token-auth/".format(self.url)

        logging.info("POST %s", url)
        payload = {"username": user, "password": password}
        ret = requests.post(url, json=payload)
        _check_status_code_raise_error(ret)
        pload = ret.json()
        if "api_token" in pload.keys():
            token = pload["api_token"]
        else:
            token = pload["token"]
        self.token = token
        self.headers = {'authorization': 'Token {}'.format(self.token)}
        return token

    def is_token_valid(self):
        """
            Utility function to check if the provided token is
            valid. Tries to retrieve the version string and in
            case of failure return false

            :return: True if token is valid for connection, False
                     otherwise
            :rtype: boolean
        """
        try:
            self.get_version()
            return True
        except PFAPIException:
            return False

    def get_capabilities(self):
        """
            Return a list of capabilities available for this user.
            Important items are:

            available_cost_models -> Name of cost models that can be used
            available_mcda_models -> Name of mcda models that can be used
            available_routing_models -> Name of routing models that can be used

            :return: List of capabilities for this user
            :rtype: dict
        """
        url = "{}/users/capabilities/".format(self.url)
        res = get_url_call_response(url, self.headers)
        return Capabilities.new_from_dict(res, api=self)

    #
    # ROUTING MODELS
    #
    def get_routing_model(self, rmodel_cname):
        """
            Returns a Routing Model with its parameters for the given class_name

            :rmodel_cname: The routing model class_name to retrieve
            :return: A routing model with a set of Parameters
            :rtype: RoutingModel
        """
        for rmodel in self.get_routing_models():
            if rmodel_cname in rmodel.class_name:
                rmodel.parameters = self.get_routing_model_parameters(rmodel_cname)
                return rmodel

        raise PFAPIException(f"The given RoutingModel name '{rmodel_cname}' has not found")

    def get_routing_models(self):
        """
            Returns the routing models (with their parameters) available for the calling user

            :return: A list of routing model instances
            :rtype: list
        """
        url = "{}/routing/models/list_available/".format(self.url)
        rmodels = []
        for rmodel in get_url_call_response(url, self.headers):
            new_rmodel = RoutingModel.new_from_dict(rmodel, api=self)
            new_rmodel.parameters = self.get_routing_model_parameters(new_rmodel.class_name)
            rmodels.append(new_rmodel)
        return rmodels

    def get_routing_model_parameters(self, rmodel_cname):
        """
            Return a list of parameters for the given routing model

            :return: A list of routing model parameters for this routing model
            :rtype: list
        """
        url = "{}/routing/models/list_parameters/{}/".format(self.url, rmodel_cname)
        res = get_url_call_response(url, self.headers)["inputs"]
        return [ModelParameter.new_from_dict(pdata, api=self) for pdata in res]

    def get_routing_model_parameters_w_values(self, rmodel_cname, project_id):
        """
            Return a list of parameters for the given routing model and project

            :return: A list of routing model parameters for this routing model and project
            :rtype: list
        """
        url = f"{self.url}/routing/models/list_parameters/{rmodel_cname}/{project_id}"
        return get_url_call_response(url, self.headers)["inputs"]
