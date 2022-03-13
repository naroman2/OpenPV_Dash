import plotly.express as px
import dash
from dash import dcc
from dash import html
from skimage import data, io

img = io.imread('IMG_3056.jpg')

fig = px.imshow(img)
fig.update_layout(dragmode="drawrect")
config = {
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
    ]
}

app = dash.Dash('OpenPV')
server = app.server
app.layout = html.Div(
    [html.H3("Draw on my cat Grayson"), dcc.Graph(figure=fig, config=config),]
)

if __name__ == "__main__":
    app.run_server(debug=True)
