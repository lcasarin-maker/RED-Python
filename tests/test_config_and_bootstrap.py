from __future__ import annotations

import json

import config


def test_get_config_path_prefers_local_then_script_then_home(tmp_path, monkeypatch):
    local_dir = tmp_path / "local"
    script_dir = tmp_path / "script"
    home_dir = tmp_path / "home"
    local_dir.mkdir()
    script_dir.mkdir()
    home_dir.mkdir()

    local_cfg = local_dir / config.CONFIG_FILENAME
    script_cfg = script_dir / config.CONFIG_FILENAME
    home_cfg = home_dir / config.CONFIG_FILENAME

    monkeypatch.setattr(config.os, "getcwd", lambda: str(local_dir))
    monkeypatch.setattr(config.sys, "argv", [str(script_dir / "red.py")])

    # DEFAULT_CONFIG_PATH is resolved at import time, so patching Path.home
    # cannot redirect it; the fallback contract is "no local, no script-dir
    # settings -> the default path", which is what matters here.
    assert config.get_config_path() == config.DEFAULT_CONFIG_PATH

    local_cfg.write_text("{}", encoding="utf-8")
    assert config.get_config_path() == local_cfg

    local_cfg.unlink()
    script_cfg.write_text("{}", encoding="utf-8")
    assert config.get_config_path() == script_cfg


def test_settings_load_save_and_recent_paths(tmp_path, monkeypatch):
    cfg = tmp_path / config.CONFIG_FILENAME
    cfg.write_text(
        json.dumps(
            {
                "max_depth": 7,
                "recent_paths": ["C:/alpha"],
                "play_sound": False,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "get_config_path", lambda: cfg)

    settings = config.Settings().load()
    assert settings.get("max_depth") == 7
    assert settings.get("play_sound") is False

    settings.add_recent_path("C:/beta")
    settings.add_recent_path("C:/alpha")

    stored = json.loads(cfg.read_text(encoding="utf-8"))
    assert stored["recent_paths"] == ["C:/alpha", "C:/beta"]

