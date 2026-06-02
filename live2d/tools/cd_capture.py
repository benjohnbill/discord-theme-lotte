"""Phase C+D verify capture: render cd_render.html in a SwiftShader throwaway Chrome via CDP and
grab the pose montage. bh-chrome has NO WebGL (memory bh-chrome-no-webgl) -> a separate Chrome
launched with --use-angle=swiftshader + --enable-unsafe-swiftshader is required for Live2D/WebGL.

Recipe (hard-won this session):
  * Serve live2d/ first:  python3 -m http.server 8777 --bind 127.0.0.1 --directory live2d
  * SwiftShader flags below; NO --virtual-time-budget (SwiftShader needs real wall-clock frames;
    cd_render.html is wall-clock driven via app.ticker).
  * Launch Chrome from python (subprocess) so we kill it by PID afterwards -- `pgrep -f` self-matches.
  * Poll window.__cdDone, then Page.captureScreenshot with clip+captureBeyondViewport (the montage
    is wider than the viewport).

Usage:  live2d/pilot/.venv/bin/python live2d/tools/cd_capture.py [URL] [OUT.png]
        (defaults: http://127.0.0.1:8777/cd_render.html , /tmp/cd_montage.png)
Needs:  pychrome (in live2d/pilot/.venv). Chrome at /usr/bin/google-chrome.
"""
import subprocess, time, base64, sys
import pychrome

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777/cd_render.html?hold=18&tw=520&cols=4"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/cd_montage.png"
PORT = 9335
prof = "/tmp/cd_chrome_prof"
subprocess.run(["rm", "-rf", prof])
chrome = subprocess.Popen([
    "/usr/bin/google-chrome", "--headless=new",
    "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
    f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
    "--no-sandbox", "--hide-scrollbars", "--window-size=1586,992",
    f"--user-data-dir={prof}", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = chrome.pid


def ev(tab, expr):
    try:
        return tab.call_method("Runtime.evaluate", expression=expr, returnByValue=True).get("result", {}).get("value")
    except Exception as e:
        return f"<err {e}>"


try:
    browser = None
    for _ in range(60):
        try:
            browser = pychrome.Browser(url=f"http://127.0.0.1:{PORT}"); browser.list_tab(); break
        except Exception:
            time.sleep(0.25)
    tab = browser.new_tab(); tab.start()
    msgs = []
    tab.set_listener("Runtime.consoleAPICalled",
                     lambda **kw: msgs.append("".join(str(a.get("value", "")) for a in kw.get("args", []))))
    tab.call_method("Runtime.enable"); tab.call_method("Page.enable")
    tab.call_method("Page.navigate", url=URL)
    done = False
    for _ in range(200):   # ~40s
        time.sleep(0.2)
        if ev(tab, "window.__cdDone===true") is True:
            done = True; break
    time.sleep(0.4)
    dim = ev(tab, "(function(){var i=document.querySelector('img');return i?[i.naturalWidth,i.naturalHeight]:[1586,992]})()") or [1586, 992]
    gw, gh = int(dim[0]), int(dim[1])
    shot = tab.call_method("Page.captureScreenshot", format="png",
                           clip={"x": 0, "y": 0, "width": gw, "height": gh, "scale": 1},
                           captureBeyondViewport=True)
    open(OUT, "wb").write(base64.b64decode(shot["data"]))
    print("done=", done, "| montage=", gw, "x", gh, "->", OUT)
    print("console:", " || ".join(m for m in msgs if "LOTTE" in m)[:400])
    tab.stop()
finally:
    chrome.terminate()
    try:
        chrome.wait(timeout=5)
    except Exception:
        chrome.kill()
    print("killed chrome pid", pid)
