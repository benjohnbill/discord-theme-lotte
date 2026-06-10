"""Self-contained blink render: serve live2d/ in a background thread (no shell job control -- WSL
returns 144 on `&` here), launch SwiftShader Chrome, capture blink_check.html, clean up. One
foreground process. Usage:
  pilot/.venv/bin/python tools/blink_render.py <model_url_path> <OUT.png>
    model_url_path e.g. rt/lotte.model3.json  (relative to live2d/)
"""
import functools, http.server, socketserver, threading, subprocess, time, base64, sys, os
import pychrome

ROOT = os.path.join(os.path.dirname(__file__), "..")   # live2d/
MODEL = sys.argv[1] if len(sys.argv) > 1 else "rt/lotte.model3.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/blink_montage.png"
SCALE = sys.argv[3] if len(sys.argv) > 3 else "0.58"
EYES = sys.argv[4] if len(sys.argv) > 4 else ""   # e.g. "1,0.75,0.5,0.25,0" -> opacity ramp
PORT_HTTP = 8788
PORT_CDP = 9337
URL = f"http://127.0.0.1:{PORT_HTTP}/blink_check.html?model={MODEL}&scale={SCALE}&oy=0.61&tw=520&still"
if EYES:
    URL += f"&eyes={EYES}"

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=os.path.abspath(ROOT))
class Q(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
httpd = Q(("127.0.0.1", PORT_HTTP), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
time.sleep(0.5)

prof = "/tmp/blink_chrome_prof"
subprocess.run(["rm", "-rf", prof])
chrome = subprocess.Popen([
    "/usr/bin/google-chrome", "--headless=new",
    "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
    f"--remote-debugging-port={PORT_CDP}", "--remote-allow-origins=*",
    "--no-sandbox", "--hide-scrollbars", "--window-size=1586,992",
    f"--user-data-dir={prof}", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ev(tab, expr):
    try:
        return tab.call_method("Runtime.evaluate", expression=expr, returnByValue=True).get("result", {}).get("value")
    except Exception as e:
        return f"<err {e}>"


try:
    browser = None
    for _ in range(60):
        try:
            browser = pychrome.Browser(url=f"http://127.0.0.1:{PORT_CDP}"); browser.list_tab(); break
        except Exception:
            time.sleep(0.25)
    tab = browser.new_tab(); tab.start()
    msgs = []
    tab.set_listener("Runtime.consoleAPICalled",
                     lambda **kw: msgs.append("".join(str(a.get("value", "")) for a in kw.get("args", []))))
    tab.call_method("Runtime.enable"); tab.call_method("Page.enable")
    tab.call_method("Page.navigate", url=URL)
    done = False
    for _ in range(250):
        time.sleep(0.2)
        if ev(tab, "window.__blinkDone===true") is True:
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
    httpd.shutdown()
    print("cleaned up")
