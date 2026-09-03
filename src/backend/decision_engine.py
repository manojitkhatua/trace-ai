class DecisionEngine:
    """
    Converts TRACE's operational risk score into an action.

    This decision layer is separate from the ML model.
    """

    def __init__(
        self,
        review_threshold: float = 40.0,
        block_threshold: float = 70.0,
    ):
        if review_threshold >= block_threshold:
            raise ValueError(
                "review_threshold must be lower than block_threshold."
            )

        self.review_threshold = float(review_threshold)
        self.block_threshold = float(block_threshold)

    def decide(self, risk_score: float):
        risk_score = float(risk_score)

        if risk_score >= self.block_threshold:
            return {
                "decision": "BLOCK",
                "risk_level": "HIGH",
                "risk_score": round(risk_score, 2),
            }

        if risk_score >= self.review_threshold:
            return {
                "decision": "REVIEW",
                "risk_level": "MEDIUM",
                "risk_score": round(risk_score, 2),
            }

        return {
            "decision": "ALLOW",
            "risk_level": "LOW",
            "risk_score": round(risk_score, 2),
        }