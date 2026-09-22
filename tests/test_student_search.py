from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def search(query: str):
    response = client.get("/students/search", params={"q": query})
    assert response.status_code == 200
    return response.json()


def test_search_by_exact_student_id():
    payload = search("MH1002")

    assert payload["search_type"] == "student_id"
    assert payload["total_matches"] == 1
    assert payload["results"][0]["student_id"] == "MH1002"


def test_search_by_partial_student_id():
    payload = search("100")

    assert payload["search_type"] == "student_id"
    assert payload["total_matches"] == 9
    assert all("100" in student["student_id"] for student in payload["results"])


def test_search_by_name_ignores_case_and_diacritics():
    payload = search("AVA GARCIA")

    assert payload["search_type"] == "name"
    assert payload["total_matches"] == 1
    assert payload["results"][0]["name"] == "Áva García"


def test_blank_query_returns_no_results():
    payload = search("   ")

    assert payload == {
        "query": "",
        "search_type": None,
        "results": [],
        "total_matches": 0,
        "has_more": False,
    }


def test_search_with_no_matches_returns_empty_results():
    payload = search("No Student Has This Name")

    assert payload["results"] == []
    assert payload["total_matches"] == 0
    assert payload["has_more"] is False


def test_search_limits_results_and_reports_more_matches():
    payload = search("MH1")

    assert len(payload["results"]) == 10
    assert payload["total_matches"] == 18
    assert payload["has_more"] is True