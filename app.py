# This file is the main plotly app file with web-browser components and callback actions

# Plotly Dash Imports:
from pickle import TRUE
import plotly.express as px
import dash
from dash import dcc, html, State, dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# data processing imports:
import pandas as pd
import numpy as np
import json

# image processing imports:
from PIL import Image
from skimage import data, io

# internet requests imports:
import requests
import urllib.request

# other imports:
import os
import math
from math import cos, pi, pow
from datetime import date
import datetime
import xmltodict
from satellite_img import SatelliteImg, get_new_lat_lng
from nrel_api import NrelApi
import traceback
import sys

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

#Global Variables
global shapedrawn
shapedrawn = False 

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
app = dash.Dash('OpenPV', external_stylesheets = [dbc.themes.SOLAR])

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
                dbc.Row(
                    [
                    html.H1(
                        'Set Location, Rooftop Area, and View Data',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                    ),
                    
                    html.Hr()
                    ]
                ),


                dbc.Row(
                    [
                        dbc.Col(
                    # Input box for address:
                            dbc.Input(
                                id = 'address_input', 
                                type = 'text', 
                                placeholder = 'type your address here', 
                                size = '100'
                                ),
                        ),

                        dbc.Col(
                            # Submit Button to click after entering in user's address
                            dbc.Button(
                                'Submit', 
                                id = 'submit-val', 
                                n_clicks = 0
                                )
                        ),

                        dbc.Col(
                            dbc.Button(
                                'Get Rooftop Image', 
                                id = 'satellite-btn', 
                                n_clicks = 0
                            )
                        )
                    ]
                ),

                dbc.Row(
                    # Text Area to display longitude and latitude which is found via Bing Maps API
                    html.Div(
                        id = 'gps_coords', 
                        children = 'GPS Coordinates'
                        )
                ),
       

                # Neighborhood View
                dbc.Card(
                    children = [
                        html.H4('Zoom To Find Your House'),
                        html.Div(
                            id = 'neighborhood-div', 
                            children = [dcc.Graph(id = 'neighborhood-graph')], 
                            ),
                    ],

                    style = {"display": "inline-block"}
                ),
                
                # Rooftop View
                dbc.Card(
                    children = [
                        html.H4(
                            children = 'Select Your available Solar Area',
                            style = {'textArea': 'center'}
                            ),
                        html.Div(
                            id = 'rooftop-div', 
                            children = [dcc.Graph(id = 'rooftop-graph')], 
                            ) 
                    ],

                    style = {"display": "inline-block"}
                ),

                dbc.Row(
                    [
                    html.Hr(),

                    html.H1(
                        'Expected Annual Solar Irradiance Availability',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                        ),
                    
                    html.Hr()
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                'Get NREL Data', 
                                id = 'nrel-collect-btn', 
                                n_clicks = 0
                                )
                        ),
                        dbc.Col(
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
                                )
                        )
                    ]
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
    Output('neighborhood-div', 'children'),
    Input('gps_coords', 'children'),
    Input('neighborhood-graph', 'relayoutData'),
    prevent_initial_call = True
)
def get_neighborhood_view(lat_lng, relayout_data):
    global rooftop_img
    try:
        lat = lat_lng.split(',')[0]
        lng = lat_lng.split(',')[1]
        try:
            if 'shapes' in relayout_data:
                shapedrawn=True
                x0 = relayout_data.get('shapes')[0].get('x0')
                y0 = relayout_data.get('shapes')[0].get('y0')
                x1 = relayout_data.get('shapes')[0].get('x1')
                y1 = relayout_data.get('shapes')[0].get('y1')

                xc = abs((x1 - x0) / 2)
                yc = abs((y1 - y0) / 2)
                new_lat, new_lng = get_new_lat_lng(26, float(lat), float(lng), xc, yc)
                
                
                rooftop_img_obj1 = SatelliteImg(new_lat, new_lng, zoom = 20)
                rooftop_img = rooftop_img_obj1.get_img_file()

                #fig = px.imshow(rooftop_img)
                #fig.update_layout(dragmode = "drawrect", width = 1000, height = 1000, autosize=False,)
                return dcc.Graph(id = 'neighborhood-graph', figure = fig, config = config)
        except:
            neighborhood_img_obj = SatelliteImg(float(lat), float(lng))
            neighborhood_img = neighborhood_img_obj.get_img_file()

            fig = px.imshow(neighborhood_img)
            fig.update_layout(dragmode = "drawrect", width = 1000, height = 1000, autosize=False,)
            return dcc.Graph(id = 'neighborhood-graph', figure = fig, config = config)
    except:
        img = io.imread('black.jpg')
        fig = px.imshow(img)
        fig.update_layout(dragmode="drawrect", width=1000, height=1000, autosize=False,)
        return dcc.Graph(id = 'neighborhood-graph', figure = fig)

@app.callback(
    Output("rooftop-div", "children"),
    Input("neighborhood-graph", "relayoutData"),
    Input('gps_coords', 'children'),
    prevent_initial_call = True,
)
def get_rooftop_view(relayout_data, lat_lng):

    try:
        lat = lat_lng.split(',')[0]
        lng = lat_lng.split(',')[1]
        if shapedrawn:
            print("If shapes in relayout data reached true")
            # x0 = relayout_data.get('shapes')[0].get('x0')
            # y0 = relayout_data.get('shapes')[0].get('y0')
            # x1 = relayout_data.get('shapes')[0].get('x1')
            # y1 = relayout_data.get('shapes')[0].get('y1')

            # xc = abs((x1 - x0) / 2)
            # yc = abs((y1 - y0) / 2)
            # new_lat, new_lng = get_new_lat_lng(26, float(lat), float(lng), xc, yc)
            
            #rooftop_img_obj2 = SatelliteImg(new_lat, new_lng, zoom = 20)

            #try:
            #    rooftop_img = rooftop_img_obj2.get_img_file()
            #except:
            #    print(traceback.format_exc())

            fig = px.imshow(rooftop_img)
            fig.update_layout(dragmode = "drawrect", width = 1000, height = 1000, autosize=False,)
            return dcc.Graph(id = 'rooftop-graph', figure = fig, config = config)

    except:
        img = io.imread('black.jpg')
        fig = px.imshow(img)
        fig.update_layout(width=1000, height=1000, autosize=False)
        return dcc.Graph(id = 'rooftop-graph', figure = fig, config = config)

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
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
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
