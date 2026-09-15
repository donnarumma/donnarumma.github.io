#!/usr/bin/env python3
"""Offline Chromium checks through CDP. Requires the optional websockets package.

Start a dedicated headless Chromium with --remote-debugging-port=9334 first.
Screenshots and a JSON report are saved in .local/checks (not published).
"""

import argparse
import asyncio
import base64
import json
import urllib.request
from pathlib import Path

import websockets

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['home', 'research', 'papers', 'personal', 'contacts', 'researchmore']


async def main(port):
    output = ROOT / '.local/checks'
    output.mkdir(parents=True, exist_ok=True)
    tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list'))
    target = next(t for t in tabs if t['type'] == 'page')
    report = {'viewports': [], 'errors': [], 'remote_requests': []}
    expected_papers = len(json.loads((ROOT / 'content/site.json').read_text())['pages']['papers']['entries'])
    async with websockets.connect(target['webSocketDebuggerUrl'], max_size=40_000_000) as ws:
        counter = 0

        async def call(method, params=None):
            nonlocal counter
            counter += 1
            await ws.send(json.dumps({'id': counter, 'method': method, 'params': params or {}}))
            while True:
                response = json.loads(await ws.recv())
                if response.get('method') == 'Runtime.exceptionThrown':
                    report['errors'].append(response['params'])
                if response.get('method') == 'Network.requestWillBeSent':
                    url = response['params']['request']['url']
                    if url.startswith(('http:', 'https:')):
                        report['remote_requests'].append(url)
                if response.get('id') == counter:
                    if 'error' in response:
                        raise RuntimeError(response['error'])
                    return response.get('result', {})

        async def evaluate(expression):
            result = await call('Runtime.evaluate', {'expression': expression, 'returnByValue': True, 'awaitPromise': True})
            if 'exceptionDetails' in result:
                raise RuntimeError(result['exceptionDetails'])
            return result['result'].get('value')

        await call('Page.enable')
        await call('Runtime.enable')
        await call('Network.enable')
        await call('Network.setBlockedURLs', {'urls': ['http://*', 'https://*']})
        await call('Network.emulateNetworkConditions', {'offline': True, 'latency': 0, 'downloadThroughput': -1, 'uploadThroughput': -1})
        viewports = [(1440, 1000, PAGES), (390, 844, PAGES), (320, 740, ['home', 'papers']),
                     (768, 1024, ['home', 'papers']), (1920, 1080, ['home', 'papers'])]
        for width, height, pages in viewports:
            await call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
            for page in pages:
                path = ROOT / 'index.html' if page == 'home' else ROOT / page / 'index.html'
                await call('Page.navigate', {'url': path.as_uri()})
                for _ in range(60):
                    if await evaluate("document.readyState==='complete' && document.body?.classList.contains('enhanced')"):
                        break
                    await asyncio.sleep(.5)
                await evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
                await evaluate("document.fonts.load('40px Pacifico').then(()=>true)")
                await evaluate('document.fonts.ready.then(()=>true)')
                for _ in range(10):
                    if await evaluate("[...document.images].every(i=>i.complete)"):
                        break
                    await asyncio.sleep(.5)
                await evaluate('''(async()=>{
                    for(const img of document.images){try{await img.decode()}catch(e){}}
                    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
                    return true;
                })()''')
                metrics = await evaluate('''({width:innerWidth, scrollWidth:document.documentElement.scrollWidth,
                    images:document.images.length, broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),
                    h1:document.querySelectorAll('h1').length, enhanced:document.body.classList.contains('enhanced'),
                    fonts:document.fonts.check('20px Lato')&&document.fonts.check('40px Pacifico'),
                    emptyLinks:[...document.querySelectorAll('a')].filter(a=>!a.textContent.trim()&&!a.querySelector('img,svg')&&!a.getAttribute('aria-label')).map(a=>a.href),
                    papers:document.querySelectorAll('.publication').length})''')
                metrics['openalexLogoFits'] = await evaluate('''(()=>{
                    const el=document.querySelector('.profile-openalex');
                    const img=el.querySelector('img'),logo=img.getBoundingClientRect(),box=el.getBoundingClientRect();
                    return img.complete&&img.naturalWidth===526&&img.alt==='OpenAlex'
                        &&logo.width<=box.width-7&&logo.height<=box.height-7
                        &&logo.left>=box.left&&logo.right<=box.right
                        &&logo.top>=box.top&&logo.bottom<=box.bottom;
                })()''')
                assert metrics['openalexLogoFits'], 'OpenAlex logo missing or incorrectly sized'
                metrics['backgrounds'] = await evaluate('''(async()=>{
                    const elements=[document.body,document.querySelector('.page-banner,.name-banner')];
                    const images=[];
                    for(const el of elements){
                        const url=getComputedStyle(el).backgroundImage.slice(5,-2);
                        const img=new Image(); img.src=url;
                        try { await img.decode(); } catch(e) {}
                        images.push({url,loaded:img.naturalWidth>0});
                    }
                    return images;
                })()''')
                assert all(b['loaded'] for b in metrics['backgrounds']), metrics['backgrounds']
                assert metrics['scrollWidth'] <= width, (page, width, 'horizontal overflow', metrics)
                assert not metrics['broken'], (page, width, metrics['broken'])
                assert metrics['h1'] == 1 and metrics['enhanced'] and metrics['fonts'], metrics
                assert not metrics['emptyLinks'], metrics['emptyLinks']
                shot = await call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
                (output / f'{page}-{width}.png').write_bytes(base64.b64decode(shot['data']))
                if page == 'papers':
                    assert metrics['papers'] == expected_papers
                    await evaluate("document.querySelector('#paper-query').value='inferential planning';document.querySelector('#paper-query').dispatchEvent(new Event('input'))")
                    assert await evaluate("document.querySelectorAll('.publication:not([hidden])').length") == 1
                    await evaluate("document.querySelector('#paper-query').value='zzz-no-result';document.querySelector('#paper-query').dispatchEvent(new Event('input'))")
                    assert await evaluate("!document.querySelector('.no-papers').hidden")
                    await evaluate("document.querySelector('.paper-filters').reset()")
                    await asyncio.sleep(.1)
                    await evaluate("document.querySelector('#paper-year').value='2026';document.querySelector('#paper-year').dispatchEvent(new Event('change'))")
                    assert await evaluate("[...document.querySelectorAll('.publication:not([hidden])')].every(p=>p.dataset.year==='2026')")
                    await evaluate("document.querySelector('.paper-filters').reset()")
                    await asyncio.sleep(.1)
                    assert await evaluate("document.querySelectorAll('.publication:not([hidden])').length") == expected_papers
                if width < 801:
                    await evaluate("document.querySelector('[data-menu-toggle]').click()")
                    assert await evaluate("document.querySelector('[data-menu-toggle]').getAttribute('aria-expanded')==='true'")
                    await call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Escape', 'code': 'Escape', 'windowsVirtualKeyCode': 27})
                    assert await evaluate("document.querySelector('[data-menu-toggle]').getAttribute('aria-expanded')==='false'")
                await evaluate("document.querySelector('[data-search-open]').click();document.querySelector('#site-query').value='inferential planning';document.querySelector('#site-query').dispatchEvent(new Event('input'))")
                assert await evaluate("document.querySelector('.search-dialog').open && document.querySelectorAll('.search-results li').length===1")
                if page == 'papers' and width in [1440, 390]:
                    shot = await call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
                    (output / f'search-{width}.png').write_bytes(base64.b64decode(shot['data']))
                await evaluate("document.querySelector('[data-search-close]').click()")
                report['viewports'].append(dict(page=page, viewport=f'{width}x{height}', **metrics))
                print('PASS', page, f'{width}x{height}', flush=True)
        assert not report['errors'], report['errors']
        assert not report['remote_requests'], report['remote_requests']
        report['result'] = 'PASS: offline rendering, images, fonts, navigation, search and filters'
        (output / 'browser-report.json').write_text(json.dumps(report, indent=2) + '\n')
        await call('Network.setBlockedURLs', {'urls': []})
        await call('Network.emulateNetworkConditions', {'offline': False, 'latency': 0, 'downloadThroughput': -1, 'uploadThroughput': -1})
        print(report['result'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=9334)
    asyncio.run(main(parser.parse_args().port))
