"""Claude Code status line.

Display order, left to right, with the toggle that controls each part:
  80k ██████░░░░     context tokens used, drawn inside the bar           SHOW_TOKENS_INSIDE_BAR
  770k               tokens used, when not inside the bar                SHOW_TOKEN_COUNTS
  /1000k             window size added after the tokens used             SHOW_CONTEXT_WINDOW_SIZE
  77% / 82% / 7%     percent numbers on all three usage parts            SHOW_USAGE_PERCENTAGES
  77% ██████░░░░     context window percent and bar                      SHOW_CONTEXT_USAGE
  5h:82% ████░░      5-hour limit percent and bar                        SHOW_FIVE_HOUR_LIMIT
  7d:7% ░░░░░░░░░░   7-day limit percent and bar                         SHOW_SEVEN_DAY_LIMIT
  21:30 / 17.09      reset time / date, only above the threshold         SHOW_LIMIT_RESET, RESET_THRESHOLD_PERCENT
  12:20 92%          percent joins the inside label when very full       PERCENT_INSIDE_BAR_THRESHOLD
                     reset drawn inside the filled bar when it fits      SHOW_RESET_INSIDE_BAR
  stone face         caveman mode is active                              SHOW_CAVEMAN_MODE
  shell              folder has a .serena directory                      SHOW_SERENA_MARKER
  Opus 5             model name, coloured per family                     SHOW_MODEL_NAME
  thinking + circle  thinking is on; circle shows effort level           SHOW_THINKING_AND_EFFORT
  $190               session cost in dollars                             SHOW_COST
  clock 843m         session duration in minutes                         SHOW_DURATION
  down 89k           output tokens, whole session                        SHOW_OUTPUT_TOKENS
                     count every reply of the session, not the last one  OUTPUT_TOKENS_WHOLE_SESSION
  ↯770k              tokens read from cache                              SHOW_CACHE_TOKENS
  v2.1.267           Claude Code version                                 SHOW_VERSION
  PAB-3344           git branch, or worktree name when no branch         SHOW_GIT_BRANCH
  repo name          git repository name                                 SHOW_REPO_NAME
  folder name        current directory name                              SHOW_FOLDER_NAME
  VIM:INSERT         vim mode, when vim mode is on                       SHOW_VIM_MODE
  style:<name>       output style, when not the default                  SHOW_OUTPUT_STYLE

Bars are green below 60%, yellow below 80%, red above.
Labels drawn inside a bar use dark text on the bar colour, and move outside when too wide.
When repo name and folder name are equal, only the repo name is shown.
"""

# Display toggles - one per part, in display order
SHOW_TOKENS_INSIDE_BAR = True
SHOW_TOKEN_COUNTS = True
SHOW_CONTEXT_WINDOW_SIZE = False
SHOW_USAGE_PERCENTAGES = False
SHOW_CONTEXT_USAGE = True
SHOW_FIVE_HOUR_LIMIT = True
SHOW_SEVEN_DAY_LIMIT = True
SHOW_LIMIT_RESET = True
RESET_THRESHOLD_PERCENT = 70
PERCENT_INSIDE_BAR_THRESHOLD = 90
SHOW_RESET_INSIDE_BAR = True
SHOW_CAVEMAN_MODE = True
SHOW_SERENA_MARKER = True
SHOW_MODEL_NAME = True
SHOW_THINKING_AND_EFFORT = True
SHOW_COST = True
SHOW_DURATION = True
SHOW_OUTPUT_TOKENS = False
OUTPUT_TOKENS_WHOLE_SESSION = False
SHOW_CACHE_TOKENS = False
SHOW_VERSION = False
SHOW_GIT_BRANCH = True
SHOW_REPO_NAME = False
SHOW_FOLDER_NAME = False
SHOW_VIM_MODE = False
SHOW_OUTPUT_STYLE = False

import sys
import json
import subprocess
import os
import io
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
WHITE = '\033[37m'
ORANGE = '\033[38;5;214m'

def fmt_tokens(n):
    try:
        n = int(n or 0)
    except Exception:
        return '0'
    return f"{round(n/1000)}k"

def get(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return d if d is not None else default

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.stdout.write('[status error]\n')
    sys.exit(0)

model_raw = get(data, 'model', 'display_name', default='') or get(data, 'model', default='') or 'unknown'
if isinstance(model_raw, dict):
    model_raw = model_raw.get('display_name', 'unknown')

cwd = get(data, 'workspace', 'current_dir') or get(data, 'cwd') or '?'
ctx = get(data, 'context_window', default={})
used_pct = get(ctx, 'used_percentage')
total_input = get(ctx, 'total_input_tokens', default=0) or 0
ctx_size = get(ctx, 'context_window_size', default=0) or 0
output_tokens = get(ctx, 'total_output_tokens', default=0) or 0
cur = get(ctx, 'current_usage', default={})
cache_read = get(cur, 'cache_read_input_tokens', default=0) or 0
cache_write = get(cur, 'cache_creation_input_tokens', default=0) or 0

repo_owner = get(data, 'workspace', 'repo', 'owner', default='')
repo_name = get(data, 'workspace', 'repo', 'name', default='')
git_worktree = get(data, 'workspace', 'git_worktree', default='')
worktree_branch = get(data, 'worktree', 'branch', default='')

transcript_path = get(data, 'transcript_path', default='')
session_name = get(data, 'session_name', default='')
version = get(data, 'version', default='?')
cost_usd = get(data, 'cost', 'total_cost_usd')
duration_ms = get(data, 'cost', 'total_duration_ms')
thinking = get(data, 'thinking', 'enabled', default=False)
effort_level = get(data, 'effort', 'level', default='')
vim_mode = get(data, 'vim', 'mode', default='')
output_style = get(data, 'output_style', 'name', default='')

rl = get(data, 'rate_limits', default={})
five_hr_pct = get(rl, 'five_hour', 'used_percentage')
five_hr_reset = get(rl, 'five_hour', 'resets_at')
week_pct = get(rl, 'seven_day', 'used_percentage')
week_reset = get(rl, 'seven_day', 'resets_at')


# Git branch
git_branch = worktree_branch or ''
if not git_branch and cwd and cwd != '?':
    try:
        r = subprocess.run(
            ['git', '--no-optional-locks', 'branch', '--show-current'],
            capture_output=True, text=True, cwd=cwd, timeout=2
        )
        git_branch = r.stdout.strip()
    except Exception:
        pass

folder = os.path.basename(cwd) if cwd and cwd != '?' else '?'

model_short = str(model_raw).replace('Claude ', '').split(' (')[0]
ml = model_short.lower()
if 'opus' in ml:
    model_color = RED if '4.8' in model_short else ORANGE if '4.6' in model_short else MAGENTA
elif 'sonnet' in ml:
    model_color = CYAN
elif 'haiku' in ml:
    model_color = GREEN
else:
    model_color = WHITE

def bar_color(pct):
    ui = int(round(float(pct)))
    return RED if ui >= 80 else YELLOW if ui >= 60 else GREEN

BACKGROUND_FOR_BAR_COLOR = {RED: '\033[41m', YELLOW: '\033[43m', GREEN: '\033[42m'}

def filled_cells(pct, width=10):
    return int(round(float(pct))) * width // 100

def session_output_tokens(path):
    total = 0
    try:
        with open(path) as transcript:
            for line in transcript:
                if '"output_tokens"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                message = entry.get('message')
                usage = message.get('usage') if isinstance(message, dict) else None
                if isinstance(usage, dict):
                    total += usage.get('output_tokens') or 0
    except Exception:
        return 0
    return total

def with_percent(label, percent, pct, width=10):
    if not label or percent < PERCENT_INSIDE_BAR_THRESHOLD:
        return label
    combined = f"{label} {percent}%"
    return combined if len(combined) <= filled_cells(pct, width) else label

def make_bar(pct, width=10, label=''):
    filled = filled_cells(pct, width)
    color = bar_color(pct)
    empty = f"{DIM}{'░' * (width - filled)}{RESET}"
    if label and len(label) <= filled:
        background = BACKGROUND_FOR_BAR_COLOR.get(color, '')
        return f"{background}\033[30m{BOLD}{label}{RESET}{color}{'█' * (filled - len(label))}{empty}"
    return f"{color}{'█' * filled}{empty}"

effort_color = {
    'low':   BLUE,
    'medium': GREEN,
    'high':  YELLOW,
    'xhigh': ORANGE,
    'max':   RED,
}.get(effort_level, model_color)

effort_circle = {
    'low':   '🔵',
    'medium': '🟢',
    'high':  '🟡',
    'xhigh': '🟠',
    'max':   '🔴',
}.get(effort_level, '')

think_glyph = f'🤔{effort_circle}' if thinking else effort_circle
if not SHOW_THINKING_AND_EFFORT:
    think_glyph = ''
inner = f"{model_color}{model_short}{RESET}{think_glyph}" if SHOW_MODEL_NAME else think_glyph

cost_dur = ''
if SHOW_COST and cost_usd is not None and float(cost_usd) > 0:
    cost_dur += f" {DIM}${round(float(cost_usd))}{RESET}"
if SHOW_DURATION and duration_ms is not None:
    secs = int(float(duration_ms) / 1000)
    dur = f"{secs // 60}m"
    cost_dur += f" {DIM}⏱ {dur}{RESET}"

# --- Line 1: stats ---
s = []

def format_reset(resets_at, time_format='%H:%M'):
    if not resets_at:
        return ''
    try:
        text = str(resets_at).strip()
        if text.replace('.', '', 1).isdigit():
            moment = datetime.fromtimestamp(float(text), timezone.utc)
        else:
            moment = datetime.fromisoformat(text.replace('Z', '+00:00'))
        return moment.astimezone().strftime(time_format)
    except Exception:
        return ''

if used_pct is not None and (SHOW_CONTEXT_USAGE or SHOW_TOKEN_COUNTS):
    used_percent = int(round(float(used_pct)))
    percent_color = bar_color(used_pct)
    token_counts = fmt_tokens(total_input) if SHOW_TOKEN_COUNTS else ""
    if token_counts and SHOW_CONTEXT_WINDOW_SIZE and ctx_size:
        token_counts += f"/{fmt_tokens(ctx_size)}"
    if SHOW_CONTEXT_USAGE:
        percent_text = f"{percent_color}{used_percent}%" if SHOW_USAGE_PERCENTAGES else ''
        inside_label = fmt_tokens(total_input) if SHOW_TOKENS_INSIDE_BAR else ''
        inside_label = with_percent(inside_label, used_percent, used_pct)
        inside = bool(inside_label) and len(inside_label) <= filled_cells(used_pct)
        if inside:
            token_counts = ''
        separator = ':' if token_counts and percent_text else ''
        bar = make_bar(used_pct, label=inside_label if inside else '')
        gap = ':' if (token_counts and not SHOW_CONTEXT_WINDOW_SIZE) else ' '
        prefix = f"{DIM}{token_counts}{separator}{percent_text}{gap}{RESET}" if (token_counts or percent_text) else ''
        s.append(f"{prefix}{bar}")
    elif token_counts:
        s.append(f"{DIM}{token_counts}{RESET}")

if SHOW_FIVE_HOUR_LIMIT and five_hr_pct is not None:
    fh = int(round(float(five_hr_pct)))
    bc = bar_color(five_hr_pct)
    show_reset = SHOW_LIMIT_RESET and fh > RESET_THRESHOLD_PERCENT
    reset_label = format_reset(five_hr_reset) if show_reset else ''
    percent_text = f"{bc}{fh}%" if SHOW_USAGE_PERCENTAGES else ''
    inside_label = with_percent(reset_label, fh, five_hr_pct)
    inside = SHOW_RESET_INSIDE_BAR and reset_label and len(inside_label) <= filled_cells(five_hr_pct)
    reset_suffix = f" {DIM}{reset_label}{RESET}" if (reset_label and not inside) else ''
    bar = make_bar(five_hr_pct, width=10, label=inside_label if inside else '')
    gap = '' if (not percent_text and not reset_suffix) else ' '
    s.append(f"{DIM}5h:{percent_text}{RESET}{reset_suffix}{gap}{bar}")

if SHOW_SEVEN_DAY_LIMIT and week_pct is not None:
    wk = int(round(float(week_pct)))
    bc = bar_color(week_pct)
    show_reset = SHOW_LIMIT_RESET and wk > RESET_THRESHOLD_PERCENT
    reset_label = format_reset(week_reset, '%d.%m') if show_reset else ''
    percent_text = f"{bc}{wk}%" if SHOW_USAGE_PERCENTAGES else ''
    inside_label = with_percent(reset_label, wk, week_pct)
    inside = SHOW_RESET_INSIDE_BAR and reset_label and len(inside_label) <= filled_cells(week_pct)
    reset_suffix = f" {DIM}{reset_label}{RESET}" if (reset_label and not inside) else ''
    bar = make_bar(week_pct, width=10, label=inside_label if inside else '')
    gap = '' if (not percent_text and not reset_suffix) else ' '
    s.append(f"{DIM}7d:{percent_text}{RESET}{reset_suffix}{gap}{bar}")

token_parts = []

if SHOW_OUTPUT_TOKENS:
    shown_output = output_tokens
    if OUTPUT_TOKENS_WHOLE_SESSION and transcript_path:
        shown_output = session_output_tokens(transcript_path) or output_tokens
    if int(shown_output) > 0:
        token_parts.append(f"{DIM}↓{fmt_tokens(shown_output)}{RESET}")

if SHOW_CACHE_TOKENS and int(cache_read) > 0:
    token_parts.append(f"{DIM}↯{GREEN}{fmt_tokens(cache_read)}{RESET}")


markers = []

try:
    if not SHOW_CAVEMAN_MODE:
        raise RuntimeError('caveman marker off')
    caveman_flag = os.path.join(os.environ.get('CLAUDE_CONFIG_DIR') or os.path.expanduser('~/.claude'), '.caveman-active')
    with open(caveman_flag, 'r') as f:
        caveman_mode = f.read().strip()
    if caveman_mode and caveman_mode != 'off':
        markers.append("🗿")
except Exception:
    pass

if SHOW_SERENA_MARKER and cwd and cwd != '?' and os.path.isdir(os.path.join(cwd, '.serena')):
    markers.append("🐚")

model_part = f"{''.join(markers)}{inner}{cost_dur}"
if model_part.strip():
    s.append(model_part)
s.extend(token_parts)
if SHOW_VERSION:
    s.append(f"{DIM}v{version}{RESET}")

line1 = ' '.join(s)

# --- Line 2: identity ---
p2 = []

identity = []
if SHOW_GIT_BRANCH and git_branch:
    identity.append(f"{BOLD}\033[38;5;66m{git_branch}{RESET}")
elif SHOW_GIT_BRANCH and git_worktree:
    identity.append(f"{BOLD}\033[38;5;66mworktree:{git_worktree}{RESET}")
if SHOW_REPO_NAME and repo_name:
    identity.append(f"{BOLD}\033[38;5;136m{repo_name}{RESET}")
if identity:
    p2.append(f"{DIM}:{RESET}".join(identity))

show_folder = SHOW_FOLDER_NAME and folder and folder != '?'
if show_folder and SHOW_REPO_NAME and repo_name == folder:
    show_folder = False
if show_folder:
    p2.append(f"{BOLD}\033[38;5;67m{folder}{RESET}")

if SHOW_VIM_MODE and vim_mode:
    vc = {'INSERT': GREEN, 'NORMAL': BLUE}.get(vim_mode, MAGENTA if 'VISUAL' in vim_mode else WHITE)
    p2.append(f"{BOLD}{vc}VIM:{vim_mode}{RESET}")

if SHOW_OUTPUT_STYLE and output_style and output_style.lower() not in ('default', ''):
    p2.append(f"{DIM}style:{output_style}{RESET}")


line2 = '  '.join(p2)

parts = [x for x in [line1, line2] if x]
sys.stdout.write('  '.join(parts) + '\n')
sys.stdout.flush()
