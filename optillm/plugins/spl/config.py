"""
Configuration settings for the System Prompt Learning (SPL) plugin.
"""

import os
import shutil
from pathlib import Path
from typing import List

# Plugin identifier
SLUG = "spl"

# Strategies shipped with the package, used to seed a new data directory
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_DATA_DIR = os.path.join(PLUGIN_DIR, 'data')

# Learned strategies live outside the package so updates never overwrite them.
# Override with OPTILLM_SPL_DATA_DIR.
DATA_DIR = os.environ.get("OPTILLM_SPL_DATA_DIR", str(Path.home() / ".optillm" / "spl"))
STRATEGY_DB_PATH = os.path.join(DATA_DIR, 'strategies.json')
STRATEGY_METRICS_PATH = os.path.join(DATA_DIR, 'metrics.json')

# Default max tokens for reasoning LLMs
DEFAULT_MAX_TOKENS = 4096

# How often to perform maintenance operations (merge, prune)
MAINTENANCE_INTERVAL = 40

# Strategy selection thresholds
STRATEGY_CREATION_THRESHOLD = 0.7  # Higher threshold to avoid creating similar strategies
STRATEGY_MERGING_THRESHOLD = 0.6   # Lower threshold to merge more similar strategies
MIN_SUCCESS_RATE_FOR_INFERENCE = 0.4  # Minimum success rate for a strategy to be used during inference

# Limits for strategy management
MAX_STRATEGIES_PER_TYPE = 10  # Maximum strategies to store in DB per problem type
MAX_STRATEGIES_FOR_INFERENCE = 3  # Maximum strategies to use during inference

# Define valid problem types (used for strict classification)
VALID_PROBLEM_TYPES: List[str] = [
    "arithmetic_calculation",
    "algebraic_equation",
    "statistical_analysis",
    "logical_reasoning",
    "word_problem",
    "coding_problem",
    "algorithm_design",
    "creative_writing",
    "creative_ideation",         # brainstorming, concepts, naming, campaign ideas
    "creative_problem_solving",  # unconventional solutions to a constrained problem
    "text_summarization",
    "information_retrieval",
    "planning_task",
    "decision_making",
    "knowledge_question",
    "language_translation",
    "sequence_completion",
    "general_problem"  # Fallback type
]

# Creative problem types are judged on the quality of the answer, not only on
# whether the strategy was followed. A strategy counts as effective when it was
# applied and the answer's average score (1 to 5) reaches the threshold.
CREATIVE_PROBLEM_TYPES = {"creative_writing", "creative_ideation", "creative_problem_solving"}
CREATIVE_CRITERIA = ["originality", "insight", "relevance", "feasibility", "craft"]
CREATIVE_QUALITY_THRESHOLD = float(os.environ.get("OPTILLM_SPL_CREATIVE_THRESHOLD", "3.5"))
# Optional separate judge model, so the model does not grade its own work. Empty means the same model.
CREATIVE_JUDGE_MODEL = os.environ.get("OPTILLM_SPL_JUDGE_MODEL", "")

# Ensure data directory exists and seed it with the bundled strategies on first use
os.makedirs(DATA_DIR, exist_ok=True)
for _name in ('strategies.json', 'metrics.json'):
    _src = os.path.join(BUNDLED_DATA_DIR, _name)
    _dst = os.path.join(DATA_DIR, _name)
    if not os.path.exists(_dst) and os.path.exists(_src):
        shutil.copyfile(_src, _dst)
