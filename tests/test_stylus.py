"""Smoke tests for D&D board stylus and gesture behavior."""
from pathlib import Path
import re
from shutil import which
from playwright.sync_api import sync_playwright

SOURCE = Path(__file__).resolve().parents[1] / "index.html"
HTML = SOURCE.read_text(encoding="utf-8")
SCRIPT = re.search(r"<script>(.*?)</script>", HTML, flags=re.S).group(1)
MARKUP = re.sub(r"<script>.*?</script>", "", HTML, flags=re.S)

TEST_JS = """() => {
  const r = stage.getBoundingClientRect();
  const x = r.left + (8 * CELL - state.panX) * state.zoom;
  const y = r.top + (8 * CELL - state.panY) * state.zoom;
  const send = (name, type, id, px, py, pressure=.5, button=0, buttons=1) =>
    stage.dispatchEvent(new PointerEvent(name, {
      bubbles:true, cancelable:true, pointerType:type, pointerId:id,
      clientX:px, clientY:py, pressure, button, buttons
    }));
  const before = map().strokes.length;
  send("pointerdown","pen",80,x,y,.2);
  send("pointermove","pen",80,x+35,y+10,.8,-1);
  send("pointerup","pen",80,x+35,y+10,0,0,0);
  const pen = map().strokes.length === before+1 &&
    map().strokes.at(-1).pressureSensitive &&
    map().strokes.at(-1).points.at(-1).pressure > .7;
  const strokeId=map().strokes.at(-1).id;
  send("pointerdown","pen",84,x+35,y+10,.5,5,32);
  send("pointerup","pen",84,x+35,y+10,0,0,0);
  const eraser=!map().strokes.some(s=>s.id===strokeId);
  setTool("pen"); penTouchGuardUntil=0;
  const count = map().strokes.length, oldPan = state.panX;
  send("pointerdown","touch",81,x,y);
  send("pointermove","touch",81,x+26,y+10,.5,-1);
  send("pointerup","touch",81,x+26,y+10,0,0,0);
  const pan = map().strokes.length === count && Math.abs(state.panX-oldPan) > .1;
  penTouchGuardUntil=0;
  const oldZoom=state.zoom;
  send("pointerdown","touch",82,x,y);
  send("pointerdown","touch",83,x+80,y);
  send("pointermove","touch",83,x+130,y,.5,-1);
  send("pointerup","touch",82,x,y,0,0,0);
  send("pointerup","touch",83,x+130,y,0,0,0);
  const zoom = state.zoom > oldZoom;

  const button=document.querySelector("#stylusAuto");
  button.click();
  const manual=!state.stylusAuto && button.getAttribute("aria-pressed")==="false";
  return {pen,pan,zoom,eraser,manual};
}"""

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True, executable_path=which("chromium") or None,
        args=["--no-sandbox"]
    )
    for width, height in [(1440, 900), (390, 844)]:
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.set_content(MARKUP)
        page.add_script_tag(content=SCRIPT)
        page.wait_for_timeout(300)
        result = page.evaluate(TEST_JS)
        assert all(result.values()), (width, result)
        assert not errors, (width, errors)
        print(f"PASS {width}x{height}: stylus, pressure, pan, pinch, eraser, manual")
        context.close()
    browser.close()
