# tests/test_byok_integration.py
import json

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

def _mock_text_reply(route, obj):
    route.fulfill(status=200, content_type="application/json",
                  body=json.dumps({"content": [{"type": "text", "text": json.dumps(obj)}]}))

def _enable_claude_mode(page, key=None):
    """Drives the real Settings UI — S/samplePromise aren't visible to page.evaluate
    (Task 1's ruling), and this also exercises the actual user-facing path."""
    page.click("#open-settings")
    if key is not None:
        page.fill("#set-byok", key)
        page.dispatch_event("#set-byok", "change")
    page.uncheck("#set-spar")  # unchecked Sparmodus == claude mode (setMode wiring)
    page.click("#close-settings")

def test_tutor_chat_gets_a_reply_through_byok(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_text_reply(route, {
        "reply": "كَيْفَ حَالُكَ؟", "translation": "How are you?", "translit": "kayfa haluka?", "tip": "", "correction": None}))
    _enable_claude_mode(page, key="sk-ant-test")
    page.evaluate("() => { location.hash = 'tutor'; }")
    page.fill("#tutor-input", "اسمي أحمد")
    page.click("#tutor-send")
    page.wait_for_selector(".msg.tutor")
    assert "كَيْفَ حَالُكَ؟" in page.evaluate("() => CHAT.tutor.msgs.at(-1).ar")

def test_roleplay_feedback_renders_through_byok(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_text_reply(route, {
        "summary": "Gut gemacht.", "good": ["Klare Aussprache"], "improve": [], "words": []}))
    _enable_claude_mode(page, key="sk-ant-test")
    page.evaluate("() => { location.hash = 'rollen'; }")
    page.locator(".scene").first.click()  # real click, same as startScene() via the delegated handler
    page.evaluate("""() => {
        CHAT.role.msgs.push({role:'me', text:'اَلسَّلَامُ عَلَيْكُمْ', hidden:false});
        CHAT.role.msgs.push({role:'tutor', ar:'وَعَلَيْكُمُ السَّلَامُ'});
        CHAT.role.msgs.push({role:'me', text:'كَيْفَ حَالُكَ', hidden:false});
        renderChat('role');
    }""")
    page.click("#role-feedback")
    page.wait_for_function("() => CHAT.role.msgs.some(m => m.role === 'fb')")
    assert page.evaluate("() => CHAT.role.msgs.find(m => m.role === 'fb').data.summary") == "Gut gemacht."

def test_translator_renders_through_byok(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_text_reply(route, {
        "sentences": [{"ar": "مَرْحَبًا", "de": "Hallo", "tl": "marhaban", "structure": "", "words": []}], "note": ""}))
    _enable_claude_mode(page, key="sk-ant-test")
    page.evaluate("() => { location.hash = 'uebersetzer'; }")
    page.fill("#tr-input", "Hallo")
    page.click("#tr-go")
    page.wait_for_selector("#tr-out .notice, #tr-out .sent")
    assert "مَرْحَبًا" in page.inner_text("#tr-out")

def test_tutor_chat_without_byok_key_still_shows_no_claude_message(page, served_app):
    page.goto(served_app)
    _enable_claude_mode(page)  # no key — byokKey stays empty
    page.evaluate("() => { location.hash = 'tutor'; }")
    page.fill("#tutor-input", "اسمي أحمد")
    page.click("#tutor-send")
    page.wait_for_selector(".err")
    assert "Claude" in page.inner_text(".err")

def test_claude_mode_banner_clears_once_a_byok_key_is_saved(page, served_app):
    """Reproduces the review finding: noClaude latches true at boot (no key
    yet) and was never reset when a key is saved afterwards, leaving a stale
    'needs Claude' banner above an actually-working chat."""
    page.goto(served_app)
    page.click("#open-settings")
    page.uncheck("#set-spar")  # claude mode, still no key -> banner expected
    page.click("#close-settings")
    assert "brauchen Claude" in page.inner_text("#tutor-msgs")
    page.click("#open-settings")
    page.fill("#set-byok", "sk-ant-test")
    page.dispatch_event("#set-byok", "change")
    page.click("#close-settings")
    assert "brauchen Claude" not in page.inner_text("#tutor-msgs")
