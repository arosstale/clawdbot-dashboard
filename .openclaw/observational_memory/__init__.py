"""
OpenClaw Observational Memory (PAOM)
Based on Mastra's Observational Memory

A text-based memory system that compresses context into observations
with emoji prioritization and multi-date temporal tracking.

Inspired by Mastra: https://mastra.ai/blog/observational-memory
"""

from .observer_agent import ObserverAgent
from .reflector_agent import ReflectorAgent
from .token_counter import TokenCounter
from .types import (
    ObservationConfig,
    Observation,
    ObservationalMemoryRecord,
    PriorityLevel,
)
from typing import Dict, List, Optional, Tuple


class ObservationalMemory:
    """
    Main Observational Memory system.

    Components:
    - Observer: Extracts observations when messages exceed threshold
    - Reflector: Condenses observations when they exceed threshold
    - Actor: Sees observations + recent messages
    """

    def __init__(self, config: Optional[ObservationConfig] = None):
        """Initialize Observational Memory system."""
        from .config import default_config

        self.config = config or default_config()
        self.token_counter = TokenCounter()
        self.observer = ObserverAgent(self.config)
        self.reflector = ReflectorAgent(self.config)

    def get_observation_record(self, thread_id: str) -> Optional[ObservationalMemoryRecord]:
        """Get memory record for a thread."""
        # This would integrate with storage
        # For now, return empty record
        return None

    def process_messages(
        self,
        thread_id: str,
        messages: List[Dict],
        existing_observations: str = ""
    ) -> ObservationalMemoryRecord:
        """
        Process new messages through observational memory pipeline.

        Pipeline:
        1. Get existing memory
        2. Extract new observations
        3. Check thresholds
        4. Trigger Observer or Reflector if needed
        5. Return updated memory
        """
        # Get existing memory
        record = self.get_observation_record(thread_id)
        if record is None:
            record = ObservationalMemoryRecord(observations=[])

        # Get existing observations as text
        existing_obs_text = self._format_observations(record.observations)

        # Extract new observations
        new_observations, current_task, suggested = self.observer.extract_observations(
            messages,
            existing_obs_text
        )

        # Combine observations
        combined = record.observations + new_observations

        # Check if reflection needed
        observation_count = self.token_counter.count_observations(combined)
        if observation_count > self.config.reflection_threshold:
            # Trigger Reflector
            combined = self.reflector.reflect(combined)

        # Update record
        record.observations = combined
        record.current_task = current_task or record.current_task
        record.suggested_response = suggested or record.suggested_response

        return record

    def get_context(self, thread_id: str) -> str:
        """
        Get formatted context for actor (main agent).

        Returns:
        - Observations (compressed history)
        - Current task (if available)
        - Suggested response (if available)
        """
        record = self.get_observation_record(thread_id)
        if record is None:
            return "No observations yet."

        # Format for actor
        context = self._format_observations(record.observations)

        # Add suggested response
        if record.suggested_response:
            context += f"\n\n<Suggested Response>\n{record.suggested_response}\n"

        # Add current task
        if record.current_task:
            context += f"\n\n<Current Task>\n{record.current_task}\n"

        return context

    def _format_observations(self, observations: List[Observation]) -> str:
        """Format observations for context."""
        if not observations:
            return ""

        # Group by date
        grouped: Dict[str, List[Observation]] = {}
        for obs in observations:
            date_key = obs.timestamp.date().isoformat()
            if date_key not in grouped:
                grouped[date_key] = []
            grouped[date_key].append(obs)

        # Format output
        lines = []
        for date_key in sorted(grouped.keys()):
            lines.append(f"Date: {date_key}")
            for obs in grouped[date_key]:
                time_str = obs.timestamp.strftime("%H:%M")
                emoji = obs.priority.value
                lines.append(f"* {emoji} ({time_str}) {obs.content}")

        return "\n".join(lines)

    def get_stats(self, thread_id: str) -> Dict:
        """Get statistics about observational memory."""
        record = self.get_observation_record(thread_id)
        if record is None:
            return {"total_observations": 0}

        return {
            "total_observations": len(record.observations),
            "last_observed_at": None,
            "has_current_task": bool(record.current_task),
        }

    def force_reflection(self, thread_id: str) -> str:
        """Force reflection on a thread."""
        record = self.get_observation_record(thread_id)
        if record is None:
            return "No observations to reflect."

        # Trigger Reflector
        reflected = self.reflector.reflect(record.observations)

        # Update record
        record.observations = reflected
        return f"✅ Reflection complete. {len(recorded.observations)} observations"


# Export for easy importing
__all__ = [
    "ObservationalMemory",
    "ObservationConfig",
    "Observation",
    "ObservationalMemoryRecord",
    "PriorityLevel",
]
