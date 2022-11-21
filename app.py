# This file is the main plotly app file with web-browser components and callback actions

# Plotly Dash Imports:
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, State, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# data processing imports:
import numpy as np
import pandas as pd

# image processing imports:
from skimage import io

# internet requests imports:
import requests

# other imports:
from math import cos, pi, pow
from datetime import date
import datetime
import xmltodict
from satellite_img import SatelliteImg, get_new_lat_lng
from nrel_api import NrelApi
from yield_calculation import YieldEstimation

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
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
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
#app.config.suppress_callback_exceptions=True
server = app.server

# side-bar as an html div element: 
sidebar = html.Div(
    [
        dbc.CardImg(src = "/static/images/OpenPV-logos.jpeg", top=True),
        html.Hr(),
        html.P(
            "Navigation Menu", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href = "/", active = "exact"),
                dbc.NavLink("1. Set Rooftop Pitch/Angle", href = "/page-1", active = "exact"),
                dbc.NavLink("2. Set Household Load", href = "/page-2", active = "exact"),
                dbc.NavLink("3. Household Location", href = "/page-3", active = "exact"),
                dbc.NavLink("4. Annual Solar Yield Estimation", href = "/page-4", active = "exact")
            ],

            vertical = True,
            pills = True,
        )
    ],

    style = SIDEBAR_STYLE
)

###############################################################################
# When you click on a sub-page on the sidebar, it uses clicking to navigate   #
# to the href url listed /page-n...  This callback generates the html layout  #
# of the page.                                                                #
###############################################################################
content = html.Div(
    id = "page-content", 
    children = [], 
    style = CONTENT_STYLE
)

app.layout = html.Div(
    [
        dcc.Location(id = "url"),    # add to the address url
        dcc.Store(id = 'ps-check-store', storage_type = 'memory'),
	    dcc.Store(id = 'ma-check-store', storage_type = 'memory'),
	    dcc.Store(id = 'mrp-check-store', storage_type = 'memory'),
        dcc.Store(id = 'rat-pwr-custom', storage_type = 'memory'),
	    dcc.Store(id = 'meff-check-store', storage_type = 'memory'),
	    dcc.Store(id = 'sv-check-store', storage_type = 'memory'),
        dcc.Store(id = 'sys-vol-custom', storage_type = 'memory'),
	    dcc.Store(id = 'mppc-check-store', storage_type = 'memory'),
        dcc.Store(id = 'max-ppc-custom', storage_type = 'memory'),
        dcc.Store(id = 'mod-azimuth', storage_type = 'memory'),
        dcc.Store(id = 'mod-azimuth-custom', storage_type = 'memory'),
        dcc.Store(id = 'rooftop-angle', storage_type = 'memory'),
        dcc.Store(id = 'rooftop-angle-custom', storage_type = 'memory'),
        dcc.Store(id = 'mod-area', storage_type = 'memory'),
        dcc.Store(id = 'panel-size', storage_type = 'memory'),
        dcc.Store(id = 'system-losses', storage_type = 'memory'),
        dcc.Store(id = 'nrel-data', storage_type = 'memory'),
        dcc.Store(id = 'lat-lng', storage_type = 'memory'),
        dcc.Store(id = 'jan-load-store', storage_type = 'memory'),
        dcc.Store(id = 'feb-load-store', storage_type = 'memory'),
        dcc.Store(id = 'mar-load-store', storage_type = 'memory'),
        dcc.Store(id = 'apr-load-store', storage_type = 'memory'),
        dcc.Store(id = 'may-load-store', storage_type = 'memory'),
        dcc.Store(id = 'jun-load-store', storage_type = 'memory'),
        dcc.Store(id = 'jul-load-store', storage_type = 'memory'),
        dcc.Store(id = 'aug-load-store', storage_type = 'memory'),
        dcc.Store(id = 'sep-load-store', storage_type = 'memory'),
        dcc.Store(id = 'oct-load-store', storage_type = 'memory'),
        dcc.Store(id = 'nov-load-store', storage_type = 'memory'),
        dcc.Store(id = 'dec-load-store', storage_type = 'memory'),
        sidebar,
        content
    ]
)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)

#################################################################
# function to load the content for each page                    #
#################################################################
def render_page_content(pathname):

    ############################################################
    # Homepage                                                 #
    ############################################################
    if pathname == "/":
        return [
                html.H1(
                    children = 'Welcome to Open PV',
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
                                                    dbc.CardImg(src = "/static/images/david.png", top=True),  
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
                                                    dbc.CardImg(src = "static/images/nicolas.png", top = True),    
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
                                                    dbc.CardImg(src = "static/images/jaron.png", top = True),  
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
                                                    dbc.CardImg(src = "static/images/Jeremiah.png", top = True), 
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
                                                    dbc.CardImg(src = "static\images\Goryll.png", top = True),    
                                                    dbc.CardBody(
                                                        [
                                                            html.H4('Dr. Michael Goryll (Project Mentor)', className = 'card-title'),
                                                            html.P('ASU associate professor in the School of Electrical, Computer and Energy Engineering')
                                                        ]
                                                    )
                                                ]    
                                            )
                                        )
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
    ##################### End Home Page ########################

    ####################################################
    # Page 1. Manual Input Params                      #
    ####################################################
    elif pathname == "/page-1":
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
                                                dbc.CardBody([html.H4("15\N{DEGREE SIGN}"),]),
                                            ]
                                                ),
                                        ),
                                dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oof30deg.jpg", top=True),
                                                dbc.CardBody([html.H4("30\N{DEGREE SIGN}"),]),    
                                            ],
                                                ),
                                        ),
                                dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oof45deg.jpg", top=True),
                                                dbc.CardBody([html.H4("45\N{DEGREE SIGN}"),]),    
                                            ],
                                                ),
                                        ),
                                dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oof60deg.jpg", top=True),
                                                dbc.CardBody([html.H4("60\N{DEGREE SIGN}"),]),    
                                            ],    
                                                ),
                                        ),
                                dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardImg(src="static\images\oofcustdeg.jpg", top=True),
                                                dbc.CardBody([html.H4("Custom"),]),    
                                            ],    
                                                ),
                                        ),
                                    ] 
                                ),                                
                                dbc.RadioItems(
                                    options = [
                                        {"label": "15\N{DEGREE SIGN}", "value": 15, "disabled": False},
                                        {"label": "30\N{DEGREE SIGN}", "value": 30, "disabled": False},
                                        {"label": "45\N{DEGREE SIGN}", "value": 45, "disabled": False},
                                        {"label": "60\N{DEGREE SIGN}", "value": 60, "disabled": False},
                                        {"label": "Custom", "value": 2, "disabled": False},                                    
                                    ],
                                    id = "rooftop-angle-radio",
                                    inline = True
                                )
                            ]
                        )
                    ]
                ),

                dbc.Row(
                        html.Div(
                        [
                            dbc.Input(
                                id = 'roofslope_custominput', 
                                type = 'number', min=0, max=90, step=1, 
                                placeholder = 'Enter custom roof angle (\N{DEGREE SIGN})',
                                size = '5',)
                                ], style= {'display': 'block'}
                            ),
                        ),                   
                dbc.Row(
                    [
                        html.Hr(),
                        html.Div(
                            [
                                dbc.Button("More Info", id="openinfo", n_clicks=0),
                                dbc.Modal(
                                     [
                                        dbc.ModalHeader(dbc.ModalTitle("Unexpected Costs")),
                                        dbc.ModalBody("Any rooftop steeper than 35\N{DEGREE SIGN} will approximately double the labor cost. Shingles that are considered old and shingles made of wood or clay would need to be replaced with composite shingles which will increase the material and labor costs.",
                                        ),
                                        dbc.ModalFooter(
                                            dbc.Button(
                                                "Close", id="closeinfo", className="infomod", n_clicks=0
                                         )
                                        ),
                                     ],
                        id="modalinfo",
                     is_open=False,
                    ),
                                
                ]
            )
        ]
    ),
                        dbc.Row(
                            [
                    html.H1(
                        'Custom Inputs',
                        style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                    ),
                    
                    html.Hr()
                    ]
                        ),
                        dbc.Row(
                            [
                            html.Div(
                            [
                                dbc.Label("Check any boxes that you want to manually input specific values, if not, approximate or standard values will be used in calculations."),
                                dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id ='mod-az-check')), dbc.InputGroupText("Module Azimuth"), dbc.Input(id = 'mod-azimuth-input', placeholder="Solar Panel Direction/Orientation (degrees)", type="number", min=1, max=360, step=1)]),
                                dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id ='mod-rp-check')), dbc.InputGroupText("Module Rated Power"), dbc.Input(id = 'rat-pwr-input', placeholder="Solar Panel Rated Power (Watts), found in specification of panel manufacturer", type="number", min=1, max=1000, step=1)]),
                                dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id ='mod-eff-check')), dbc.InputGroupText("System Losses"), dbc.Input(id = 'mod-eff-input', placeholder="(decimal percentage), number between 0.01-0.99 usually around 0.15 - 0.25", type="number", min=0.01, max=0.99, step=0.001)]),
                                dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id ='sys-volt-check')), dbc.InputGroupText("System Voltage"), dbc.Input(id = 'sys-vol-input', placeholder="System Voltage (Volts), usually 12V, 24V, or 48V are most common", type="number", min=1, max=100, step=1)]),
                                dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id ='max-ppc-check')), dbc.InputGroupText("Maximum Power Point Current"), dbc.Input(id = 'max-ppc-input', placeholder="Maximum Power Point Current (amps), found in spec sheet, usually around 10A", type="number", min=1, max=30, step=0.01)]),
                                dbc.InputGroup([dbc.InputGroupText(dbc.Checkbox(id ='panel-size-check')), dbc.InputGroupText("Number of Panels"), dbc.Input(id = 'panel-size-input', placeholder="Enter number of panels, this will be calculated at a later step if left blank.", type="number", min=1, step=1)])
                            ]
                        )
                    ]
                )
            ]
    #################### End of Page 1 ################################


    ###################################################################
    # Page 2. Estimation of Household consumption                     #
    ###################################################################
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
                        [
                        dbc.Label("Enter January Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'January-Consumption', 
                            type = 'number',
                            value = 0, 
                            size = '100'
                            ),

                        dbc.Label("Enter February Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'February-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter March Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'March-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter April Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'April-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter May Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'May-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter June Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'June-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            )
                        ]
                   ),

                    dbc.Col(
                        [
                        
                        dbc.Label("Enter July Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'July-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter August Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'August-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter September Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'September-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter October Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'October-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter November Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'November-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        
                        dbc.Label("Enter December Consumption in kW (numerical only)"),

                        dbc.Input(
                            id = 'December-Consumption', 
                            type = 'number', 
                            value = 0, 
                            size = '100'
                            ),
                        ]
                    ),
                    ]
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
                    ]
                )
        ]
    #################### End of Page 2 ################################

    ##################################################################################################
    # Page 3 - Choose Address, find lng-lat, get rooftop-satellite imagery, select outline of roof   #
    ##################################################################################################
    elif pathname == "/page-3":
        return [
                
                dbc.Row(
                    [
                        html.H1(
                            children = 'Set Location, Rooftop Area, and View Data',
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
                        children = 'GPS Coordinates',
                    ),
    
                ),
       
                # Neighborhood View
                dbc.Card(
                    children = [
                        html.H4('Zoom To Find Your House'),
                        html.Div(
                            id = 'neighborhood-div', 
                            children = [dcc.Graph(id = 'neighborhood-graph')], 
                        )
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
                html.H5('Choose Panel Orientation:'),
                dcc.Dropdown(
                    options = [
                        {'label': 'North', 'value': '1'},
                        {'label': 'East', 'value': '90'},
                        {'label': 'South', 'value': '180'},
                        {'label': 'West', 'value': '270'},
                    ],
                    value = '180', 
                    id = 'module-azimuth-dropdown'
                ),

                dbc.Button("Help", id="DirectionHelp", n_clicks=0),
                        dbc.Modal(
                                    [
                                    dbc.ModalHeader(dbc.ModalTitle("Select Rooftop Slope Direction")),
                                    dbc.ModalBody("Select the direction that the slope of the roof will be facing." 
                                    " The image is oriented so that the top is North."
                                    " TIP: In most instances, locations in the US would not have panels facing North. ",
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="closehelp", className="modhelp", n_clicks=0
                                        )
                                    ),
                                    ],
                    id="modhelp",
                    is_open=False,
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
                                    initial_visible_month = date(YEAR, 1, 1),
                                    start_date = date(YEAR, 1, 1),
                                    end_date = date(YEAR, 12, 31)
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
    ############################### End of Page 3 ###########################

    elif pathname =="/page-4":
        return [

            dbc.Row(
                    html.Div(
                        id = 'yield_calculation_div',
                        children = [
                            html.Hr(),

                            html.H1(
                                children = 'Expected Annual Generation & Savings',
                                style = {'textAlign':'center',' background':'darkcyan', 'color':'white'}
                            ),

                            dbc.Button('Generate Annual Solar Energy Yield', color = 'primary', className = 'yield-button'),
                        
                            html.Hr(),

                            html.Div(
                                id = 'ann-power-yield',
                                children = 'Complete steps on Previous Pages to see a yield estimate'
                            ),


                        ],

                        style = {"display": "inline-block"}
                    )
                )
        ]
    # If the user tries to reach a different page, return a 404 message
    else:
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

################################################
# monthly pwr usage                            #
################################################
@app.callback(
    Output('jan-load-store', 'data'),
    Input('January-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('January-Consumption', 'value'),
    Input('jan-load-store', 'data')
)
def render(v):
    return v


@app.callback(
    Output('feb-load-store', 'data'),
    Input('February-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('February-Consumption', 'value'),
    Input('feb-load-store', 'data')
)
def render(v):
    return v


@app.callback(
    Output('mar-load-store', 'data'),
    Input('March-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('March-Consumption', 'value'),
    Input('mar-load-store', 'data')
)
def render(v):
    return v


@app.callback(
    Output('apr-load-store', 'data'),
    Input('April-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('April-Consumption', 'value'),
    Input('apr-load-store', 'data')
)
def render(v):
    return v


@app.callback(
    Output('may-load-store', 'data'),
    Input('May-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('May-Consumption', 'value'),
    Input('may-load-store', 'data')
)
def render(v):
    return v


@app.callback(
    Output('June-Consumption', 'value'),
    Input('jun-load-store', 'data')
)
def render(v):
    return v

@app.callback(
    Output('jun-load-store', 'data'),
    Input('June-Consumption', 'value'),
)
def store(v):
    return v


@app.callback(
    Output('July-Consumption', 'value'),
    Input('jul-load-store', 'data')
)
def render(v):
    return v

@app.callback(
    Output('jul-load-store', 'data'),
    Input('July-Consumption', 'value'),
)
def store(v):
    return v


@app.callback(
    Output('August-Consumption', 'value'),
    Input('aug-load-store', 'data')
)
def render(v):
    return v

@app.callback(
    Output('aug-load-store', 'data'),
    Input('August-Consumption', 'value'),
)
def store(v):
    return v


@app.callback(
    Output('September-Consumption', 'value'),
    Input('sep-load-store', 'data')
)
def render(v):
    return v

@app.callback(
    Output('sep-load-store', 'data'),
    Input('September-Consumption', 'value'),
)
def store(v):
    return v



@app.callback(
    Output('oct-load-store', 'data'),
    Input('October-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('October-Consumption', 'value'),
    Input('oct-load-store', 'data')
)
def render(v):
    return v


@app.callback(
    Output('nov-load-store', 'data'),
    Input('November-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('November-Consumption', 'value'),
    Input('nov-load-store', 'data')
)
def render(v):
    return v

@app.callback(
    Output('dec-load-store', 'data'),
    Input('December-Consumption', 'value'),
)
def store(v):
    return v

@app.callback(
    Output('December-Consumption', 'value'),
    Input('dec-load-store', 'data')
)
def render(v):
    return v
################################################

#################################################
# User Custom Input Checkbox Save
##################################################
#Max Power Point Current Checkbox Store
@app.callback(
    Output('mppc-check-store', 'data'),
    Input('max-ppc-check', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('max-ppc-check', 'value'),
    Input('mppc-check-store', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Max Power Point Current Custom input Store
@app.callback(
    Output('max-ppc-custom', 'data'),
    Input('max-ppc-input', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('max-ppc-input', 'value'),
    Input('max-ppc-custom', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#System Voltage Checkbox Store
@app.callback(
    Output('sv-check-store', 'data'),
    Input('sys-volt-check', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('sys-volt-check', 'value'),
    Input('sv-check-store', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#System Voltage Custom input Store
@app.callback(
    Output('sys-vol-custom', 'data'),
    Input('sys-vol-input', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('sys-vol-input', 'value'),
    Input('sys-vol-custom', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Module Efficiency Checkbox Store
@app.callback(
    Output('meff-check-store', 'data'),
    Input('mod-eff-check', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('mod-eff-check', 'value'),
    Input('meff-check-store', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Module Rated Power Checkbox Store
@app.callback(
    Output('mrp-check-store', 'data'),
    Input('mod-rp-check', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('mod-rp-check', 'value'),
    Input('mrp-check-store', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Module Rated Power Custom input Store
@app.callback(
    Output('rat-pwr-custom', 'data'),
    Input('rat-pwr-input', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('rat-pwr-input', 'value'),
    Input('rat-pwr-custom', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Module Azimuth Checkbox Store
@app.callback(
    Output('ma-check-store', 'data'),
    Input('mod-az-check', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('mod-az-check', 'value'),
    Input('ma-check-store', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Module Azimuth Custom Value
@app.callback(
    Output('mod-azimuth-custom', 'data'),
    Input('mod-azimuth-input', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('mod-azimuth-input', 'value'),
    Input('mod-azimuth-custom', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#Panel Size Checkbox Store
@app.callback(
    Output('ps-check-store', 'data'),
    Input('panel-size-check', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('panel-size-check', 'value'),
    Input('ps-check-store', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#################################################
# dropdown menu panel azimuth
##################################################
@app.callback(
    Output('mod-azimuth', 'data'),
    Input('module-azimuth-dropdown', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('module-azimuth-dropdown', 'value'),
    Input('mod-azimuth', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

#################################################
# custom roofslope 
##################################################
@app.callback(
    Output('rooftop-angle-custom', 'data'),
    Input('roofslope_custominput', 'value'),
)
def update_custom_roofslope_memory(m_az):
    return m_az

@app.callback(
    Output('roofslope_custominput', 'value'),
    Input('rooftop-angle-custom', 'data')
)
def update_custom_roofslope_page(m_az):
    return m_az

################################################
# circular dependency to store module azimuth  #
################################################
@app.callback(
    Output('rooftop-angle', 'data'),
    Input('rooftop-angle-radio', 'value'),
)
def update_mod_azimuth(m_az):
    return m_az

@app.callback(
    Output('rooftop-angle-radio', 'value'),
    Input('rooftop-angle', 'data')
)
def update_mod_azimuth(m_az):
    return m_az

#########################################

@app.callback(
    Output('panel-size', 'data'),
    Input('panel-size-input', 'value')
)
def update_mod_area(m_area):
    return m_area

@app.callback(
    Output('panel-size-input', 'value'),
    Input('panel-size', 'data')
)
def update_mod_area(m_area):
    return m_area

#############################################
@app.callback(
    Output('system-losses', 'data'),
    Input('mod-eff-input', 'value')
)
def update_mod_eff(m_eff):
    return m_eff

@app.callback(
    Output('mod-eff-input', 'value'),
    Input('system-losses', 'data')
)
def update_mod_eff(m_eff):
    return m_eff

#################################################
# Callback for the Submit Button
@app.callback(
    # updates the output of the 
    Output('lat-lng', 'data'),
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
    Input('lat-lng', 'data'),
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
            fig.update_layout(
                dragmode = "drawrect", 
                width = 1000, 
                height = 1000, 
                autosize=False, 
                newshape = dict(fillcolor = "yellow", opacity = 0.3, line = dict(color = "darkblue", width = 8))
                )
            neighborhood_graph = dcc.Graph(id = 'neighborhood-graph', figure = fig, config = config)
            return neighborhood_graph
        except:
            img = io.imread('black.jpg')
            fig = px.imshow(img)
            fig.update_layout(
                dragmode = "drawrect", 
                width = 1000, 
                height = 1000, 
                autosize=False, 
                newshape = dict(fillcolor = "yellow", opacity = 0.3, line = dict(color = "darkblue", width = 8))
                )
            return dcc.Graph(id = 'neighborhood-graph', figure = fig)
    else:
            img = io.imread('black.jpg')
            fig = px.imshow(img)
            fig.update_layout(
                dragmode = "drawrect", 
                width = 1000, 
                height = 1000, 
                autosize=False, 
                newshape = dict(fillcolor = "yellow", opacity = 0.3, line = dict(color = "darkblue", width = 8))
                )
            return dcc.Graph(id = 'neighborhood-graph', figure = fig)



################################################
# getting and setting rooftop view             #
################################################
@app.callback(
    Output("rooftop-div", "children"),
    Input('lat-lng', 'data'),
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
            fig.update_layout(
                dragmode = "drawrect", 
                width = 1000, 
                height = 1000, 
                autosize=False, 
                newshape = dict(fillcolor = "yellow", opacity = 0.3, line = dict(color = "darkblue", width = 8))
                )
            return dcc.Graph(id = 'rooftop-graph', figure = fig, config = config)
        else:
            raise Exception

    except:
        img = io.imread('black.jpg')
        fig = px.imshow(img)
        fig.update_layout(
                dragmode = "drawrect", 
                width = 1000, 
                height = 1000, 
                autosize=False, 
                newshape = dict(fillcolor = "yellow", opacity = 0.3, line = dict(color = "darkblue", width = 8))
                )
        return dcc.Graph(id = 'rooftop-graph', figure = fig, config = config)


######################################
# drawing on roof and computing area #
######################################
@app.callback(
    Output('mod-area', 'data'),
    Input('lat-lng', 'data'),
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

        return area
    except:
        return 0

#Callback for Help Modal after rooftop Image
@app.callback(
    Output("modhelp", "is_open"),
    [Input("DirectionHelp", "n_clicks"), Input("closehelp", "n_clicks")],
    [State("modhelp", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('available-roof-area', 'children'),
    Input('mod-area', 'data')
)
def display_selected_area(mod_area):
    return [html.H1(f'The Available Rooftop Area is {round(mod_area, 2)} square meters')]


@app.callback(
    Output('nrel-data', 'data'),
    Input('gps_coords', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
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
        df, gmt_offset = nr.get_nrel_df()

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

        solar_json = df.to_json(orient = 'records')
        return solar_json, gmt_offset

    except Exception as e:
        print(e)
        return []

@app.callback(
    Output('nrel_table_div', 'children'),
    Input('nrel-data', 'data')
)
def display_nrel_df(nrel_data):
    try:
        solar_json = nrel_data[0]
        df = pd.DataFrame(eval(solar_json))
        data_table = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], persistence = True)
        return data_table
    except:
        return None

@app.callback(
    Output('irradiance-timeplot', 'children'),
    [Input('nrel-data', 'data')]
    )        
def irradiance_plotter(df):
    try:
        solar_df = pd.DataFrame(eval(df[0]))
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

# Callback for the Custom Rooftop Slope Input to be hidden unless "Custom" Radio button is selected
@app.callback(
    # updates the output of the 
    Output(component_id = 'roofslope_custominput', component_property = 'style'),
    [Input(component_id = 'rooftop-angle-radio', component_property = 'value')]
)
#If Radio Button 5 (Custom) is selected: dislay custom value input. Else: hide custom value input
def show_hide_customroofslope(roofslope_radio):
    if roofslope_radio == 2:
        return {'display': 'block'}
    else :
        return {'display': 'none'}
#Call Back for the Roof Slope Page More Info Modal
@app.callback(
    Output("modalinfo", "is_open"),
    [Input("openinfo", "n_clicks"), Input("closeinfo", "n_clicks")],
    [State("modalinfo", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open   

@app.callback(
    Output('gps_coords', 'children'),
    Input('lat-lng', 'data')
)
def print_coords(coords):
    return coords


@app.callback(
    Output('ann-power-yield', 'children'),
    Input('lat-lng', 'data'),
    Input('mod-area', 'data'),
    Input('nrel-data', 'data'),
    Input('rooftop-angle', 'data'),
    Input('rooftop-angle-custom', 'data'),
    Input('mod-azimuth', 'data'),
    Input('ps-check-store', 'data'),
    Input('panel-size', 'data'),
    Input('ma-check-store', 'data'),
    Input('mod-azimuth-custom', 'data'),
    Input('mrp-check-store', 'data'),
    Input('rat-pwr-custom', 'data'),
    Input('meff-check-store', 'data'),
    Input('system-losses', 'data'),
    Input('sv-check-store', 'data'),
    Input('sys-vol-custom', 'data'),
    Input('mppc-check-store', 'data'),
    Input('max-ppc-custom', 'data'),

    Input('jan-load-store', 'data'),
    Input('feb-load-store', 'data'),
    Input('mar-load-store', 'data'),
    Input('apr-load-store', 'data'),
    Input('may-load-store', 'data'),
    Input('jun-load-store', 'data'),
    Input('jul-load-store', 'data'),
    Input('aug-load-store', 'data'),
    Input('sep-load-store', 'data'),
    Input('oct-load-store', 'data'),
    Input('nov-load-store', 'data'),
    Input('dec-load-store', 'data')
)
def mon_consume_vs_yield(coords, area, nrel_data, ra, rac, ma, psc, psi, mac, mai, mrpc, mrpi, meffc, meffi, svc, svi, mppcc, mppci, jan, feb, mar, apr, may, jun, jul, aug, sep, october, nov, dec):
    AVERAGE_PANEL_AREA_MM = 1.64
    try:
        monthly_consumption = [jan, feb, mar, apr, may, jun, jul, aug, sep, october, nov, dec]
        nrel_df = pd.DataFrame(eval(nrel_data[0]))
        gmt_offset = nrel_data[1]
        lat = coords.split(',')[0]
        lng = coords.split(',')[1]

        # module elevation logic
        if ra == 2:
            me = rac
        else:
            me = ra
        # panel size area checkbox logic
        if psc == True:
            modarea = psi
        else:
            modarea = round(area / AVERAGE_PANEL_AREA_MM)

	    # module azimuth checkbox logic
        if mac == True:
            modaz = mai
        else:
            modaz = int(ma)

        # module rated power checkbox logic
        if mrpc == True:
            modratpow = mrpi
        else:
            modratpow = 320

	    # module efficiency checkbox logic
        if meffc == True:
            modeff = meffi
        else:
            modeff = 0.2

	    # system voltage checkbox logic
        if svc == True:
            sysvolt = svi
        else:
            sysvolt = 48

	    # max power point current checkbox logic
        if mppcc == True:
            maxpowpc = mppci
        else:
            maxpowpc = 10

        ay = YieldEstimation(
            module_azimuth = modaz,
            module_elevation = me,
            module_area = modarea, # needs to be changed to number of panels
            rated_power = modratpow,
            maximum_power_point_current = maxpowpc,
            system_voltage = sysvolt,
            system_losses = modeff,
            nrel_data = nrel_df,
            gmt_offset = gmt_offset,
            latitude = lat,
            longitude = lng
        )

        ap = ay.get_total_yearly_power()
        
        monthly_yields = ay.get_monthly_yields()
        
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        fig = go.Figure(
            data = [
                go.Bar(name = 'PV Generated Power', x = months, y = monthly_yields),
                go.Bar(name = 'Household Consumed Power', x = months, y = monthly_consumption)
            ],
            
        )
        fig.update_layout(title = 'Monthly Generated vs Consumed PV power [kWh]', barmode = 'group')

        savings_factor = 0.176
        total_savings = 0
        for i in monthly_yields:
            total_savings = total_savings + i * savings_factor
        
        return [
            html.H3(f'Your estimated Annual Power Yield is {round(ap, 2)} kWh'), 
            dcc.Graph(id = 'monthly-consume-vs-yield', figure = fig),
            html.H3(f'This PV system is estimated to save you ${total_savings} per year on your electricity bill')
            ]
    except Exception as e:
        print(e)
        return fig

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@ PAGE 3 Load. Callback Functions                         @
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
                    July_Consumption,August_Consumption,September_Consumption,October_Consumption,November_Consumption,December_Consumption):
    if n_clicks is not None: 
        load_sum = January_Consumption + Febrary_Consumption + March_Consumption + April_Consumption + May_Consumption + June_Consumption + July_Consumption + August_Consumption + September_Consumption + October_Consumption + November_Consumption + December_Consumption
        annual_load = f'{load_sum} kW'

        return [annual_load]

    else :
        annual_load = f'0 kW'
        return [annual_load]

if __name__ == "__main__":
    app.run_server(debug = True)#, dev_tools_ui = False, dev_tools_props_check = False)