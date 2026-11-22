"""
Mathematical format generators - set, group, category theory
"""

import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class MathFormatGenerator:
    """Generates mathematical data formats."""
    
    def generate_set_operations(self, set_a: Set[str], set_b: Set[str]) -> Dict:
        return {
            "format": "set_operations",
            "set_a": list(set_a),
            "set_b": list(set_b),
            "union": list(set_a | set_b),
            "intersection": list(set_a & set_b),
            "difference_a_b": list(set_a - set_b),
            "difference_b_a": list(set_b - set_a),
            "symmetric_difference": list(set_a ^ set_b),
            "jaccard_similarity": len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 0
        }
    
    def generate_reachable_set(self, start: str, transitions: Dict[str, Set[str]],
                              max_depth: int = 3) -> Dict:
        reachable = {start}
        frontier = {start}
        
        for _ in range(max_depth):
            next_frontier = set()
            for s in frontier:
                if s in transitions:
                    next_frontier.update(transitions[s])
            next_frontier -= reachable
            if not next_frontier:
                break
            reachable.update(next_frontier)
            frontier = next_frontier
        
        return {
            "format": "reachable_set",
            "start_state": start,
            "reachable_states": list(reachable),
            "cardinality": len(reachable)
        }
    
    def generate_orbit(self, element: str, generators: List) -> Dict:
        orbit = {element}
        frontier = {element}
        
        for _ in range(3):
            next_frontier = set()
            for s in frontier:
                for g in generators:
                    transformed = g(s)
                    if transformed not in orbit:
                        next_frontier.add(transformed)
            orbit.update(next_frontier)
            frontier = next_frontier
            if not frontier:
                break
        
        return {
            "format": "orbit",
            "element": element,
            "orbit_elements": list(orbit),
            "orbit_size": len(orbit)
        }
    
    def generate_composition_chain(self, morphisms: List[Dict], max_length: int = 3) -> List[Dict]:
        chains = []
        
        def dfs(current_chain, current_obj, depth):
            if depth >= max_length:
                if len(current_chain) >= 2:
                    chains.append({
                        "format": "composition_chain",
                        "length": len(current_chain),
                        "source": current_chain[0]["source"],
                        "target": current_chain[-1]["target"],
                        "actions": [m["action"] for m in current_chain]
                    })
                return
            
            for m in morphisms:
                if m["source"] == current_obj:
                    dfs(current_chain + [m], m["target"], depth + 1)
        
        for m in morphisms:
            dfs([m], m["target"], 1)
        
        return chains[:50]
