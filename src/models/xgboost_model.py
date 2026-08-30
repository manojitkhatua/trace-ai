from xgboost import XGBClassifier


class XGBoostModel:

    def __init__(
        self,
        scale_pos_weight,
        n_estimators=300,
        max_depth=6,
        min_child_weight=1,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0,
        reg_lambda=1
    ):
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_child_weight=min_child_weight,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            objective="binary:logistic",
            eval_metric="aucpr",
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1
        )

    def train(self, X_train, y_train, X_validation, y_validation):
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_validation, y_validation)],
            verbose=False
        )

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:, 1]

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)