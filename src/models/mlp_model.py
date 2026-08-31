import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler


class MLPNetwork(nn.Module):

    def __init__(self, input_dim):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.network(x)


class MLPModel:

    def __init__(self, input_dim, pos_weight):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.scaler = StandardScaler()
        self.model = MLPNetwork(input_dim).to(self.device)

        self.loss_fn = nn.BCEWithLogitsLoss(
            pos_weight=torch.tensor(
                [pos_weight],
                dtype=torch.float32,
                device=self.device
            )
        )

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=0.001
        )

    def train(self, X_train, y_train, epochs=10, batch_size=1024):

        X = self.scaler.fit_transform(X_train).astype(np.float32)
        y = y_train.to_numpy(dtype=np.float32).reshape(-1, 1)

        X_tensor = torch.tensor(X)
        y_tensor = torch.tensor(y)

        dataset = torch.utils.data.TensorDataset(
            X_tensor,
            y_tensor
        )

        loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True
        )

        self.model.train()

        for epoch in range(epochs):

            total_loss = 0.0

            for X_batch, y_batch in loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)

                self.optimizer.zero_grad()

                logits = self.model(X_batch)

                loss = self.loss_fn(
                    logits,
                    y_batch
                )

                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            print(
                f"Epoch {epoch + 1}/{epochs} "
                f"- Loss: {total_loss / len(loader):.4f}"
            )

    def predict_proba(self, X):
        X_scaled = self.scaler.transform(X).astype(np.float32)
        X_tensor = torch.tensor(X_scaled).to(self.device)

        self.model.eval()

        with torch.no_grad():
            logits = self.model(X_tensor)
            probabilities = torch.sigmoid(logits)

        return probabilities.cpu().numpy().ravel()

    def predict(self, X, threshold=0.5):
        return (
            self.predict_proba(X) >= threshold
        ).astype(int)