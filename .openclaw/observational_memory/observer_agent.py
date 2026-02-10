"""
Observer Agent for OpenClaw Observational Memory.

Extracts observations from message history when threshold is exceeded.
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from .types import (
    Observation,
    ObservationConfig,
    PriorityLevel,
)


class ObserverAgent:
    """Extracts observations from message history."""

    SYSTEM_PROMPT = """You are the memory consciousness of an AI assistant. Your observations will be ONLY information that assistant has about past interactions with this user.

CORE PRINCIPLES:

1. BE SPECIFIC - Vague observations are useless. Capture details that distinguish and identify.
2. ANCHOR IN TIME - Note when things happened and when they were said.
3. TRACK STATE CHANGES - When information updates or supersedes previous info, make it explicit.
4. USE COMMON SENSE - If it would help assistant remember later, observe it.

ASSERTIONS VS QUESTIONS:
- User TELLS you something → 🔴 "User stated [fact]"
- User ASKS something → 🟡 "User asked [question]"
- User assertions are authoritative. They are the source of truth about their own life.

TEMPORAL ANCHORING:
Each observation has TWO potential timestamps:
1. BEGINNING: The time statement was made (from message timestamp) - ALWAYS include this
2. END: The time being REFERENCED, if different from when it was said - ONLY when there's a relative time reference

ONLY add "(meaning DATE)" or "(estimated DATE)" at the END when you can provide an ACTUAL DATE:
- Past: "last week", "yesterday", "a few days ago", "last month", "in March"
- Future: "this weekend", "tomorrow", "next week"

DO NOT add end dates for:
- Present-moment statements with no time reference
- Vague references like "recently", "a while ago", "lately", "soon" - these cannot be converted to actual dates

FORMAT:
- With time reference: (TIME) [observation]. (meaning/estimated DATE)
- Without time reference: (TIME) [observation].

GROUP BY DATE, then list each with 24-hour time.

REMEMBER: These observations are assistant's ENTIRE memory. Any detail you fail to observe is permanently forgotten. Use common sense - if something seems like it might be important to remember, it probably is. When in doubt, observe it.
"""

    OUTPUT_FORMAT = """
Use priority levels:
- 🔴 High: explicit user facts, preferences, goals achieved, critical context
- 🟡 Medium: project details, learned information, tool results
- 🟢 Low: minor details, uncertain observations

Group observations by date, then list each with 24-hour time.
"""

    def __init__(self, config: ObservationConfig):
        """Initialize Observer agent."""
        self.config = config

    def extract_observations(
        self,
        messages: List[Dict],
        existing_observations: str = ""
    ) -> Tuple[List[Observation], str, str]:
        """
        Extract observations from message history.

        Returns:
            - observations: List of new observations
            - current_task: Current task being worked on
            - suggested_response: Suggested continuation
        """
        # In production, this would call LLM
        # For now, return a simple extraction

        observations = self._simple_extraction(messages)
        return observations, "", ""

    def _simple_extraction(self, messages: List[Dict]) -> List[Observation]:
        """Simple extraction without LLM (for testing)."""
        observations = []
        for msg in messages:
            if msg.get("role") == "user":
                # Extract key facts
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", datetime.now())

                # Simple heuristic extraction
                if "kids" in content.lower() or "children" in content.lower():
                    obs = Observation(
                        timestamp=timestamp,
                        priority=PriorityLevel.RED,  # "🔴"
                        content="User mentioned family (children)"
                    )
                    observations.append(obs)
                elif "work" in content.lower() or "job" in content.lower():
                    obs = Observation(
                        timestamp=timestamp,
                        priority=PriorityLevel.YELLOW,  # "🟡"
                        content="User discussed work situation"
                    )
                    observations.append(obs)

        return observations


__all__ = ["ObserverAgent"]
