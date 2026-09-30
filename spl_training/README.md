# Training SPL for creative work

SPL (System Prompt Learning) is an optillm plugin that writes its own problem-solving strategies, scores them, and adds the best ones to the system prompt of future requests. This folder has everything needed to train it on your local Ollama model, with a focus on creative tasks.

| File | What it is |
|---|---|
| `train-spl.bat` | Double-click or run from a terminal to start training |
| `train_spl.py` | The script the batch file runs. It sends prompts to optillm with learning switched on |
| `prompts/creative.jsonl` | 40 ready-made creative prompts, fictional brands only |
| `prompts/template.jsonl` | Empty template for your own prompt sets |
| `STRATEGIES.md` | The 49 strategies that ship with optillm and what each one fits |

## How learning works

For every request in learning mode, SPL makes three to five calls to the model:

1. It classifies the prompt into one problem type. Three of them are creative: `creative_ideation` (brainstorming, concepts, naming), `creative_problem_solving` (unconventional answers to a constrained problem) and `creative_writing` (copy and storytelling).
2. If the type has fewer than 10 strategies and none looks like this prompt, it asks the model to write a new strategy.
3. It answers the prompt with up to 3 strategies added to the system prompt.
4. It asks the model whether the answer followed each strategy. For the three creative types it also scores the answer's quality (see below). The result is recorded as a success or a failure.
5. Every 10 uses of a strategy, it rewrites that strategy using the latest answer.

Every 40 prompts it merges near-duplicate strategies. It also deletes strategies with 5 or more attempts whose success rate is under 30%.

Once training is done, a strategy is used in normal requests only if it has at least 5 attempts and a 40% success rate. That is why you need many prompts per problem type. Aim for at least 15 prompts of each type, run twice, and check the summary afterwards.

## How creative answers are judged

For other problem types, SPL only asks whether the answer followed the strategy. For creative work that is too weak: a strategy that says "use SCAMPER" would pass whenever the answer walks through SCAMPER, even if the ideas are flat.

So for `creative_ideation`, `creative_problem_solving` and `creative_writing` there is a second judge. It reads the brief and the answer as a demanding creative director would, and scores five criteria from 1 to 5:

| Criterion | 1 means | 5 means |
|---|---|---|
| originality | the first ideas anyone would have | surprising ideas not seen before |
| insight | no reason it would work on people | built on a sharp, true audience observation |
| relevance | ignores the brief or its constraints | answers exactly what was asked |
| feasibility | could not realistically be produced | clearly executable with the budget and time |
| craft | vague or clumsy | precise, vivid, well structured |

A strategy only earns a success if it was followed *and* the average score is 3.5 or higher. The judge is told that competent but predictable work scores 3, so ordinary answers count as failures. The score appears in the optillm window as `Creative quality: {...} -> average 3.80`. If the judge's reply cannot be read, SPL falls back to the follow-the-strategy check and logs a warning.

Two settings, set before starting optillm:

```powershell
$env:OPTILLM_SPL_CREATIVE_THRESHOLD = "3.8"     # stricter bar, default 3.5
$env:OPTILLM_SPL_JUDGE_MODEL = "gemma4:26b"      # judge with a different model
```

A separate judge model is worth trying. By default the model grades its own work, and models tend to be generous with themselves. Any model name Ollama knows works here, including the `:cloud` ones.

Each creative training prompt makes one extra call for the judge, about 20 to 40 seconds on qwen3.8. The judge is only used in learning mode, so normal requests are not slower.

The judge is a model too, so its taste has limits. Read the learned strategies yourself after training (step 4 below) and delete or edit the weak ones.

## Before you start

- Ollama must be running with the model you want to train. Strategies are specific to a model, so train the one you will use.
- Restart optillm if it was already running before the SPL fixes on the `ollama-default` branch. An older server writes strategies into the repo and crashes SPL on streamed requests.
- Plan the time. Training is slow. On qwen3.8 one creative training prompt took about 3 minutes in testing, judge included, so the creative set (40 prompts, 2 passes) takes around 4 hours. It can run unattended.

## Step 1: start from a clean slate

Your working strategies live in `%USERPROFILE%\.optillm\spl\`. They were reset to empty on 2026-09-30, and the old set is in the `backup-...` folder next to them. To reset again later, stop optillm and run:

```
spl_training\train-spl.bat --reset
```

This saves the current files into a new `backup-<date>` folder and writes empty ones. Do not just delete the files: if they are missing, optillm copies the 49 bundled strategies back on its next start.

## Step 2: run the training

```
spl_training\train-spl.bat
```

This starts optillm in its own window if it is not running, then works through `prompts/creative.jsonl` twice. Each line shows the prompt and how long it took. Other options:

```
spl_training\train-spl.bat prompts\my_prompts.jsonl --passes 3
spl_training\train-spl.bat --model gemma4:26b
spl_training\train-spl.bat --log answers.jsonl        keep every answer for review
spl_training\train-spl.bat --start 25                 resume the first pass at prompt 26
```

Press Ctrl+C to stop. The script prints the `--start` value that resumes from where you stopped. Everything learned up to that point is already saved.

## Step 3: check what was learned

```
spl_training\train-spl.bat --summary
```

The output looks like this (example numbers):

```
problem type                 total usable       best
creative_ideation                8      2       6/9
creative_problem_solving         7      1       5/8
creative_writing                 9      0       3/7
```

`usable` is the number of strategies that will be used outside learning mode. If a type shows 0, run another pass or add more prompts of that kind.

## Step 4: review the strategies by hand

Open `%USERPROFILE%\.optillm\spl\strategies.json` in an editor. Each strategy has a `problem_type`, the `strategy_text` that gets added to the prompt, and its score in `success_count` and `total_attempts`. Things worth doing:

- Delete strategies that are generic ("be creative, think outside the box"). They pass the YES/NO check easily and add nothing.
- Edit `strategy_text` directly to sharpen a good strategy, for example by adding "reject the first three ideas as too obvious" or "tie every idea to a human insight".
- To trust a hand-written strategy straight away, set `success_count` and `total_attempts` to 5 and 5.

Stop optillm first. A running server can overwrite your edits the next time it saves.

## Step 5: use it

In the chat GUI, start the server with SPL as the default approach:

```
start-optillm.bat --approach spl
```

From code or other apps, use the model name `spl-qwen3.8:latest` with base URL `http://127.0.0.1:8000/v1`. Leave out `spl_learning` so normal use does not keep changing the strategies.

## Writing your own training prompts

Copy `prompts/template.jsonl` and add one JSON object per line:

```json
{"prompt": "Brainstorm 10 concepts for ...", "temperature": 0.9, "system": "You are a senior strategist."}
```

- Write the prompts the way you really ask. SPL learns from the kind of request, so realistic briefs give useful strategies.
- Write 15 or more prompts for each kind of task, and vary the industry, the constraint and the format.
- Use a temperature of 0.8 to 1.0 for ideation and copy, and 0.2 to 0.4 for analysis.
- Romanian prompts work. Classification is done by the model. The similarity check that decides whether a prompt needs a new strategy uses English stop words, so Romanian-only sets tend to create a few more strategies.
- Use fictional brands or public information only. Client briefs, unreleased strategies, financial data and interview transcripts must not go into training prompts. Strategies store example prompts in plain text.

## Bringing back a bundled strategy

To copy one of the strategies listed in `STRATEGIES.md` into your working set:

```powershell
.venv\Scripts\python -c "import json,pathlib; src=json.load(open('optillm/plugins/spl/data/strategies.json')); p=pathlib.Path.home()/'.optillm/spl/strategies.json'; cur=json.loads(p.read_text()); cur+= [s for s in src if s['strategy_id'] in ('strategy_53','strategy_101')]; p.write_text(json.dumps(cur, indent=2))"
```

Run it from the repo root with optillm stopped. Change the IDs to the ones you want.

## Settings

Change these in `optillm/plugins/spl/config.py` if the defaults do not suit you:

| Setting | Default | Effect |
|---|---|---|
| `MAX_STRATEGIES_PER_TYPE` | 10 | Strategies kept per problem type |
| `MAX_STRATEGIES_FOR_INFERENCE` | 3 | Strategies added to one prompt |
| `MIN_SUCCESS_RATE_FOR_INFERENCE` | 0.4 | Success rate needed outside learning mode |
| `MAINTENANCE_INTERVAL` | 40 | Prompts between merge and prune runs |

Set `OPTILLM_SPL_DATA_DIR` to keep separate strategy sets, for example one per model or per team.
