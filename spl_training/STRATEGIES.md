# Bundled SPL strategies and where each one fits

These are the 49 strategies that ship with optillm in `optillm/plugins/spl/data/strategies.json`. The maintainers learned them with gemini-2.0-flash-lite on 500 OptiLLMBench questions, mostly multiple-choice maths and trivia with some law. Your working copy in `~/.optillm/spl/` was reset to empty on 2026-09-30, and the full set is backed up in `~/.optillm/spl/backup-20260930-192242/`.

The score is successes out of attempts, judged by Gemini. "Usable" means at least 5 attempts and 40% success, the bar for a strategy to be used outside learning mode. Only three pass it.

None of the 49 is about creative work. There were no strategies for `creative_writing`, and the two new creative types did not exist yet. For GRF+ work the set is mainly useful as a reference for analysis and fact-checking tasks.

## Word problems (10)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_3 | 85/192, usable | Read, list facts, organise in a table or diagram, define variables with units, solve, check | Any multi-step numeric question: budget splits, media reach maths, pricing scenarios |
| strategy_4 | 84/193, usable | Plan the steps before calculating, translate the text into an equation | Word problems where the order of operations is easy to get wrong |
| strategy_5 | 126/243, usable | Same frame, tuned for percentages and probability | Survey results, share-of-voice percentages, conversion rates |
| strategy_6 | 0/1 | Speed = distance / time, written for one train question | Only that kind of question. Too specific to reuse |
| strategy_9 | 0/0 | Percentages, profit, commission, discounts | Margin and commission calculations, price promotions |
| strategy_10 | 0/0 | Generic read, plan, solve, check | Duplicates strategy_3 |
| strategy_11 | 0/0 | Weighted averages across groups | Averaging results across segments or markets |
| strategy_12 | 0/0 | Physics word problems, starting with a diagram | Physics tasks only |
| strategy_16 | 0/0 | Generic, with emphasis on units | Duplicates strategy_3 |
| strategy_86 | 0/0 | Define a variable for each unknown price, then compare deals | "Which offer is cheaper" questions |

## Logical reasoning (10)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_85 | 4/14 | Identify question type, scan context, map entities, infer | Yes/no questions answered from a given text |
| strategy_97 | 0/0 | Judge whether an action is morally wrong by US 2020 standards | Ethics checks on scenarios. Useful as a first pass on campaign ideas that could offend |
| strategy_101 | 0/0 | Find the conclusion, premises, assumptions, what weakens or strengthens | Testing an argument, a claim in a press release, a competitor's message |
| strategy_102 | 0/0 | Extract parties, actions and intent, then pick the best-supported option | Case-style questions with several plausible answers |
| strategy_105 | 0/0 | Define every key term before reasoning | Anything where one ambiguous word changes the answer, such as legal or regulatory wording |
| strategy_109 | 0/0 | Rephrase the question, look for "implies", "same as", "necessary" | Checking whether a text supports a statement |
| strategy_110 | 0/0 | Reason with numeric constraints and ranges | Min/max questions under constraints |
| strategy_114 | 0/0 | Read the whole context, highlight facts, answer yes/no | Quick fact checks against a source |
| strategy_120 | 0/0 | Near duplicate of strategy_97 | Same as strategy_97 |
| strategy_122 | 0/0 | Sort the question into definition, inference, conditional or analogy | Mixed logic questions |

## Knowledge questions (10)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_94 | 5/21 | Understand the question, then gather and weigh the evidence | General knowledge questions with some reasoning |
| strategy_98 | 0/0 | Try direct recall first, then eliminate options | Multiple-choice trivia |
| strategy_103 | 0/0 | Read a historical passage and place it in its period | Questions based on a source text |
| strategy_106 | 0/0 | Eliminate wrong choices from what you know | Multiple-choice trivia |
| strategy_108 | 0/0 | Break the question into entities, scan context for them | Yes/no questions about a given text |
| strategy_112 | 0/0 | Rephrase, define each choice, compare | Definition questions (psychology, marketing terms) |
| strategy_116 | 0/0 | Scan context for keywords, extract, answer | Yes/no questions about a given text |
| strategy_121 | 0/0 | Find the explicit question, then the matching sentence in context | Yes/no questions about a given text |
| strategy_127 | 0/0 | Note prior knowledge about each choice | "Who was the first to" style questions |
| strategy_128 | 0/0 | Identify the entity, then read context closely | Questions about people from a bio text |

## Arithmetic (6)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_56 | 0/4 | Order of a factor group in modular arithmetic | Abstract algebra only |
| strategy_67 | 0/1 | Cost price and profit formulas | Retail pricing questions |
| strategy_92 | 0/3 | Classify the concept (average, percentage, rate), then compute | Everyday numeric questions |
| strategy_100 | 0/0 | Proton polarisation formula | Physics only |
| strategy_111 | 0/0 | Prime factorisation and counting divisors | Number theory only |
| strategy_129 | 0/0 | Train crossing a platform | Only that kind of question |

## Decision making (4)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_47 | 0/3 | Find the core legal issue, sort the facts by party | Legal liability scenarios |
| strategy_53 | 0/2 | Define the objective, constraints and criteria, then score the options | Choosing between campaign routes, vendors or channels. The closest match to agency decisions |
| strategy_90 | 0/0 | Find the core concept, then test each option against it | Audit and fraud questions |
| strategy_126 | 0/0 | State the goal, note the constraints, compare options | Presentation and data-visualisation choices |

## Statistics (4)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_95 | 1/4 | Mean and standard deviation, how many SDs a value is from the mean | Reading survey or campaign KPI spreads |
| strategy_99 | 0/2 | Identify the statistical problem type before calculating | Mixed statistics questions |
| strategy_107 | 0/1 | Separate correlation from causation, check study design | Judging research claims before quoting them in a release |
| strategy_119 | 0/0 | Median and mean from a frequency table | Grouped survey data |

## Algebra (3), information retrieval (1), sequences (1)

| ID | Score | What it does | Fits best |
|---|---|---|---|
| strategy_65 | 0/3 | Clear fractions, simplify, solve for a ratio | Ratio equations |
| strategy_89 | 0/1 | Rewrite powers to a common base | Exponent equations |
| strategy_125 | 0/0 | Translate a word problem into an algebraic equation | Algebra word problems |
| strategy_73 | 0/1 | Extract keywords, clarify the question, search the context | Answering questions from a document or brief |
| strategy_117 | 0/1 | Look at differences between terms to find the rule | Number patterns |

## What to keep if you want some of them back

Only strategy_3, strategy_4 and strategy_5 have real evidence behind them. strategy_53 (decision criteria), strategy_101 (argument testing), strategy_107 (correlation versus causation) and strategy_97 (ethics check) are the ones closest to agency work, but they were never properly tested. The tutorial explains how to copy individual strategies into your working file.
