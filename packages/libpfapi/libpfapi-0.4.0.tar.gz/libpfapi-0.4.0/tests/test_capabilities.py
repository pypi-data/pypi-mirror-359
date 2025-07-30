from tests.base import api


def test_get_account_info():
    ai = api.get_account_info()
    print(f"Account Info: {ai}")
    print(f"id: {ai.id}")
    print(f"Username: {ai.username}")
    print(f"Last Name: {ai.last_name}")
    print(f"email: {ai.email}")
    print(f"type: {ai.type}")
    print(f"caps: {ai.capabilities}")

    print()
    print(ai.capabilities.project_caps)


def test_get_capabilities():
    c = api.get_capabilities()
    print(f"project_caps: {c.project_caps}")
    print(f"scenario_caps: {c.scenario_caps}")
    print(f"available_routing_models: {c.available_routing_models}")
    print(f"available_mcda_models: {c.available_mcda_models}")
    print(f"available_cost_models: {c.available_cost_models}")
    print(f"available_ui_modules: {c.available_ui_modules}")
    print(f"available_scenario_types: {c.available_scenario_types}")
    print(f"raster_ui_limit: {c.raster_ui_limit}")
    if c.can_load_scenario_config:
        print("It does can_load_scenario_config")
    else:
        print("It does not can_load_scenario_config")
    if c.can_change_category:
        print("It does can_change_category")
    else:
        print("it does not can_change_category")


if __name__ == "__main__":
    test_get_account_info()
    test_get_capabilities()
