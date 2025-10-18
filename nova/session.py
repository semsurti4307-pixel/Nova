from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .agent import NovaAgent, Action, Observation
from .memory import append_turn


@dataclass
class Turn:
    user: str
    action: Action
    observation: Observation


@dataclass
class Session:
    turns: List[Turn] = field(default_factory=list)

    def run(self, goal: str) -> Observation:
        agent = NovaAgent()
        action = agent.plan(goal)
        obs = agent.act(action)
        self.turns.append(Turn(user=goal, action=action, observation=obs))
        # persist minimal turn data
        append_turn({
            "user": goal,
            "action": {"name": action.name, "input": action.input},
            "observation": obs.text,
        })
        return obs
