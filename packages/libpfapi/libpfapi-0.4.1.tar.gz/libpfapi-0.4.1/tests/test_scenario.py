from libpfapi.exceptions import PFAPIException
from libpfapi.models import Scenario
from tests.base import api, TEST_PROJECT_ID, TEST_SCENARIO_ID


def test_new_scenario():
    p = api.get_project(TEST_PROJECT_ID)
    try:
        s = Scenario.new_scenario(p, "APISCEN", api=api)
        print(s)
    except PFAPIException as e:
        print(e)


def test_internally_shared_scenarios():
    shared_scenarios = []
    projs = api.get_projects()
    for p in projs:
        shared_scenarios += api.get_internally_shared_scenarios(p.id)
    print("Current shared scenarios")
    print(len(shared_scenarios))

    p = api.get_project(TEST_PROJECT_ID)

    try:
        s = Scenario.new_scenario(p, "API_Shared_Scenario", api=api)
        s.set_internally_shared(True)
        s.push_changes_to_server()

        shared_scenarios = []
        projs = api.get_projects()
        for p in projs:
            shared_scenarios += api.get_internally_shared_scenarios(p.id)
        print("Current shared scenarios")
        print(len(shared_scenarios))

    except PFAPIException:
        print("We could not create a new scenario because of the scenario limit per company")


def test_get_scenario_paths():
    s = api.get_scenario(TEST_SCENARIO_ID)
    paths = s.paths
    for p in paths:
        print(p.path)


def test_scenario_set_gilytics_fast_routing():
    s = api.get_scenario(TEST_SCENARIO_ID)

    # Project scenarios are not fully loaded, so we can re-retrieve
    # information for the scenario that we need to handle
    s.get_changes_from_server()
    s.set_routing_gilytics_fast()
    s.set_pylon_min_max_distances(20, 60)
    s.push_changes_to_server()


def test_scenario_set_start_and_end_points():
    p = api.get_project(TEST_PROJECT_ID)
    s = p.scenarios[0]
    s.get_changes_from_server()

    p1 = '{type: "Point", coordinates: [4.08729850769043, 49.97660184585698]}'
    p2 = '{type: "Point", coordinates: [4.186347122192383, 50.03507589061829]}'
    s.start_point = p1
    s.end_point = p2


def test_copy_scenarios():
    p = api.get_project(TEST_PROJECT_ID)
    s1 = p.scenarios[0]
    s2 = p.scenarios[1]
    s1.recursive_copy(s2)
    print(s1.name, 'copy from', s2.name)
    print(p.id)


if __name__ == "__main__":
    test_new_scenario()
    test_internally_shared_scenarios()
    test_get_scenario_paths()
    test_scenario_set_gilytics_fast_routing()
    test_scenario_set_start_and_end_points()
    test_copy_scenarios()
