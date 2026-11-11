"""Synthetic browser checks for the unbounded grid and transient zoom controls."""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright
import re

HTML=Path(__file__).resolve().parents[1]/'index.html'
content=HTML.read_text(encoding='utf-8')
script=re.search(r'<script>(.*?)</script>',content,re.S).group(1)
markup=re.sub(r'<script>.*?</script>','',content,flags=re.S)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=which('chromium') or None,args=['--no-sandbox'])
    for width,height in [(1440,900),(390,844)]:
        ctx=browser.new_context(viewport={'width':width,'height':height},is_mobile=width<500,has_touch=width<500)
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda err: errors.append(str(err)))
        page.set_content(markup)
        page.add_script_tag(content=script)
        page.wait_for_timeout(250)
        assert page.locator('.brand').count()==0
        assert page.locator('#mapTitle').count()==1
        assert page.locator('#mapTitle').input_value()=='La cripta perduta'
        assert page.locator('#gridInfo').inner_text()=='Griglia infinita'
        assert not page.locator('#zoomControls').evaluate('(el)=>el.classList.contains("is-visible")')
        # No clipping layer and no finite grid rectangle.
        assert page.locator('#paperClip').count()==0
        assert page.locator('#infinitePaper').count()==1
        assert page.locator('#gridMinorFill').count()==1
        # Pan far in both directions. Grid bounds must follow viewport.
        page.evaluate('state.panX=-7500;state.panY=-6300;view(true)')
        assert page.locator('#zoomControls').evaluate('(el)=>el.classList.contains("is-visible")')
        assert page.locator('#gridMinorFill').get_attribute('x')=='-7502'
        assert page.locator('#gridMinorFill').get_attribute('y')=='-6302'
        # Off-origin tokens can now be placed on negative grid cells.
        page.evaluate("addToken('mage',cellOf({x:-1455,y:-2010}))")
        assert page.evaluate('map().tokens.at(-1).col')<0
        assert page.evaluate('map().tokens.at(-1).row')<0
        assert page.locator('[data-token-id]').count()>0
        # Off-origin pen strokes also survive re-renders.
        page.evaluate("setTool('pen')")
        coords=page.evaluate('''() => {const r=stage.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}}''')
        x,y=coords['x'],coords['y']
        def emit(name, px, py):
            page.evaluate('''({name,x,y})=>stage.dispatchEvent(new PointerEvent(name,{bubbles:true,cancelable:true,pointerType:'mouse',pointerId:75,button:name==='pointermove'?-1:0,buttons:name==='pointerup'?0:1,clientX:x,clientY:y}))''',{'name':name,'x':px,'y':py})
        initial=page.evaluate('map().strokes.length')
        emit('pointerdown',x,y)
        emit('pointermove',x+40,y+30)
        emit('pointerup',x+40,y+30)
        assert page.evaluate('map().strokes.length')==initial+1
        assert page.evaluate('map().strokes.at(-1).points[0].x')<0
        # Zoom should be revealed from pinch/wheel/click too; reset at 100% centers the reference area.
        page.evaluate('zoomAt(1.9,...stageCenter())')
        assert page.locator('#zoomLabel').inner_text()=='190%'
        page.locator('#zoomFit').click(force=True)
        assert page.locator('#zoomLabel').inner_text()=='100%'
        assert page.evaluate('state.zoom')==1
        centers=page.evaluate('''() => {const r=stage.getBoundingClientRect(),d=dimensions();return {actualX:state.panX+r.width/(2*state.zoom),actualY:state.panY+r.height/(2*state.zoom),expectedX:d.w/2,expectedY:d.h/2}}''')
        assert abs(centers['actualX']-centers['expectedX'])<.01
        assert abs(centers['actualY']-centers['expectedY'])<.01
        # Rename remains editable in the top-left card.
        page.locator('#mapTitle').fill('Il mondo infinito')
        page.locator('#mapTitle').dispatch_event('change')
        assert page.evaluate('map().name')=='Il mondo infinito'
        assert not errors,errors
        print('PASS',width,'x',height,'infinite pan, negative tokens/strokes, HUD, centering, filename')
        ctx.close()
    browser.close()
