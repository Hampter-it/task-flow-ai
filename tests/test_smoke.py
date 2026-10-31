from taskflow.main import app


def test_app_has_expected_title() -> None:
    assert app.title == "TaskFlow API"
