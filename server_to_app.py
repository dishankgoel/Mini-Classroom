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

        if "/classrooms/" in self.path:
            # try:
            args = self.path.split("/")
            class_id = int(args[2])
            app.set_request_data(self.headers, self.query_string, self.form_data, self.method)
            if(len(args) == 3):
                return app.routes["access_classroom"](class_id)
            elif(args[3] == "live"):
                return app.routes["join_live_class"](class_id)
            elif args[3]=="group_discussions":
                if len(args)==4:
                    return app.routes["discussions"](class_id)
                else:
                    gdID = int(self.path.split("/")[4])
                    return app.routes["access_discussion"](gdID, class_id)
            # except:
            # return error(404)

        if self.path not in app.routes:
            try:
                with open(os.getcwd() + self.path, "rb") as f:
                    body = f.read()
                content_type = find_content_type(self.path)
                headers = {"Server": server_name, "Content-Type": content_type, "Connection": "close"}
                status_code = 200
                return status_code, headers, body
            except:
                return error(404)
        else:
            app.set_request_data(self.headers, self.query_string, self.form_data, self.method)
            return app.routes[self.path]()

error_reasons = {
    404: "The requested file was not found on this server",
    405: "This method is not allowed"
}
    
def error(error_code, reason = None):
    headers = {"Server": server_name, "Content-Type": "text/html", "Connection": "close"}
    status_code = error_code
    template = env.get_template("error.html")
    if reason is not None:
        body = template.render(error_code = error_code, reason = reason)
    else:
        body = template.render(error_code = error_code, reason = error_reasons[error_code])
        
    return status_code, headers, bytes(body, "utf-8")

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

def redirect(new_route, token = None):
    status_code = 302
    headers = {"Location": new_route}
    if token is not None:
        headers = {**headers, "Set-Cookie":"access_token={}".format(token)}
    return status_code, headers, b""

def render_html(html_page, **kwargs):
    status_code = 200
    template = env.get_template(html_page)
    body = template.render(**kwargs)
    headers = {"Server": server_name, "Content-Type": "text/html", "Connection": "close"}
    return status_code, headers, bytes(body, "utf-8")
