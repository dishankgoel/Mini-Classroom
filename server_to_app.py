from http_lib import HttpParser, HttpResponse
import jinja2
from jinja2 import select_autoescape
import os


server_name = "Custom Server"

template_loader = jinja2.FileSystemLoader(searchpath = "./static/")
env = jinja2.Environment(loader = template_loader, autoescape=select_autoescape(['html', 'xml']))

class Interface():

    def __init__(self):
        
        self.routes = {}
        self.method = ""
        self.headers = {}
        self.query_string = {}
        self.form_data = {}

    def route(self, url, func):

        self.routes[url] = func
    
    def set_request_data(self, headers, query_string, form_data, method):

        self.headers = headers
        self.method = method
        self.query_string = query_string
        self.form_data = form_data
    

class Handler():

    def __init__(self, http_object):
        
        self.headers = http_object.get_headers()
        self.method = http_object.get_method()
        self.path = http_object.get_requested_path()
        self.query_string = http_object.get_query_string()
        self.form_data = http_object.get_form_data()

    def handle(self, app):

        if self.path not in app.routes:
            try:
                with open(os.getcwd() + self.path, "rb") as f:
                    body = f.read()
                content_type = find_content_type(self.path)
                headers = {"Server": server_name, "Content-Type": content_type, "Connection": "close"}
                status_code = 200
                return status_code, headers, body
            except:
                return not_found()
        else:
            app.set_request_data(self.headers, self.query_string, self.form_data, self.method)
            return app.routes[self.path]()

    
def not_found():
    headers = {"Server": server_name, "Content-Type": "text/html", "Connection": "close"}
    status_code = 404
    with open("static/404.html", "rb") as f:
        body = f.read()
    return status_code, headers, body

def find_content_type(path_of_file):

    content_type = ""
    if path_of_file.endswith(".js"):
        content_type = "text/javascript"
    elif path_of_file.endswith(".css"):
        content_type = "text/css"
    elif path_of_file.endswith(".png"):
        content_type = "image/png"
    elif path_of_file.endswith(".jpg") or path_of_file.endswith(".jpeg"):
        content_type = "image/jpeg"
    return content_type

def redirect(new_route):

    pass

def render_html(html_page, **kwargs):
    template = env.get_template(html_page)
    body = template.render()
    headers = {"Server": server_name, "Content-Type": "text/html", "Connection": "close"}
    status_code = 200
    return status_code, headers, bytes(body, "utf-8")
