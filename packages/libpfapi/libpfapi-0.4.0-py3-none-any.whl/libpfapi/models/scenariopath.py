from . import base
from libpfapi.exceptions import PFModelException


class ScenarioPath(base.Model):
    """
        ScenarioPath object

        :ivar id: ID of this ScenarioPath in the server
        :ivar cost_analytics_raw: Raw cost analytics data from the server
        :ivar is_optimal_path: Boolean marking this path as the optimal for the scenario
        :ivar ~.name: Name of this path
        :ivar path: GeoJSON representation of the given path
        :ivar user_uploaded: Was this path computed by the server or uploaded by the user
    """
    def __init__(self, api):
        self.pdefaults = {
            "id": None,
            "cost_analytics_raw": None,
            "is_optimal_path": None,
            "monetary_cost": None,
            "name": None,
            "path": None,
            "path_3d": None,
            "user_uploaded": None,
            "scenario_id": None,
        }

        super(ScenarioPath, self).__init__(api)

    def recalculate_cost_models(self):
        """
            Petitions a new task to the server to re-calculate the cost models
            with possibly new values.

            :return: The task associated with the processing of the given file
            :rtype: :class:`~libpfapi.task.Task`
        """
        return self._api.post_scenariopath_recompute_costs(self.id)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new ScenarioPath instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict
        # TODO how should we treat geojsons? So far
        # simply RAW so it can be handled by the
        # upper layers using this library
        properties = []

        for k, v in ddict.items():
            # Store scenario as scenario_id so we can keep the property
            if k == 'scenario':
                setattr(result, 'scenario_id', v)
                continue
            if k == 'cost_analytics':
                setattr(result, 'cost_analytics_raw', v)
                continue
            if k in properties:
                continue
            setattr(result, k, v)

        return result

    @property
    def cost_model_list(self):
        """
            Returns a list of cost-models computed for this ScenarioPath

            :rtype: List of strings
        """
        return self.cost_analytics_raw.keys()

    def get_cost_analytics(self, cmodel):
        """
            Get the structure of cost analytics for a given model.

            Returns a dictionary with the following items::

                items
                    desc
                        LIST
                            key: STR
                            label: STR
                    items
                        LIST
                            LIST <- as many items as desc list contents
                summary
                    pairs of key and value
                units
                    type STR
                    value STR
                error
                    STR (if any)

            :rtype: dictionary
        """
        return self.cost_analytics_raw.get(cmodel, {})

    @property
    def scenario(self):
        """
            :return: Scenario that this path belongs to
            :rtype: :class:`~libpfapi.modules.scenario.Scenario`
            :raises PFModelException: If there's no defined reference
            :raises PFAPIException: If the Scenario can't be retrieved from the server.
        """
        if self.scenario_id is None:
            raise PFModelException("Instance not initialized, or unknown scenario")

        return self._api.get_scenario(self.scenario_id)

    def __repr__(self):
        return "Path ({}): {}".format(self.id, self.name)
