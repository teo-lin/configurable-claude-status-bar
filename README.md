# configurable-claude-status-bar

A fully configurable Claude Code status line. One Python file, no dependencies.

```
144k:█░░░░░░░░░ 5h:12:20 88%███░░ 7d:17.09░░ 🗿🐚Opus 5🤔🟡 $190 ⏱ 29m ↓108k ↯147k PAB-3344
```

## What it shows

Context window use, the 5-hour and 7-day limits with their reset time and date, session cost
and duration, output and cache tokens, model with thinking and effort marks, git branch, and
more. Bars are green below 60%, yellow below 80%, red above. Labels are drawn inside the
filled part of a bar when they fit.

## Install

1. Clone this repository.
2. Copy the `statusLine` block from `settings.example.json` into `~/.claude/settings.json`,
   with the absolute path to `statusline-command.py`.
3. Start Claude Code. The line appears under the prompt.

Requires Python 3. Nothing to install.

## Configure

Every part has an on/off switch at the top of `statusline-command.py`, listed in display
order. Set a switch to `False` to hide that part:

```python
SHOW_TOKEN_COUNTS = True
SHOW_CONTEXT_WINDOW_SIZE = False
SHOW_VERSION = False
```

Two thresholds control the labels inside the bars:

| Constant | Meaning |
| --- | --- |
| `RESET_THRESHOLD_PERCENT` | Above this percent, the reset time or date appears. |
| `PERCENT_INSIDE_BAR_THRESHOLD` | Above this percent, the percent joins the label inside the bar. |

The comment at the top of the file lists each part, an example of it, and its switch.

## Try a change without Claude Code

The script reads the session data on standard input, so you can render any state by hand:

```bash
echo '{"cwd":"/tmp","model":{"display_name":"Claude Opus 5"},
"context_window":{"used_percentage":77,"total_input_tokens":770000,"context_window_size":1000000},
"rate_limits":{"five_hour":{"used_percentage":88,"resets_at":1789032000}}}' \
  | python3 statusline-command.py
```
