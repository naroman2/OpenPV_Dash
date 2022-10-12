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
                dbc.NavLink("Set Rooftop Pitch/Angle", href = "/page-3", active = "exact"),
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
                html.H4("Open PV is an open source toolkit to provide consumers with the power to model real world solar production!"),
                html.Hr(),

                dbc.Row(
                    [
                        html.Div(
                            [
                                html.H1("Meet The Team:"),

                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardImg(src="/static/images/david.png", top=True),  
                                                    dbc.CardBody(
                                                        [
                                                            html.H4('David Montiel', className = 'card-title'),
                                                            html.P('ASU Online Student from Chicago, IL')
                                                        ]
                                                    )  
                                                ]
                                            )
                                        ),

                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardImg(src="static/images/nicolas.png", top=True),    
                                                    dbc.CardBody(
                                                        [
                                                            html.H4('Nicolas Romano', className = 'card-title'),
                                                            html.P('ASU Online Student from Cleveland, OH')
                                                        ]
                                                    )
                                                ]
                                            )
                                        ),

                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardImg(src="static/images/jaron.png", top=True),  
                                                    dbc.CardBody(
                                                        [
                                                            html.H4('Jaron Guisa', className = 'card-title'),
                                                            html.P('ASU Online Student from Ridgecrest, CA')
                                                        ]
                                                    )  
                                                ]       
                                            )
                                        ),

                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardImg(src="static/images/Jeremiah.png", top=True), 
                                                    dbc.CardBody(
                                                        [
                                                            html.H4('Jeremiah Simmons', className = 'card-title'),
                                                            html.P('ASU Online Student from Sierra Vista, AZ')
                                                        ]
                                                    )   
                                                ]    
                                            )
                                        ),

                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    dbc.CardImg(src="static\images\Goryll.png", top=True),    
                                                    dbc.CardBody(
                                                        [
                                                            html.H4('Dr. Michael Goryll (Project Mentor)', className = 'card-title'),
                                                            html.P('ASU associate professor in the School of Electrical, Computer and Energy Engineering')
                                                        ]
                                                    )
                                                ]    
                                            )
                                        ),
                                    ] 
                                )
                            ]
                        )
                    ]
                ),

                html.Hr(),

                html.H5('To reload previous estimations, enter username and password below:',
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
                    html.Div(
                        id = 'available-roof-area',
                        children = [
                            html.H1('The Available Rooftop Area is 0 m')
                        ]

                    )
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

                dbc.Row(
                    # DHI, GHI, DNI Plot W/m^2
                    html.Div(
                        id = 'irradiance-timeplot',
                        children = [],
                        style = {'display': 'inline-block'}
                    )
                ),

                dbc.Row(
                    html.Div(
                        id = 'nrel_table_div', 
                        children = [], 
                        style = {"display": "inline-block"}
                        )
                )
        ]
    
    # Page 2. Estimation of Household consumption
    elif pathname == "/page-2":
        return [
                html.H1('Define Houshold Power Consumption',
                        style={'textAlign':'center','background':'darkcyan', 'color':'white'}),
                html.Hr(), 
                html.H1('Using monthly statements from your power company, enter your total',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}),
                html.Br(),
                html.H1('household power consumption over the last year in kilowatts (kW).',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}),
                html.Hr(),
                # Input box for last 12 months of conumption:
                dbc.Row(
                    [
                    dbc.Col(
                        dbc.Input(
                            id = 'January-Consumption', 
                            type = 'number',
                            value = 0, 
                            placeholder = 'Enter January Consumption in kW (numerical only)', 
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'February-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)', 
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'March-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)', 
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'April-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)', 
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'May-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)', 
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'June-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)',  
                            size = '100'
                            ),
                   ),
                    dbc.Col(
                        dbc.Input(
                            id = 'July-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)',  
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'August-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)',  
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'September_Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)',  
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'October-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)', 
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'November-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)',  
                            size = '100'
                            ),
                        dbc.Input(
                            id = 'December-Consumption', 
                            type = 'number', 
                            value = 0, 
#                            placeholder = 'Enter January Consumption in kW (numerical only)',  
                            size = '100'
                            ),
                    ),
                    ],
                ),
                dbc.Row(
                    [
                dbc.Col(
                # Submit Button to click after entering in user's monthly load usage
                    dbc.Button(
                        'Submit Load.', 
                        id = 'submit-load', 
                        n_clicks = 0
                            ),
                    ),
                
                dbc.Col(
                    # Text Area to display total annual load in kW
                    html.Div(
                        id = 'total-annual-load', 
                        children = 'Total Annual Load'
                        )
                    ),
                    ],
                ),
                    ]
    # Page 3. Estimation of Rooftop Angle/Pitch
    elif pathname == "/page-3":
        return [
    dbc.Row(
                    [
                    html.H1(
                        'Define Rooftop Angle',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                    ),
                    
                    html.Hr()
                    ]
                ),
                dbc.Row(
                    [
                        html.Div(
                            [
                                dbc.Label("Choose the rooftop angle closest to your roof, or enter a custom angle."),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                dbc.Card(
                                            [
                                                dbc.CardImg(src="/static/images/oof15deg.jpg", top=True),    
                                            ],
                                        ),),
                                        dbc.Col(
                                dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oof30deg.jpg", top=True),    
                                            ],
                                        ),),
                                        dbc.Col(
                                dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oof45deg.jpg", top=True),    
                                            ],
                                        ),),
                                        dbc.Col(
                                dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oof60deg.jpg", top=True),    
                                            ],    
                                ),),
                                dbc.Col(
                                dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oofcustdeg.jpg", top=True),    
                                            ],    
                                ),),
                                    ] 
                                        ),                                
                                dbc.RadioItems(
                                    options=[
                                        {"label": "15\N{DEGREE SIGN}____________________", "value": 1, "disabled": False},
                                        {"label": "30\N{DEGREE SIGN}____________________", "value": 2, "disabled": False},
                                        {"label": "45\N{DEGREE SIGN}____________________", "value": 3, "disabled": False},
                                        {"label": "60\N{DEGREE SIGN}____________________", "value": 4, "disabled": False},
                                        {"label": "Custom_____________", "value": 5, "disabled": False},                                    
                                        ],
                                    #value=1,
                                    id="roofslope_radio",
                                    inline=True,
                                ),
                            ]
                        )
                    ]
                ),
                        dbc.Row(
                        html.Div(
                        [
                            dbc.Input(
                                id = 'roofslope_custominput', 
                                type = 'text', 
                                placeholder = 'Enter custom roof angle (\N{DEGREE SIGN})',
                                size = '150'
                              )
                        ], style= {'display': 'block'}
                        ),
                        ),                   
                        dbc.Row(
                    [
                        html.H1(
                        'Additional Information',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                    ),
                        html.Hr(),
                        html.Div(
                            [
                                dbc.Label("Unexpected Costs: Any rooftop steeper than 35\N{DEGREE SIGN} will approximately double the labor cost. Shingles that are considered old and shingles made of wood or clay would need to be replaced with composite shingles which will increase the material and labor costs."),   
                            dbc.Col(
                                dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\shinglesamp.jpg", top=True),    
                                            ],
                                           style={"width": "35rem"}, 
                                        ),),
                            ]
                        )
                    ]
                    )
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

####################################################
# Getting Neighborhood View Satellite Img          #
####################################################
@app.callback(
    Output('neighborhood-div', 'children'),
    Input('gps_coords', 'children'),
    Input('satellite-btn', 'n_clicks'),
    prevent_initial_call = True
)
def get_neighborhood_view(lat_lng, n_clicks):
    if n_clicks is not None:
        try:
            lat = lat_lng.split(',')[0]
            lng = lat_lng.split(',')[1]
            neighborhood_img_obj = SatelliteImg(float(lat), float(lng))
            neighborhood_img_obj.set_img_file()
            fig = px.imshow(neighborhood_img_obj.sat_img)
            fig.update_layout(dragmode = "drawrect", width = 1000, height = 1000, autosize=False,)
            return dcc.Graph(id = 'neighborhood-graph', figure = fig, config = config)
        except:
            img = io.imread('black.jpg')
            fig = px.imshow(img)
            fig.update_layout(dragmode="drawrect", width=1000, height=1000, autosize=False,)
            return dcc.Graph(id = 'neighborhood-graph', figure = fig)
    else:
            img = io.imread('black.jpg')
            fig = px.imshow(img)
            fig.update_layout(dragmode="drawrect", width=1000, height=1000, autosize=False,)
            return dcc.Graph(id = 'neighborhood-graph', figure = fig)



################################################
# getting and setting rooftop view             #
################################################
@app.callback(
    Output("rooftop-div", "children"),
    Input('gps_coords', 'children'),
    Input('neighborhood-graph', 'relayoutData'),
    prevent_initial_call = True
)
def get_rooftop_view(lat_lng, relayout_data):
    try:
        lat = lat_lng.split(',')[0]
        lng = lat_lng.split(',')[1]
        if 'shapes' in relayout_data:
            x0 = relayout_data.get('shapes')[0].get('x0')
            y0 = relayout_data.get('shapes')[0].get('y0')
            x1 = relayout_data.get('shapes')[0].get('x1')
            y1 = relayout_data.get('shapes')[0].get('y1')

            xc = abs((x1 - x0) / 2)
            yc = abs((y1 - y0) / 2)
            new_lat, new_lng = get_new_lat_lng(26, float(lat), float(lng), xc, yc)
            
            
            rooftop_img_obj = SatelliteImg(new_lat, new_lng, zoom = 20)
            rooftop_img_obj.set_img_file()
            fig = px.imshow(rooftop_img_obj.sat_img)
            fig.update_layout(dragmode = "drawrect", width = 1000, height = 1000, autosize = False)
            return dcc.Graph(id = 'rooftop-graph', figure = fig, config = config)
        else:
            raise Exception

    except:
        img = io.imread('black.jpg')
        fig = px.imshow(img)
        fig.update_layout(width=1000, height=1000, autosize=False)
        return dcc.Graph(id = 'rooftop-graph', figure = fig, config = config)


######################################
# drawing on roof and computing area #
######################################
@app.callback(
    Output('available-roof-area', 'children'),
    Input('gps_coords', 'children'),
    Input('rooftop-graph', 'relayoutData'),
    prevent_initial_call = True
)
def calculate_available_rooftop_area(lat_lng, relayout_data):
    try:
        lat = lat_lng.split(',')[0]
        lng = lat_lng.split(',')[1]
        if 'shapes' in relayout_data:
            rects = relayout_data.get('shapes')
            area = 0
            for s in rects:
                x0 = s.get('x0')
                y0 = s.get('y0')
                x1 = s.get('x1')
                y1 = s.get('y1')
                width_p = abs(x1 - x0)
                height_p = abs(y1 - y0)
                # Convert a pixel displacement at a given zoom level into a meter displacement:
                meters_per_px = 156543.03392 * cos(float(lat) * pi / 180) / pow(2, 20)
                width_m = width_p * meters_per_px  #  Needs to be generalized.
                height_m = height_p * meters_per_px
                area = area + width_m * height_m


        return [html.H1(f'The Available Rooftop Area is {area} square meters')]
    except:
        return [html.H1('The Available Rooftop Area is 0 m')]


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
    global solar_df
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

        solar_df = df

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
        fig_ghi = px.line(solar_df, x = "Date", y = "GHI")
        fig_dhi = px.line(solar_df, x = "Date", y = "DHI")
        fig_dni = px.line(solar_df, x = "Date", y = "DNI")
        fig_temp = px.line(solar_df, x = "Date", y = "Temperature")
        return [
            html.H1('Global Horizontal Irradiance [W/m^2] vs. Date'),
            dcc.Graph(figure = fig_ghi), 
            html.Hr(),

            html.H1('Direct Horizontal Irradiance [W/m^2] vs. Date'),
            dcc.Graph(figure = fig_dhi),
            html.Hr(), 

            html.H1('Direct Normal Irradiance [W/m^2] vs. Date'),
            dcc.Graph(figure = fig_dni),
            html.Hr(),

            html.H1('Temperature [Celcius] vs Date'),
            dcc.Graph(figure = fig_temp),
            html.Hr()
            ]
    except:
        return []
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@ PAGE 3 Load. Callback Functions                      @
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.callback(
    # updates the output of the 
    Output('total-annual-load', 'children'),
    
    Input('submit-load', 'n_clicks'),
    Input('January-Consumption', 'value'),
    Input('February-Consumption', 'value'),
    Input('March-Consumption', 'value'),
    Input('April-Consumption', 'value'),
    Input('May-Consumption', 'value'),
    Input('June-Consumption', 'value'),
    Input('July-Consumption', 'value'),
    Input('August-Consumption', 'value'),
    Input('September-Consumption', 'value'),
    Input('October-Consumption', 'value'),
    Input('November-Consumption', 'value'),
    Input('December-Consumption', 'value'),
    
)

def total_load_Cons(n_clicks,January_Consumption,Febrary_Consumption,March_Consumption,April_Consumption,May_Consumption,June_Consumption,
                    July_Consumption,August_Consumption,September_Consumption,October_Consumption,November_Consumption,December_Consumption,annual_load):
    if n_clicks is not None:    
        load_sum = sum(January_Consumption,Febrary_Consumption,March_Consumption,April_Consumption,May_Consumption,June_Consumption,
                        July_Consumption,August_Consumption,September_Consumption,October_Consumption,November_Consumption,December_Consumption)
        annual_load = f'{load_sum} kW'

        return [annual_load]

    else :
        annual_load = f'0 kW'
        return [annual_load]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@ PAGE 4 Rooftop. Callback Functions                      @
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# Callback for the Custom Rooftop Slope Input to be hidden unless "Custom" Radio button is selected
@app.callback(
    # updates the output of the 
    Output(component_id='roofslope_custominput', component_property='style'),
    [Input(component_id='roofslope_radio', component_property='value')]
)
#If Radio Button 5 (Custom) is selected: dislay custom value input. Else: hide custom value input
def show_hide_customroofslope(roofslope_radio):
    if roofslope_radio == 5:
        return {'display': 'block'}
    else :
        return {'display': 'none'}        

if __name__ == "__main__":
    app.run_server(debug=True)