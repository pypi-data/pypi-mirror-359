import pytest
from hybrid_fuzzy_matcher import HybridFuzzyMatcher

@pytest.fixture
def matcher():
    """Provides a HybridFuzzyMatcher instance for testing."""
    return HybridFuzzyMatcher()

def test_initialization(matcher):
    """Tests if the matcher initializes correctly."""
    assert matcher.syntactic_weight == 0.3
    assert matcher.semantic_weight == 0.7
    assert matcher.corpus == []

def test_add_data(matcher):
    """Tests adding data to the corpus."""
    data = ["test string 1", "test string 2"]
    matcher.add_data(data)
    assert len(matcher.corpus) == 2
    assert len(matcher.preprocessed_corpus) == 2
    assert matcher.corpus_embeddings is not None

def test_find_matches(matcher):
    """Tests the find_matches functionality."""
    data = ["apple iphone 13", "samsung galaxy s22"]
    matcher.add_data(data)
    matches = matcher.find_matches("iphone 13 pro")
    assert len(matches) > 0
    assert matches[0]["original_text"] == "apple iphone 13"

def test_find_duplicates(matcher):
    """Tests the find_duplicates functionality."""
    data = ["dr john smith", "doctor john smith", "jane doe"]
    matcher.add_data(data)
    duplicates = matcher.find_duplicates(min_combined_score=0.8)
    assert len(duplicates) == 1
    assert duplicates[0]["text1"] == "dr john smith"
    assert duplicates[0]["text2"] == "doctor john smith"
