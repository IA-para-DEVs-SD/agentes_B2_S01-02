import pandas as pd
import json
from pathlib import Path

base = Path(__file__).parent
csv_path = base / "users_problems.csv"
metrics_path = base / "metrics.json"

df = pd.read_csv(csv_path)
df["data"] = pd.to_datetime(df["data"])
df = df.sort_values(["user_id", "data"])

user_counts = df.groupby("user_id").size()
returning_users = user_counts[user_counts > 1].index.tolist()

same_problem_users = []
for user_id, group in df.groupby("user_id"):
    if len(group) > 1 and group["problema"].duplicated().any():
        same_problem_users.append(user_id)

last_status_df = df.groupby("user_id").tail(1)[["user_id", "solved_status"]]

metrics = {
    "total_users": int(df["user_id"].nunique()),
    "returning_users": int(len(returning_users)),
    "returning_same_problem": int(len(same_problem_users)),
    "stopped_responding": int((last_status_df["solved_status"] == "stopped responding").sum()),
    "cancelled": int((last_status_df["solved_status"] == "cancelled").sum()),
    "completed": int((last_status_df["solved_status"] == "completed").sum())
}

metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
print("metrics.json updated")