#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D13 Observable Behavior (Sprint 28.5): HOOK channel - agent observability,
not repo pass/fail. Consolidates the four d13_* scripts (token meter, decision
logger, divergence detector, D13Report) into one module (S19, copied without a
bridge). The gate SKIPS it; its role in the Stop hook is to OBSERVE the session
(token usage), not to block.

tiktoken is optional: if it is missing, count_tokens degrades to 0 (the hook
does not crash)."""
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dimensions.context import AuditContext

try:
    import tiktoken
except ImportError:
    tiktoken = None

logger = logging.getLogger("dimensions.d13")


def count_tokens(file_path: str) -> int:
    """cl100k_base tokens for a file. 0 if it does not exist or tiktoken is missing."""
    if tiktoken is None:
        logger.debug("tiktoken ausente: count_tokens degrada a 0")
        return 0
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return 0
    return len(tiktoken.get_encoding("cl100k_base").encode(content))


def estimate_cost(tokens: int, rate_per_1k: float = 0.002) -> float:
    return (tokens / 1000) * rate_per_1k


class DecisionLogger:
    """Logs agent decisions in JSONL (behavioral observability)."""

    def __init__(self, log_dir: str = "~/.cerberus/decision_logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"decisions_{now}.jsonl"

    def log_decision(
        self,
        agent: str,
        decision: str,
        reasoning: str,
        action: str,
        result: str,
        metadata: dict = None,
    ) -> str:
        decision_id = str(uuid.uuid4())
        record = {
            "decision_id": decision_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
            "action": action,
            "result": result,
            "metadata": metadata or {},
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return decision_id


class DivergenceDetector:
    """Detects divergence between an action and the CAN/NO-CAN rules in AGENT.md."""

    def __init__(self, agent_md_path: str = "AGENT.md"):
        self.agent_md = Path(agent_md_path)
        self.can_do, self.cannot_do = set(), set()
        self._parse_agent_md()

    def _parse_agent_md(self):
        if not self.agent_md.exists():
            return
        content = self.agent_md.read_text(encoding="utf-8")
        for match in re.finditer(r"PUEDE:\s*([^\n]+)", content):
            self.can_do.add(match.group(1).strip().lower())
        for match in re.finditer(r"NO PUEDE:\s*([^\n]+)", content):
            self.cannot_do.add(match.group(1).strip().lower())

    def check(self, action: str, context: str = None) -> dict:
        low = action.lower()
        if low in self.cannot_do:
            return {
                "action": action,
                "allowed": False,
                "severity": "CRITICAL",
                "reason": f"'{action}' en NO PUEDE",
                "context": context,
            }
        if low in self.can_do:
            return {
                "action": action,
                "allowed": True,
                "severity": "OK",
                "reason": f"'{action}' en PUEDE",
                "context": context,
            }
        return {
            "action": action,
            "allowed": False,
            "severity": "WARNING",
            "reason": f"'{action}' not explicit",
            "context": context,
        }


class D13Report:
    """Orchestrator/dashboard: manifest token cost + decisions."""

    def __init__(self, max_decisions: int = 100):
        self.max_decisions = max_decisions
        self.decision_logger = DecisionLogger()
        self.divergence_detector = DivergenceDetector()
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def _load_token_data(self) -> dict:
        root = Path(".").resolve()
        files = {
            "SPEC.md": root / "SPEC.md",
            "AGENT.md": root / "AGENT.md",
            "PLAN.md": root / "PLAN.md",
        }
        data, total = {}, 0
        for label, path in files.items():
            tokens = count_tokens(str(path))
            total += tokens
            data[label] = {
                "tokens": tokens,
                "cost_usd": round(estimate_cost(tokens), 6),
            }
        data["TOTAL"] = {"tokens": total, "cost_usd": round(estimate_cost(total), 6)}
        return data

    def _load_recent_decisions(self) -> list:
        decisions = []
        if self.decision_logger.log_file.exists():
            with open(self.decision_logger.log_file, "r", encoding="utf-8") as f:
                decisions = [json.loads(line) for line in f]
        return decisions[-self.max_decisions :]

    def generate_json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "tokens": self._load_token_data(),
            "recent_decisions": self._load_recent_decisions(),
            "divergence_rules": {
                "can_do": list(self.divergence_detector.can_do),
                "cannot_do": list(self.divergence_detector.cannot_do),
            },
        }

    def generate_html(self) -> str:
        data = self.generate_json()
        total = data["tokens"].get("TOTAL", {})
        return (
            "<html><head><title>D13 Observable Behavior</title></head><body>"
            f"<h1>D13 Observable Behavior</h1><p>timestamp: {data['timestamp']}</p>"
            f"<p>tokens TOTAL: {total.get('tokens', 0)} (${total.get('cost_usd', 0)})</p>"
            f"<p>decisiones recientes: {len(data['recent_decisions'])}</p></body></html>"
        )


class D13Observable:
    """D13 dimension (hook channel): observability of agent behavior."""

    id = "d13"
    name = "OBSERVABLE BEHAVIOR"
    channel = "hook"

    def audit(self, ctx: AuditContext) -> list:
        """Hook channel: does not audit the repo. The gate skips it."""
        return []

    def observe_session(self, transcript_path: str) -> dict:
        """Adds up token usage for assistant messages in the transcript (observes
        the session in the Stop hook). Counts ONLY from the last /compact marker
        (line with isCompactSummary:true) to avoid false positives when the JSONL
        accumulates prior history."""
        try:
            with open(transcript_path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except OSError as exc:
            logger.warning(
                "observe_session: unreadable transcript %s: %s", transcript_path, exc
            )
            return {"assistant_messages": 0, "output_tokens": 0}
        # Find the last compact marker (isCompactSummary:true) and start there.
        # This Claude Code version does NOT emit type=="summary"; the real marker is
        # a type=="user" line with isCompactSummary:true. Without this, the entire
        # session would be measured.
        last_summary_idx = -1
        for idx, line in enumerate(lines):
            obj = _parse_line(line)
            if obj is not None and obj.get("isCompactSummary"):
                last_summary_idx = idx
        session_lines = lines[last_summary_idx + 1 :]
        msgs, out_tokens = 0, 0
        for line in session_lines:
            obj = _parse_line(line)
            if obj is None or obj.get("type") != "assistant":
                continue
            msgs += 1
            out_tokens += (
                obj.get("message", {}).get("usage", {}).get("output_tokens", 0) or 0
            )
        return {"assistant_messages": msgs, "output_tokens": out_tokens}


def _parse_line(line: str):
    """Parses a JSONL line; returns None if empty or non-JSON (logged, not silent)."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        logger.debug("non-JSON transcript line skipped")
        return None
