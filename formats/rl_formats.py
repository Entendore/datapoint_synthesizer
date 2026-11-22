"""
RL format generators - SARS, trajectories, DPO, KTO, ORPO, SimPO, etc.
"""

import math
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

import numpy as np


@dataclass
class State:
    document_id: str
    sentence_idx: int
    text: str
    features: List[float]
    entities: List[str]
    keywords: List[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Action:
    action_type: str
    action_params: Dict
    action_id: int
    probability: float
    log_prob: float = 0.0
    ref_log_prob: float = 0.0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Step:
    state: State
    action: Action
    reward: float
    step_reward: float = 0.0
    next_state: Optional[State] = None
    done: bool = False
    advantage: float = 0.0
    value_target: float = 0.0
    n_step_return: float = 0.0
    return_to_go: float = 0.0
    importance_weight: float = 1.0
    kl_penalty: float = 0.0
    entropy_bonus: float = 0.0
    token_rewards: Optional[List[float]] = None
    info: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "state": self.state.to_dict(),
            "action": self.action.to_dict(),
            "reward": self.reward,
            "step_reward": self.step_reward,
            "next_state": self.next_state.to_dict() if self.next_state else None,
            "done": self.done,
            "advantage": self.advantage,
            "value_target": self.value_target,
            "n_step_return": self.n_step_return,
            "return_to_go": self.return_to_go,
            "importance_weight": self.importance_weight,
            "kl_penalty": self.kl_penalty,
            "entropy_bonus": self.entropy_bonus,
            "token_rewards": self.token_rewards,
            "info": self.info
        }


class RLFormatGenerator:
    """Generates various RL data formats."""
    
    ACTIONS = {
        0: {"type": "extract_entity"},
        1: {"type": "summarize"},
        2: {"type": "generate_question"},
        3: {"type": "extract_relation"},
        4: {"type": "skip"},
        5: {"type": "extract_keyphrase"},
    }
    
    def __init__(self):
        self.n_actions = len(self.ACTIONS)
    
    def generate_trajectory(self, sentences: List[str], doc_id: str,
                           policy: str = "epsilon_greedy", gamma: float = 0.99) -> Dict:
        steps = []
        
        for i, sentence in enumerate(sentences):
            state = State(
                document_id=doc_id,
                sentence_idx=i,
                text=sentence,
                features=np.random.randn(32).tolist(),
                entities=self._extract_entities(sentence),
                keywords=self._extract_keywords(sentence)
            )
            
            action = self._sample_action(state, policy)
            reward = self._compute_reward(state, action)
            step_reward = self._compute_step_reward(state, action)
            
            next_state = None
            done = False
            if i < len(sentences) - 1:
                next_state = State(
                    document_id=doc_id,
                    sentence_idx=i+1,
                    text=sentences[i+1],
                    features=np.random.randn(32).tolist(),
                    entities=self._extract_entities(sentences[i+1]),
                    keywords=self._extract_keywords(sentences[i+1])
                )
            else:
                done = True
            
            step = Step(
                state=state, action=action, reward=reward,
                step_reward=step_reward, next_state=next_state, done=done,
            )
            steps.append(step)
        
        self._compute_returns(steps, gamma)
        self._compute_gae(steps, gamma, lam=0.95)
        self._compute_n_step_returns(steps, gamma, n=5)
        self._compute_return_to_go(steps, gamma)
        
        return {
            "trajectory_id": f"{doc_id}_{policy}",
            "document_id": doc_id,
            "policy": policy,
            "steps": [s.to_dict() for s in steps],
            "total_reward": float(sum(s.reward for s in steps)),
            "total_step_reward": float(sum(s.step_reward for s in steps)),
            "length": len(steps),
            "mean_kl": float(np.mean([s.kl_penalty for s in steps])),
            "mean_entropy": float(np.mean([s.entropy_bonus for s in steps])),
            "returns": [s.value_target for s in steps]
        }
    
    def generate_dpo_pair(self, chosen: Dict, rejected: Dict) -> Dict:
        margin = math.tanh((chosen["total_reward"] - rejected["total_reward"]) / 2.0)
        
        return {
            "format": "dpo",
            "prompt": chosen["steps"][0]["state"]["text"],
            "chosen": [s["action"]["action_type"] for s in chosen["steps"]],
            "rejected": [s["action"]["action_type"] for s in rejected["steps"]],
            "chosen_logps": [s["action"]["log_prob"] for s in chosen["steps"]],
            "rejected_logps": [s["action"]["log_prob"] for s in rejected["steps"]],
            "chosen_ref_logps": [s["action"]["ref_log_prob"] for s in chosen["steps"]],
            "rejected_ref_logps": [s["action"]["ref_log_prob"] for s in rejected["steps"]],
            "margin": margin
        }
    
    def generate_kto_sample(self, trajectory: Dict, is_good: bool) -> Dict:
        return {
            "format": "kto",
            "prompt": trajectory["steps"][0]["state"]["text"],
            "completion": [s["action"]["action_type"] for s in trajectory["steps"]],
            "logps": [s["action"]["log_prob"] for s in trajectory["steps"]],
            "ref_logps": [s["action"]["ref_log_prob"] for s in trajectory["steps"]],
            "label": is_good,
            "reward": trajectory["total_reward"]
        }
    
    def _sample_action(self, state: State, policy: str) -> Action:
        if policy == "uniform":
            action_id = random.randrange(self.n_actions)
            prob = 1.0 / self.n_actions
        elif policy == "epsilon_greedy":
            if random.random() < 0.1:
                action_id = random.randrange(self.n_actions)
                prob = 0.1 / self.n_actions
            else:
                action_id = 2 if state.entities else 0
                prob = 0.9
        elif policy == "expert":
            if len(state.entities) >= 2:
                action_id = 2
            elif len(state.keywords) >= 3:
                action_id = 5
            else:
                action_id = 0
            prob = 0.95
        else:
            action_id = random.randrange(self.n_actions)
            prob = 1.0 / self.n_actions
        
        log_prob = math.log(max(prob, 1e-10))
        ref_log_prob = math.log(1.0 / self.n_actions)
        
        return Action(
            action_type=self.ACTIONS[action_id]["type"],
            action_params={"target": state.text},
            action_id=action_id,
            probability=prob,
            log_prob=log_prob,
            ref_log_prob=ref_log_prob
        )
    
    def _compute_reward(self, state: State, action: Action) -> float:
        if action.action_type in ["extract_entity", "generate_question", "extract_relation"]:
            return min(1.0, len(state.entities) * 0.3 + len(state.keywords) * 0.1)
        elif action.action_type == "skip":
            return 0.0
        return 0.3
    
    def _compute_step_reward(self, state: State, action: Action) -> float:
        base = {"extract_entity": 0.4, "generate_question": 0.6,
                "extract_relation": 0.5, "extract_keyphrase": 0.4,
                "summarize": 0.5, "skip": 0.0}.get(action.action_type, 0.1)
        entity_bonus = min(0.3, len(state.entities) * 0.1)
        return base + entity_bonus
    
    def _compute_returns(self, steps: List[Step], gamma: float):
        cumulative = 0.0
        for step in reversed(steps):
            cumulative = step.reward + gamma * cumulative
            step.value_target = cumulative
    
    def _compute_gae(self, steps: List[Step], gamma: float, lam: float):
        gae = 0.0
        for t in reversed(range(len(steps))):
            step = steps[t]
            next_value = 0.0 if step.done else steps[t+1].value_target
            delta = step.reward + gamma * next_value - step.value_target
            gae = delta + gamma * lam * gae
            step.advantage = gae
    
    def _compute_n_step_returns(self, steps: List[Step], gamma: float, n: int):
        for i in range(len(steps)):
            n_ret = 0.0
            for k in range(n):
                if i + k >= len(steps):
                    break
                n_ret += (gamma ** k) * steps[i+k].reward
                if steps[i+k].done:
                    break
            steps[i].n_step_return = n_ret
    
    def _compute_return_to_go(self, steps: List[Step], gamma: float):
        rtg = 0.0
        for step in reversed(steps):
            rtg = step.reward + gamma * rtg
            step.return_to_go = rtg
    
    def _extract_entities(self, text: str) -> List[str]:
        import re
        return re.findall(r'\b[A-Z][a-z]+\b', text)[:5]
    
    def _extract_keywords(self, text: str) -> List[str]:
        return [w for w in text.split() if len(w) > 4][:5]
