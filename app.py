import plotly.express as px
import dash
from dash import dcc, html, State
from dash.dependencies import Input, Output
from skimage import data, io
import xmltodict
import requests
import urllib.request
from PIL import Image
import os
import math
from satellite_img import get_img_file
from dash.exceptions import PreventUpdate


BingMapsKey = 'AgPVfqkpC5Z-qfxWFx2tOOgFwsr-hMNKrZC5gX5D7EqVnkHRSbZQfRf0eoYxQsgz'

img = io.imread('black.jpg')

fig = px.imshow(img)
fig.update_layout(dragmode="drawrect", )
config = {
    "modeBarButtonsToAdd": [
        #"drawline",
        #"drawopenpath",
        #"drawclosedpath",
        #"drawcircle",
        "drawrect",
        "eraseshape",
    ],
    "fillFrame": True

}

app = dash.Dash('OpenPV')
server = app.server

# Input button allowed entry types for address:
ALLOWED_TYPES = ('text')
app.layout = html.Div(
        [
        html.H3('OpenPV - Photovoltaic System Prediction Tool'), 
        dcc.Input(id = 'address_input', type = 'text', placeholder = 'type your address here', size = '100'),
        html.Button('Submit', id='submit-val', n_clicks=0), 
        html.Div(id='gps_coords', children='GPS Coordinates'),
        html.Button('Get Rooftop Image', id='satellite-btn', n_clicks=0),
        html.Div(id = 'graph_div', children = [dcc.Graph(id = 'graph')], style={"display": "inline-block"}),
        html.Div(id = 'zoom_graph_div', children = [dcc.Graph(id = 'zoom-graph')], style={"display": "inline-block"})
        ]
)

@app.callback(
    Output('gps_coords', 'children'),
    Input('submit-val', 'n_clicks'),
    State('address_input', 'value')
)
def get_lat_lng(n_clicks, address):      
    try: 
        street_address = '%20'.join(address.split())
        bing_maps_url = f'http://dev.virtualearth.net/REST/v1/Locations?addressLine={street_address}&key={BingMapsKey}&o=xml'
        r = requests.get(bing_maps_url)
        obj = xmltodict.parse(r.text)
        coords = dict(obj.get('Response').get('ResourceSets').get('ResourceSet').get('Resources').get('Location').get('Point'))
        lat = coords.get('Latitude')
        lng = coords.get('Longitude')
        coords = f'{lat}, {lng}'
        return coords
    except:
        return ''
@app.callback(
    Output('graph_div', 'children'),
    Input('satellite-btn', 'n_clicks'),
    State('gps_coords', 'children')
)
def get_rooftop_img(n_clicks, lat_lng):
    try:
        lat = lat_lng.split(',')[0]
        lng = lat_lng.split(',')[1]
        global satellite_img 
        satellite_img = get_img_file(float(lat), float(lng))
        fig = px.imshow(satellite_img)
        fig.update_layout(dragmode="drawrect", width=800, height=800, autosize=False,)
        return dcc.Graph(id = 'graph', figure = fig, config = config)
    except:
        img = io.imread('black.jpg')
        fig = px.imshow(img)
        fig.update_layout(dragmode="drawrect", width=800, height=800, autosize=False,)
        return dcc.Graph(id = 'graph', figure = fig, config = config)

@app.callback(
    Output("zoom_graph_div", "children"),
    Input("graph", "relayoutData"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data):
    try:
        if "shapes" in relayout_data:
            last_shape = relayout_data["shapes"][-1]
            # shape coordinates are floats, we need to convert to ints for slicing
            x0, y0 = int(last_shape["x0"]), int(last_shape["y0"])
            x1, y1 = int(last_shape["x1"]), int(last_shape["y1"])
            roi_img = satellite_img[y0:y1, x0:x1]
            fig = px.imshow(roi_img)
            return dcc.Graph(id = 'zoom-graph', figure = fig)
    except:
        img = io.imread('black.jpg')
        fig = px.imshow(img)
        fig.update_layout(dragmode="drawrect", width=800, height=800, autosize=False,)
        return dcc.Graph(id = 'zoom-graph', figure = fig, config = config)

if __name__ == "__main__":
    app.run_server(debug=True)
