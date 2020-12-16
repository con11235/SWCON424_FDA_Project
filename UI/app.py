import dash
import dash_html_components as html

app = dash.Dash(__name__, title = 'FDA',suppress_callback_exceptions=True)

app.head = [
    html.Meta(charSet ="utf-8"),
    html.Meta(httpEquiv='X-UA-Compatible', content ="IE=edge"),
    html.Meta(name="viewport", content="width=device-width, initial-scale=1, shrink-to-fit=no"),
    html.Meta(name="description", content=""),
    html.Meta(name="author", content=""),
    
    # Custom fonts for this template
    html.Link(href="vendor/fontawesome-free/css/all.min.css", rel="stylesheet"),# style={type:"text/css"}),
    html.Link(
        href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i",
        rel="stylesheet"),

    # Custom styles for this template
    html.Link( href="css/sb-admin-2.min.css", rel="stylesheet")
]

server = app.server