from pathlib import Path

from libpfapi.exceptions import PFAPIException
from tests.base import TEST_LAYER_ID, TEST_PROJECT_ID, TEST_SCENARIO_ID, api


def test_get_layer_config(project):
    lay = project.layers[0]
    print(lay)
    scen = project.scenarios[0]
    print(scen)
    conf = lay.get_config(scen.id)
    print(conf)


def test_modify_and_patch_layer_config(project):
    vlayers = [lay for lay in project.layers if lay.is_vector]
    if vlayers:
        lay = vlayers[0]
        scen = project.scenarios[0]
        conf = lay.get_config(scen.id)
        conf.set_mode_vector_av(2)
        conf.push_changes_to_server()


def test_modify_and_patch_layer_config_to_pr(project):
    vlayers = [lay for lay in project.layers if lay.is_vector]
    if vlayers:
        lay = vlayers[0]
        scen = project.scenarios[0]
        conf = lay.get_config(scen.id)
        conf.set_mode_vector_av(2)
        conf.push_changes_to_server()


def test_rebuffer_existing_layer_set_new_resistances_in_senario(project):
    vlayers = [lay for lay in project.layers if lay.is_vector]
    if vlayers:
        lay = vlayers[0]
        scen = project.scenarios[0]  # Scenario we'll update
        conf = lay.get_config(scen.id)  # Configuration of roads layer in scenario

        lay.set_buffer_rings([10, 100, 100, 100])  # Set buffers to local instance
        tsk = lay.push_changes_to_server()  # Update the server with changes
        if tsk is not None:  # Server might return a task (or not)
            tsk.wait_till_finished()  # Wait for the task to finish
            lay.get_changes_from_server()  # retrieve new changes from server
        conf.set_mode_vector_pr([1, 2, 3, 4], forbidden=[True, False, False, False])  # config
        conf.push_changes_to_server()  # Send changes to config


def test_get_layer_ranges(project):
    lay = next(lay for lay in project.layers if "dem" in lay.name)
    print(lay.get_data_ranges())


def download_layer_geojson(project):
    vlayers = [lay for lay in project.layers if lay.is_vector]
    if vlayers:
        lay = vlayers[0]
        lay.get_geojson_original()


def download_layer_geojson_to_file(project):
    vlayers = [lay for lay in project.layers if lay.is_vector]
    if vlayers:
        lay = vlayers[0]
        lay.get_geojson_original(path='/tmp/mydata.geojson')
        lay.get_geojson_processed(path='/tmp/mydata-processed.geojson')


def test_set_layerconf_to_res(project, scenario, layer, resistance_val):
    try:
        print(project.name, scenario.name, layer.name, '->', resistance_val)
        lconf = scenario.get_layerconfig(layer.id)
        lconf.set_mode_vector_av(resistance_val)
        lconf.push_changes_to_server()
    except StopIteration:
        print("No data found to keep going with this test")


def test_set_layerconf_forbidden(project, scenario, layer):
    try:
        print(project.name, scenario.name, layer.name, '-> FB')
        lconf = scenario.get_layerconfig(layer.id)
        lconf.set_mode_forbidden()
        lconf.push_changes_to_server()
    except PFAPIException:
        print("No layer matches with the given ID")


def test_rebuffer_layer(layer, buffers):
    try:
        layer.set_buffer_rings(buffers)  # Set buffers to local instance
        tsk = layer.push_changes_to_server()  # Update the server with changes
        if tsk is not None:  # Server might return a task (or not)
            tsk.wait_till_finished()  # Wait for the task to finish
            layer.get_changes_from_server()  # retrieve new changes from server
    except PFAPIException:
        print("No layer matches the given ID")


def test_set_layerconf_per_ring(project, scenario, layer, ring_values):
    try:
        print(project.name, scenario.name, layer.name, '->', ring_values)
        lconf = scenario.get_layerconfig(layer.id)

        lconf.set_mode_vector_pr(ring_values, forbidden=[False]*len(ring_values))  # config
        lconf.push_changes_to_server()  # Send changes to config
    except PFAPIException:
        print("No layer matches the given ID")


def test_set_raster_av_mode(project, scenario):
    """
        Modify this test according to your possible rasters.

        gets the first raster that finds and assigns some
        possible values
    """
    rst = [lay for lay in project.layers if lay.is_raster]
    if not rst:
        print("project {} has no Raster layer".format(project.name))
    rst = rst[0]

    try:
        lconf = scenario.get_layerconfig(rst.id)

        # We get our minimum and maximum raster values
        rmin, rmax = rst.get_data_ranges()
        valid_res = list(range(1, 10))
        resistances_to_set = []

        # Assign resistances each steps of 5 raster values.
        # if the raster value is higher than half the maximum
        # we'll set that step to Forbidden (with a False)
        for idx, rst_val in enumerate(range(int(rmin), int(rmax), 5)):
            if rst_val > rmax / 2:
                res_value = False
            else:
                res_value = valid_res[idx % len(valid_res)]

            resistances_to_set.append(
                [rst_val, res_value]
            )

        # Set the defined raster_values previously, alongside a default
        # value of resistance=1 for any non-assigned raster values
        lconf.set_mode_raster_av(resistances_to_set, 1)
        lconf.push_changes_to_server()
    except PFAPIException:
        print("The Given Layer does not exist")


def test_set_raster_ranges_mode(project, scenario):
    rst = [lay for lay in project.layers if lay.is_raster]
    if not rst:
        print("project {} has no Raster layer".format(project.name))
    rst = rst[0]

    print(project.name, scenario.name, rst.name)
    try:
        lconf = scenario.get_layerconfig(rst.id)

        # We get our minimum and maximum raster values
        rmin, rmax = rst.get_data_ranges()
        step = rmax/4
        resistances_to_set = [
            (rmin, rmin+step, 1),
            (rmin+step, rmin+2*step, 2),
            (rmin+2*step, rmin+3*step, False),
        ]

        # Set the defined raster_values previously, alongside a default
        # value of resistance=1 for any non-assigned raster values
        lconf.set_mode_raster_ranges(resistances_to_set, 2)
        lconf.push_changes_to_server()

        default, ranges = lconf.get_raster_ranges_conf()
        print(ranges)
    except PFAPIException:
        print("The Given Layer does not exist")


def test_get_packed_data_file(project):
    vlayers = [lay for lay in project.layers if lay.is_vector]
    if vlayers:
        layer = vlayers[0]

        zip_file = layer.get_packed_data_file()
        if zip_file:
            print("OK -> layer.get_packed_data_file() returned 'something'")

        # path = filename with a wrong extension
        zip_file, filepath = layer.get_packed_data_file("test_file.geopackage")
        filepath = Path(filepath)
        assert filepath.is_file(), "The object returned is not a file"
        assert filepath.suffix == ".zip", "The file returned is not a zip file"
        print(filepath)

        # path without filename
        zip_file, filepath = layer.get_packed_data_file("/tmp/")
        filepath = Path(filepath)
        assert filepath.is_file(), "The object returned is not a file"
        assert filepath.suffix == ".zip", "The file returned is not a zip file"
        print(filepath)

        # path without filename
        zip_file, filepath = layer.get_packed_data_file("/tmp/test_file_path.zip")
        filepath = Path(filepath)
        assert filepath.is_file(), "The object returned is not a file"
        assert filepath.suffix == ".zip", "The file returned is not a zip file"
        print(filepath)


if __name__ == "__main__":
    test_project = api.get_project(TEST_PROJECT_ID)
    test_scenario = api.get_scenario(TEST_SCENARIO_ID)
    test_layer = api.get_layer(TEST_LAYER_ID)

    test_get_layer_config(test_project)
    test_modify_and_patch_layer_config(test_project)
    test_modify_and_patch_layer_config_to_pr(test_project)
    test_rebuffer_existing_layer_set_new_resistances_in_senario(test_project)
    test_get_layer_ranges(test_project)
    download_layer_geojson(test_project)
    download_layer_geojson_to_file(test_project)
    test_get_packed_data_file(test_project)
    test_set_layerconf_to_res(test_project, test_scenario, test_layer, 14)
    test_set_layerconf_forbidden(test_project, test_scenario, test_layer)

    # REBUFF AND PER RING VALUES
    test_rebuffer_layer(test_layer, [10, 20])
    test_set_layerconf_per_ring(test_project, test_scenario, test_layer, [18, 19])

    test_rebuffer_layer(test_layer, [1000])
    test_set_raster_av_mode(test_project, test_scenario)
    test_set_raster_ranges_mode(test_project, test_scenario)
