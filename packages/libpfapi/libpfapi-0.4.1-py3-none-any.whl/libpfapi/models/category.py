from . import base


class Category(base.Model):
    """
        Pathfinder Category.

        Any project holds its information in different categories, and
        all Layers should be assigned a category.

        Categories can have custom weights from given :class:`libpfapi.models.scenario`
        CategoryConfig

        :ivar id: Identifier for this Category in the server
        :ivar ~.name: Name of this Category
    """
    def __init__(self, api):
        self.pdefaults = {
            "name": None,
            "id": None,
        }

        # Things used by FE but that we think have no place in the API
        self.skips = ["config_lst"]
        super(Category, self).__init__(api)

    @classmethod
    def new_category(cls, name, project_id, api=None):
        """
            Create a new category in the server

            :raises PFAPIException: If any problem appeared while creating the category
        """
        pload = {
                "name": name,
                "project": project_id,
        }

        return api.post_category(**pload)

    def delete(self):
        """
            Delete this Category from the server alongside
            all its assigned layers

            .. warning::
                This action is not reversible. Once deleted there is
                no way to recover the deleted information.

            :raises PFAPIException: If the server responds with an error
        """
        self._api.delete_category(self.id)

    @classmethod
    def new_from_dict(cls, ddict, api=None, **kwargs):
        """
            Return a new Category instance from a JSON dictionary
        """
        result = cls(api)
        result._raw = ddict

        for k, v in ddict.items():
            if k in result.skips:
                continue
            setattr(result, k, v)

        return result
