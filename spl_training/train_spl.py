"""
Train the SPL (System Prompt Learning) plugin by sending prompts through a
running optillm server with learning mode switched on.

Usage:
    python spl_training/train_spl.py                      (prompts/creative.jsonl, 2 passes)
    python spl_training/train_spl.py prompts/mine.jsonl --passes 3 --model gemma4:26b
    python spl_training/train_spl.py --summary

Prompt files:
    .jsonl  one object per line: {"prompt": "...", "system": "...", "temperature": 0.9}
            only "prompt" is required
    .txt    one prompt per line, blank lines and lines starting with # are skipped
"""

import argparse
import json
import os
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).resolve().parent
DEFAULT_SYSTEM = "You are a helpful assistant."
MIN_ATTEMPTS = 5          # mirrors evaluation.py: attempts needed before a strategy is used outside learning
MIN_SUCCESS_RATE = 0.4    # mirrors config.MIN_SUCCESS_RATE_FOR_INFERENCE
METRIC_KEYS = ("total_queries", "strategy_applications", "strategies_created", "strategies_refined",
               "successful_resolutions", "last_strategy_id", "reasoning_examples_collected", "strategies_merged")


def load_prompts(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if path.suffix == ".jsonl":
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    sys.exit(f"{path}:{line_no}: invalid JSON ({e})")
                if "prompt" not in item:
                    sys.exit(f"{path}:{line_no}: missing \"prompt\"")
                items.append(item)
            else:
                items.append({"prompt": line})
    return items


def data_dir():
    return Path(os.environ.get("OPTILLM_SPL_DATA_DIR", Path.home() / ".optillm" / "spl"))


def reset():
    d = data_dir()
    d.mkdir(parents=True, exist_ok=True)
    backup = d / f"backup-{time.strftime('%Y%m%d-%H%M%S')}"
    backup.mkdir()
    for name in ("strategies.json", "metrics.json"):
        if (d / name).exists():
            shutil.copy2(d / name, backup / name)
    # Write empty files rather than deleting them: missing files are re-seeded from the bundled set
    (d / "strategies.json").write_text("[]", encoding="utf-8")
    (d / "metrics.json").write_text(json.dumps(dict.fromkeys(METRIC_KEYS, 0), indent=2), encoding="utf-8")
    print(f"Strategies emptied. Previous files saved in {backup}")


def print_summary():
    db = data_dir() / "strategies.json"
    if not db.exists():
        print(f"No strategy file at {db}")
        return
    strategies = json.loads(db.read_text(encoding="utf-8"))
    by_type = defaultdict(list)
    for s in strategies:
        by_type[s["problem_type"]].append(s)

    print(f"\nStrategy database: {db}")
    if not strategies:
        print("No strategies learned yet.")
        return
    print(f"{'problem type':28} {'total':>5} {'usable':>6} {'best':>10}")
    for ptype, items in sorted(by_type.items()):
        usable = [s for s in items
                  if s["total_attempts"] >= MIN_ATTEMPTS
                  and s["success_count"] / s["total_attempts"] >= MIN_SUCCESS_RATE]
        best = max(items, key=lambda s: (s["success_count"] / s["total_attempts"]) if s["total_attempts"] else 0)
        best_str = f"{best['success_count']}/{best['total_attempts']}"
        print(f"{ptype:28} {len(items):5} {len(usable):6} {best_str:>10}")
    print(f"Usable = at least {MIN_ATTEMPTS} attempts and {MIN_SUCCESS_RATE:.0%} success, "
          "the bar for use without learning mode.")


def main():
    parser = argparse.ArgumentParser(description="Train SPL strategies through an optillm server")
    parser.add_argument("prompts", type=Path, nargs="?", default=HERE / "prompts" / "creative.jsonl",
                        help=".jsonl or .txt prompt file (default: prompts/creative.jsonl)")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1", help="optillm server URL")
    parser.add_argument("--model", default="qwen3.8:latest", help="model name, the spl- prefix is added for you")
    parser.add_argument("--passes", type=int, default=2, help="how many times to run the whole prompt file")
    parser.add_argument("--start", type=int, default=0, help="skip the first N prompts of the first pass (resume)")
    parser.add_argument("--temperature", type=float, default=None, help="default temperature for prompts without one")
    parser.add_argument("--timeout", type=float, default=900, help="seconds to wait for one prompt")
    parser.add_argument("--log", type=Path, default=None, help="append prompt/answer pairs to this .jsonl file")
    parser.add_argument("--summary", action="store_true", help="only print the strategy summary and exit")
    parser.add_argument("--reset", action="store_true", help="back up and empty the learned strategies, then exit")
    args = parser.parse_args()

    if args.reset:
        reset()
        return
    if args.summary:
        print_summary()
        return

    if not args.prompts.exists() and (HERE / args.prompts).exists():
        args.prompts = HERE / args.prompts
    prompts = load_prompts(args.prompts)
    if not prompts:
        sys.exit(f"No prompts found in {args.prompts}")

    model = args.model if args.model.startswith("spl-") else f"spl-{args.model}"
    client = OpenAI(api_key="optillm", base_url=args.base_url, timeout=args.timeout)
    total = len(prompts) * args.passes
    done = failed = 0
    started = time.time()

    print(f"Training {model} on {len(prompts)} prompts x {args.passes} passes via {args.base_url}")
    for p in range(args.passes):
        for i, item in enumerate(prompts):
            if p == 0 and i < args.start:
                continue
            done += 1
            label = f"[pass {p + 1}/{args.passes} | {i + 1}/{len(prompts)} | {done}/{total}]"
            print(f"{label} {item['prompt'][:70]!r}", flush=True)

            kwargs = {}
            temperature = item.get("temperature", args.temperature)
            if temperature is not None:
                kwargs["temperature"] = temperature
            t0 = time.time()
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": item.get("system", DEFAULT_SYSTEM)},
                        {"role": "user", "content": item["prompt"]},
                    ],
                    extra_body={"spl_learning": True},
                    **kwargs,
                )
                answer = response.choices[0].message.content or ""
            except KeyboardInterrupt:
                print(f"\nStopped. Resume with --start {i} (pass {p + 1}).")
                print_summary()
                return
            except Exception as e:
                failed += 1
                print(f"    failed: {e}")
                continue

            print(f"    ok in {time.time() - t0:.0f}s, {len(answer)} chars")
            if args.log:
                with open(args.log, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"pass": p + 1, "prompt": item["prompt"], "answer": answer},
                                       ensure_ascii=False) + "\n")

    minutes = (time.time() - started) / 60
    print(f"\nFinished {done - failed}/{done} prompts in {minutes:.1f} min ({failed} failed)")
    print_summary()


if __name__ == "__main__":
    main()
