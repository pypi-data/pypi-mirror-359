# Hybrid Fuzzy Matcher

A robust fuzzy string matching library that combines syntactic (character-based) and semantic (meaning-based) approaches to provide more accurate and context-aware matching.

This package is ideal for tasks like data cleaning, record linkage, and duplicate detection where simple fuzzy matching isn't enough. It leverages `thefuzz` for syntactic analysis and `sentence-transformers` for semantic similarity.

## Key Features

- **Hybrid Scoring:** Combines `fuzz.WRatio` and `fuzz.token_sort_ratio` with cosine similarity from sentence embeddings.
- **Configurable:** Easily tune weights and thresholds for syntactic and semantic scores to fit your specific data.
- **Preprocessing:** Includes text normalization, punctuation removal, and a customizable abbreviation/synonym map.
- **Efficient Blocking:** Uses a blocking strategy to reduce the search space and improve performance on larger datasets.
- **Easy to Use:** A simple, intuitive API for adding data, finding matches, and detecting duplicates.

## Installation

You can install the package via pip:

```bash
pip install hybrid-fuzzy-matcher
```

## How to Use

Here is a complete example of how to use the `HybridFuzzyMatcher`.

### 1. Initialize the Matcher

First, create an instance of the `HybridFuzzyMatcher`. You can optionally provide a custom abbreviation map and adjust the weights and thresholds.

```python
from hybrid_fuzzy_matcher import HybridFuzzyMatcher

# Custom abbreviation map (optional)
custom_abbr_map = {
    "dr.": "doctor",
    "st.": "street",
    "co.": "company",
    "inc.": "incorporated",
    "ny": "new york",
    "usa": "united states of america",
}

# Initialize the matcher
matcher = HybridFuzzyMatcher(
    syntactic_weight=0.4,
    semantic_weight=0.6,
    syntactic_threshold=70,
    semantic_threshold=0.6,
    combined_threshold=0.75,
    abbreviation_map=custom_abbr_map
)
```

### 2. Add Data

Add the list of strings you want to match against. The matcher will automatically preprocess the text and generate the necessary embeddings.

```python
data_corpus = [
    "Apple iPhone 13 Pro Max, 256GB, Sierra Blue",
    "iPhone 13 Pro Max 256 GB, Blue, Apple Brand",
    "Samsung Galaxy S22 Ultra 512GB Phantom Black",
    "Apple iPhone 12 Mini, 64GB, Red",
    "Dr. John Smith, PhD",
    "Doctor John Smith",
    "New York City Department of Parks and Recreation",
    "NYC Dept. of Parks & Rec",
]

# Add data to the matcher
matcher.add_data(data_corpus)
```

### 3. Find Matches for a Query

Use the `find_matches` method to find the most similar strings in the corpus for a given query.

```python
query = "iPhone 13 Pro Max, 256GB, Blue"
matches = matcher.find_matches(query, top_n=3)

print(f"Query: '{query}'")
for match in matches:
    print(f"  Match: '{match['original_text']}'")
    print(f"    Scores: Syntactic={match['syntactic_score']:.2f}, "
          f"Semantic={match['semantic_score']:.4f}, Combined={match['combined_score']:.4f}")

# Query: 'iPhone 13 Pro Max, 256GB, Blue'
#   Match: 'Apple iPhone 13 Pro Max, 256GB, Sierra Blue'
#     Scores: Syntactic=95.00, Semantic=0.9801, Combined=0.9681
#   Match: 'iPhone 13 Pro Max 256 GB, Blue, Apple Brand'
#     Scores: Syntactic=95.00, Semantic=0.9734, Combined=0.9640
```

### 4. Find Duplicates in the Corpus

Use the `find_duplicates` method to identify highly similar pairs within the entire corpus.

```python
duplicates = matcher.find_duplicates(min_combined_score=0.8)

print("\n--- Finding Duplicate Pairs ---")
for pair in duplicates:
    print(f"\nDuplicate Pair (Score: {pair['combined_score']:.4f}):")
    print(f"  Text 1: '{pair['text1']}'")
    print(f"  Text 2: '{pair['text2']}'")

# --- Finding Duplicate Pairs ---
#
# Duplicate Pair (Score: 0.9933):
#   Text 1: 'Dr. John Smith, PhD'
#   Text 2: 'Doctor John Smith'
```

## How It Works

The matching process follows these steps:

1.  **Preprocessing:** Text is lowercased, punctuation is removed, and custom abbreviations are expanded.
2.  **Blocking:** To avoid comparing every string to every other string, candidate pairs are generated based on simple keys (like the first few letters of words). This dramatically speeds up the process.
3.  **Syntactic Scoring:** Candidates are scored using `thefuzz`'s `WRatio` and `token_sort_ratio`. This catches character-level similarities and typos.
4.  **Semantic Scoring:** The pre-trained `sentence-transformers` model (`all-MiniLM-L6-v2` by default) converts strings into vector embeddings. The cosine similarity between these embeddings measures how close they are in meaning.
5.  **Score Combination:** The final score is a weighted average of the syntactic and semantic scores. This hybrid score provides a more holistic measure of similarity.

This approach ensures that the matcher can identify similarities even when the wording is different but the meaning is the same.
