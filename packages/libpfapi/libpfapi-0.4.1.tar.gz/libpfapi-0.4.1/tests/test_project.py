from libpfapi.models.project import Project
from tests.base import api, TEST_PROJECT_ID


def test_get_projects():
    projs = api.get_projects()
    print([(p.id, p.name) for p in projs])
    return projs


def test_print_project_scenarios():
    projs = api.get_projects()

    for p in projs:
        for s in p.scenarios:
            print(p.name, s.name)
            try:
                rm = s.resistance_map
                print('rmap:', rm)
            except Exception:
                print('no rmap')


def test_print_project_shared_scenarios():
    projs = api.get_projects()
    for p in projs:
        print(f"shared scenarios for project: {p.id} - {p.name}")
        shared_scenarios = api.get_internally_shared_scenarios(p.id)
        print([(s.id, s.name) for s in shared_scenarios])


def test_project_scenarios_count():
    projs = api.get_projects()
    for p in projs:
        print(p.name, len(p.scenarios))


def test_project_scenarios_path_count():
    projs = api.get_projects()
    for p in projs:
        for s in p.scenarios:
            print(p.name, s.name, len(s.paths))


def test_get_project_layers():
    p = api.get_project(TEST_PROJECT_ID)

    for lay in p.layers:
        print(lay.id, lay.name)
    for s in p.scenarios:
        print(s.id, s.name)


def test_new_project():
    # Creates an empty project, expects GeoJSON strings as area,start,end and intermediate
    areajson = ('{"type":"Polygon","coordinates":'
                '[[[3.943579933665008,50.62110627648519],[3.945085074626865,50.595793812433925],'
                '[3.98534759535655,50.595793812433925],[3.984218739635157,50.622061197174475],'
                '[3.943579933665008,50.62110627648519]]]}')
    start_json = '{"type":"Point","coordinates":[3.951858208955224,50.61824139807419]}'
    end_json = '{"type":"Point","coordinates":[3.9755641791044773,50.60057079139321]}'

    p = Project.NewProject("API-PROJECT", areajson, start_json, end_json,
                           resolution=10, api=api)
    print(p.id, p.name)


def test_get_datasets_within_project():
    p = api.get_project(TEST_PROJECT_ID)
    dsets = p.get_datasets_within()
    print([d.name for d in dsets])


def test_list_projects():
    projects = api.get_projects()
    for p in projects:
        print(p)


def test_list_project_scenarios():
    p = api.get_project(TEST_PROJECT_ID)
    for s in p.scenarios:
        print(s)


def test_list_project_layers():
    p = api.get_project(TEST_PROJECT_ID)
    for l in p.layers:
        print(l)


def test_generate_dem_slope():
    p = api.get_project(TEST_PROJECT_ID)
    layer_names = [l.name for l in p.layers]
    print("DEM existence: {}".format("dem" in layer_names))

    if "dem" not in layer_names:
        print("Generating DEM and SLOPE layers")
        p.generate_dem_slope()


def test_generate_thumbnail():
    p = api.get_project(TEST_PROJECT_ID)
    print("Thumbnail existence: {}".format(p.thumbnail is not None))

    if p.thumbnail is None:
        print("Generating project thumbnail")
        p.generate_thumbnail()


def test_get_project_owner_username():
    p = api.get_project(TEST_PROJECT_ID)
    print(p.owner_username)


if __name__ == "__main__":
    # lists
    test_list_projects()
    test_list_project_scenarios()
    test_list_project_layers()

    # project scenario
    test_print_project_scenarios()
    test_print_project_shared_scenarios()
    test_project_scenarios_count()
    test_project_scenarios_path_count()

    # gets
    test_get_datasets_within_project()
    test_get_project_layers()
    test_get_project_owner_username()

    # create project related
    test_new_project()
    test_generate_dem_slope()
    test_generate_thumbnail()
