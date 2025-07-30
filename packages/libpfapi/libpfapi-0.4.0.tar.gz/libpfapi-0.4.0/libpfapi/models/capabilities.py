"""
    This module manages capabilities for the current Pathfinder user. It determines system access
    based on user grants, rights level, and company settings.

    Key functionalities:

    - Represents the current Pathfinder User Profile
    - Defines system user capabilities based on user grants
    - Defines user capabilities based on User rights level and company settings

    This module is crucial for enforcing access control and ensuring that users can only perform
    actions they are authorized to perform.
"""
from . import base

# Known kinds of users
ADMIN = 'Admin'
EDITOR = 'Editor'
VIEWER = 'Viewer'
SUPERUSER = 'Superuser'


class UserProfile(base.Model):
    """
        Pathfinder Account -> UserProfile.

        Representing the current pathfinder User Profile.
        Enumeration type with the different kinds of users.

        :ivar id: Unique identifier for this UserProfile
    """
    def __init__(self, api=None):
        self.capabilities = None
        self.type = None
        self.pdefaults = {
            "id": None,
            "username": None,
            "last_name": None,
            "email": None,
            "type": None,
            "capabilities": None,
        }

        self.__pload_items = []
        super(UserProfile, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            if k == "user_type":
                if v == "ADMIN":
                    self.type = ADMIN
                elif v == "STANDARD":
                    self.type = EDITOR
                elif v == "ROOT":
                    self.type = SUPERUSER
                else:
                    self.type = VIEWER

            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new UserProfile instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)
        return result

    def get_changes_from_server(self):
        user_profile = self._api.get_account_info()
        self._parse_from_dict(user_profile._raw)

    def load_capabilities(self):
        """
            :return: Capabilities for the current user
            :rtype: :class:`~libpfapi.models.capabilities.UserProfile.Capabilities`
            :raises PFModelException: If there's no defined reference
            :raises PFAPIException: If the UserProfile can't be retrieved from the server.
        """
        if self.capabilities is None:
            self.capabilities = self._api.get_capabilities()

        return self.capabilities

    def __repr__(self):
        return "User Profile ({}): {}".format(self.id, self.username)


class Capabilities(base.Model):
    """
        Pathfinder Capabilities.
        Class representing the current pathfinder user Capabilities.
    """
    def __init__(self, api=None):
        self.pdefaults = {
            "project_caps": [],
            "scenario_caps": [],
            "available_routing_models": [],
            "available_mcda_models": [],
            "available_cost_models": [],
            "available_ui_modules": [],
            "available_scenario_types": [],
            "raster_ui_limit": 0,
        }

        self.__pload_items = []
        super(Capabilities, self).__init__(api)

    def _parse_from_dict(self, ddict):
        """
            Private function parsing from a dictionary
        """
        for k, v in ddict.items():
            setattr(self, k, v)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new Capabilities instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict
        result._parse_from_dict(ddict)
        return result

    def get_changes_from_server(self):
        capabilities = self._api.get_account_info()
        self._parse_from_dict(capabilities._raw)

    #
    # Project Capabilities
    #
    def can_create_project(self):
        return "ADD-PROJECT" in self.project_caps

    def can_edit_project_points(self):
        return "EDIT-POINTS" in self.project_caps

    def can_delete_project(self):
        return "DELETE-PROJECT" in self.project_caps

    def can_add_category(self):
        return "ADD-CATEGORY" in self.project_caps

    def can_delete_category(self):
        return "DELETE-CATEGORY" in self.project_caps

    def can_add_layer(self):
        return "ADD-LAYER" in self.project_caps

    def can_download_layer(self):
        return "DOWNLOAD-LAYER" in self.project_caps

    def can_delete_layer(self):
        return "DELETE-LAYER" in self.project_caps

    def can_rebuffer_layer(self):
        return "BUFFER-LAYERS" in self.project_caps

    def can_upload_base_layer(self):
        return "ADD-BASELAYER" in self.project_caps

    def can_change_layer(self):
        return "CHANGE-LAYER" in self.project_caps

    def can_change_category(self):
        return "CHANGE-CATEGORY" in self.project_caps

    def can_export_project_results(self):
        return "EXPORT-RESULTS" in self.project_caps

    #
    # Scenario Capabilities
    #
    def can_create_scenario(self):
        return "ADD-SCENARIO" in self.scenario_caps

    def can_change_scenario(self):
        return "CHANGE-SCENARIO" in self.scenario_caps

    def can_delete_scenario(self):
        return "DELETE-SCENARIO" in self.scenario_caps

    def can_create_scenario_catalog(self):
        return "ADD-CATALOG" in self.scenario_caps

    def can_load_scenario_catalog(self):
        return "LOAD-CATALOG" in self.scenario_caps

    def can_load_scenario_config(self):
        return "SCENARIO-SETTINGS" in self.scenario_caps

    def can_edit_layer_config(self):
        return "EDIT-LAYERS" in self.scenario_caps

    def can_export_scenario_file(self):
        return "EXPORT-CSV" in self.scenario_caps

    def can_import_scenario_file(self):
        return "IMPORT-CSV" in self.scenario_caps

    def can_import_path_to_scenario(self):
        return "IMPORT-PATH" in self.scenario_caps

    def can_export_scenario_results(self):
        return "EXPORT-RESULTS" in self.scenario_caps
