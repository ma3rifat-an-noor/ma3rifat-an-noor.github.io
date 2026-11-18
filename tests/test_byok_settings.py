# tests/test_byok_settings.py
import json

def test_byok_key_field_persists_across_reload(page, served_app):
    page.goto(served_app)
    page.click("#open-settings")
    page.fill("#set-byok", "  sk-ant-test-123  ")
    page.dispatch_event("#set-byok", "change")
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert stored["settings"]["byokKey"] == "sk-ant-test-123"  # trimmed
    page.reload()
    page.click("#open-settings")
    assert page.input_value("#set-byok") == "sk-ant-test-123"

def test_empty_byok_key_is_default(page, served_app):
    page.goto(served_app)
    page.click("#open-settings")
    assert page.input_value("#set-byok") == ""
