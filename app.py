from server_to_app import Interface, redirect, render_html

app = Interface()

def hello():
    return render_html("index.html")

app.route("/", hello)