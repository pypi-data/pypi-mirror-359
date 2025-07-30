from libpfapi.models import BaseLayer
from libpfapi.models.layer import Layer
from tests.base import TEST_PROJECT_ID, api


def test_create_bl_new_mode_nolimit():
    # Create a vector BaseLayer
    bl, tsk = BaseLayer.new_from_file(
        '/tmp/vies_ciclables.zip', api=api,
        name='MyBaseLayer-2', description='A desc'
    )
    tsk.wait_till_finished()
    bl.get_changes_from_server()

    print(bl)

    # Create a raster BaseLayer
    bl, tsk = BaseLayer.new_from_file(
        '/tmp/ESP_wind-speed_100m.tif', api=api,
        name='MyBaseLayer-RASTER-TEST',
        description='What could this be?'
    )
    tsk.wait_till_finished()
    bl.get_changes_from_server()


def test_upload_vector_baselayer_file():
    tsk = api.upload_file_as_baselayer("/tmp/TEST-ATTRIB.zip")
    tsk.wait_till_finished()
    print('DONE')


def test_upload_vector_baselayer_file_single_reference():
    bl, tsk = api.upload_file_as_single_baselayer("/tmp/TEST-ATTRIB.zip")
    print("At this point the BaseLayer id is ready {}, ".format(bl.id))
    print("but we need to wait the task")
    tsk.wait_till_finished()
    print("Once the task is finished, we can retrieve the latest information")
    bl.get_changes_from_server()
    print("Name: {}".format(bl.name))
    print("Features: {}".format(bl.feature_count))
    print("Type: {}".format(bl.ltype))
    print("Owner: {}".format(bl.owner_name))


def test_change_baselayer_prefix():
    prefix = "CH: "
    test_baselayer_id = 222
    bl = api.get_baselayer_file(test_baselayer_id)
    bl.set_name(prefix + bl.name)
    bl.set_description(prefix + bl.description)
    bl.push_changes_to_server()


def test_get_all_baselayers():
    dsets = api.get_base_datasets()
    for dset in dsets:
        print(dset.name, '-', dset.type, '-', dset.feature_count)
    return dsets


def test_list_my_baselayers():
    dsets = api.get_base_datasets()
    for dset in dsets:
        print(dset.name, '-', dset.owner_name)
    return dsets


def test_upload_and_reference_baselayer():
    """
        TODO this is cumbersome and we should provide a better way
            to do so
    """
    tsk = api.upload_file_as_baselayer("/tmp/TEST-ATTRIB.zip")
    tsk.wait_till_finished()
    dsets = api.get_base_datasets()
    dsets = [d for d in dsets if 'TEST-ATTRIB.zip' in d.filename]
    print([(d.id, d.name, d.filename) for d in dsets])


def test_upload_baselayer_and_add_layer_to_project():
    """
        This would be the minimum amount of steps to add a file to
        an existing project in Pathfinder
    """
    # We retrieve a project
    p = api.get_project(TEST_PROJECT_ID)

    # We upload a BaseLayer and get a reference to it (as discussed
    # this is a soft-reference and we should provide a better way
    # to do so)
    tsk = api.upload_file_as_baselayer("/tmp/TEST-ATTRIB.zip")
    tsk.wait_till_finished()
    bls = api.get_base_datasets()
    bls = [d for d in bls if 'TEST-ATTRIB.zip' in d.filename]
    bl = bls[0]

    # We reference a new Layer from a BaseLayer. User of the api
    # should know what's going on otherwise there might be a problem
    # when handling it. In this case I know it's a VECTOR so I'll
    # set proper vector values
    lay, tsk = Layer.new_from_base_layer(
        bl, p.categories[0],
        buffer_rings=[30, 40], name='TEST_LAYER',
        api=api
    )
    print(lay.is_processed)
    tsk.wait_till_finished()
    lay.get_changes_from_server()
    # The example file I used does not match with the project,
    # so it has errors, but it's there
    print(lay.has_errors, lay.error_msg)


if __name__ == "__main__":
    # test_create_bl_new_mode_nolimit()
    # test_upload_vector_baselayer_file()
    # test_upload_vector_baselayer_file_single_reference()
    # test_change_baselayer_prefix()
    test_get_all_baselayers()
    test_list_my_baselayers()
    # test_upload_and_reference_baselayer()
    # test_upload_baselayer_and_add_layer_to_project()
