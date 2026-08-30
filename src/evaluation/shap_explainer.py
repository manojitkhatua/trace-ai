import shap
import pandas as pd


class SHAPExplainer:

    def __init__(self, model):
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def explain(self, row: pd.DataFrame, top_n: int = 10):
        shap_values = self.explainer.shap_values(row)

        values = shap_values[0]
        result = pd.DataFrame({
            "feature": row.columns,
            "value": row.iloc[0].values,
            "shap_value": values
        })

        result["direction"] = result["shap_value"].apply(
            lambda x: "fraud" if x > 0 else "legitimate"
        )

        return result.assign(
            abs_shap=result["shap_value"].abs()
        ).sort_values(
            "abs_shap",
            ascending=False
        ).head(top_n).reset_index(drop=True)

    def explain_row(self, row: pd.DataFrame):
        return self.explainer.shap_values(row)
    
    
    def explain_prediction(self, row: pd.DataFrame, top_n: int = 5):
        probability = self.model.predict_proba(row)[:, 1][0]
        reasons = self.explain(row, top_n)

        return {
            "fraud_probability": probability,
            "reasons": reasons
        }