# %%

from art.utils.benchmarking.load_trajectories import (
    load_trajectories,
    pull_model_trajectories,
)
from art_e.evaluate.charts import training_progress_chart, comparison_models_bar_chart
from all_models import models
import asyncio

ds_size_models = [m for m in models.values() if m.name.startswith("ea-210")]

await asyncio.gather(*[pull_model_trajectories(m) for m in ds_size_models])  # type: ignore

# %%

models = [
    "o3",
    "o4-mini",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "qwen3-32b",
    *[m.name for m in ds_size_models],
]

# await load_trajectories.bust_cache()
df = await load_trajectories(
    "../../.art/email_agent",
    models=models,
)  # type: ignore

# %%

training_progress_chart(
    df,
    "val",
    "answer_correct",
    models=models,
    title="Fraction of Questions Answered Correctly",
    y_label="Val set success rate",
)

# %%
import polars as pl

labeled_models = []
for m in ds_size_models:
    model_size = m.name.split("-")[-1]
    unit = "scenario" if model_size == "1" else "scenarios"
    labeled_models.append((m.name, f"{model_size} {unit}"))

comparison_models_bar_chart(
    df.filter(pl.col("step").ne(144)),
    "val",
    "answer_correct",
    models=["gemini-2.5-flash", "o3", "gemini-2.5-pro", *labeled_models],
    title="Eval Accuracy vs Training Dataset Size",
    y_label="Val set success rate",
    figsize=(20, 5),
)

# %%


# df.filter(pl.col("model").eq("ea-210-16")).filter(pl.col("split").eq("val")).group_by("step").count()


# %%

from art_e.data.query_iterators import load_synthetic_queries

scenarios = load_synthetic_queries(split="train", limit=10)

for i, scenario in enumerate(scenarios):
    print(scenario.inbox_address)
