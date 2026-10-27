"""
TED Talks Information Retrieval System
INT309 Multimedia Information Retrieval and Technology - Assignment 2

=== KEY INFORMATION RETRIEVAL CONCEPTS IMPLEMENTED ===

[Query Processing] - Text preprocessing, cleaning, and normalization
    - Lowercasing, special character removal
    - Applied to both documents and queries

[Vocabulary] - Term vocabulary construction and management
    - Extracted from document collection
    - Unigram and bigram features
    - Stop word filtering
    - Frequency-based filtering (min_df, max_df)

[Index Construction] - Building inverted index structure
    - Document-term matrix construction
    - Efficient sparse matrix representation

[Weighting] - TF-IDF term weighting scheme
    - Term Frequency (TF): Importance of term in document
    - Inverse Document Frequency (IDF): Rarity of term across collection
    - Applied to both documents and queries

[Evaluation] - Retrieval performance and ranking
    - Cosine similarity for relevance scoring
    - Top-k result ranking
    - Content-based recommendation
    - System performance metrics
"""

import pandas as pd
import numpy as np
import re
import json
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class TEDRetrievalSystem:
    """TED Talks Information Retrieval System"""
    
    def __init__(self, dataset_path):
        """Initialize system and load data"""
        print("Loading dataset...")
        self.df = pd.read_csv(dataset_path)
        self.original_df = self.df.copy()
        
        # Data preprocessing
        self._preprocess_data()
        
        # Build index
        self._build_index()
        
        print(f"System initialized! Loaded {len(self.df)} talks")
    
    def _preprocess_data(self):
        """
        Data preprocessing and cleaning
        
        [Query Processing] - Text preprocessing and normalization
        """
        print("Preprocessing data...")
        
        # Handle missing values
        self.df['description'] = self.df['description'].fillna('')
        self.df['title'] = self.df['title'].fillna('')
        self.df['tags'] = self.df['tags'].fillna('[]')
        
        # Merge text fields to create document content
        self.df['document'] = (
            self.df['title'] + ' ' + 
            self.df['description'] + ' ' + 
            self.df['tags'].apply(self._extract_tags)
        )
        
        # [Query Processing] - Text cleaning and normalization
        self.df['document_clean'] = self.df['document'].apply(self._clean_text)
        
        print("Data preprocessing completed")
    
    def _extract_tags(self, tags_str):
        """Extract tags from tag string"""
        try:
            tags = eval(tags_str)
            if isinstance(tags, list):
                return ' '.join(tags)
        except:
            pass
        return ''
    
    def _clean_text(self, text):
        """Clean text: convert to lowercase, remove special characters"""
        text = text.lower()
        # Keep only letters, numbers and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _build_index(self):
        """
        Build TF-IDF index
        
        [Index Construction] - Building inverted index with TF-IDF weighting
        [Vocabulary] - Creating vocabulary from document collection
        [Weighting] - TF-IDF term weighting scheme
        """
        print("Building TF-IDF index...")
        
        # [Vocabulary] - Extract vocabulary with stop words removal
        # [Weighting] - TF-IDF vectorization with term frequency and inverse document frequency
        self.vectorizer = TfidfVectorizer(
            max_features=5000,  # [Vocabulary] - Limit vocabulary size to top 5000 terms
            stop_words='english',  # [Vocabulary] - Remove common stop words from vocabulary
            ngram_range=(1, 2),  # [Vocabulary] - Use unigram and bigram features
            min_df=2,  # [Vocabulary] - Minimum document frequency threshold
            max_df=0.8  # [Vocabulary] - Maximum document frequency threshold
        )
        
        # [Index Construction] - Build document-term matrix with TF-IDF weights
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['document_clean'])
        
        print(f"Index built! Vocabulary size: {len(self.vectorizer.vocabulary_)}")
    
    def search(self, query, top_k=10):
        """
        Text query search
        
        [Query Processing] - Process and execute search query
        [Weighting] - Apply TF-IDF weighting to query terms
        [Evaluation] - Rank documents by relevance score (cosine similarity scoring)

        Scoring (relevance score) explanation:
        - Represent both query and documents as TF-IDF vectors in the same feature space
        - Use cosine similarity to measure the angle between query vector q and document vector d
        - cos_sim(q, d) = (q · d) / (||q|| * ||d||), with values in [0, 1]
        - A higher score means the document is more relevant to the query; results are sorted
          by score in descending order and the top_k documents are returned
        
        Args:
            query: Query string
            top_k: Return top k results
        
        Returns:
            List of retrieval results
        """
        # [Query Processing] - Clean and normalize query text
        query_clean = self._clean_text(query)
        
        # [Weighting] - Convert query to TF-IDF vector using same vocabulary
        query_vector = self.vectorizer.transform([query_clean])
        
        # [Evaluation] - Calculate cosine similarity between query and all documents
        # scoring: similarities[i] is the relevance score (cosine similarity) of document i
        # with respect to the current query
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # [Evaluation] - Get top-k results sorted by similarity score
        # argsort() gives indices from lowest to highest similarity;
        # we take the last top_k indices and reverse to get scores from high to low
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # [Evaluation] - Build ranked results list
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only return results with similarity > 0
                results.append({
                    'rank': len(results) + 1,
                    'title': self.df.iloc[idx]['title'],
                    'speaker': self.df.iloc[idx]['main_speaker'],
                    'description': self.df.iloc[idx]['description'][:200] + '...',
                    'views': self.df.iloc[idx]['views'],
                    'duration': self.df.iloc[idx]['duration'],
                    'url': self.df.iloc[idx]['url'],
                    'score': float(similarities[idx]),
                    'index': int(idx)
                })
        
        return results
    
    def find_similar_talks(self, talk_index, top_k=5):
        """
        Find similar talks
        
        [Evaluation] - Content-based similarity recommendation
        [Weighting] - Use TF-IDF weighted vectors for comparison
        
        Scoring (similarity score) explanation:
        - Use the same TF-IDF feature space as in text search
        - Fix one base talk vector and compute its cosine similarity with all other talk vectors
        - similarity[i] is the content similarity between talk i and the base talk
        - The more similar two talks are, the closer the cosine similarity is to 1;
          talks are ranked by similarity score in descending order to form the recommendation list
        
        Args:
            talk_index: Index of talk in dataset
            top_k: Return top k similar talks
        
        Returns:
            List of similar talks
        """
        # [Weighting] - Get TF-IDF vector of this talk
        talk_vector = self.tfidf_matrix[talk_index]
        
        # [Evaluation] - Calculate similarity with all talks using cosine similarity
        # scoring: similarities[i] is the recommendation score of talk i relative
        # to the current base talk
        similarities = cosine_similarity(talk_vector, self.tfidf_matrix).flatten()
        
        # [Evaluation] - Exclude itself, get top-k most similar talks
        similarities[talk_index] = -1
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # [Evaluation] - Build ranked results list
        results = []
        for idx in top_indices:
            results.append({
                'rank': len(results) + 1,
                'title': self.df.iloc[idx]['title'],
                'speaker': self.df.iloc[idx]['main_speaker'],
                'description': self.df.iloc[idx]['description'][:200] + '...',
                'similarity': float(similarities[idx]),
                'index': int(idx)
            })
        
        return results
    
    def get_dataset_statistics(self):
        """Get dataset statistics"""
        stats = {
            'total_talks': len(self.df),
            'avg_duration': self.df['duration'].mean() / 60,  # Convert to minutes
            'total_views': self.df['views'].sum(),
            'avg_views': self.df['views'].mean(),
            'unique_speakers': self.df['main_speaker'].nunique(),
            'vocabulary_size': len(self.vectorizer.vocabulary_),
            'avg_document_length': self.df['document_clean'].str.split().str.len().mean()
        }
        return stats
    
    def evaluate_retrieval(self, test_queries):
        """
        Evaluate retrieval performance
        
        [Evaluation] - System performance evaluation with test queries
        
        Args:
            test_queries: List of test queries
        
        Returns:
            Evaluation metrics
        """
        results = []
        for query in test_queries:
            # [Evaluation] - Execute search and collect results
            search_results = self.search(query, top_k=10)
            # [Evaluation] - Calculate evaluation metrics (number of results, average score)
            results.append({
                'query': query,
                'num_results': len(search_results),
                'avg_score': np.mean([r['score'] for r in search_results]) if search_results else 0,
                'results': search_results
            })
        return results


class ResultVisualizer:
    """Result visualization class"""
    
    def __init__(self, retrieval_system):
        self.system = retrieval_system
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_dataset_overview(self, save_path='dataset_overview.png'):
        """Plot dataset overview"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Talk duration distribution
        durations = self.system.df['duration'] / 60  # Convert to minutes
        axes[0, 0].hist(durations, bins=50, color='skyblue', edgecolor='black')
        axes[0, 0].set_xlabel('Duration (minutes)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Distribution of Talk Durations')
        axes[0, 0].axvline(durations.mean(), color='red', linestyle='--', 
                           label=f'Mean: {durations.mean():.1f} min')
        axes[0, 0].legend()
        
        # 2. Views distribution (log scale)
        views = self.system.df['views']
        axes[0, 1].hist(np.log10(views + 1), bins=50, color='lightcoral', edgecolor='black')
        axes[0, 1].set_xlabel('Log10(Views)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Distribution of Views (Log Scale)')
        
        # 3. Top 10 speakers
        top_speakers = self.system.df['main_speaker'].value_counts().head(10)
        axes[1, 0].barh(range(len(top_speakers)), top_speakers.values, color='lightgreen')
        axes[1, 0].set_yticks(range(len(top_speakers)))
        axes[1, 0].set_yticklabels(top_speakers.index)
        axes[1, 0].set_xlabel('Number of Talks')
        axes[1, 0].set_title('Top 10 Speakers by Number of Talks')
        axes[1, 0].invert_yaxis()
        
        # 4. Dataset statistics summary
        stats = self.system.get_dataset_statistics()
        stats_text = f"""
        Dataset Statistics:
        
        Total Talks: {stats['total_talks']:,}
        Unique Speakers: {stats['unique_speakers']:,}
        
        Average Duration: {stats['avg_duration']:.1f} minutes
        Total Views: {stats['total_views']:,}
        Average Views: {stats['avg_views']:,.0f}
        
        Vocabulary Size: {stats['vocabulary_size']:,}
        Avg Document Length: {stats['avg_document_length']:.0f} words
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, 
                        verticalalignment='center', family='monospace')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Dataset overview saved to: {save_path}")
        plt.close()
    
    def plot_search_results(self, query, results, save_path=None):
        """Visualize search results"""
        if not results:
            print("No search results to visualize")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. Similarity scores
        ranks = [r['rank'] for r in results]
        scores = [r['score'] for r in results]
        
        ax1.bar(ranks, scores, color='steelblue', edgecolor='black')
        ax1.set_xlabel('Rank')
        ax1.set_ylabel('Similarity Score')
        ax1.set_title(f'Search Results for: "{query}"')
        ax1.set_xticks(ranks)
        
        # 2. Views comparison
        views = [r['views'] for r in results]
        titles = [r['title'][:30] + '...' if len(r['title']) > 30 else r['title'] 
                  for r in results]
        
        ax2.barh(range(len(results)), views, color='coral', edgecolor='black')
        ax2.set_yticks(range(len(results)))
        ax2.set_yticklabels([f"{i+1}. {t}" for i, t in enumerate(titles)], fontsize=8)
        ax2.set_xlabel('Views')
        ax2.set_title('Views of Retrieved Talks')
        ax2.invert_yaxis()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Search results saved to: {save_path}")
        else:
            plt.savefig(f'search_results_{query[:20]}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_evaluation_results(self, eval_results, save_path='evaluation_results.png'):
        """Visualize evaluation results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        queries = [r['query'] for r in eval_results]
        num_results = [r['num_results'] for r in eval_results]
        avg_scores = [r['avg_score'] for r in eval_results]
        
        # 1. Number of results per query
        axes[0, 0].bar(range(len(queries)), num_results, color='skyblue', edgecolor='black')
        axes[0, 0].set_xlabel('Query Index')
        axes[0, 0].set_ylabel('Number of Results')
        axes[0, 0].set_title('Number of Results per Query')
        axes[0, 0].set_xticks(range(len(queries)))
        
        # 2. Average similarity scores
        axes[0, 1].bar(range(len(queries)), avg_scores, color='lightcoral', edgecolor='black')
        axes[0, 1].set_xlabel('Query Index')
        axes[0, 1].set_ylabel('Average Similarity Score')
        axes[0, 1].set_title('Average Similarity Score per Query')
        axes[0, 1].set_xticks(range(len(queries)))
        
        # 3. Query list
        query_text = "Test Queries:\n\n" + "\n".join([f"{i+1}. {q}" for i, q in enumerate(queries)])
        axes[1, 0].text(0.1, 0.5, query_text, fontsize=10, 
                        verticalalignment='center', family='monospace')
        axes[1, 0].axis('off')
        
        # 4. Overall statistics
        stats_text = f"""
        Evaluation Summary:
        
        Total Queries: {len(queries)}
        Avg Results per Query: {np.mean(num_results):.1f}
        Avg Similarity Score: {np.mean(avg_scores):.4f}
        
        Min Results: {min(num_results)}
        Max Results: {max(num_results)}
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, 
                        verticalalignment='center', family='monospace')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Evaluation results saved to: {save_path}")
        plt.close()


def main():
    """Main function: demonstrate system functionality"""
    print("=" * 80)
    print("TED Talks Information Retrieval System")
    print("INT309 Multimedia Information Retrieval and Technology - Assignment 2")
    print("=" * 80)
    print()
    
    # 1. Initialize system
    system = TEDRetrievalSystem('dataset.csv')
    visualizer = ResultVisualizer(system)
    
    print("\n" + "=" * 80)
    print("1. Dataset Analysis")
    print("=" * 80)
    
    # Get and display statistics
    stats = system.get_dataset_statistics()
    print(f"\nDataset Statistics:")
    print(f"  - Total talks: {stats['total_talks']:,}")
    print(f"  - Unique speakers: {stats['unique_speakers']:,}")
    print(f"  - Average duration: {stats['avg_duration']:.1f} minutes")
    print(f"  - Total views: {stats['total_views']:,}")
    print(f"  - Average views: {stats['avg_views']:,.0f}")
    print(f"  - Vocabulary size: {stats['vocabulary_size']:,}")
    print(f"  - Average document length: {stats['avg_document_length']:.0f} words")
    
    # Generate dataset overview
    visualizer.plot_dataset_overview()
    
    print("\n" + "=" * 80)
    print("2. Text Query Retrieval Examples")
    print("=" * 80)
    
    # Test queries
    test_queries = [
        "education and creativity in children",
        "climate change and global warming",
        "data visualization and statistics",
        "artificial intelligence and technology",
        "design and architecture"
    ]
    
    # Perform retrieval for each query
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: \"{query}\"")
        print("-" * 80)
        
        results = system.search(query, top_k=5)
        
        if results:
            for result in results:
                print(f"\n  [{result['rank']}] {result['title']}")
                print(f"      Speaker: {result['speaker']}")
                print(f"      Similarity: {result['score']:.4f}")
                print(f"      Views: {result['views']:,}")
                print(f"      Description: {result['description']}")
        else:
            print("  No relevant results found")
        
        # Generate visualization for first query
        if i == 1:
            visualizer.plot_search_results(query, results, 
                                          save_path='search_example.png')
    
    print("\n" + "=" * 80)
    print("3. Similar Talk Recommendation Examples")
    print("=" * 80)
    
    # Select a talk for similar recommendations
    example_talk_idx = 0  # Ken Robinson's talk
    example_talk = system.df.iloc[example_talk_idx]
    
    print(f"\nBase talk: \"{example_talk['title']}\"")
    print(f"Speaker: {example_talk['main_speaker']}")
    print(f"Description: {example_talk['description'][:200]}...")
    print("\nSimilar talk recommendations:")
    print("-" * 80)
    
    similar_talks = system.find_similar_talks(example_talk_idx, top_k=5)
    
    for talk in similar_talks:
        print(f"\n  [{talk['rank']}] {talk['title']}")
        print(f"      Speaker: {talk['speaker']}")
        print(f"      Similarity: {talk['similarity']:.4f}")
        print(f"      Description: {talk['description']}")
    
    print("\n" + "=" * 80)
    print("4. System Evaluation")
    print("=" * 80)
    
    # Evaluate system performance
    eval_results = system.evaluate_retrieval(test_queries)
    
    print(f"\nEvaluation results:")
    print(f"  - Number of test queries: {len(test_queries)}")
    print(f"  - Average results per query: {np.mean([r['num_results'] for r in eval_results]):.1f}")
    print(f"  - Average similarity score: {np.mean([r['avg_score'] for r in eval_results]):.4f}")
    
    # Generate evaluation visualization
    visualizer.plot_evaluation_results(eval_results)
    
    print("\n" + "=" * 80)
    print("System demonstration completed!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - dataset_overview.png: Dataset overview")
    print("  - search_example.png: Search results example")
    print("  - evaluation_results.png: Evaluation results")
    print()


if __name__ == "__main__":
    main()
