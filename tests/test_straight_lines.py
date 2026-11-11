"""Browser checks for straight-line Shift and long-press drawing."""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright
import re

html=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
javascript=re.search(r"<script>(.*?)</script>",html,re.S).group(1)
markup=re.sub(r"<script>.*?</script>","",html,flags=re.S)

def emit(page,kind,x,y,pid=41,ptype="mouse",shift=False):
    page.evaluate("""({kind,x,y,pid,ptype,shift})=>{
      stage.dispatchEvent(new PointerEvent(kind,{bubbles:true,cancelable:true,
        pointerId:pid,pointerType:ptype,clientX:x,clientY:y,
        shiftKey:shift,button:kind==='pointermove'?-1:0,
        buttons:kind==='pointerup'?0:1,pressure:.5}));
    }""",{"kind":kind,"x":x,"y":y,"pid":pid,"ptype":ptype,"shift":shift})

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,executable_path=which("chromium") or None,args=["--no-sandbox"])
    for w,h in [(1440,900),(390,844)]:
        ctx=browser.new_context(viewport={"width":w,"height":h},is_mobile=w<500,has_touch=w<500)
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.set_content(markup)
        page.add_script_tag(content=javascript)
        page.wait_for_timeout(270)
        page.evaluate("""() => {setTool('pen');state.maps=[blankMap()];state.activeMapId=state.maps[0].id;renderAll();centerCanvas()}""")
        xy=page.evaluate("""() => {const r=stage.getBoundingClientRect();return [r.left+r.width*.36,r.top+r.height*.33]}""")
        x,y=xy
        emit(page,"pointerdown",x,y,shift=True)
        emit(page,"pointermove",x+96,y+91,shift=True)
        assert page.locator("#straightPreview").count()==1
        assert page.locator("#straightAngleHud").is_visible()
        assert page.locator("#straightDegrees").inner_text()=="45°"
        assert page.evaluate("map().strokes.at(-1).points.length")==1
        emit(page,"pointerup",x+96,y+91)
        assert page.locator("#straightPreview").count()==0
        assert not page.locator("#straightAngleHud").is_visible()
        assert page.evaluate("map().strokes.at(-1).points.length")==2
        assert abs(page.evaluate("""() => {const p=map().strokes.at(-1).points;return (p[1].x-p[0].x)-(p[1].y-p[0].y)}"""))<1e-5
        # Hold at the end of a freehand stroke, then reposition the end.
        pointer_type="pen" if w<500 else "mouse"
        emit(page,"pointerdown",x,y+88,pid=42,ptype=pointer_type)
        emit(page,"pointermove",x+27,y+105,pid=42,ptype=pointer_type)
        emit(page,"pointermove",x+58,y+96,pid=42,ptype=pointer_type)
        page.wait_for_timeout(550)
        assert page.locator("#straightPreview").count()==1
        emit(page,"pointermove",x+113,y+98,pid=42,ptype=pointer_type)
        emit(page,"pointerup",x+113,y+98,pid=42,ptype=pointer_type)
        assert page.evaluate("map().strokes.at(-1).points.length")==2
        # Press Shift midway through a freehand stroke.
        emit(page,"pointerdown",x,y+135,pid=43)
        emit(page,"pointermove",x+22,y+150,pid=43)
        emit(page,"pointermove",x+39,y+140,pid=43)
        assert page.evaluate("map().strokes.at(-1).points.length")>=3
        page.keyboard.down("Shift")
        assert page.locator("#straightPreview").count()==1
        emit(page,"pointerup",x+75,y+166,pid=43)
        page.keyboard.up("Shift")
        assert page.evaluate("map().strokes.at(-1).points.length")==2
        # No stale hold timer after normal freehand pointer-up.
        emit(page,"pointerdown",x,y+185,pid=44)
        emit(page,"pointermove",x+21,y+200,pid=44)
        emit(page,"pointermove",x+36,y+191,pid=44)
        emit(page,"pointerup",x+36,y+191,pid=44)
        page.wait_for_timeout(530)
        assert page.evaluate("map().strokes.at(-1).points.length")>=3
        assert page.locator("#straightPreview").count()==0
        n=page.evaluate("map().strokes.length")
        page.evaluate("undo()")
        assert page.evaluate("map().strokes.length")==n-1
        assert not errors,errors
        print("PASS",w,"x",h,"Shift, hold, 45-degree snap, ghost line, undo")
        ctx.close()
    browser.close()
