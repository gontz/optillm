"""
Tests for the SPL creative quality evaluator. Uses a fake client, no LLM needed.
"""

from types import SimpleNamespace

from optillm.plugins.spl.evaluation import (
    parse_quality_scores,
    evaluate_strategy_effectiveness,
)
from optillm.plugins.spl.strategy import Strategy
from optillm.plugins.spl.config import CREATIVE_PROBLEM_TYPES
from optillm.plugins.spl.main import EXCLUDED_REQUEST_KEYS

HIGH = '{"originality": 5, "insight": 4, "relevance": 5, "feasibility": 4, "craft": 4}'
LOW = '{"originality": 2, "insight": 2, "relevance": 4, "feasibility": 3, "craft": 3}'


class FakeClient:
    """Answers the quality judge with `quality_reply` and the adherence check with `adherence_reply`."""

    def __init__(self, quality_reply, adherence_reply="YES"):
        self.calls = []
        self.quality_reply = quality_reply
        self.adherence_reply = adherence_reply
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages, **kwargs):
        system = messages[0]["content"]
        kind = "quality" if "creative director" in system else "adherence"
        self.calls.append((kind, model))
        content = self.quality_reply if kind == "quality" else self.adherence_reply
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def make_strategy(sid="s1", ptype="creative_ideation"):
    return Strategy(strategy_id=sid, problem_type=ptype, strategy_text="Reject the first three ideas.")


def test_parse_json_scores():
    assert parse_quality_scores(HIGH) == {
        "originality": 5, "insight": 4, "relevance": 5, "feasibility": 4, "craft": 4
    }


def test_parse_json_after_thinking_and_text():
    text = 'Here is my verdict:\n{"Originality": 3, "insight": 3, "relevance": 4, "feasibility": 4, "craft": 3.5}'
    assert parse_quality_scores(text)["craft"] == 3.5


def test_parse_key_value_fallback():
    text = "originality: 4\ninsight: 3\nrelevance: 5\nfeasibility: 4\ncraft: 4"
    assert parse_quality_scores(text)["insight"] == 3


def test_parse_rejects_missing_or_out_of_range():
    assert parse_quality_scores('{"originality": 4, "insight": 3}') is None
    assert parse_quality_scores(HIGH.replace('"craft": 4', '"craft": 9')) is None
    assert parse_quality_scores("no scores here") is None


def test_creative_high_quality_is_effective():
    client = FakeClient(HIGH)
    result = evaluate_strategy_effectiveness("ideas", None, [make_strategy()], client, "m",
                                             query="brief", problem_type="creative_ideation")
    assert result == {"s1": True}
    assert [k for k, _ in client.calls] == ["quality", "adherence"]


def test_creative_low_quality_is_not_effective_even_if_applied():
    client = FakeClient(LOW)
    result = evaluate_strategy_effectiveness("ideas", None, [make_strategy()], client, "m",
                                             query="brief", problem_type="creative_problem_solving")
    assert result == {"s1": False}


def test_quality_scored_once_for_several_strategies():
    client = FakeClient(HIGH)
    strategies = [make_strategy("s1"), make_strategy("s2"), make_strategy("s3")]
    evaluate_strategy_effectiveness("ideas", None, strategies, client, "m",
                                    query="brief", problem_type="creative_writing")
    assert [k for k, _ in client.calls].count("quality") == 1


def test_unparseable_quality_falls_back_to_adherence():
    client = FakeClient("I liked it a lot")
    result = evaluate_strategy_effectiveness("ideas", None, [make_strategy()], client, "m",
                                             query="brief", problem_type="creative_ideation")
    assert result == {"s1": True}


def test_non_creative_types_skip_quality_check():
    client = FakeClient(LOW)
    result = evaluate_strategy_effectiveness("42", None, [make_strategy(ptype="word_problem")], client, "m",
                                             query="brief", problem_type="word_problem")
    assert result == {"s1": True}
    assert all(k == "adherence" for k, _ in client.calls)


def test_creative_types_and_excluded_keys():
    assert {"creative_writing", "creative_ideation", "creative_problem_solving"} <= CREATIVE_PROBLEM_TYPES
    assert {"stream", "n", "spl_learning"} <= EXCLUDED_REQUEST_KEYS
