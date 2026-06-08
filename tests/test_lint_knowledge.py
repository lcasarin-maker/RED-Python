#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for lint_knowledge.py
"""

import sys
import yaml
from pathlib import Path
import pytest

# Adjust PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import lint_knowledge

@pytest.fixture
def setup_mock_vault(tmp_path, monkeypatch):
    """Sets up a temporary directory structure mimicking the Golden Standard repo."""
    gs_dir = tmp_path / "VibeCoding_GoldenStandard"
    wiki_dir = gs_dir / "Wiki"
    
    gs_dir.mkdir(parents=True)
    wiki_dir.mkdir(parents=True)
    
    monkeypatch.setattr(lint_knowledge, "GS_DIR", gs_dir)
    monkeypatch.setattr(lint_knowledge, "WIKI_DIR", wiki_dir)
    
    return gs_dir, wiki_dir

class TestLintKnowledge:
    def test_validate_yaml_integrity_clean(self, setup_mock_vault):
        """Verifies clean YAML passes validation."""
        gs_dir, _ = setup_mock_vault
        
        yaml_content = {
            "vices": [
                {
                    "id": "VC-111",
                    "title": "Uncommented gitignore exclusions",
                    "symptom": "Secrets exposed",
                    "cause": "Laxity",
                    "solution": "Add comments"
                },
                {
                    "id": "VC-112",
                    "title": "Another Vice",
                    "symptom": "Buggy code",
                    "cause": "Speed",
                    "solution": "Slow down"
                }
            ]
        }
        
        with open(gs_dir / "golden_standard_coding_vices.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(yaml_content, f)
            
        errors = lint_knowledge.validate_yaml_integrity()
        assert len(errors) == 0

    def test_validate_yaml_integrity_duplicate(self, setup_mock_vault):
        """Verifies duplicate IDs across YAML files are flagged."""
        gs_dir, _ = setup_mock_vault
        
        yaml_content_1 = {
            "vices": [{"id": "VC-111", "title": "A", "symptom": "A", "cause": "A", "solution": "A"}]
        }
        yaml_content_2 = {
            "testing_vices": [{"id": "VC-111", "title": "B", "symptom": "B", "cause": "B", "solution": "B"}]
        }
        
        with open(gs_dir / "golden_standard_coding_vices.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(yaml_content_1, f)
        with open(gs_dir / "golden_standard_testing_vices.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(yaml_content_2, f)
            
        errors = lint_knowledge.validate_yaml_integrity()
        assert any("Duplicate ID found across Golden Standard: 'VC-111'" in err for err in errors)

    def test_validate_yaml_integrity_invalid_format(self, setup_mock_vault):
        """Verifies incorrect ID formatting is flagged."""
        gs_dir, _ = setup_mock_vault
        
        # VC-ABC instead of VC-123
        yaml_content = {
            "vices": [{"id": "VC-ABC", "title": "A", "symptom": "A", "cause": "A", "solution": "A"}]
        }
        
        with open(gs_dir / "golden_standard_coding_vices.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(yaml_content, f)
            
        errors = lint_knowledge.validate_yaml_integrity()
        assert any("invalid ID format: 'VC-ABC'" in err for err in errors)

    def test_check_wiki_links_clean(self, setup_mock_vault):
        """Verifies clean wiki links and relationships pass check."""
        _, wiki_dir = setup_mock_vault
        
        # Create Home page, VC-111 note and VC-112 note
        (wiki_dir / "Home.md").write_text("Welcome to [[VC-111]] and [[VC-112]]", encoding="utf-8")
        (wiki_dir / "VC-111.md").write_text("This is VC-111 linking back to [[Home]]", encoding="utf-8")
        (wiki_dir / "VC-112.md").write_text("This is VC-112 linking to [VC-111](VC-111.md)", encoding="utf-8")
        
        errors, orphans = lint_knowledge.check_wiki_links()
        assert len(errors) == 0
        assert len(orphans) == 0

    def test_check_wiki_links_broken_obsidian(self, setup_mock_vault):
        """Verifies broken Obsidian links [[NonExistent]] are flagged."""
        _, wiki_dir = setup_mock_vault
        
        (wiki_dir / "Home.md").write_text("Link to [[VC-999]]", encoding="utf-8")
        
        errors, _ = lint_knowledge.check_wiki_links()
        assert any("Broken Obsidian link" in err and "[[VC-999]]" in err for err in errors)

    def test_check_wiki_links_broken_markdown(self, setup_mock_vault):
        """Verifies broken markdown links are flagged."""
        _, wiki_dir = setup_mock_vault
        
        (wiki_dir / "Home.md").write_text("Link to [NonExistent](missing_file.md)", encoding="utf-8")
        
        errors, _ = lint_knowledge.check_wiki_links()
        assert any("Broken markdown link" in err and "missing_file.md" in err for err in errors)

    def test_check_wiki_links_orphans(self, setup_mock_vault):
        """Verifies orphaned notes (notes with no incoming links) are detected."""
        _, wiki_dir = setup_mock_vault
        
        # Home links to VC-111, but VC-112 is orphan (no incoming links)
        (wiki_dir / "Home.md").write_text("Link to [[VC-111]]", encoding="utf-8")
        (wiki_dir / "VC-111.md").write_text("Content", encoding="utf-8")
        (wiki_dir / "VC-112.md").write_text("Content", encoding="utf-8")
        
        errors, orphans = lint_knowledge.check_wiki_links()
        assert "VC-112.md" in orphans
        assert any("Orphaned note found: 'VC-112.md'" in err for err in errors)
