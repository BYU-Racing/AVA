from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import cProfile

from Plots import *
from Converter import get_latest_data
from Config import themes, Sensor

# TODO play button

# create Dash object
app = Dash(__name__)

# load data
source, file_names = get_latest_data() if REAL_DATA else DEFAULT_SOURCE
print("Loading data from", source)
print("Files used:", file_names)
default_file = file_names[-1] if REAL_DATA else DEFAULT_FILE
all_sensors, start_time, end_time = readData(source, return_times=True)

# initialize local starting variables
duration = end_time + start_time
ready = False
view = SELECTED_THEME

# construct initial plots
frame_ids = [sid for sid in all_sensors.keys()]
fig = display_dashboard(all_sensors, theme=view, avail=frame_ids, num_plots=3)
spd = speedometer(0, theme=view)
pdl = pedals(theme=view)

# styles
button_style = [  # selected
    {'fontFamily': themes[view]["font"]["title"],
     'color': themes[view]["color"][1][2],
     'backgroundColor': themes[view]["color"][2][2],
     'fontSize': themes[view]["size"]["medium"] + "px",
     'display': 'inline-block', 'width': '9%', 'marginLeft': '6px',
     'marginBottom': '10px',
     'border': "1.5px solid " + themes[view]["color"][0][0],
     },
    # deselected
    {'fontFamily': themes[view]["font"]["title"],
     'color': themes[view]["color"][2][2],
     'backgroundColor': themes[view]["color"][0][0],
     'fontSize': themes[view]["size"]["medium"] + "px",
     'display': 'inline-block', 'width': '9%', 'marginLeft': '6px',
     'marginBottom': '10px',
     'border': "1.5px solid " + themes[view]["color"][2][2],
     },
]

# CONSTRUCT INSTANT GRAPHS
instant_graphs = []
call_back_ids = []
# speedometer
if Sensor.SPEED.value in frame_ids:
    instant_graphs.append(
        dcc.Graph(
            id='speedometer',
            figure=spd,
            style={'width': '50vh', 'height': '40vh', 'display': 'inline-block', }
        ))
    call_back_ids.append('speedometer')

# bar chart for brake and accelerator
if Sensor.BRAKE.value in frame_ids or Sensor.THROT.value in frame_ids:
    instant_graphs.append(
        dcc.Graph(
            id='pedals',
            figure=pdl,
            style={'width': '50vh', 'height': '40vh', 'display': 'inline-block', }
        ))
    call_back_ids.append('pedals')
# accelerometer g force
if Sensor.GFORCE.value in frame_ids:
    instant_graphs.append(
        dcc.Graph(id='g-force',
                  config={'displayModeBar': False},
                  style={'width': '50vh', 'height': '40vh', 'display': 'inline-block', }))
    call_back_ids.append('g-force')
# steering wheel
if Sensor.ANGLE.value in frame_ids:
    instant_graphs.append(
        dcc.Graph(id='steering-wheel',
                  config={'displayModeBar': False},
                  style={'width': '50vh', 'height': '40vh', 'display': 'inline-block', }))
    call_back_ids.append('steering-wheel')

# track position
if Sensor.GPS.value in frame_ids:
    instant_graphs.append(
        dcc.Graph(id='track-position',
                  config={'displayModeBar': False},
                  style={'width': '50vh', 'height': '40vh', 'display': 'inline-block', }))
    call_back_ids.append('track-position')

# additional text data
instant_graphs.append(
    html.P(id='output-values', children="",
           style={'width': '50vh', 'height': '40vh', 'display': 'inline-block',
                  'margin': '10px',
                  'color': themes[view]["color"][2][2],
                  'fontFamily': themes[view]["font"]["p"],
                  'fontSize': themes[view]["size"]["small"] + "px",
                  'verticalAlign': 'top', 'whiteSpace': 'pre-line'}))

# DISPLAY DASHBOARD
app.layout = html.Div([
    html.Div([

        # loading animation
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1"),
            style={'width': '100px', 'display': 'inline-block', 'textAlign': 'center', },
            color=themes[view]["color"][2][2],
        ),

        # logo
        # html.Img(src=app.get_asset_url("club_logo.JPG"),
        #          style={'width': '8%', 'height': 'auto', 'marginLeft': '10px', 'marginBottom': '5px',
        #                 'display': 'inline-block', 'verticalAlign': 'bottom'}),

        # title
        html.H1('A.V.A.', style={'color': themes[view]["color"][2][2],
                                 'paddingLeft': '10px', 'paddingTop': '0px',
                                 'paddingBottom': '0px', 'margin': '0px',
                                 'display': 'inline-block', 'width': '8%',
                                 'fontFamily': themes[view]["font"]["title"],
                                 'fontStyle': 'italic', 'verticalAlign': 'bottom',
                                 'marginBottom': '5px',
                                 },
                id='dashboard-title'),

        # tab buttons
        html.Button('Throttle', id='acc-button', n_clicks=0,
                    style=button_style[0]),
        html.Button('Brake', id='brk-button', n_clicks=0,
                    style=button_style[0]),
        html.Button('Tires', id='tir-button', n_clicks=0,
                    style=button_style[0]),
        html.Button('Steering', id='str-button', n_clicks=0,
                    style=button_style[0]),
        html.Button('Dampers', id='dmp-button', n_clicks=0,
                    style=button_style[0]),
        html.Button('Battery', id='bat-button', n_clicks=0,
                    style=button_style[0]),
        html.Button('G-Force', id='g-button', n_clicks=0,
                    style=button_style[0]),

        # display toggle
        dcc.RadioItems(['Expanded', 'Condensed'], 'Expanded',
                       id='size_radio',
                       labelStyle={'display': 'block'},
                       style={
                           'fontFamily': themes[view]["font"]["title"],
                           'color': themes[view]["color"][2][2],
                           'fontSize': themes[view]["size"]["small"] + "px",
                           'display': 'inline-block', 'width': '9%', "padding": '0px',
                           'marginLeft': '15px', 'marginTop': '0px', 'verticalAlign': 'bottom',
                           'marginBottom': '5px',
                       }),

        dcc.Dropdown(file_names, default_file,
                     id='file_dropdown',
                     placeholder="Select a file",
                     style={
                         'height': '35px', 'width': '110px', 'display': 'inline-block',
                         'padding': '0px', 'marginLeft': '10px',
                         'fontFamily': themes[view]["font"]["title"],
                         'color': themes[view]["color"][2][2],
                         'fontSize': themes[view]["size"]["small"] + "px",
                         'verticalAlign': 'bottom', 'marginBottom': '5px',
                     }),
    ]),

    # main line charts
    dcc.Graph(
        id='car_go_fast',
        figure=fig,
        style={'width': '100%', 'height': '120vh', 'margin': '0px'}
    ),

    # slider to select and view instantaneous values
    html.Div([
        dcc.Slider(id='time-slider', min=start_time, max=end_time, step=1 / PARTITION, value=0,
                   marks={0: {'label': "0",
                              'style': {'color': themes[view]["color"][2][2]}},
                          duration / 2: {'label': str(round(duration / 2, 1)),
                                         'style': {'color': themes[view]["color"][2][2]}},
                          end_time: {'label': str(round(end_time, 1)),
                                     'style': {'color': themes[view]["color"][2][2]}}
                          },
                   updatemode='drag',
                   ),
    ], style={'marginLeft': '50px', 'width': '80%',
              'fontFamily': themes[view]["font"]["title"],
              'color': themes[view]["color"][2][2],
              'fontSize': themes[view]["size"]["small"] + "px", },
        id='time-slider-container'
    ),

    html.Div(instant_graphs)

],  # overall styling
    style={'backgroundColor': themes[view]["color"][0][2],
           'color': themes[view]["color"][0][2],
           'margin': '0px', 'padding': '0px', 'border': '0px', 'outline': '0px'})


# CALLBACK FUNCTIONS ---------------------------------------------------------------------------------------------------

# CHANGE DATA BASED ON FILE SELECTION
# @app.callback(
#     Output('car_go_fast', 'figure'),
#     Output('time-slider', 'max'),
#     Output(component_id='output-values', component_property='children'),
#     *[Output(component_id=call_id, component_property='figure') for call_id in call_back_ids],
#     Input('file_dropdown', 'value'),
# )
# def update_source(file_name):
#     """
#     Update the data source based on the selected file
#     :param file_name: the name of the selected file
#     :return: updated main line chart, updated time slider, and updated instantaneous values
#     """
#     global all_sensors, start_time, end_time, duration, frame_ids, fig, source, spd, pdl
#
#     # load data
#     source = DATA_PATH + file_name + FILE_TYPE
#     all_sensors, start_time, end_time = readData(source, return_times=True)
#     duration = end_time + start_time
#
#     # construct initial plots
#     frame_ids = [sid for sid in all_sensors.keys()]
#     fig = display_dashboard(all_sensors, theme=view, avail=frame_ids, num_plots=3)
#     spd = speedometer(0, theme=view)
#     pdl = pedals(theme=view)
#
#     # return figures
#     final_tuple = (fig, end_time, "", spd, pdl)
#     input_length = 3 + len(call_back_ids)
#     while len(final_tuple) < input_length:
#         final_tuple += (spd,)
#
#     return final_tuple


# SELECT SUBPLOT BUTTONS
@app.callback(
    Output(component_id='acc-button', component_property='style'),
    Output(component_id='brk-button', component_property='style'),
    Output(component_id='tir-button', component_property='style'),
    Output(component_id='str-button', component_property='style'),
    Output(component_id='dmp-button', component_property='style'),
    Output(component_id='bat-button', component_property='style'),
    Output(component_id='g-button', component_property='style'),
    Output(component_id='car_go_fast', component_property='figure'),
    Output(component_id='car_go_fast', component_property='style'),
    Output(component_id="loading-output-1", component_property="children"),

    Input(component_id='acc-button', component_property='n_clicks'),
    Input(component_id='brk-button', component_property='n_clicks'),
    Input(component_id='tir-button', component_property='n_clicks'),
    Input(component_id='str-button', component_property='n_clicks'),
    Input(component_id='dmp-button', component_property='n_clicks'),
    Input(component_id='bat-button', component_property='n_clicks'),
    Input(component_id='g-button', component_property='n_clicks'),
    Input(component_id='size_radio', component_property='value'),
)
def select_plots(n_click0, n_click1, n_click2, n_click3, n_click4, n_click5, n_click6, size):
    """
    Select which subplots to show and the size of the overall chart
    :param n_click0: number of times the accelerator tab has been clicked
    :param n_click1: number of times the brake tab has been clicked
    :param n_click2: number of times the tires tab has been clicked
    :param n_click3: number of times the steering wheel tab has been clicked
    :param n_click4: number of times the damper position tab has been clicked
    :param n_click5: number of times the battery tab has been clicked
    :param n_click6: number of times the g-force tab has been clicked
    :param size: selection for display size
    :return: button style and new main line chart
    """
    # turn click input into a list
    index = [n_click0, n_click1, n_click2, n_click3, n_click4, n_click5, n_click6]
    on = [i % 2 for i in index]

    # build available list based on which subplots to display
    avail = []
    show_count = 0

    # Iterate over the sensor map
    for i, sensor in button_sensor_map.items():
        # If the plot is turned on
        if on[i] == 0:
            # If the plot index has a list of values (tires or dampers)
            if isinstance(sensor, list):
                # Add the available sensors to the list
                avail.extend([s for s in sensor if s in frame_ids])
                # Increment the show count if any of the sensors are available
                show_count += any(s in frame_ids for s in sensor)
            else:
                # If the sensor is a single value, add it to the list if it's available
                if sensor in frame_ids:
                    avail.append(sensor)
                    show_count += 1

    # built output list
    buttons = [button_style[i % 2] for i in index]

    # resize the additional charts based on size input
    if size == "Expanded":
        tall = '90vh'
        resize = "small"
    else:
        tall = '60vh'
        resize = "mini"

    # rebuild the main plot with the new availability list
    new_plot = display_dashboard(all_sensors, theme=view, size=resize, avail=avail, num_plots=show_count)
    buttons.append(new_plot)

    reformat = {'width': '100%', 'height': tall, 'margin': '0px'}
    buttons.append(reformat)
    buttons.append(size)

    # return output list
    return buttons


@app.callback(
    Output('time-slider-container', 'style'),
    Input('size_radio', 'value')
)
def update_slider_width(size):
    if size == "Expanded":
        return {'marginLeft': '50px', 'width': '80%',
                'fontFamily': themes[view]["font"]["title"],
                'color': themes[view]["color"][2][2],
                'fontSize': themes[view]["size"]["small"] + "px", }
    else:
        return {'marginLeft': '50px', 'width': '83.5%',
                'fontFamily': themes[view]["font"]["title"],
                'color': themes[view]["color"][2][2],
                'fontSize': themes[view]["size"]["small"] + "px", }


# SELECT TIME SLIDER AND DISPLAY MODE RADIO BUTTONS
@app.callback(
    Output(component_id='output-values', component_property='children'),
    *[Output(component_id=call_id, component_property='figure') for call_id in call_back_ids],
    *[Output(component_id=call_id, component_property='style') for call_id in call_back_ids],
    Input(component_id='time-slider', component_property='value'),
    Input(component_id='size_radio', component_property='value'),
)
def update_output_div(input_value, size):
    """
    Update each chart based on the input time from the slider object
    Parameters:
        :param size: (string) the size of the display
        :param input_value: (string) the desired time to view data at
    Returns:
        :return: list of updated plots
    """
    # parse the input time and convert it to an integer
    try:
        time = float(input_value)
    except ValueError:
        time = None

    # if the input is not a valid integer, display an error message
    if time is None:
        return 'Please enter a valid decimal time greater than zero.', \
            speedometer(0, maxim=10, theme=view), \
            pedals(theme=view), \
            steering(theme=view), \
            track(theme=view), \
            g_force(0, 0, theme=view)

    else:
        # get the values of each subplot at the input time
        values = []
        out_index = 0
        for i in range(len(legend)):
            trace = fig['data'][i]
            # find the index where trace['x'] is closest to the input time
            time_index = np.abs(np.array(trace['x'] / 60) - time).argmin()
            out_index = trace['x'][time_index]
            value = round(trace['y'][time_index], 4)
            values.append(f'{legend[i]}: {value}')

        # compute the average speed to display
        speed = np.mean(
            [float(values[i].split(":")[1][1:]) for i in range(3, 7)]) if Sensor.SPEED.value in frame_ids else 0

        # get brake and accelerator values
        brake = float(values[1].split(":")[1][1:]) / BRAKE_MAX if Sensor.BRAKE.value in frame_ids else 0
        acceleration = float(values[0].split(":")[1][1:]) / THROT_MAX if Sensor.THROT.value in frame_ids else 0

        # compute the instantaneous g-force to display
        lat_g = brake
        lon_g = speed

        # display extra values
        minute = int(time)
        second = int((time - minute) * 60)
        placeholder = "0" if second < 10 else ""
        extra = f"Time = {minute}:{placeholder}{second}" + " | " + str(out_index) + "s\n\n" + '\n'.join(values[-5:])

        # get steering angle
        angle = float(values[9].split(":")[1][1:]) if Sensor.ANGLE.value in frame_ids else 0

        # update sizes
        if size == "Expanded":
            wide = '50vh'
            tall = '40vh'
            resize = "medium"
        else:
            wide = '35vh'
            tall = '28vh'
            resize = "small"

        update = {'width': wide, 'height': tall, 'display': 'inline-block'}

        # return figures
        global ready
        if not ready:
            print("AVA is ready")
            ready = True

        final_tuple = (extra,)
        if Sensor.SPEED.value in frame_ids:
            final_tuple += (speedometer(speed, maxim=2, theme=view, size=resize),)
        if Sensor.BRAKE.value in frame_ids and Sensor.THROT.value in frame_ids:
            final_tuple += (pedals(brake, acceleration, maxim=UNIT_PERCENT, theme=view, size=resize),)
        if Sensor.ANGLE.value in frame_ids:
            final_tuple += (steering(angle=angle, theme=view, size=resize),)
        if Sensor.GPS.value in frame_ids:
            final_tuple += (track(time_stamp=input_value, theme=view, size=resize),)
        if Sensor.GFORCE.value in frame_ids:
            final_tuple += (g_force(lat_g, lon_g, theme=view, size=resize),)
        input_length = 1 + len(call_back_ids) * 2
        while len(final_tuple) < input_length:
            final_tuple += (update,)

        return final_tuple


def do_the_thing():
    app.run_server(debug=False)


if __name__ == '__main__':
    # webbrowser.get(CHROME).open(LOCAL_HOST)
    # app.run_server(debug=False)
    cProfile.run('do_the_thing()', filename='my_profiling_results')
