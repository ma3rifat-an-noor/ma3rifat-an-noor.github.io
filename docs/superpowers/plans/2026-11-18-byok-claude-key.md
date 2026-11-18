# Eigener Claude-Schlüssel (BYOK) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a user who already has their own Anthropic API key enter it in Settings and have the Tutor, Rollenspiel-feedback, and Übersetzer talk directly to Claude from their own browser, with zero change to the three existing call sites and zero effect on anyone who leaves the field empty.

**Architecture:** `getSample()` (`arabisch-app/madina-arabisch.html:3127`) currently resolves to the claude.ai-sandbox object or `null`. It gains a third branch: when no sandbox is present but `S.settings.byokKey` is set, it resolves to a locally-built object exposing the same `sample.json(input, opts)` interface the three call sites already call, backed by a direct `fetch()` to `https://api.anthropic.com/v1/messages`. Because the interface is identical, `requestReply()`, `roleFeedback()`, and `translate()` need no changes at all.

**Tech Stack:** Plain browser JS (no build step, single HTML file), Anthropic Messages API via direct browser `fetch` (`anthropic-dangerous-direct-browser-access` header), pytest + pytest-playwright for tests (run via `uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest ...` — no project venv exists; this is the established way this repo's 117 existing tests are run).

**Spec:** `docs/superpowers/specs/2026-11-18-byok-claude-key-design.md`

## Global Constraints
- An empty/whitespace-only `byokKey` must behave exactly like today (falls through to `NO_CLAUDE()`), not attempt a request.
- The key is stored only in `localStorage` (via the existing `S`/`save()` mechanism) — never sent anywhere except directly to `api.anthropic.com`.
- Only Claude in this round — no Gemini/Groq/ChatGPT/Ollama branch.
- The three existing call sites (`requestReply` using `sample.json` at line 3485, `roleFeedback` at line 3950, `translate` at line 4120) are not modified.
- Model mapping: `opts.modelTier === 'default'` → `claude-sonnet-5`; anything else (including `'quick'` or missing) → `claude-haiku-4-5-20251001`.
- Request headers: `x-api-key: <byokKey>`, `anthropic-version: 2023-06-01`, `anthropic-dangerous-direct-browser-access: true`, `content-type: application/json`.

## Review Focus
- **A key that is only whitespace, or has leading/trailing spaces pasted in.** Must be trimmed and, if then empty, treated as "no key" — not sent to Anthropic as a malformed request. Tested in Task 2.
- **Anthropic rejects the key (401).** Must surface a specific, understandable message rather than the generic "connection interrupted" text. Tested in Task 2.
- **The user edits or clears the key while `getSample()`'s result is already cached (`samplePromise`).** The next call must use the new value, not the stale cached source. Tested in Task 1.
- **Claude's reply text isn't valid JSON** (model didn't follow the format instruction in `tutorRules()`/the feedback/translate prompts). Must reject with `{code:'invalid_json'}`, not throw an uncaught `SyntaxError`. Tested in Task 2.
- **The user cancels an in-flight request** (translator's "Stopp" button, or a new tutor message aborting the previous one via `ctx.ctl`). Must still surface as `{code:'cancelled'}` so the existing cancel-handling branches in `requestReply`/`translate` keep working, not show a scary error for a deliberate stop. Tested in Task 2.

---

## Task 1: Settings field, storage, and cache invalidation

**Files:**
- Modify: `arabisch-app/madina-arabisch.html:2966` (`DEFAULTS`)
- Modify: `arabisch-app/madina-arabisch.html:608` (settings sheet HTML, insert after the `set-precise` row)
- Modify: `arabisch-app/madina-arabisch.html:403-411` (CSS, add a text-input rule next to `.sw`)
- Modify: `arabisch-app/madina-arabisch.html:4188` (`I18N_EN`, add two keys)
- Modify: `arabisch-app/madina-arabisch.html:4227` (`applySettingsUI`, populate the field)
- Modify: `arabisch-app/madina-arabisch.html:4383-4385` (event wiring, add the change listener)
- Test: `tests/test_byok_settings.py`

**Interfaces:**
- Produces: `S.settings.byokKey: string` (default `''`), persisted through the existing `save()`/`mergeState()` mechanism — no changes needed there.
- Consumes: existing globals `samplePromise`, `aiOff` (declared at `:3126`) — the new change listener resets both so Task 2's `getSample()` re-evaluates on the next call.

- [ ] **Step 1: Write the failing test**

```python
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
```

**Ruling (recorded during execution, see ledger):** the whole script is wrapped in a top-level IIFE, so no `let`/`const`/`function` inside it is visible to `page.evaluate` as a bare identifier (or via `window.x`) unless explicitly exposed with a `window.x = x;` line — an established pattern already used 10x in this file for exactly this reason (`window.CHAT`, `window.TABLES`, etc.). A third test asserting on `S.settings.byokKey` / `samplePromise` directly was dropped from this task for that reason; the cache-invalidation behavior it was meant to prove is instead tested in Task 2 as an observable effect (a second request after changing the key via the real Settings UI actually uses the new key), where `getSample` gets its own exposure line anyway.

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd arabisch-app/.. && uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest tests/test_byok_settings.py -v`
Expected: FAIL — `#set-byok` does not exist yet.

- [ ] **Step 3: Implement**

In `DEFAULTS()` (`:2966`), add `byokKey:''` to the `settings` object literal.

In the settings sheet HTML, immediately after the `set-precise` `<div class="set">` row (`:608`), insert:
```html
<div class="set col"><label class="l" for="set-byok"><b data-i18n="byokTitle">Eigener Claude-Schlüssel</b><span data-i18n="byokDesc">Optional: spricht direkt mit deinem eigenen Claude-Zugang, ohne Kontingent.</span></label><input type="password" id="set-byok" autocomplete="off" spellcheck="false" placeholder="sk-ant-…"></div>
```

In the CSS block near `.sw` (`:403-411`), add:
```css
.set input[type=password]{width:100%;border:1px solid var(--line);background:var(--surface);border-radius:10px;padding:8px 10px;font-size:.9rem;color:var(--ink)}
```

In `I18N_EN` (`:4188`, right after the `preciseTitle`/`preciseDesc` line), add:
```js
byokTitle:'Your own Claude key', byokDesc:'Optional: talks directly to your own Claude access, no quota.',
```

In `applySettingsUI()`, right after the `$('#set-rate').value = st.rate;` line (`:4227`), add:
```js
$('#set-byok').value = st.byokKey || '';
```

Near the other settings listeners (`:4383-4385`), add:
```js
$('#set-byok').addEventListener('change', e => { S.settings.byokKey = e.target.value.trim(); save(); samplePromise = null; aiOff = false; });
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest tests/test_byok_settings.py -v`
Expected: PASS, all 3 tests.

- [ ] **Step 5: Syntax-check the whole file**

Run: find the current `<script>`/`</script>` line numbers (`grep -n '<script>\|^</script>' arabisch-app/madina-arabisch.html`), then `sed -n '<open+1>,<close-1>p' arabisch-app/madina-arabisch.html > /tmp/madina-script-check.js && node --check /tmp/madina-script-check.js` (confirmed as lines 630,4407 as of this task).
Expected: no output (clean).

- [ ] **Step 6: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_byok_settings.py
git commit -m "feat: add own-Claude-key settings field with local storage"
```

---

## Task 2: BYOK Claude wrapper and error mapping

**Files:**
- Modify: `arabisch-app/madina-arabisch.html:3126-3132` (`getSample`)
- Modify: `arabisch-app/madina-arabisch.html:3133` (`PERMANENT` set)
- Modify: `arabisch-app/madina-arabisch.html:3134-3146` (`errText`)
- Test: `tests/test_byok_claude.py`

**Interfaces:**
- Consumes: `S.settings.byokKey` from Task 1.
- Produces: a `byokSample()` function returning `{ json: async (input, opts) => object }`, wired into `getSample()`'s fallback branch.
- `input` may be a string (wrapped as a single `{role:'user', content:input}`) or an array of `{role, content}` turns (used as-is) — both forms are already used by the three existing call sites.
- `opts` is `{modelTier?: 'quick'|'default', cache?: boolean, signal?: AbortSignal}` — `cache` is accepted and ignored (no sandbox-style caching for direct API calls).
- On success, resolves to the parsed JSON object from Claude's reply text.
- On failure, rejects with an object carrying `.code`, one of: `'cancelled'`, `'byok_invalid_key'`, `'invalid_json'`, or `undefined` (falls through to the existing default error text).

- [ ] **Step 1: Write the failing tests**

```python
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
```

**Exposure needed:** add `window.getSample = getSample;` immediately after `getSample`'s definition, matching the file's own established convention (`window.CHAT = CHAT;`, `window.TABLES = TABLES;`, etc.) — `getSample`, like everything else in this file, is declared inside the top-level IIFE and invisible to `page.evaluate` otherwise.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest tests/test_byok_claude.py -v`
Expected: FAIL — `byokSample` doesn't exist, `getSample()` still returns `null` regardless of `byokKey`.

- [ ] **Step 3: Implement**

Replace `getSample()`'s body (`:3127-3131`) so that when `window.claude.use` is unavailable, it checks `S.settings.byokKey.trim()`: if non-empty, resolve to `byokSample(S.settings.byokKey.trim())`; otherwise resolve to `null` as today. Immediately after `function getSample(){...}`, add `window.getSample = getSample;` (same convention as `window.CHAT = CHAT;` elsewhere in this file).

Add `byokSample(key)` near `getSample()`:
```js
function byokSample(key){
  return { json: async (input, opts) => {
    const messages = typeof input === 'string' ? [{role:'user', content:input}] : input;
    const model = (opts && opts.modelTier === 'default') ? 'claude-sonnet-5' : 'claude-haiku-4-5-20251001';
    let res;
    try {
      res = await fetch('https://api.anthropic.com/v1/messages', {
        method:'POST',
        headers:{'x-api-key':key, 'anthropic-version':'2023-06-01', 'anthropic-dangerous-direct-browser-access':'true', 'content-type':'application/json'},
        body:JSON.stringify({model, max_tokens:1024, messages}),
        signal: opts && opts.signal
      });
    } catch (e) {
      if (e && e.name === 'AbortError') throw {code:'cancelled'};
      throw {code:undefined};
    }
    if (res.status === 401 || res.status === 403) throw {code:'byok_invalid_key'};
    if (!res.ok) throw {code:undefined};
    const data = await res.json();
    try { return JSON.parse(data.content[0].text); }
    catch (e) { throw {code:'invalid_json'}; }
  }};
}
```
(An already-aborted `signal` makes `fetch` reject synchronously with an `AbortError` per the Fetch spec, before any network attempt — this is what Step 1's cancelled-signal test relies on.)

Add `'byok_invalid_key'` to the `PERMANENT` set (`:3133`).

Add a case to `errText()`'s switch (`:3136-3145`), next to the other cases:
```js
case 'byok_invalid_key': return en ? 'Your own Claude key was rejected. Check it in Settings.' : 'Dein eigener Claude-Schlüssel wurde abgelehnt. Prüfe ihn in den Einstellungen.';
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest tests/test_byok_claude.py -v`
Expected: PASS, all 8 tests.

- [ ] **Step 5: Syntax-check the whole file**

Run: `sed -n '630,4407p' arabisch-app/madina-arabisch.html > /tmp/madina-script-check.js && node --check /tmp/madina-script-check.js` (line numbers shift as tasks are added — re-check with `grep -n '<script>\|^</script>'` if unsure)
Expected: no output (clean).

- [ ] **Step 6: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_byok_claude.py
git commit -m "feat: add direct-to-Claude BYOK wrapper behind getSample()"
```

---

## Task 3: End-to-end proof through the three existing call sites

**Files:**
- Test only: `tests/test_byok_integration.py`

**Interfaces:**
- Consumes: `getSample()`/`byokSample()` from Task 2, `requestReply()`, `roleFeedback()`, `translate()` (unmodified, existing functions).

- [ ] **Step 1: Write the tests**

```python
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
```

(`CHAT` and `renderChat` are already exposed via existing `window.CHAT = CHAT;` / `window.renderChat = renderChat;` lines in this file — only `getSample`, added in Task 2, was new.)

- [ ] **Step 2: Run the tests**

Run: `uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest tests/test_byok_integration.py -v`
Expected: PASS, all 4 tests. If any fails, use `systematic-debugging` to find whether the test's selectors/assumptions are wrong or the Task 1/2 code has a real integration bug — fix the real cause, then re-run.

- [ ] **Step 3: Run the full suite**

Run: `uv run --with pytest --with pytest-playwright --with playwright python3 -m pytest tests/ -q`
Expected: `124 passed` (117 existing + 3 + 7 + 4 new).

- [ ] **Step 4: Commit**

```bash
git add tests/test_byok_integration.py
git commit -m "test: prove tutor/roleplay/translator work end-to-end through BYOK"
```
