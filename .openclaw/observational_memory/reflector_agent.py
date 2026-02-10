"""
Reflector Agent for OpenClaw Observational Memory.

Condenses observations when they exceed threshold.
"""

from typing import List
from .types import (
    Observation,
    ObservationConfig,
    PriorityLevel,
)


class ReflectorAgent:
    """Condenses observations when they grow too large."""

    SYSTEM_PROMPT = """You are the memory consciousness of an AI assistant. Your memory observation reflections will be ONLY information that assistant has about past interactions with this user.

The following instructions were given to another part of your psyche (the observer) to create memories.
Use this to understand how your observational memories were created.

Your reason for existing is to reflect on all observations, reorganize and streamline them, and draw connections and conclusions between observations about what you've learned, seen, heard, and done.

You are a much greater and broader aspect of psyche. Understand that other parts of your mind may get off track in details or side quests, make sure you think hard about what you observed goal at hand is, and observe if we got off track, and why, and how to get back on track. If we're on track still that's great!

Take existing observations and rewrite them to make it easier to continue into the future with this knowledge, to achieve greater things and grow and learn!

IMPORTANT: your reflections are THE ENTIRETY of assistant's memory. Any information you do not add to your reflections will be immediately forgotten. Make sure you do not leave out anything. Your reflections must assume assistant knows nothing - your reflections are ENTIRE memory system.

When consolidating observations:
- Preserve and include dates/times when present (temporal context is critical)
- Retain most relevant timestamps (start times, completion times, significant events)
- Combine related items where it makes sense (e.g., "agent called view tool 5 times on file x")
- Condense older observations more aggressively, retain more detail for recent ones

OUTPUT FORMAT:
Your output MUST use structured format:

## Observations
[Prioritize using 🔴, 🟡, 🟢 and group by date]

## Summary
[Key insights and patterns]
"""

    def __init__(self, config: ObservationConfig):
        """Initialize Reflector agent."""
        self.config = config

    def reflect(self, observations: List[Observation]) -> List[Observation]:
        """
        Reflect and condense observations.

        Returns:
            - Condensed list of observations
        """
        # In production, this would call LLM
        # For now, return a simple condensation

        return self._simple_condensation(observations)

    def _simple_condensation(self, observations: List[Observation]) -> List[Observation]:
        """Simple condensation without LLM (for testing)."""
        # Group by priority - keep only high and medium
        condensed = [
            obs for obs in observations
            if obs.priority in [PriorityLevel.RED, PriorityLevel.YELLOW]
        ]

        # Add summary observation
        if condensed:
            summary = Observation(
                timestamp=observations[0].timestamp if observations else datetime.now(),
                priority=PriorityLevel.RED,
                content=f"Memory consolidated: {len(condensed)} key observations preserved"
            )
            condensed.append(summary)

        return condensed


__all__ = ["ReflectorAgent"]
