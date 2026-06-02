# ═══════════════════════════════════════════════════════════
# BLOCO PARA COLAR NO DIGIFY.LIVE — link equity para o scraper
# Cole este HTML em uma seção ou widget do digify.live
# ═══════════════════════════════════════════════════════════
#
# <section style="background:#f4f4f8;padding:40px 24px;text-align:center;border-top:3px solid #380e76">
#   <h2 style="color:#380e76;font-size:22px;margin-bottom:12px">🖼️ Ferramenta Gratuita de Image Scraping</h2>
#   <p style="color:#555;font-size:15px;max-width:500px;margin:0 auto 20px;line-height:1.7">
#     Baixe todas as imagens de qualquer site em um clique.<br>
#     Sem cadastro, sem instalação — export direto em ZIP.
#   </p>
#   <a href="https://imagescrapper.digify.live" 
#      style="background:#380e76;color:#fff;padding:13px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:15px;display:inline-block">
#     Baixar imagens de sites grátis →
#   </a>
#   <p style="margin-top:16px;font-size:12px;color:#999">
#     Também disponível em: 
#     <a href="https://imagescrapper.digify.live/en/" style="color:#380e76">English version</a>
#   </p>
# </section>
#
# ═══════════════════════════════════════════════════════════
from __future__ import annotations
import re, time, urllib.parse, json, os
from collections import deque
from pathlib import Path
from flask import Flask, jsonify, request, Response, render_template, send_from_directory
from flask_cors import CORS
import requests as req
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
IMAGE_EXTENSIONS = {".jpg",".jpeg",".png",".gif",".webp",".svg",".bmp",".tiff",".tif",".avif",".ico",".jfif"}

def normalize_url(url, base):
    try:
        full = urllib.parse.urljoin(base, url)
        p = urllib.parse.urlparse(full)
        if p.scheme not in ("http","https"): return None
        return p._replace(fragment="").geturl()
    except: return None

def is_image_url(url):
    try: return Path(urllib.parse.urlparse(url).path.lower()).suffix in IMAGE_EXTENSIONS
    except: return False

def extract_images(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    imgs = set()
    for tag in soup.find_all(["img","source"]):
        for attr in ("src","srcset","data-src","data-lazy-src","data-original"):
            raw = tag.get(attr,"")
            if not raw: continue
            for part in raw.split(","):
                u = normalize_url(part.strip().split()[0], base_url)
                if u and is_image_url(u): imgs.add(u)
    for tag in soup.find_all(style=True):
        for m in re.findall(r'url\(["\']?(.*?)["\']?\)', tag["style"]):
            u = normalize_url(m, base_url)
            if u and is_image_url(u): imgs.add(u)
    return imgs

def extract_links(html, base_url, base_domain, same_domain):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        link = normalize_url(a["href"], base_url)
        if not link: continue
        try:
            if same_domain and urllib.parse.urlparse(link).netloc != base_domain: continue
            links.add(link.split("#")[0])
        except: pass
    return links

# ── Pages ──────────────────────────────────────────────────────
@app.route("/")
def index(): return render_template("index.html")


@app.route("/en/")
@app.route("/en")
def index_en(): return render_template("index_en.html")

@app.route("/blog")
def blog(): return render_template("blog.html")

@app.route("/blog/como-baixar-imagens-de-sites")
def artigo1(): return render_template("artigo1.html")

@app.route("/blog/o-que-e-image-scraping")
def artigo2(): return render_template("artigo2.html")

@app.route("/blog/melhores-ferramentas-download-imagens")
def artigo3(): return render_template("artigo3.html")

@app.route("/blog/como-fazer-backup-imagens-wordpress")
def artigo4(): return render_template("artigo4.html")

@app.route("/blog/image-scraping-python")
def artigo5(): return render_template("artigo5.html")

@app.route("/blog/direitos-autorais-scraping-imagens")
def artigo6(): return render_template("artigo6.html")

@app.route("/privacidade")
def privacidade(): return render_template("privacidade.html")

@app.route("/termos")
def termos(): return render_template("termos.html")

@app.route("/health")
def health(): return jsonify({"status":"ok"})

@app.route("/sitemap.xml")
def sitemap():
    pages = [
        ("https://imagescrapper.digify.live/",                                      "1.0",  "weekly"),
        ("https://imagescrapper.digify.live/blog",                                  "0.9",  "weekly"),
        ("https://imagescrapper.digify.live/blog/como-baixar-imagens-de-sites",     "0.8",  "monthly"),
        ("https://imagescrapper.digify.live/blog/o-que-e-image-scraping",           "0.8",  "monthly"),
        ("https://imagescrapper.digify.live/blog/melhores-ferramentas-download-imagens", "0.8", "monthly"),
        ("https://imagescrapper.digify.live/blog/como-fazer-backup-imagens-wordpress",  "0.8", "monthly"),
        ("https://imagescrapper.digify.live/blog/image-scraping-python",            "0.8",  "monthly"),
        ("https://imagescrapper.digify.live/blog/direitos-autorais-scraping-imagens","0.8", "monthly"),
        ("https://imagescrapper.digify.live/contato",                               "0.4",  "yearly"),
        ("https://imagescrapper.digify.live/privacidade",                           "0.3",  "yearly"),
        ("https://imagescrapper.digify.live/termos",                                "0.3",  "yearly"),
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url, priority, freq in pages:
        xml += f"""  <url>
    <loc>{url}</loc>
    <priority>{priority}</priority>
    <changefreq>{freq}</changefreq>
  </url>\n"""
    xml += '</urlset>'
    return Response(xml, mimetype="application/xml")

@app.route("/robots.txt")
def robots():
    txt = """User-agent: *
Allow: /
Disallow: /scrape
Disallow: /download
Disallow: /en/

Sitemap: https://imagescrapper.digify.live/sitemap.xml
"""
    return Response(txt, mimetype="text/plain")

import threading, uuid

# ── Job store (in-memory) ──────────────────────────────────────
jobs = {}

def run_job(job_id, url, depth, delay, same_dom):
    job = jobs[job_id]
    try:
        base_domain = urllib.parse.urlparse(url).netloc
        visited = set(); queue = deque([(url,0)]); images = set()
        session = req.Session(); session.headers.update(HEADERS)
        while queue and not job.get("stop"):
            page_url, d = queue.popleft()
            if page_url in visited: continue
            visited.add(page_url)
            try:
                r = session.get(page_url, timeout=12)
                ct = r.headers.get("Content-Type","")
                if "image/" in ct:
                    images.add(page_url)
                elif "text/html" in ct:
                    found = extract_images(r.text, page_url)
                    images.update(found)
                    if d < depth:
                        for link in extract_links(r.text, page_url, base_domain, same_dom):
                            if link not in visited: queue.append((link, d+1))
                job["images"] = list(images)
                job["pages"] = len(visited)
                job["current_page"] = page_url
                job["cur_depth"] = d
            except Exception as e:
                job["errors"] = job.get("errors",0) + 1
            if delay > 0: time.sleep(delay)
    except Exception as e:
        job["error"] = str(e)
    job["done"] = True

@app.route("/scrape/start", methods=["POST"])
def scrape_start():
    data = request.json or {}
    url = data.get("url","").strip()
    if not url: return jsonify({"error":"URL obrigatória"}), 400
    if not url.startswith(("http://","https://")): url = "https://" + url
    depth    = int(data.get("depth", 2))
    delay    = float(data.get("delay", 0.3))
    same_dom = data.get("same_domain", True)
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"done":False,"images":[],"pages":0,"errors":0,"current_page":"","cur_depth":0,"stop":False}
    threading.Thread(target=run_job, args=(job_id,url,depth,delay,same_dom), daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/scrape/status/<job_id>")
def scrape_status(job_id):
    job = jobs.get(job_id)
    if not job: return jsonify({"error":"não encontrado"}), 404
    return jsonify({
        "done": job["done"],
        "total": len(job["images"]),
        "pages": job["pages"],
        "current_page": job.get("current_page",""),
        "cur_depth": job.get("cur_depth",0),
        "errors": job.get("errors",0),
        "images": job["images"] if job["done"] else [],
    })

@app.route("/scrape/stop/<job_id>", methods=["POST"])
def scrape_stop(job_id):
    job = jobs.get(job_id)
    if not job: return jsonify({"error":"não encontrado"}), 404
    job["stop"] = True
    return jsonify({"ok":True,"images":job["images"]})


# ── Download ───────────────────────────────────────────────────
@app.route("/download")
def download_image():
    url = request.args.get("url","").strip()
    if not url: return jsonify({"error":"URL obrigatória"}), 400
    try:
        r = req.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200: return jsonify({"error":f"HTTP {r.status_code}"}), 400
        ct = r.headers.get("Content-Type","image/jpeg")
        fname = re.sub(r"[^\w.\-]","_", Path(urllib.parse.urlparse(url).path).name or "image.jpg")[:80]
        return Response(r.content, mimetype=ct,
                        headers={"Content-Disposition":f'attachment; filename="{fname}"'})
    except Exception as e:
        return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

@app.route("/contato")
def contato(): return render_template("contato.html")
