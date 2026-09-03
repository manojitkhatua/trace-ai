from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd


class EntityRiskEngine:
    """
    Calculates risk for entities connected to a transaction.

    Uses the same training-derived mappings already used by TRACE.
    """

    def __init__(
        self,
        entity_maps: Dict[str, Any],
        pair_map: Dict[Any, Any],
        card_device_map: Dict[Any, Any],
        device_card_map: Dict[Any, Any],
    ):
        self.entity_maps = entity_maps
        self.pair_map = pair_map
        self.card_device_map = card_device_map
        self.device_card_map = device_card_map

    @staticmethod
    def _clip(value: float) -> float:
        return float(np.clip(value, 0.0, 1.0))

    def _get_entity_count(
        self,
        transaction: pd.DataFrame,
        column: str,
    ) -> int:

        value = transaction.iloc[0].get(column)
        mapping = self.entity_maps.get(column)

        if mapping is None or pd.isna(value):
            return 0

        return int(mapping.get(value, 0))

    def calculate_card_risk(
        self,
        transaction: pd.DataFrame,
    ) -> float:

        count = self._get_entity_count(
            transaction,
            "card1",
        )

        if count == 0:
            return 0.80

        # Extremely high activity receives higher risk.
        risk = min(count / 12000.0, 1.0)

        return round(self._clip(risk), 4)

    def calculate_device_risk(
        self,
        transaction: pd.DataFrame,
    ) -> float:

        device = transaction.iloc[0].get(
            "DeviceInfo"
        )

        if pd.isna(device):
            return 0.40

        card_count = int(
            self.device_card_map.get(
                device,
                0,
            )
        )

        # Unseen device.
        if card_count == 0:
            return 0.85

        risk = min(card_count / 20.0, 1.0)

        return round(self._clip(risk), 4)

    def calculate_address_risk(
        self,
        transaction: pd.DataFrame,
    ) -> float:

        address = transaction.iloc[0].get(
            "addr1"
        )

        if pd.isna(address):
            return 0.35

        count = self._get_entity_count(
            transaction,
            "addr1",
        )

        if count == 0:
            return 0.75

        risk = min(count / 50000.0, 1.0)

        return round(self._clip(risk), 4)

    def calculate_relationship_risk(
        self,
        transaction: pd.DataFrame,
    ) -> float:

        card = transaction.iloc[0].get(
            "card1"
        )

        device = transaction.iloc[0].get(
            "DeviceInfo"
        )

        if pd.isna(card) or pd.isna(device):
            return 0.40

        pair_count = int(
            self.pair_map.get(
                (card, device),
                0,
            )
        )

        if pair_count == 0:
            return 0.85

        if pair_count == 1:
            return 0.70

        if pair_count <= 5:
            return 0.45

        return 0.20

    def calculate_network_risk(
        self,
        transaction: pd.DataFrame,
    ) -> float:

        card = transaction.iloc[0].get(
            "card1"
        )

        device = transaction.iloc[0].get(
            "DeviceInfo"
        )

        if pd.isna(card) or pd.isna(device):
            return 0.40

        unique_cards = int(
            self.device_card_map.get(
                device,
                0,
            )
        )

        unique_devices = int(
            self.card_device_map.get(
                card,
                0,
            )
        )

        device_risk = min(
            unique_cards / 20.0,
            1.0,
        )

        card_risk = min(
            unique_devices / 10.0,
            1.0,
        )

        return round(
            self._clip(
                0.60 * device_risk
                + 0.40 * card_risk
            ),
            4,
        )

    def calculate(
        self,
        transaction: pd.DataFrame,
    ) -> Dict[str, Any]:

        if not isinstance(
            transaction,
            pd.DataFrame,
        ):
            raise TypeError(
                "transaction must be a pandas DataFrame."
            )

        if len(transaction) != 1:
            raise ValueError(
                "EntityRiskEngine expects exactly one transaction."
            )

        card_risk = self.calculate_card_risk(
            transaction
        )

        device_risk = self.calculate_device_risk(
            transaction
        )

        address_risk = self.calculate_address_risk(
            transaction
        )

        relationship_risk = (
            self.calculate_relationship_risk(
                transaction
            )
        )

        network_risk = self.calculate_network_risk(
            transaction
        )

        entity_risk = (
            0.25 * card_risk
            + 0.25 * device_risk
            + 0.15 * address_risk
            + 0.20 * relationship_risk
            + 0.15 * network_risk
        )

        entity_risk = round(
            self._clip(entity_risk),
            4,
        )

        if entity_risk >= 0.70:
            entity_level = "HIGH"
        elif entity_risk >= 0.40:
            entity_level = "MEDIUM"
        else:
            entity_level = "LOW"

        return {
            "entity_risk": entity_risk,
            "entity_level": entity_level,
            "card_risk": card_risk,
            "device_risk": device_risk,
            "address_risk": address_risk,
            "relationship_risk": relationship_risk,
            "network_risk": network_risk,
        }