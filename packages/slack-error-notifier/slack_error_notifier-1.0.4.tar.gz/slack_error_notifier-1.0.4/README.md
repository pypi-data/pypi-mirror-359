---
## 1. Purpose
A tiny helper that emits a Slack message whenever your Python code raises an *uncaught* exception.  
Designed for cron/ETL scripts, ad-hoc maintenance jobs, CI steps and any service where a Slack ping is easier than trawling logs.

*No daemons • No infra agents • Pure Python import*

---
## 2. Requirements
* Python ≥ 3.7 (tested through 3.12)  
* `slack_sdk` ≥ 3.19  — installed automatically by `pip`

---
## 3. Installation (private sources)
```bash
# Git-over-SSH (GitLab / GitHub Enterprise)
pip install git+ssh://git@our-git.example.com/infra/slack-error-notifier.git

# Private PyPI example
pip install --index-url https://pypi.ourcompany.com/simple slack-error-notifier==1.*
```
The library is a *single file* (`slack_error_notifier.py`).  If you prefer you
may simply copy that file into any repository and commit it.

---
## 4. Configuration
| Variable | Required | Purpose |
|----------|:-------:|---------|
| `SLACK_BOT_TOKEN`        | **✓** | Bot token with `chat:write` scope (`xoxb-…`) |
| `SLACK_ERROR_CHANNEL_ID` | ‑ | Default Slack channel to post to (`C01…`). Can be overridden per-call via `channel=` |

Set them in the *runtime environment* of the script/service.  Examples:
```bash
# Bash / Z-shell
export SLACK_BOT_TOKEN="xoxb-…"
export SLACK_ERROR_CHANNEL_ID="C01ABCDE"

# PowerShell
$Env:SLACK_BOT_TOKEN        = "xoxb-…"
$Env:SLACK_ERROR_CHANNEL_ID = "C01ABCDE"
```
Alternatively pass `token=` / `channel=` directly to every call (see API).

---
## 5. Public API (all reside in `slack_error_notifier`)
### 5.1  `notify_failure()` – low-level helper
```python
notify_failure(job_name: str,
               message: str,
               owners: Iterable[str] | None = None,
               *,
               channel: str | None = None,
               token: str | None = None) -> bool
```
Sends *one* message. Returns **True** if Slack confirmed delivery.

### 5.2  `slack_error_handler()` – decorator factory
```python
slack_error_handler(job_name: str | None = None,
                    owners: Iterable[str] | None = None,
                    *,
                    channel: str | None = None,
                    token: str | None = None,
                    reraise: bool = True) -> Callable[[F], F]
```
Wrap a function; if that function raises, the traceback is posted, then the
exception is optionally re-raised.

### 5.3  `SlackErrorReporter` – context manager
```python
SlackErrorReporter(job_name: str,
                   owners: Iterable[str] | None = None,
                   *,
                   channel: str | None = None,
                   token: str | None = None,
                   reraise: bool = True)
```
`with SlackErrorReporter(…):` → any exception inside the `with` block triggers
a post.

### 5.4  `setup_error_reporting()` – global hook
```python
setup_error_reporting(job_name: str,
                      owners: Iterable[str] | None = None,
                      *,
                      channel: str | None = None,
                      token: str | None = None)
```
Installs a process-wide `sys.excepthook`.  **One call per entry-point**.

---
## 6. Integration matrix
| ID | Pattern (import name)      | Scope covered                       | Modification needed | Pros | Cons |
|----|----------------------------|-------------------------------------|---------------------|------|------|
| A  | *Global hook* (`setup_error_reporting`) | Entire process (main thread) | 1 call at top of entry-point file | One-liner, catches everything that bubbles out | Misses exceptions swallowed by existing `try/except`; child threads need manual hook |
| B  | *Decorator* (`slack_error_handler`) | The decorated function         | Add `@slack_error_handler()` above function | Zero boilerplate inside body; easy to target | Multiple decorators required for many functions |
| C  | *Context manager* (`SlackErrorReporter`) | Arbitrary code block          | Wrap block with `with` | Fine-grained; works in async & threads | Slightly verbose; must select blocks manually |
| D  | *Direct call* (`notify_failure`) | Manual                          | Call in your own `except` | Maximum control (custom messages, conditional send) | You must remember to call it everywhere |

Choose **A** for most batch scripts, **B** for reusable utilities, **C** for a
few critical statements, **D** when you already have elaborate error handling.

---
## 7. Message anatomy & formatting options
```
:warning: *<job_name>* failed
<@U123ABC> <@U456DEF>      ← owners pinged (omit if None)
```text
<first 1 500 chars of traceback>
```
• Tracebacks longer than 1 500 characters are truncated (Slack block limit).  
• Text is wrapped in a triple-backtick block for mono-font readability.

---
## 8. Runtime flags / parameters
| Parameter | Where available | Default | Notes |
|-----------|-----------------|---------|-------|
| `job_name` | all helpers | function name (decorator) / `"error"` | Appears bold at top of Slack message |
| `owners`   | all helpers | `None` | List of Slack user IDs to `<@mention>` |
| `channel`  | all helpers | `SLACK_ERROR_CHANNEL_ID` | Override per-call |
| `token`    | all helpers | `SLACK_BOT_TOKEN`        | Useful for multi-workspace tooling |
| `reraise`  | decorator / ctx mgr | `True` | `False` swallows the exception after posting |

---
## 9. Performance & limits
* Overhead: ~5 ms per post (network latency not included).  
* The code calls Slack **once** per failure; there is no batching.  
* Slack rate-limits to ~1 msg/sec per bot; if you expect cascades, add your own throttling.

---
## 10. Versioning & support
* Semantic-versioned (`MAJOR.MINOR.PATCH`).  
* Breaking changes → announce in `#engineering-announce`.  
* Open issues / PRs in the private repo `infra/slack-error-notifier`.

For questions ping **@sarthak-sharma** on Slack. 

---
## 11. Practical examples

```python
# -----------------------------------------------
# A. Global hook – simplest for most batch jobs
# -----------------------------------------------
from slack_error_notifier import setup_error_reporting

setup_error_reporting(
    job_name="nightly-backup",
    owners=["U08PPJ3AXE0"],          # ping yourself
)

run_backup()          # any uncaught exception posts to Slack
```

```python
# -------------------------------------------------
# B. Decorator – protect a specific function
# -------------------------------------------------
from slack_error_notifier import slack_error_handler

@slack_error_handler(
    job_name="email-digest",
    owners=["U08PPJ3AXE0"],
    channel="C0TEAMDEV",            # override default channel
)

def send_digest():
    compile_stats()
    raise RuntimeError("SMTP down")  # will post to Slack then re-raise
```

```python
# -------------------------------------------------
# C. Context manager – wrap only part of the code
# -------------------------------------------------
from slack_error_notifier import SlackErrorReporter

fetch_data()

with SlackErrorReporter("transform-step", owners=["U08PPJ3AXE0"]):
    transform_big_dataframe()        # errors inside block → Slack

upload_results()
```

```python
# -------------------------------------------------
# D. Manual notify_failure – full DIY control
# -------------------------------------------------
from slack_error_notifier import notify_failure

try:
    risky_io()
except Exception as exc:
    # send a trimmed custom message, don't include traceback
    notify_failure(
        job_name="io-pipeline",
        message=f"I/O failed: {exc}",
        owners=["U08PPJ3AXE0"],
    )
    # decide whether to swallow or re-raise
```

```python
# -------------------------------------------------
# E. No env vars available – supply token/channel directly
# -------------------------------------------------
from slack_error_notifier import slack_error_handler

BOT_TOKEN = "xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"      # DO NOT commit real token
CHANNEL   = "C0123ABCDEF"                                 # destination channel

@slack_error_handler(
    job_name="lambda-import",
    token   = BOT_TOKEN,          # overrides env var completely
    channel = CHANNEL,
)
def handler(event, ctx):
    ...                         # any crash still posts to Slack
```

```python
# -------------------------------------------------
# F. Dry-run / unit-test – mock out the network call
# -------------------------------------------------
import slack_error_notifier as sen
from unittest.mock import patch

with patch.object(sen, "notify_failure", lambda *a, **kw: print("[DRY-RUN]", a, kw)):
    # code under test – will print instead of hitting Slack
    try:
        raise ValueError("example")
    except Exception as err:
        sen.notify_failure("dry-run", str(err))
```

Add these snippets to your project's docs or paste directly into scripts as
starter templates. 