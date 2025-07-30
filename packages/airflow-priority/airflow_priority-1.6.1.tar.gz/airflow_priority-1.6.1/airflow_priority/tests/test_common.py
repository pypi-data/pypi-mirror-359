from airflow_priority import get_config_option, has_priority_tag


def test_has_priority_tag(dag_run):
    assert has_priority_tag(dag_run) == ("UNIT TEST", 1)


def test_get_config_option(airflow_config):
    assert get_config_option("datadog", "api_key") == "datadog_api_key"


def test_get_config_option_alt(airflow_config_alt):
    assert get_config_option("datadog", "api_key") == "datadog_api_key"
