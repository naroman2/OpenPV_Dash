import plotly.express as px
import dash
from dash import dcc
from dash import html
from skimage import data

img = data.chelsea()
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
    [html.H3("Drag and draw annotations"), dcc.Graph(figure=fig, config=config),]
)

if __name__ == "__main__":
    app.run_server(debug=True)
