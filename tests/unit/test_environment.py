from nyc_taxi_data_platform.environment.checks import run_local_checks


def test_local_checks_run():
    results = run_local_checks()
    names = {r.name for r in results}
    assert "python_version" in names
    assert all(r.name for r in results)
