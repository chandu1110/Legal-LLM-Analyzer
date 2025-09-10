import pytest
from fastapi.testclient import TestClient
from src.main import app  # Import the FastAPI app instance from your main.py

# A TestClient is a tool that lets you send requests to your FastAPI app in a test
client = TestClient(app)

# A sample legal text to use in our tests
SAMPLE_TEXT = (
    "This Agreement is made and entered into on this 1st day of January, 2025. "
    "The Service Provider shall indemnify the Client against all liabilities. "
    "This agreement may be terminated by either party with 30 days written notice."
)


@pytest.fixture
def mock_legal_analyzer(mocker):
    """
    This is a pytest fixture using pytest-mock.
    It replaces the real LegalAnalyzer methods with fake ones that return predictable data.
    This allows us to test the API layer in isolation, without slow model loading.
    """
    # Define the fake data our mock methods will return
    mock_clauses = [{"entity_group": "CLAUSE", "word": "indemnify", "score": 0.99}]
    mock_summary = "This is a contract summary."
    mock_risk = "Medium Risk"

    # Use mocker to find the methods in 'src.main.analyzer' and replace them
    mocker.patch(
        "src.main.analyzer.extract_clauses", return_value=mock_clauses
    )
    mocker.patch(
        "src.main.analyzer.summarize_document", return_value=mock_summary
    )
    mocker.patch(
        "src.main.analyzer.analyze_risk", return_value=mock_risk
    )


def test_analyze_document_success(mock_legal_analyzer):
    """
    Tests the /analyze endpoint with a valid request.
    It uses the mock_legal_analyzer fixture to ensure predictable behavior.
    """
    # 1. Arrange: Define the request payload
    payload = {"text": SAMPLE_TEXT}

    # 2. Act: Send a POST request to the /analyze endpoint
    response = client.post("/analyze", json=payload)

    # 3. Assert: Check if the response is correct
    assert response.status_code == 200  # Check for a successful HTTP status
    
    data = response.json()  # Get the JSON response body
    assert data["summary"] == "This is a contract summary."
    assert data["risk_assessment"] == "Medium Risk"
    assert data["extracted_clauses"][0]["word"] == "indemnify"


def test_analyze_document_empty_text():
    """
    Tests the /analyze endpoint with an invalid request (empty text).
    FastAPI should automatically return a 422 Unprocessable Entity error.
    """
    # 1. Arrange: Define an invalid payload
    payload = {"text": ""}

    # 2. Act: Send the request
    response = client.post("/analyze", json=payload)

    # 3. Assert: Check for the expected validation error
    assert response.status_code == 422 # FastAPI's code for validation errors
    data = response.json()
    assert "detail" in data
    # Optional: check for a more specific error message if your Pydantic model has it
    # assert "field required" in str(data['detail']).lower()


def test_health_check():
    """
    Tests the root endpoint '/' which can serve as a simple health check.
    We need to add this endpoint to our main.py first.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Legal LLM API is running!"}
