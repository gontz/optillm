"""
Approaches that request several completions with n must still get them from
providers like Ollama, which ignore n and silently return one choice.
Uses a fake client, no LLM needed.
"""

from types import SimpleNamespace

from optillm.bon import best_of_n_sampling
from optillm.moa import mixture_of_agents
from optillm.mcts import MCTS, DialogueState
from optillm.pvg import generate_solutions


class OllamaLikeClient:
    """Ignores n and returns one numbered choice per call, like Ollama."""

    def __init__(self):
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        content = f"answer {len(self.requests)}"
        # Rating requests in bon expect a number
        if any("Rate the" in m.get("content", "") for m in kwargs["messages"]):
            content = "5"
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content), finish_reason="stop")],
            usage=SimpleNamespace(completion_tokens=1),
        )

    def generation_requests(self):
        return [r for r in self.requests if r.get("temperature") == 1 or r.get("n", 1) > 1]


def test_bon_gets_n_candidates():
    client = OllamaLikeClient()
    best_of_n_sampling("sys", "q", client, "m", n=3)
    # one n=3 call answered with a single choice, then two top-ups; each candidate rated once
    ratings = [r for r in client.requests if r.get("max_tokens") == 256]
    assert len(ratings) == 3


def test_moa_gets_three_candidates():
    client = OllamaLikeClient()
    mixture_of_agents("sys", "q", client, "m")
    critique = [r for r in client.requests if "answer 3" in str(r["messages"])]
    assert critique, "the critique step should see all three candidates"


def test_mcts_generate_actions_tops_up():
    client = OllamaLikeClient()
    mcts = MCTS(simulation_depth=1, exploration_weight=0.2, client=client, model="m")
    actions = mcts.generate_actions(DialogueState("sys", [], "q"))
    assert len(actions) == 3
    assert all("n" not in r for r in client.requests[1:])


def test_pvg_generate_solutions_tops_up():
    client = OllamaLikeClient()
    solutions = generate_solutions(client, "sys", "q", "m", num_solutions=3)
    assert solutions == ["answer 1", "answer 2", "answer 3"]
