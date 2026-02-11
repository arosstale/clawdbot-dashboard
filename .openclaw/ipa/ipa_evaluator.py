"""
IPA (Interaction-Perceptive Agentic Policy Optimization) Style Evaluator.

Implements IPA's key innovation: credit assignment over semantic interaction chunks
rather than individual tokens. Provides better long-horizon training stability.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from observational_memory import ObservationalMemory, ObservationConfig
except ImportError:
    # Fallback
    ObservationalMemory = None


@dataclass
class InteractionChunk:
    """A semantic chunk of interactions."""
    chunk_id: str
    start_idx: int
    end_idx: int
    messages: List[Dict]
    semantic_type: str  # 'question', 'explanation', 'correction', 'task'
    importance: float  # 0-1, how critical this chunk is
    timestamp: datetime


@dataclass
class ChunkEvaluationResult:
    """Result of evaluating a chunk."""
    chunk_id: str
    credit_assigned: float  # How much credit for overall performance
    reconstruction_quality: float  # How well memory reconstructed the chunk
    temporal_relevance: float  # How relevant this chunk is to recent context
    overall_score: float


class InteractionChunker:
    """
    Groups messages into semantic interaction chunks.

    Inspired by IPA: Assigns credit over interaction chunks for better
    long-horizon training stability.
    """

    def __init__(
        self,
        min_chunk_size: int = 3,
        max_chunk_size: int = 10,
        semantic_patterns: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize chunker.

        Args:
            min_chunk_size: Minimum messages per chunk
            max_chunk_size: Maximum messages per chunk
            semantic_patterns: Patterns for identifying chunk types
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

        if semantic_patterns is None:
            self.semantic_patterns = {
                "question": ["?", "how", "what", "why", "can you", "help"],
                "explanation": ["because", "since", "the reason", "as a result"],
                "correction": ["no", "actually", "that's wrong", "not exactly"],
                "task": ["do this", "create", "write", "build", "implement"],
            }
        else:
            self.semantic_patterns = semantic_patterns

    def chunk(self, messages: List[Dict], thread_id: str = "default") -> List[InteractionChunk]:
        """
        Chunk messages into semantic interaction units.

        Args:
            messages: List of message dicts
            thread_id: Thread identifier

        Returns:
            List of InteractionChunk objects
        """
        chunks = []
        i = 0

        while i < len(messages):
            # Determine chunk size
            chunk_size = self._determine_chunk_size(messages, i)

            # Extract chunk messages
            chunk_messages = messages[i:i + chunk_size]

            # Determine semantic type
            semantic_type = self._classify_semantic_type(chunk_messages)

            # Calculate importance (more recent = more important)
            importance = self._calculate_importance(i, len(messages))

            # Create chunk
            chunk = InteractionChunk(
                chunk_id=f"{thread_id}_chunk_{len(chunks)}",
                start_idx=i,
                end_idx=i + chunk_size,
                messages=chunk_messages,
                semantic_type=semantic_type,
                importance=importance,
                timestamp=datetime.now(),
            )

            chunks.append(chunk)
            i += chunk_size

        return chunks

    def _determine_chunk_size(self, messages: List[Dict], start_idx: int) -> int:
        """Determine optimal chunk size starting from start_idx."""
        remaining = len(messages) - start_idx
        size = min(self.max_chunk_size, max(self.min_chunk_size, remaining))

        # Check for semantic boundaries
        if start_idx + size < len(messages):
            # Look ahead for semantic shift
            current_type = self._classify_semantic_type(messages[start_idx:start_idx + 1])

            for j in range(start_idx + 1, min(start_idx + size, len(messages))):
                next_type = self._classify_semantic_type(messages[j:j + 1])

                # If semantic type shifts, end chunk here
                if next_type != current_type:
                    size = j - start_idx
                    if size >= self.min_chunk_size:
                        break

        return size

    def _classify_semantic_type(self, messages: List[Dict]) -> str:
        """Classify the semantic type of messages."""
        if not messages:
            return "task"

        text = " ".join(str(m.get("content", "")) for m in messages).lower()

        # Score each type
        type_scores = {}
        for semantic_type, patterns in self.semantic_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            type_scores[semantic_type] = score

        # Return highest scoring type
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return "task"

    def _calculate_importance(self, idx: int, total: int) -> float:
        """Calculate importance based on recency."""
        # More recent = more important
        recency = (total - idx) / total
        return 0.5 + (recency * 0.5)  # 0.5 to 1.0


class IPAEvaluator:
    """
    IPA-style evaluator for memory systems.

    Evaluates by assigning credit over interaction chunks
    rather than individual observations.
    """

    def __init__(
        self,
        chunker: Optional[InteractionChunker] = None,
        paom: Optional[ObservationalMemory] = None
    ):
        """
        Initialize IPA evaluator.

        Args:
            chunker: Interaction chunker (creates default if None)
            paom: Observational Memory instance (optional)
        """
        self.chunker = chunker or InteractionChunker()
        self.paom = paom

    def evaluate_thread(
        self,
        messages: List[Dict],
        thread_id: str = "eval-thread"
    ) -> Tuple[List[ChunkEvaluationResult], float]:
        """
        Evaluate a thread using IPA methodology.

        Args:
            messages: Messages to evaluate
            thread_id: Thread identifier

        Returns:
            (chunk_results, overall_score)
        """
        # Chunk interactions
        chunks = self.chunker.chunk(messages, thread_id)

        # Evaluate each chunk
        chunk_results = []
        for chunk in chunks:
            result = self._evaluate_chunk(chunk, thread_id)
            chunk_results.append(result)

        # Calculate overall score (credit-weighted average)
        overall_score = self._calculate_overall_score(chunk_results, chunks)

        return chunk_results, overall_score

    def _evaluate_chunk(
        self,
        chunk: InteractionChunk,
        thread_id: str
    ) -> ChunkEvaluationResult:
        """Evaluate a single chunk."""
        # Get PAOM context for this chunk
        reconstruction_quality = self._measure_reconstruction_quality(chunk, thread_id)

        # Measure temporal relevance
        temporal_relevance = self._measure_temporal_relevance(chunk)

        # Assign credit based on chunk importance and performance
        credit_assigned = chunk.importance * reconstruction_quality

        # Calculate overall score
        overall_score = (
            credit_assigned * 0.5 +
            temporal_relevance * 0.3 +
            reconstruction_quality * 0.2
        )

        return ChunkEvaluationResult(
            chunk_id=chunk.chunk_id,
            credit_assigned=credit_assigned,
            reconstruction_quality=reconstruction_quality,
            temporal_relevance=temporal_relevance,
            overall_score=overall_score,
        )

    def _measure_reconstruction_quality(
        self,
        chunk: InteractionChunk,
        thread_id: str
    ) -> float:
        """
        Measure how well PAOM reconstructed this chunk.

        In a real implementation, this would compare PAOM's compressed
        context against the original chunk to measure reconstruction accuracy.
        """
        if not self.paom:
            # Mock implementation
            return 0.85 + (chunk.importance * 0.1)

        # Get PAOM context for this thread
        paom_context = self.paom.get_context(thread_id)

        # Extract chunk content
        chunk_text = " ".join(str(m.get("content", "")) for m in chunk.messages)

        # Measure reconstruction (simplified)
        # In production, use semantic similarity or LLM-based comparison
        if chunk_text in paom_context:
            return 1.0
        else:
            # Check for partial matches
            chunk_words = set(chunk_text.lower().split())
            context_words = set(paom_context.lower().split())

            overlap = len(chunk_words & context_words) / max(len(chunk_words), 1)
            return overlap * 0.9

    def _measure_temporal_relevance(self, chunk: InteractionChunk) -> float:
        """
        Measure how temporally relevant this chunk is.

        Questions from earlier are less relevant than recent task executions.
        """
        # Temporal types (ordered by relevance)
        type_relevance = {
            "task": 1.0,        # Most relevant: actual task execution
            "correction": 0.9,   # High: corrections imply recent activity
            "explanation": 0.7,   # Medium: context setting
            "question": 0.5,       # Lower: earlier questions
        }

        return type_relevance.get(chunk.semantic_type, 0.7)

    def _calculate_overall_score(
        self,
        chunk_results: List[ChunkEvaluationResult],
        chunks: List[InteractionChunk]
    ) -> float:
        """
        Calculate overall score using IPA credit assignment.

        Credit is assigned over chunks, not individual tokens.
        """
        if not chunk_results:
            return 0.0

        # Credit-weighted average
        total_credit = sum(r.credit_assigned for r in chunk_results)
        total_importance = sum(c.importance for c in chunks)

        if total_importance > 0:
            return (total_credit / total_importance) * 100.0
        return 0.0


def example_ipa_evaluation():
    """Example of IPA-style evaluation."""
    print("🐺📿 IPA (Interaction-Perceptive) Evaluation Example")
    print("=" * 60)

    # Sample messages
    messages = [
        {"role": "user", "content": "Can you help me with Python?", "timestamp": datetime.now()},
        {"role": "assistant", "content": "Sure, what do you need?", "timestamp": datetime.now()},
        {"role": "user", "content": "Write a function to sort a list", "timestamp": datetime.now()},
        {"role": "assistant", "content": "Here's a sorting function...", "timestamp": datetime.now()},
        {"role": "user", "content": "Great! Can you explain how it works?", "timestamp": datetime.now()},
        {"role": "assistant", "content": "The algorithm works by...", "timestamp": datetime.now()},
        {"role": "user", "content": "Actually, I think it should be different", "timestamp": datetime.now()},
        {"role": "assistant", "content": "You're right, here's the corrected version", "timestamp": datetime.now()},
    ]

    # Create evaluator
    evaluator = IPAEvaluator()

    # Evaluate
    chunk_results, overall_score = evaluator.evaluate_thread(messages, "example-thread")

    # Print results
    print(f"\\n📊 Chunk Evaluation Results:")
    print(f"   Number of chunks: {len(chunk_results)}")
    print(f"   Overall IPA Score: {overall_score:.2f}")

    print(f"\\n   Top Chunks:")
    sorted_results = sorted(chunk_results, key=lambda r: r.overall_score, reverse=True)
    for result in sorted_results[:3]:
        print(f"   {result.chunk_id}: {result.overall_score:.2f} (credit: {result.credit_assigned:.2f})")

    print("\\n✅ IPA evaluation example complete")


if __name__ == "__main__":
    example_ipa_evaluation()
