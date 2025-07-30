"""
    Project module contains the top level
    :class:`~libpfapi.models.project.Project` class.

    It's useful as a starting point for any kind of interaction with the
    pathfinder, although you can access directly by IDs to any required model.

    For example, to retrieve all the projects accessible by a user::

        a = API(token)
        projects = a.get_projects()

    And from there, one can list and retrieve the latest information from the
    existing scenarios/layers/categories for that project::

        a = API(token)
        projects = a.get_projects()
        project = projects[0]

        s = next(s for s in project.scenarios if s.name == 'MyScenario')
        s.get_changes_from_server()

    Note that in most cases it's necessary to retrieve more specific
    information from the server from the
    :class:`~libpfapi.models.scenario.Scenario`
    :class:`~libpfapi.models.category.Category` and
    :class:`~libpfapi.models.layer.Layer`
    since project only holds basic information for each of those instances.

    ---

"""
from . import base
from .category import Category
from .layer import Layer
from .scenario import Scenario


class Project(base.Model):
    """
        Pathfinder project
    """
    def __init__(self, api):
        self.pdefaults = {
            "name": None,
            "description": None,
            "id": None,
            "area": None,
            "area_bbox": None,
            "start_point": None,
            "end_point": None,
            "intermediate_points": None,
            "raster_resolution": None,
            "scenarios": [],
            "layers": [],
            "categories": [],
            "thumbnail": None,
            "owner_username": None,
        }

        self.__pload_items = []

        super(Project, self).__init__(api)

    @classmethod
    def NewProject(cls, name, area, start_point, end_point, resolution=10, api=None):
        """
            Crate a new project In the server

            :return: Project instance representing this new project
        """
        pload = {
                "name": name,
                "area": area,
                "start_point": start_point,
                "end_point": end_point,
                "raster_resolution": resolution
        }

        return api.post_project(**pload)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            if k == 'scenarios':
                v = [
                    Scenario.new_from_dict(sdata, api=self._api)
                    for sdata in ddict['scenarios']
                ]
            if k == 'layers':
                v = [
                    Layer.new_from_dict(sdata, api=self._api)
                    for sdata in ddict['layers']
                ]
            if k == 'categories':
                v = [
                    Category.new_from_dict(sdata, api=self._api)
                    for sdata in ddict['categories']
                ]

            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new project instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(result._raw)
        return result

    def delete(self):
        """
            Delete this Project from the server

            .. warning::
                This action is not reversible. Once deleted there is
                no way to recover

            :raises PFAPIException: If the server responds with an error
        """
        self._api.delete_project(self.id)

    def add_category(self, name):
        """
            Create a new category for this project in the server

            :return: The new category created for this project
            :raises PFAPIException: If any problem arised while creating the category
        """
        ncat = Category.new_category(name, self.id, api=self._api)
        self.categories.append(ncat)
        return ncat

    @property
    def resolution(self):
        """
            Resolution configured for this project
        """
        return self.raster_resolution

    def set_name(self, name=None):
        """
            Change the name of the project
            :param name: New name of the project
            :ptype string:
        """
        self.name = name
        self.__pload_items.append("name")

    def set_description(self, description=None):
        """
            Change the description of the project

            :param description: New description of the project
            :ptype string:
        """
        self.description = description
        self.__pload_items.append("description")

    def set_start_point(self, geojson_point=None):
        """
            Sets the start point for a Project.
            This implies a change on all the Scenarios that do not define
            their own project points (beware)

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
            Sets the end point for a Project.
            This implies a change on all the Scenarios that do not define
            their own project points (beware)


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

    def generate_dem_slope(self):
        """
            Launches a Task that will end up generating DEM and SLOPE Layers for
            this Project.

            :return: Task reference. Once task is finished, refreshing
                     the Project instance is necessary.
                     Or None if the task instance was not created.
            :rtype: :class:`libpfapi.task.Task`
            :raises PFAPIException: For any server side error message
        """
        return self._api.post_project_post_create_task(self.id, True, False)

    def generate_thumbnail(self):
        """
            Launches a Task that will end up generating the thumbnail for
            this Project.

            :return: Task reference. Once task is finished, refreshing
                     the Project instance is necessary.
                     Or None if the task instance was not created.
            :rtype: :class:`libpfapi.task.Task`
            :raises PFAPIException: For any server side error message
        """
        return self._api.post_project_post_create_task(self.id, False, True)

    def get_changes_from_server(self):
        nproj = self._api.get_project(self.id)
        self._parse_from_dict(nproj._raw)

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
        proj = self._api.patch_project(self.id, **payload)
        self._raw = proj._raw
        self._parse_from_dict(proj._raw)
        self.__pload_items = []

    def get_datasets_within(self):
        """
            Return a list of the Base Layers with coverages overlapping
            this project bounding box.

            :return: List of base datasets with potential data within this project
            :rtype: list of :class:`~libpfapi.models.baselayer.BaseLayer`
            :raises PFAPIException:
        """
        return self._api.get_base_datasets_within_project(self.id)

    def __repr__(self):
        return "Project ({}): {} res={}".format(self.id, self.name, self.raster_resolution)
