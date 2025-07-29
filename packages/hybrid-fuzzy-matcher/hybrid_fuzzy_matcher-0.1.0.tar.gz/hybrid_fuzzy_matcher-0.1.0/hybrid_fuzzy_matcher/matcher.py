import re
from collections import defaultdict
import numpy as np
from thefuzz import fuzz
from thefuzz import process
from sentence_transformers import SentenceTransformer, util
import torch # Required by sentence_transformers for tensor operations

class HybridFuzzyMatcher:
    """
    A robust fuzzy string matching library that combines syntactic and semantic approaches.

    This class provides functionality to:
    1. Add a corpus of strings for matching.
    2. Find the most similar strings to a given query using a hybrid approach.
    3. Identify duplicate or highly similar pairs within the added corpus.

    The hybrid approach involves:
    - Preprocessing: Standardizing text (lowercasing, punctuation removal, optional abbreviation mapping).
    - Blocking: Reducing the search space using fast, simple key generation.
    - Syntactic Matching: Using fuzz.WRatio and fuzz.token_sort_ratio for character-level similarity.
    - Semantic Matching: Using Sentence-BERT embeddings for contextual and meaning-based similarity.
    - Score Combination: A weighted average of syntactic and semantic scores.
    """

    def __init__(self,
                 semantic_model_name: str = 'all-MiniLM-L6-v2',
                 syntactic_weight: float = 0.3,
                 semantic_weight: float = 0.7,
                 syntactic_threshold: int = 60,
                 semantic_threshold: float = 0.5,
                 combined_threshold: float = 0.75,
                 abbreviation_map: dict = None):
        """
        Initializes the HybridFuzzyMatcher.

        Args:
            semantic_model_name (str): Name of the Sentence-BERT model to use.
                                       'all-MiniLM-L6-v2' is a good default.
                                       See https://www.sbert.net/docs/pretrained_models.html
            syntactic_weight (float): Weight for the syntactic similarity score (0.0 to 1.0).
            semantic_weight (float): Weight for the semantic similarity score (0.0 to 1.0).
                                     (syntactic_weight + semantic_weight should ideally be 1.0)
            syntactic_threshold (int): Minimum syntactic score (0-100) for a candidate to be considered.
            semantic_threshold (float): Minimum semantic score (0.0-1.0) for a candidate to be considered.
            combined_threshold (float): Minimum combined score (0.0-1.0) for a result to be returned.
            abbreviation_map (dict, optional): A dictionary for custom abbreviation/synonym mapping.
                                               e.g., {"dr.": "doctor", "st.": "street"}. Defaults to None.
        """
        if not (0 <= syntactic_weight <= 1 and 0 <= semantic_weight <= 1 and
                abs(syntactic_weight + semantic_weight - 1.0) < 1e-6):
            raise ValueError("Syntactic and semantic weights must be between 0 and 1 and sum to 1.")

        self.semantic_model_name = semantic_model_name
        self.syntactic_weight = syntactic_weight
        self.semantic_weight = semantic_weight
        self.syntactic_threshold = syntactic_threshold
        self.semantic_threshold = semantic_threshold
        self.combined_threshold = combined_threshold
        self.abbreviation_map = abbreviation_map if abbreviation_map is not None else {}

        self.corpus = []  # Stores original strings
        self.preprocessed_corpus = []  # Stores preprocessed strings
        self.corpus_embeddings = None  # Stores semantic embeddings (torch.Tensor)
        self.blocking_map = defaultdict(list) # Maps blocking keys to list of corpus indices

        self.model = self._load_semantic_model()
        print(f"HybridFuzzyMatcher initialized with model: {self.semantic_model_name}")

    def _load_semantic_model(self):
        """Loads the pre-trained Sentence-BERT model."""
        try:
            return SentenceTransformer(self.semantic_model_name)
        except Exception as e:
            print(f"Error loading semantic model {self.semantic_model_name}: {e}")
            print("Please ensure you have an active internet connection or the model is cached.")
            raise

    def _preprocess_text(self, text: str) -> str:
        """
        Applies standard text preprocessing steps.

        Args:
            text (str): The input string.

        Returns:
            str: The preprocessed string.
        """
        text = text.lower()
        # Replace common abbreviations/synonyms based on the map
        for abbr, full in self.abbreviation_map.items():
            text = text.replace(abbr, full)

        # Remove punctuation (keeping spaces)
        text = re.sub(r'[^\w\s]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _generate_blocking_keys(self, text: str) -> list[str]:
        """
        Generates simple blocking keys for a given text.
        This helps in reducing the number of comparisons.

        Args:
            text (str): The preprocessed text.

        Returns:
            list[str]: A list of blocking keys.
        """
        keys = []
        words = text.split()

        if len(words) > 0:
            # Key 1: First 3 characters of the first word
            if len(words[0]) >= 3:
                keys.append(words[0][:3])
            else:
                keys.append(words[0]) # Use the whole word if shorter

            # Key 2: First 3 characters of the last word (if different from first)
            if len(words) > 1 and words[0] != words[-1]:
                if len(words[-1]) >= 3:
                    keys.append(words[-1][:3])
                else:
                    keys.append(words[-1])

            # Key 3: A sorted token key (useful for reordered words)
            sorted_tokens = " ".join(sorted(words))
            if len(sorted_tokens) > 0:
                keys.append(sorted_tokens)

        # Add the full preprocessed text as a blocking key for exact match potential
        keys.append(text)

        return list(set(keys)) # Return unique keys

    def add_data(self, data_list: list[str]):
        """
        Adds a list of strings to the matcher's internal corpus.
        This also preprocesses the data, generates blocking keys, and computes embeddings.

        Args:
            data_list (list[str]): A list of strings to add to the corpus.
        """
        new_preprocessed_texts = []
        start_idx = len(self.corpus)

        for i, item in enumerate(data_list):
            self.corpus.append(item)
            preprocessed_item = self._preprocess_text(item)
            self.preprocessed_corpus.append(preprocessed_item)
            
            # Generate blocking keys for the current item and add to map
            index = start_idx + i
            for key in self._generate_blocking_keys(preprocessed_item):
                self.blocking_map[key].append(index)
            
            new_preprocessed_texts.append(preprocessed_item)

        # Generate embeddings for the new data
        if new_preprocessed_texts:
            print(f"Generating embeddings for {len(new_preprocessed_texts)} new items...")
            new_embeddings = self.model.encode(new_preprocessed_texts, convert_to_tensor=True)
            if self.corpus_embeddings is None:
                self.corpus_embeddings = new_embeddings
            else:
                self.corpus_embeddings = torch.cat((self.corpus_embeddings, new_embeddings), dim=0)
            print("Embeddings generation complete.")
        else:
            print("No new data to add.")

    def find_matches(self, query_string: str, top_n: int = 5) -> list[dict]:
        """
        Finds the top_n most similar strings to the query string from the corpus.

        Args:
            query_string (str): The string to find matches for.
            top_n (int): The number of top matches to return.

        Returns:
            list[dict]: A list of dictionaries, each containing 'original_text',
                        'preprocessed_text', and 'combined_score'.
        """
        if not self.corpus:
            print("Corpus is empty. Add data using add_data() first.")
            return []

        preprocessed_query = self._preprocess_text(query_string)
        query_embedding = self.model.encode(preprocessed_query, convert_to_tensor=True)

        # Stage 2: Blocking - Get potential candidates
        candidate_indices = set()
        for key in self._generate_blocking_keys(preprocessed_query):
            candidate_indices.update(self.blocking_map[key])

        if not candidate_indices:
            print(f"No candidates found via blocking for query: '{query_string}'")
            return []

        results = []
        for idx in candidate_indices:
            candidate_original = self.corpus[idx]
            candidate_preprocessed = self.preprocessed_corpus[idx]
            candidate_embedding = self.corpus_embeddings[idx]

            # Stage 3: Syntactic Scoring
            syntactic_score_wratio = fuzz.WRatio(preprocessed_query, candidate_preprocessed)
            syntactic_score_token_sort = fuzz.token_sort_ratio(preprocessed_query, candidate_preprocessed)
            syntactic_score = max(syntactic_score_wratio, syntactic_score_token_sort)

            if syntactic_score < self.syntactic_threshold:
                continue # Skip if syntactic similarity is too low

            # Stage 4: Semantic Scoring
            semantic_score = util.cos_sim(query_embedding, candidate_embedding).item()

            if semantic_score < self.semantic_threshold:
                continue # Skip if semantic similarity is too low

            # Stage 5: Combine Scores
            combined_score = (self.syntactic_weight * (syntactic_score / 100.0)) + \
                             (self.semantic_weight * semantic_score)

            if combined_score >= self.combined_threshold:
                results.append({
                    "original_text": candidate_original,
                    "preprocessed_text": candidate_preprocessed,
                    "syntactic_score": syntactic_score,
                    "semantic_score": semantic_score,
                    "combined_score": combined_score
                })

        # Sort results by combined score in descending order
        results.sort(key=lambda x: x["combined_score"], reverse=True)

        return results[:top_n]

    def find_duplicates(self, min_combined_score: float = None) -> list[dict]:
        """
        Identifies duplicate or highly similar pairs within the added corpus.
        This method is computationally intensive for very large corpora without strong blocking.

        Args:
            min_combined_score (float, optional): The minimum combined score for a pair to be considered a duplicate.
                                                  Defaults to the object's combined_threshold.

        Returns:
            list[dict]: A list of dictionaries, each representing a duplicate pair,
                        containing 'text1', 'text2', and 'combined_score'.
        """
        if not self.corpus or self.corpus_embeddings is None:
            print("Corpus is empty or embeddings not generated. Add data using add_data() first.")
            return []

        if min_combined_score is None:
            min_combined_score = self.combined_threshold

        duplicate_pairs = []
        processed_pairs = set() # To avoid duplicate (A, B) and (B, A) and self-comparison

        print("Starting duplicate detection. This may take a while for large datasets...")

        # Iterate through unique blocking keys to get candidate groups
        for key, indices in self.blocking_map.items():
            if len(indices) < 2: # No pairs to compare in this block
                continue

            # Compare all pairs within this block
            for i in range(len(indices)):
                idx1 = indices[i]
                for j in range(i + 1, len(indices)): # Avoid self-comparison and duplicate pairs
                    idx2 = indices[j]

                    # Ensure the pair hasn't been processed from another block
                    pair_key = tuple(sorted((idx1, idx2)))
                    if pair_key in processed_pairs:
                        continue
                    processed_pairs.add(pair_key)

                    text1_original = self.corpus[idx1]
                    text2_original = self.corpus[idx2]
                    text1_preprocessed = self.preprocessed_corpus[idx1]
                    text2_preprocessed = self.preprocessed_corpus[idx2]
                    embedding1 = self.corpus_embeddings[idx1]
                    embedding2 = self.corpus_embeddings[idx2]

                    # Stage 3: Syntactic Scoring
                    syntactic_score_wratio = fuzz.WRatio(text1_preprocessed, text2_preprocessed)
                    syntactic_score_token_sort = fuzz.token_sort_ratio(text1_preprocessed, text2_preprocessed)
                    syntactic_score = max(syntactic_score_wratio, syntactic_score_token_sort)

                    if syntactic_score < self.syntactic_threshold:
                        continue

                    # Stage 4: Semantic Scoring
                    semantic_score = util.cos_sim(embedding1, embedding2).item()

                    if semantic_score < self.semantic_threshold:
                        continue

                    # Stage 5: Combine Scores
                    combined_score = (self.syntactic_weight * (syntactic_score / 100.0)) + \
                                     (self.semantic_weight * semantic_score)

                    if combined_score >= min_combined_score:
                        duplicate_pairs.append({
                            "text1": text1_original,
                            "text2": text2_original,
                            "syntactic_score": syntactic_score,
                            "semantic_score": semantic_score,
                            "combined_score": combined_score
                        })
        
        duplicate_pairs.sort(key=lambda x: x["combined_score"], reverse=True)
        print(f"Duplicate detection complete. Found {len(duplicate_pairs)} pairs.")
        return duplicate_pairs
