# This file is the main plotly app file with web-browser components and callback actions

# Plotly Dash Imports:
import plotly.express as px
import dash
from dash import dcc, html, State
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
#Dash Bootstrap Imports:
#Dash Bootstrap AlsoRequires:
#   import dash
#   from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
#import dash_html_components as html
#import dash_core_components as dcc
#from dash import dcc
import plotly.express as px
import pandas as pd


# image processing imports:
from PIL import Image
from skimage import data, io

# internet requests imports:
import requests
import urllib.request

# other imports:
import os
import math
import xmltodict
from satellite_img import get_img_file


# Nicolas's API Key for Bing Maps:
BingMapsKey = 'AgPVfqkpC5Z-qfxWFx2tOOgFwsr-hMNKrZC5gX5D7EqVnkHRSbZQfRf0eoYxQsgz'

# Black Image for initial website (Could be replaced with a OpenPV logo?)
# Need to figure out how to make rectangle a brighter color like yellow?
img = io.imread('black.jpg')
fig = px.imshow(img)  # creating a plotly graph figure
fig.update_layout(dragmode="drawrect")  # enabling rectangle drawing upon drags

# Configuration dictionary for the graph interactions enabled:
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

#Sidebar Styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
#Content Styling
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# creating the dash app and server
app = dash.Dash('OpenPV', external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#SideBar Menu
sidebar = html.Div(
    [
        html.H2("Open PV", className="display-4"),
        html.Hr(),
        html.P(
            "Navigation Menu", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Household Location", href="/page-1", active="exact"),
                dbc.NavLink("Set Household Load", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                html.H1('Welcome to Open PV',
                        style={'textAlign':'center','background':'darkcyan', 'color':'white'}),
                html.Hr(),
                html.P("Open PV is an open source toolkit to provide consumers with the power to model real world solar production!"),
                html.H5('To reload previous work, enter username and password below:',
                        style={'textAlign':'left'}),
                dcc.Input(id = 'username_input', type = 'text', placeholder = 'Username', size = '30'),
                html.Br(),
                dcc.Input(id = 'password_input', type = 'text', placeholder = 'Password', size = '30'),
                html.Br(),
                html.Button('Submit', id='submit-val', n_clicks=0),

                ]
    elif pathname == "/page-1":
        return [
                html.H1('Set Location for Solar Production Modeling',
                        style={'textAlign':'center','background':'darkcyan', 'color':'white'}),
                html.Hr(),
                 # Input box for address:
                dcc.Input(id = 'address_input', type = 'text', placeholder = 'type your address here', size = '100'),

                 # Submit Button to click after entering in user's address
                html.Button('Submit', id='submit-val', n_clicks=0), 

                # Text Area to display longitude and latitude which is found via Bing Maps API
                html.Div(id='gps_coords', children='GPS Coordinates'),
       
                html.Button('Get Rooftop Image', id='satellite-btn', n_clicks=0),
                html.Div(id = 'graph_div', children = [dcc.Graph(id = 'graph')], style={"display": "inline-block"}),
                html.Div(id = 'zoom_graph_div', children = [dcc.Graph(id = 'zoom-graph')], style={"display": "inline-block"})
        
                ]
    elif pathname == "/page-2":
        return [
                html.H1('Define Houshold Power Consumption',
                        style={'textAlign':'center','background':'darkcyan', 'color':'white'}),
                ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__=='__main__':
    app.run_server(debug=True, port=3000)

# Website layout which contains HTML and Dash Components
#app.layout = html.Div(
#        [
#
#        # Header Title:
#        html.H3('OpenPV - Photovoltaic System Prediction Tool'), 
#
#        # Input box for address:
#        dcc.Input(id = 'address_input', type = 'text', placeholder = 'type your address here', size = '100'),
#
#        # Submit Button to click after entering in user's address
#        html.Button('Submit', id='submit-val', n_clicks=0), 
#
#        # Text Area to display longitude and latitude which is found via Bing Maps API
#        html.Div(id='gps_coords', children='GPS Coordinates'),
#
#       
#        html.Button('Get Rooftop Image', id='satellite-btn', n_clicks=0),
#        html.Div(id = 'graph_div', children = [dcc.Graph(id = 'graph')], style={"display": "inline-block"}),
#        html.Div(id = 'zoom_graph_div', children = [dcc.Graph(id = 'zoom-graph')], style={"display": "inline-block"})
#        ]
#)


# Callback for the Submit Button
@app.callback(
    # update the output of the 
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
