# This file is the main plotly app file with web-browser components and callback actions

# Plotly Dash Imports:
import plotly.express as px
import dash
from dash import dcc, html, State, dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# data processing imports:
import pandas as pd
import numpy as np

# test

# image processing imports:
from PIL import Image
from skimage import data, io

# internet requests imports:
import requests
import urllib.request

# other imports:
import os
import math
from datetime import date
import datetime
import xmltodict
from satellite_img import get_img_file
from nrel_api import NrelApi

# Nicolas's API Key for Bing Maps:
BingMapsKey = 'AgPVfqkpC5Z-qfxWFx2tOOgFwsr-hMNKrZC5gX5D7EqVnkHRSbZQfRf0eoYxQsgz'

# NREL Constants:
ATTRIBUTES = 'ghi,dhi,dni,wind_speed,air_temperature,solar_zenith_angle'
LEAP_YEAR = 'false'
INTERVAL = '60'
UTC = 'false'
FULL_NAME = 'Nicolas+Romano'
REASON_FOR_USE = 'beta+testing'
AFFILIATION = 'Arizona+State+University'
EMAIL = 'naroman2@asu.edu'
MAILING_LIST = 'true'
YEAR = 2010

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
app = dash.Dash('OpenPV', external_stylesheets = [dbc.themes.BOOTSTRAP])

#suppress ALL callback reference errrors, may need to disable to perform debugging.
app.config.suppress_callback_exceptions = True
server = app.server

# side-bar as an html div element: 
sidebar = html.Div(
    [
        html.H2("Open PV", className = "display-4"),
        html.Hr(),
        html.P(
            "Navigation Menu", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href = "/", active = "exact"),
                dbc.NavLink("Household Location", href = "/page-1", active = "exact"),
                dbc.NavLink("Set Household Load", href = "/page-2", active = "exact"),
            ],
            vertical = True,
            pills = True,
        ),
    ],
    style = SIDEBAR_STYLE,
)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# When you click on a sub-page on the sidebar, it uses clicking to navigate   @
# to the href url listed /page-n...  This callback generates the html layout  @
# of the page.                                                                @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
content = html.Div(id = "page-content", children = [], style = CONTENT_STYLE)
app.layout = html.Div([
    dcc.Location(id = "url"),    # add to the address url
    sidebar,
    content
])
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# function to load the content for each page                    @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def render_page_content(pathname):
    if pathname == "/":    # homepage
        return [
                html.H1('Welcome to Open PV',
                    style = {'textAlign':'center', 'background':'darkcyan', 'color':'white'}
                ),
                html.Hr(),
                html.P("Open PV is an open source toolkit to provide consumers with the power to model real world solar production!"),
                html.H5('To reload previous work, enter username and password below:',
                    style = {'textAlign':'left'}
                    ),
                # User-name login (to be implemented)
                dcc.Input(id = 'username_input', type = 'text', placeholder = 'Username', size = '30'),
                html.Br(),
                dcc.Input(id = 'password_input', type = 'text', placeholder = 'Password', size = '30'),
                html.Br(),
                html.Button('Submit', id = 'submit-val', n_clicks=0),
                ]

    # Page 1 - Choose Address, find lng-lat, get rooftop-satellite imagery, select outline of roof
    # To-Do: convert pixels to square meters for solar availability calculation.
    elif pathname == "/page-1":
        return [
                html.H1(
                    'Set Location for Solar Production Modeling',
                    style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                    ),

                html.Hr(),

                # Input box for address:
                dcc.Input(
                    id = 'address_input', 
                    type = 'text', 
                    placeholder = 'type your address here', 
                    size = '100'
                    ),

                 # Submit Button to click after entering in user's address
                html.Button(
                    'Submit', 
                    id = 'submit-val', 
                    n_clicks = 0
                    ), 

                # Text Area to display longitude and latitude which is found via Bing Maps API
                html.Div(
                    id = 'gps_coords', 
                    children = 'GPS Coordinates'
                    ),
       
                html.Button(
                    'Get Rooftop Image', 
                    id = 'satellite-btn', 
                    n_clicks = 0
                    ),

                html.Div(
                    id = 'graph_div', 
                    children = [dcc.Graph(id = 'graph')], 
                    style = {"display": "inline-block"}
                    ),

                html.Div(
                    id = 'zoom_graph_div', 
                    children = [dcc.Graph(id = 'zoom-graph')], 
                    style = {"display": "inline-block"}
                    ), 

                html.H1(
                    'Expected Annual Solar Irradiance Availability',
                    style = {'textAlign':'center','background':'darkcyan', 'color':'white'}
                    ),

                html.Button(
                    'Get NREL Data', 
                    id = 'nrel-collect-btn', 
                    n_clicks = 0
                    ),

                html.Div(
                    id = 'calendar_div', 
                    children = [
                        dcc.DatePickerRange(
                            id = 'my-date-picker-range',
                            min_date_allowed = date(YEAR, 1, 1),
                            max_date_allowed = date(YEAR, 12, 31),
                            initial_visible_month = date(YEAR, 8, 1),
                            start_date = date(YEAR, 8, 1),
                            end_date = date(YEAR, 8, 31)
                            )
                        ], 
                    style = {"display": "inline-block"}
                    ),

                # DHI, GHI, DNI Plot W/m^2
                html.Div(
                    id = 'irradiance-timeplot',
                    children = [],
                    style = {'display': 'inline-block'}
                ),

                html.Div(
                    id = 'nrel_table_div', 
                    children = [], 
                    style = {"display": "inline-block"}
                    )
                ]
    
    # Page 3. Estimation of Household consumption
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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@ PAGE 1. Callback Functions                              @
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# Callback for the Submit Button
@app.callback(
    # updates the output of the 
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
        return '', None


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
    prevent_initial_call = True,
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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@ PAGE 2. Callback Functions                              @
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.callback(
    Output('nrel_table_div', 'children'),
    [
        Input('gps_coords', 'children'),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
        ],
    #State('gps_coords', 'children'),
    prevent_initial_call = True
)
def generate_data_table(lat_lng, sd, ed):
    try:
        lat = lat_lng.split(',')[0]
        lng = lat_lng.split()[1]
        nr = NrelApi()
        nr.initialize(
            lat = float(lat), 
            lon = float(lng), 
            yr = YEAR, 
            attr = ATTRIBUTES, 
            leap_yr = LEAP_YEAR, 
            int_val = INTERVAL, 
            utc = UTC, 
            f_name = FULL_NAME, 
            use = REASON_FOR_USE, 
            aff = AFFILIATION, 
            email = EMAIL, 
            ml = MAILING_LIST
        )
        df = nr.get_nrel_df()

        # Code to retrieve calendar start and end times
        format = "%Y-%m-%d"
        sd = datetime.datetime.strptime(sd, format)
        ed = datetime.datetime.strptime(ed, format)
        sdoy = int(sd.strftime("%j")) - 1
        edoy = int(ed.strftime("%j"))
        df = df[sdoy * 24: edoy * 24]
        format_t = "%Y-%m-%d-%H-%M"
        df['Date'] = df.apply(
            lambda row: datetime.datetime.strptime(
                f"{int(row['Year'])}-{int(row['Month'])}-{int(row['Day'])}-{int(row['Hour'])}-{int(row['Minute'])}", 
                format_t
                ), 
            axis = 1
            )
        df['Date'] = df.apply(
            lambda row: np.datetime64(str(row['Date'])),
            axis = 1
        )

        #df.to_csv('myNRELData.csv')
        return dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
    except:
        return []
    
@app.callback(
    Output('irradiance-timeplot', 'children'),
    [Input('nrel_table_div', 'children')]
    )      
    
def irradiance_plotter(df):
    try:
        df = df.get('props').get('data')
        df = pd.DataFrame.from_dict(df)
        #print(df.head())
        fig_ghi = px.line(df, x = "Date", y = "GHI")
        fig_dhi = px.line(df, x = "Date", y = "DHI")
        fig_dni = px.line(df, x = "Date", y = "DNI")
        fig_temp = px.line(df, x = "Date", y = "Temperature")
        return [
            dcc.Graph(figure = fig_ghi), 
            dcc.Graph(figure = fig_dhi), 
            dcc.Graph(figure = fig_dni), 
            dcc.Graph(figure = fig_temp)
            ]
    except:
        return []

if __name__ == "__main__":
    app.run_server(debug=True)
