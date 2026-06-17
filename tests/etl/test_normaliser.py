from src.etl.normaliser import normalize_text

def test_normalize_text():
    assert normalize_text(" TCS ") == "TCS"