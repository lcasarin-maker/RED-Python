"""Tests para el validador federado de conocimiento y vaults locales (lint-vault)."""
import pytest
from pathlib import Path
from scripts.protocol_cli import ProtocolClient


def test_lint_vault_with_broken_links(tmp_path):
    wiki_dir = tmp_path / "docs" / "knowledge"
    wiki_dir.mkdir(parents=True)
    
    note1 = wiki_dir / "note1.md"
    note1.write_text("Hello [[note2_broken]]", encoding="utf-8")
    
    cli = ProtocolClient()
    code = cli.command_lint_vault(str(tmp_path))
    assert code != 0  # FAIL

def test_lint_vault_passing(tmp_path):
    wiki_dir = tmp_path / "docs" / "knowledge"
    wiki_dir.mkdir(parents=True)
    
    note1 = wiki_dir / "note1.md"
    note1.write_text("Link to [[note2]]", encoding="utf-8")
    note2 = wiki_dir / "note2.md"
    note2.write_text("Back to [[note1]]", encoding="utf-8")
    
    cli = ProtocolClient()
    code = cli.command_lint_vault(str(tmp_path))
    assert code == 0
