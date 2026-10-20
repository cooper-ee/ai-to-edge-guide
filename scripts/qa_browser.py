"""Optional UI verification using Playwright and an installed Chrome/Chromium."""
import argparse
import json
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=ROOT/'artifacts/ui')
    p.add_argument('--browser',type=Path)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    candidates=[args.browser,Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),
                Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
                Path(shutil.which('chromium') or '/nonexistent')]
    executable=next((str(x) for x in candidates if x and x.exists()),None)
    events=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable,headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1080},device_scale_factor=1)
        page.on('pageerror',lambda error:events.append(str(error)))
        page.goto((ROOT/'index.html').as_uri(),wait_until='load')
        assert page.locator('.course').count()==18
        assert page.locator('#kv-total').inner_text()=='48.00'
        page.locator('#tokens').fill('4096')
        assert page.locator('#kv-total').inner_text()=='96.00'
        page.locator('#tokens').fill('2048')
        page.screenshot(path=str(args.output/'desktop.png'),full_page=True)
        page.locator('#tab-attention').click()
        page.locator('#position').fill('8')
        assert page.locator('#attention-grid .visible').count()==8
        assert page.locator('#attention-grid .masked').count()==0
        page.locator('#tab-quant').click()
        page.locator('#bits').fill('8')
        assert abs(float(page.locator('#quant-scale').inner_text())-30/127)<1e-4
        page.locator('#tab-batch').click()
        page.locator('#play-batch').click()
        page.wait_for_timeout(900)
        page.locator('#play-batch').click()
        assert int(page.locator('#tick').input_value())>8
        page.locator('#panel-batch').screenshot(path=str(args.output/'batch-panel.png'))
        page.set_viewport_size({'width':390,'height':844})
        page.locator('#tab-kv').click()
        page.evaluate('scrollTo(0,0)')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(args.output/'mobile.png'),full_page=True)
        # Block all network requests: the reader's math bundle must work offline.
        page.route('https://**',lambda route:route.abort())
        page.route('http://**',lambda route:route.abort())
        page.set_viewport_size({'width':1440,'height':1080})
        page.goto((ROOT/'reader.html').as_uri()+'#c11',wait_until='domcontentloaded')
        assert page.locator('article').count()>=20
        math_count=page.evaluate('''async () => {await MathJax.startup.promise;return document.querySelectorAll('mjx-container[jax="SVG"]').length;}''')
        assert math_count>80
        assert page.locator('mjx-merror, [data-mml-node="merror"]').count()==0
        page.locator('#c11').scroll_into_view_if_needed()
        page.screenshot(path=str(args.output/'reader.png'))
        # Detect clipping in all static SVG text using the actual browser font metrics.
        svg_checks=[]
        for svg in (ROOT/'assets').glob('*.svg'):
            page.goto(svg.as_uri(),wait_until='load')
            clipped=page.evaluate('''() => { const s=document.querySelector('svg'); const v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.x<0||b.y<0||b.x+b.width>v.width+1||b.y+b.height>v.height+1}).map(t=>t.textContent); }''')
            svg_checks.append({'file':svg.name,'clipped_text':clipped})
        browser.close()
    result=dict(desktop_viewport=[1440,1080],mobile_viewport=[390,844],
                no_mobile_horizontal_overflow=True,interactive_assertions=8,
                page_errors=events,svg_checks=svg_checks,
                reader_test='All HTTP/HTTPS blocked; local MathJax SVG rendering passed',
                math_formulas_rendered=math_count)
    (args.output/'browser-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if events or any(x['clipped_text'] for x in svg_checks):raise SystemExit(1)


if __name__=='__main__':main()
