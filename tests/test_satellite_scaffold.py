"""Tests para la inicialización y andamiaje de proyectos satélite federados (init-satellite)."""
import pytest
from pathlib import Path
import json
from scripts.protocol_cli import ProtocolClient

def test_init_satellite_creates_all_templates(tmp_path):
    cli = ProtocolClient()
    code = cli.command_init_satellite(str(tmp_path))
    assert code == 0
    
    assert (tmp_path / ".protocol" / "metadata" / "contract.json").is_file()
    assert (tmp_path / "docs" / "knowledge" / "home.md").is_file()
    assert (tmp_path / "docs" / "knowledge" / "architecture.md").is_file()
    assert (tmp_path / "tests" / "test_compliance.py").is_file()
    
    # Verify contract file structure
    contract_data = json.loads((tmp_path / ".protocol" / "metadata" / "contract.json").read_text(encoding="utf-8"))
    assert contract_data["project_name"] == tmp_path.name
    assert contract_data["version"] == "0.0.1"

def test_init_satellite_fails_when_target_is_file(tmp_path):
    # Negative path: target path is a file, causing FileExistsError on mkdir
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a directory", encoding="utf-8")
    
    cli = ProtocolClient()
    with pytest.raises(FileExistsError) as exc_info:
        cli.command_init_satellite(str(file_path))
    assert exc_info.value is not None

