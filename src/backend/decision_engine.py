class DecisionEngine:

    def __init__(
        self,
        review_threshold=0.20,
        block_threshold=0.70
    ):
        self.review_threshold = review_threshold
        self.block_threshold = block_threshold

    def decide(self, fraud_probability):

        if fraud_probability >= self.block_threshold:
            risk_level = "HIGH"
            decision = "BLOCK"

        elif fraud_probability >= self.review_threshold:
            risk_level = "MEDIUM"
            decision = "REVIEW"

        else:
            risk_level = "LOW"
            decision = "ALLOW"

        risk_score = round(fraud_probability * 100, 2)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "decision": decision
        }