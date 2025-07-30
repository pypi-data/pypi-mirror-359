import pytest

from libpfapi.exceptions import PFModelException
from tests.base import test_base  # noqa: F401


@pytest.mark.usefixtures("test_base")
def test_routing_models(test_base):
    """
    Test the retrieval and validation of routing models and their parameters.
    """
    s = test_base['api'].get_scenario(test_base['scenario_id'])
    print(f"Scenario name: {s.name}")

    routing_params = s.config.routing_params
    print(f"sconfig routing_params: {routing_params}")

    routing_models = test_base['api'].get_routing_models()
    for rmodel in routing_models:
        print(f"rmodel class_name: {rmodel.class_name}")
        try:
            rmodel.load_parameter_values_from_sconfig(s.config)
            print(f"rmodel params: {rmodel.parameters}")
            assert isinstance(rmodel.parameters, list), "RModel parameters should be a list"
            assert len(rmodel.parameters) > 0, "RModel parameters list should not be empty"
        except PFModelException:
            print("The given ScenarioConfig does not have values for this RoutingModel")
            continue

        for param in rmodel.parameters:
            print(f"p.name: {param.name}")
            print(f"p.value: {param.value}")
            assert rmodel.get_parameter(param.name) is not None, "Parameter should not be None"

    assert routing_models is not None, "Routing models should not be None"
    assert len(routing_models) > 0, "Routing models should not be empty"

@pytest.mark.usefixtures("test_base")
def test_get_routing_model(test_base):
    """
    Test the retrieval of a specific routing model by its name.
    """
    rmodel = test_base['api'].get_routing_model("GilyticsFastRouting")
    assert rmodel.label == "Fast single path", "Routing model label should be Fast single path"
    assert rmodel is not None, "Routing model should not be None"
    assert isinstance(rmodel.parameters, list), "Routing model parameters should be a list"
    assert len(rmodel.parameters) > 0, "Routing model parameters list should not be empty"

@pytest.mark.usefixtures("test_base")
def test_get_routing_models(test_base):
    """
    Test the retrieval of all routing models.
    """
    rmodels = test_base['api'].get_routing_models()
    print([(r.label, r.class_name) for r in rmodels])
    assert rmodels is not None, "Routing models should not be None"
    assert len(rmodels) > 0, "Routing models should not be empty"

@pytest.mark.usefixtures("test_base")
def test_get_parameter(test_base):
    """
    Test the retrieval of parameters for each routing model.
    """
    s = test_base['api'].get_scenario(test_base['scenario_id'])
    print(f"Scenario name: {s.name}")

    routing_params = s.config.routing_params
    print(f"sconfig routing_params: {routing_params}")

    routing_models = test_base['api'].get_routing_models()
    for rmodel in routing_models:
        print(f"rmodel class_name: {rmodel.class_name}")
        try:
            rmodel.load_parameter_values_from_sconfig(s.config)
            print(f"rmodel params: {rmodel.parameters}")
        except PFModelException:
            print("The given ScenarioConfig does not have values for this RoutingModel")
            continue

        for param in rmodel.parameters:
            print(f"p.name: {param.name}")
            print(f"p.value: {param.value}")
            print(f"{rmodel.get_parameter(param.name)}")
            assert rmodel.get_parameter(param.name) is not None, "Parameter should not be None"

@pytest.mark.usefixtures("test_base")
def test_get_routing_model_parameters(test_base, rmodel="GilyticsFastRouting"):
    """
    Test the retrieval of routing model parameters.

    This test checks if the routing model parameters can be successfully retrieved
    from the API and verifies that the parameters meet certain conditions.
    """
    params = test_base['api'].get_routing_model_parameters(rmodel)
    assert params is not None, "Routing model parameters should not be None"
    assert len(params) > 0, "Routing model parameters should not be empty"
    assert isinstance(params, list), "Routing model parameters should be a list"
    assert len(params) > 0, "Routing model parameters list should not be empty"

@pytest.mark.usefixtures("test_base")
def test_get_routing_model_parameters_w_values(test_base, rmodel="GilyticsFastRouting"):
    """
    Test the retrieval of routing model parameters with values for a specific routing model.
    """
    pvalues = test_base['api'].get_routing_model_parameters_w_values(
        rmodel, test_base.get("project_id", 1))
    assert pvalues is not None, "Routing model parameters should not be None"
    assert len(pvalues) > 0, "Routing model parameters should not be empty"
    assert isinstance(pvalues, list), "Routing model parameters should be a list"
    assert len(pvalues) > 0, "Routing model parameters list should not be empty"
