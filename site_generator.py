#!/usr/bin/env python3
import os, json, shutil, re
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

def copy_assets(tpl):
    src = f"templates/{tpl}/assets"
    dst = "dist/assets"
    if os.path.isdir(src):
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)

def minify_css(path):
    data = open(path).read()
    data = re.sub(r"/\*.*?\*/","",data,flags=re.DOTALL)
    data = re.sub(r"\s+"," ",data)
    open(path,"w").write(data)

def minify_js(path):
    data = open(path).read()
    data = re.sub(r"/\*.*?\*/","",data,flags=re.DOTALL)
    data = re.sub(r"//.*","",data)
    data = re.sub(r"\s+"," ",data)
    open(path,"w").write(data)

def minify_assets():
    for root, _, files in os.walk("dist/assets"):
        for f in files:
            p = os.path.join(root,f)
            (minify_css if f.endswith(".css") else minify_js if f.endswith(".js") else lambda x: None)(p)

def generate_site():
    spec = json.load(open("spec.json"))
    tpl = spec["template"]
    env = Environment(loader=FileSystemLoader([f"templates/{tpl}", "templates/partials"]))
    def include(name, **ctx):
        return Markup(env.get_template(f"{name}.html").render(**ctx))
    env.globals["include"] = include

    html = env.get_template(f"{tpl}.html").render(brand=spec["brand"], sections=spec["sections"])
    os.makedirs("dist", exist_ok=True)
    open("dist/index.html","w").write(html)
    copy_assets(tpl)
    minify_assets()

if __name__=="__main__":
    generate_site()
