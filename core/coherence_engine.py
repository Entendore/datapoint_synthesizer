"""
Semantic coherence engine
"""

from typing import Dict
import networkx as nx

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


class SemanticCoherenceEngine:
    """Ensures generated datapoints are semantically consistent."""
    
    def __init__(self):
        self.knowledge_graph = self._build_knowledge_graph()
    
    def _build_knowledge_graph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        
        g.add_edge("France", "Paris", relation="capital")
        g.add_edge("Japan", "Tokyo", relation="capital")
        g.add_edge("Germany", "Berlin", relation="capital")
        g.add_edge("Italy", "Rome", relation="capital")
        g.add_edge("Spain", "Madrid", relation="capital")
        g.add_edge("Brazil", "Brasilia", relation="capital")
        g.add_edge("Canada", "Ottawa", relation="capital")
        g.add_edge("Australia", "Canberra", relation="capital")
        
        return g
    
    def ensure_coherence(self, datapoint: Dict, signatures: Dict) -> Dict:
        if "question" in datapoint and "answer" in datapoint:
            question = datapoint["question"]
            answer = datapoint["answer"]
            
            if nlp:
                try:
                    doc = nlp(question)
                    for ent in doc.ents:
                        if ent.label_ in ["GPE", "LOC"]:
                            if ent.text in self.knowledge_graph:
                                successors = list(self.knowledge_graph.successors(ent.text))
                                if successors and answer not in successors:
                                    datapoint["answer"] = successors[0]
                except Exception:
                    pass
        
        return datapoint
