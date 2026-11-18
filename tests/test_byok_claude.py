# tests/test_byok_claude.py
import json

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

def _mock_text_reply(route, text, status=200):
    route.fulfill(status=status, content_type="application/json",
                  body=json.dumps({"content": [{"type": "text", "text": text}]}))

def _set_byok_key(page, key):
    """Sets the key through the real Settings UI, not internal state — `S` and
    `samplePromise` are not visible to page.evaluate (see Task 1's ruling)."""
    page.click("#open-settings")
    page.fill("#set-byok", key)
    page.dispatch_event("#set-byok", "change")
    page.click("#close-settings")

def test_byok_wrapper_returns_parsed_json_on_success(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_text_reply(
        route, json.dumps({"reply": "سَلَامٌ", "translation": "Peace", "translit": "salam", "tip": "", "correction": None})))
    _set_byok_key(page, "sk-ant-test")
    result = page.evaluate("""async () => {
        const sample = await getSample();
        return await sample.json([{role:'user', content:'hi'}], {modelTier:'quick'});
    }""")
    assert result["reply"] == "سَلَامٌ"

def test_byok_wrapper_accepts_a_plain_string_input(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_text_reply(route, '{"summary":"ok"}'))
    _set_byok_key(page, "sk-ant-test")
    result = page.evaluate("""async () => {
        const sample = await getSample();
        return await sample.json('a single prompt', {modelTier:'default'});
    }""")
    assert result["summary"] == "ok"

def test_byok_wrapper_sends_haiku_for_quick_and_sonnet_for_default(page, served_app):
    page.goto(served_app)
    seen = []
    def handler(route):
        seen.append(json.loads(route.request.post_data)["model"])
        _mock_text_reply(route, '{"reply":"x"}')
    page.route(ANTHROPIC_URL, handler)
    _set_byok_key(page, "sk-ant-test")
    page.evaluate("async () => { const s = await getSample(); await s.json('hi', {modelTier:'quick'}); }")
    page.evaluate("async () => { const s = await getSample(); await s.json('hi', {modelTier:'default'}); }")
    assert seen == ["claude-haiku-4-5-20251001", "claude-sonnet-5"]

def test_byok_wrapper_rejects_401_as_invalid_key(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: route.fulfill(status=401, content_type="application/json", body='{"error":{"message":"bad"}}'))
    _set_byok_key(page, "bad-key")
    code = page.evaluate("""async () => {
        const sample = await getSample();
        try { await sample.json('hi', {modelTier:'quick'}); return null; }
        catch (e) { return e.code; }
    }""")
    assert code == "byok_invalid_key"

def test_byok_wrapper_rejects_non_json_reply_text(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_text_reply(route, "not json at all"))
    _set_byok_key(page, "sk-ant-test")
    code = page.evaluate("""async () => {
        const sample = await getSample();
        try { await sample.json('hi', {modelTier:'quick'}); return null; }
        catch (e) { return e.code; }
    }""")
    assert code == "invalid_json"

def test_byok_wrapper_rejects_already_aborted_signal_as_cancelled(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: None)  # must never be reached
    _set_byok_key(page, "sk-ant-test")
    code = page.evaluate("""async () => {
        const sample = await getSample();
        const ctl = new AbortController(); ctl.abort();
        try { await sample.json('hi', {modelTier:'quick', signal: ctl.signal}); return null; }
        catch (e) { return e.code; }
    }""")
    assert code == "cancelled"

def test_changing_the_key_makes_the_next_request_use_the_new_key(page, served_app):
    page.goto(served_app)
    seen_keys = []
    def handler(route):
        seen_keys.append(route.request.headers.get("x-api-key"))
        _mock_text_reply(route, '{"reply":"x"}')
    page.route(ANTHROPIC_URL, handler)
    _set_byok_key(page, "key-a")
    page.evaluate("async () => { const s = await getSample(); await s.json('hi', {modelTier:'quick'}); }")
    _set_byok_key(page, "key-b")
    page.evaluate("async () => { const s = await getSample(); await s.json('hi', {modelTier:'quick'}); }")
    assert seen_keys == ["key-a", "key-b"]

def test_getSample_returns_null_when_no_key_and_no_sandbox(page, served_app):
    page.goto(served_app)
    assert page.evaluate("async () => await getSample()") is None

def test_byok_wrapper_merges_consecutive_same_role_turns(page, served_app):
    """Reproduces the review finding: a failed/cancelled exchange leaves two
    consecutive 'me' (user) messages in a tutor conversation's history, which
    buildTurns() passes straight through. Anthropic's API requires strict
    role alternation, so byokSample must sanitize the history itself."""
    page.goto(served_app)
    captured = []
    def handler(route):
        captured.append(json.loads(route.request.post_data)["messages"])
        _mock_text_reply(route, '{"reply":"x"}')
    page.route(ANTHROPIC_URL, handler)
    _set_byok_key(page, "sk-ant-test")
    page.evaluate("""async () => {
        const s = await getSample();
        await s.json([
            {role:'user', content:'rules'},
            {role:'assistant', content:'opening'},
            {role:'user', content:'first try'},
            {role:'user', content:'second try'}
        ], {modelTier:'quick'});
    }""")
    sent = captured[0]
    assert [m["role"] for m in sent] == ["user", "assistant", "user"]
    assert "first try" in sent[2]["content"] and "second try" in sent[2]["content"]

def test_byok_wrapper_requests_enough_tokens_for_long_translations(page, served_app):
    """The translator asks for up to 6 sentences with a full per-word
    breakdown each — 1024 max_tokens (the plan's original value) truncates
    realistic replies mid-JSON."""
    page.goto(served_app)
    captured = []
    def handler(route):
        captured.append(json.loads(route.request.post_data)["max_tokens"])
        _mock_text_reply(route, '{"reply":"x"}')
    page.route(ANTHROPIC_URL, handler)
    _set_byok_key(page, "sk-ant-test")
    page.evaluate("async () => { const s = await getSample(); await s.json('hi', {modelTier:'default'}); }")
    assert captured[0] >= 4096
