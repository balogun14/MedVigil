import requests
from typing import List, Dict, Any

class RAGAgent:
    def __init__(self):
        self.openfda_url = "https://api.fda.gov/drug/event.json"

    def search_literature(self, entities: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Searches OpenFDA and PubMed for the given extracted entities.
        Returns a classification and summary.
        """
        drugs = [e["entity"] for e in entities if "drug" in e.get("label", "").lower()]
        effects = [e["entity"] for e in entities if "effect" in e.get("label", "").lower() or "ade" in e.get("label", "").lower()]

        if not drugs or not effects:
            return {
                "classification": "Unknown",
                "summary": "Insufficient entities extracted to perform a literature search."
            }

        # Simplified openFDA check (mocking actual LLM summarization for now)
        # In production, we'd fetch actual reports and pass them to an LLM.
        drug = drugs[0].lower()
        effect = effects[0].lower()
        
        try:
            # Basic OpenFDA query (example structure)
            res = requests.get(f"{self.openfda_url}?search=patient.drug.medicinalproduct:{drug}+AND+patient.reaction.reactionmeddrapt:{effect}&limit=1")
            if res.status_code == 200:
                data = res.json()
                count = data.get("meta", {}).get("results", {}).get("total", 1)
                return {
                    "classification": "Known",
                    "summary": f"Found {count} matching reports in OpenFDA for {drug} causing {effect}."
                }
            else:
                return {
                    "classification": "Unknown",
                    "summary": f"No definitive reports found in OpenFDA for {drug} causing {effect}."
                }
        except Exception as e:
            return {
                "classification": "Unlabeled",
                "summary": "Error reaching literature databases."
            }
