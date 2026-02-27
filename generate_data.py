"""
Generate synthetic training data for the reorder prediction model.

Produces data/training_data.csv with 5,000 rows.
Run once, commit the CSV: python generate_data.py
"""

import csv
import os
import numpy as np

HIGH_REORDER_STATES = {"OH", "TX", "CA", "IL", "FL"}
MED_REORDER_STATES = {"IN", "MI", "MN", "CO", "MA", "TN", "OR"}
LOW_REORDER_STATES = {"WA", "AZ", "ND", "SD", "NE", "KS"}
ALL_STATES = sorted(HIGH_REORDER_STATES | MED_REORDER_STATES | LOW_REORDER_STATES)


def state_score(state: str) -> float:
    if state in HIGH_REORDER_STATES:
        return 1.0
    if state in MED_REORDER_STATES:
        return 0.5
    return 0.0


def generate(n: int = 5000, seed: int = 42) -> None:
    rng = np.random.RandomState(seed)

    states = rng.choice(ALL_STATES, size=n)
    num_items = rng.randint(1, 7, size=n)
    has_electronics = rng.binomial(1, 0.4, size=n)
    order_totals = rng.uniform(50, 1500, size=n).round(2)
    state_scores = np.array([state_score(s) for s in states])
    total_normalized = (order_totals - 50) / (1500 - 50)

    # Logit with interaction term and reduced noise
    logit = (
        -1.5
        + 1.4 * state_scores
        + 0.6 * has_electronics
        + 0.12 * num_items
        + 0.4 * total_normalized
        + 0.5 * (has_electronics * total_normalized)
        + rng.normal(0, 0.35, size=n)
    )
    prob = 1 / (1 + np.exp(-logit))
    will_reorder = (prob > 0.5).astype(int)

    avg_item_price = (order_totals / num_items).round(2)

    # Write CSV
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", "training_data.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "num_items", "has_electronics", "state", "order_total",
            "avg_item_price", "will_reorder",
        ])
        for i in range(n):
            writer.writerow([
                int(num_items[i]),
                int(has_electronics[i]),
                states[i],
                float(order_totals[i]),
                float(avg_item_price[i]),
                int(will_reorder[i]),
            ])

    # Summary stats
    reorder_rate = will_reorder.mean() * 100
    elec_reorder = will_reorder[has_electronics == 1].mean() * 100
    no_elec_reorder = will_reorder[has_electronics == 0].mean() * 100

    print(f"Wrote {n} rows to {path}")
    print(f"  Reorder rate:          {reorder_rate:.1f}%")
    print(f"  Electronics reorder:   {elec_reorder:.1f}%")
    print(f"  No electronics:        {no_elec_reorder:.1f}%")
    print(f"  Avg order total:       ${order_totals.mean():.2f}")
    print(f"  Avg items per order:   {num_items.mean():.1f}")


if __name__ == "__main__":
    generate()
