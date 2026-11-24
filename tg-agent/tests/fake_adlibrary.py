"""Локальний фейк Ad Library: HTML з вшитим JSON + /api/graphql/ з префіксом for(;;); при скролі."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def ad(i, page="p1"):
    return {"ad_archive_id": str(5000 + i), "page_id": page, "page_name": f"ЖК {page}", "is_active": True,
            "start_date": 1790000000 + i * 86400, "end_date": None, "collation_count": 1 + i % 4,
            "collation_id": f"c{i}", "publisher_platform": ["FACEBOOK", "INSTAGRAM"],
            "snapshot": {"body": {"text": f"Розстрочка 0% · оголошення {i}"}, "title": "ЖК", "cta_text": "Дізнатися",
                         "display_format": "VIDEO" if i % 2 else "IMAGE", "link_url": "https://x.ua",
                         "videos": [{"video_hd_url": f"https://v/{i}.mp4"}] if i % 2 else [],
                         "images": [] if i % 2 else [{"original_image_url": f"https://i/{i}.jpg"}]}}


def wrap(ads):  # вкладеність, схожа на справжню: edges -> node -> collated_results
    return {"data": {"ad_library_main": {"search_results_connection": {
        "edges": [{"node": {"collated_results": [a]}} for a in ads]}}}}


PAGE = """<html><body style="height:20000px"><div id=list>results</div>
<script type="application/json" data-sjs>{init}</script>
<script>
let p=0, busy=false;
window.addEventListener('scroll', async ()=>{{
  if(busy||p>=3) return; busy=true; p++;
  await fetch('/api/graphql/', {{method:'POST', body:'page='+p}});
  busy=false;
}});
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        html = PAGE.format(init=json.dumps({"require": [["x", {"__bbox": {"result": wrap([ad(0), ad(1)])}}]]}))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        n = int(self.rfile.read(int(self.headers["Content-Length"])).decode().split("=")[1])
        body = "for (;;);" + json.dumps(wrap([ad(n * 10 + k) for k in range(5)]))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode())


def serve():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
