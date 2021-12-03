"""
    Embed bokeh server session into a flask framework
    Adapted from bokeh-master/examples/howto/serve_embed/flask_gunicorn_embed.py
"""

import asyncio
import logging
import os
from threading import Thread
import time

from bokeh import __version__ as bokeh_release_ver
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Div, Select, TextInput, RangeSlider, LinearColorMapper, ColorBar, Legend
from bokeh.models.ranges import FactorRange
from bokeh.plotting import figure
from bokeh.resources import get_sri_hashes_for_version
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.sampledata.us_states import data as states
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from bokeh.themes import Theme
from bokeh.transform import factor_cmap, dodge
import pandas as pd
import numpy as np
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


from server.config import (
    BOKEH_ADDR,
    BOKEH_CDN,
    BOKEH_PATH,
    BOKEH_URL,
    FLASK_ADDR,
    FLASK_PORT,
    cwd,
    set_bokeh_port,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


BOKEH_BROWSER_LOGGING = """
    <script type="text/javascript">
      Bokeh.set_log_level("debug");
    </script>
"""


def bkapp(doc):
    """Bokeh App

    Arguments:
        doc {Bokeh Document} -- bokeh document

    Returns:
        Bokeh Document --bokeh document with plot and slider
    """
    
    data = pd.read_csv("https://github.com/gottharsis/4242fall2021/blob/bokeh_working/server/vaers_jan_nov_2021.csv?raw=true", usecols=['VAERS_ID', "SYMPTOM1", "SYMPTOM2", "SYMPTOM3", "SYMPTOM4", "SYMPTOM5", 'SEX', 'STATE', 'AGE_YRS', 'VAX_MANU', 'ALLERGIES', 'HISTORY'], encoding='utf-8-sig', encoding_errors='ignore')
    data.drop_duplicates(subset=['VAERS_ID'], inplace=True)
    data['ALLERGIES'] = data['ALLERGIES'].str.lower()
    data['HISTORY'] = data['HISTORY'].str.lower()

    symptoms = ["Headache", "Fatigue", "Chills", "Dizziness", "Pain"]
    vaccines = ["Janssen", "Moderna", "Pfizer\Biontech"]
    sexes = ["Male", "Female"]
    ages = ["12 - 30", "30 - 48", "48 - 66", "66 - 84"]

    group = {'Vaccine Manufacturer': vaccines, symptoms[0]: [], symptoms[1]: [], symptoms[2]: [], symptoms[3]: [], symptoms[4]: []}

    for vax in vaccines:
        vax = vax.upper()

        divisor = data[data['VAX_MANU'] == vax].count()['VAERS_ID']

        df = pd.concat([data[(data['SYMPTOM1'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM1')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM2'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM2')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM3'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM3')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM4'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM4')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM5'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM5')[['VAERS_ID']].count()], axis = 1).sum(axis = 1) \
                .divide(pd.Series(data=[divisor]*5, index=symptoms), fill_value=0)
        
        for i in range(len(symptoms)):
            group[symptoms[i]].append(df[symptoms[i]])
    

    x = [(vaccine, symptom) for vaccine in vaccines for symptom in symptoms]
    counts = sum(zip(group[symptoms[0]], group[symptoms[1]], group[symptoms[2]], group[symptoms[3]], group[symptoms[4]]), ())

    # Create Input controls
    x_axis = Select(title="X-axis", value="Vaccine Manufacturer", options=["Vaccine Manufacturer", "Sex", "Age"])
    allergy = TextInput(title="Allergy contains")
    history = TextInput(title="Medical history contains")

    # Create Column Data Source that will be used by the plot
    source = ColumnDataSource(data={'x': x, 'counts': counts})

    desc = Div(text="COVID-19 Vaccine Adverse Reactions (VAERS) Visualiations", sizing_mode="stretch_width")

    # Select new data
    def select_data():
        allergy_val = allergy.value
        history_val = history.value

        selected = data

        if (allergy_val != ""):
            selected = selected[selected['ALLERGIES'].str.contains(allergy_val.lower()) == True]

        if (history_val != ""):
            selected = selected[selected['HISTORY'].str.contains(history_val.lower()) == True]

        return selected

    # Update data
    def update():
        df = select_data()
        option = x_axis.value

        if option == 'Vaccine Manufacturer':
            
            new_group = {'Vaccine Manufacturer': vaccines, symptoms[0]: [], symptoms[1]: [], symptoms[2]: [], symptoms[3]: [], symptoms[4]: []}

            for vax in vaccines:
                vax = vax.upper()

                divisor = df[df['VAX_MANU'] == vax].count()['VAERS_ID']

                new_data = pd.concat([df[(df['SYMPTOM1'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM1')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM2'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM2')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM3'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM3')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM4'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM4')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM5'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM5')[['VAERS_ID']].count()], axis = 1).sum(axis = 1) \
                        .divide(pd.Series(data=[divisor]*5, index=symptoms), fill_value=0)
                
                for i in range(len(symptoms)):
                    new_group[symptoms[i]].append(new_data[symptoms[i]])

            new_x = [(vaccine, symptom) for vaccine in vaccines for symptom in symptoms]
            new_counts = sum(zip(new_group[symptoms[0]], new_group[symptoms[1]], new_group[symptoms[2]], new_group[symptoms[3]], new_group[symptoms[4]]), ())
            
            source.data = {'x': new_x, 'counts': new_counts}
            p.x_range.factors = new_x
            
        elif option == 'Sex':

            new_group = {'Sex': sexes, symptoms[0]: [], symptoms[1]: [], symptoms[2]: [], symptoms[3]: [], symptoms[4]: []}

            for sex in sexes:
                sex = sex[0]

                divisor = df[df['SEX'] == sex].count()['VAERS_ID']

                new_data = pd.concat([df[(df['SYMPTOM1'].isin(symptoms)) & (df['SEX'] == sex)].groupby(by='SYMPTOM1')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM2'].isin(symptoms)) & (df['SEX'] == sex)].groupby(by='SYMPTOM2')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM3'].isin(symptoms)) & (df['SEX'] == sex)].groupby(by='SYMPTOM3')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM4'].isin(symptoms)) & (df['SEX'] == sex)].groupby(by='SYMPTOM4')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM5'].isin(symptoms)) & (df['SEX'] == sex)].groupby(by='SYMPTOM5')[['VAERS_ID']].count()], axis = 1).sum(axis = 1) \
                        .divide(pd.Series(data=[divisor]*5, index=symptoms), fill_value=0)
                
                for i in range(len(symptoms)):
                    new_group[symptoms[i]].append(new_data[symptoms[i]])

            new_x = [(sex, symptom) for sex in sexes for symptom in symptoms]
            new_counts = sum(zip(new_group[symptoms[0]], new_group[symptoms[1]], new_group[symptoms[2]], new_group[symptoms[3]], new_group[symptoms[4]]), ())
            
            source.data = {'x': new_x, 'counts': new_counts}
            p.x_range.factors = new_x

        else:

            new_group = {'Age': ages, symptoms[0]: [], symptoms[1]: [], symptoms[2]: [], symptoms[3]: [], symptoms[4]: []}

            for age in ages:
                age_range = (float(age[:2]), float(age[-2:]))

                divisor = df[(df['AGE_YRS'] >= age_range[0]) & (df['AGE_YRS'] < age_range[1])].count()['VAERS_ID']

                new_data = pd.concat([df[(df['SYMPTOM1'].isin(symptoms)) & (df['AGE_YRS'] >= age_range[0]) & (df['AGE_YRS'] < age_range[1])].groupby(by='SYMPTOM1')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM2'].isin(symptoms)) & (df['AGE_YRS'] >= age_range[0]) & (df['AGE_YRS'] < age_range[1])].groupby(by='SYMPTOM2')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM3'].isin(symptoms)) & (df['AGE_YRS'] >= age_range[0]) & (df['AGE_YRS'] < age_range[1])].groupby(by='SYMPTOM3')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM4'].isin(symptoms)) & (df['AGE_YRS'] >= age_range[0]) & (df['AGE_YRS'] < age_range[1])].groupby(by='SYMPTOM4')[['VAERS_ID']].count(), \
                        df[(df['SYMPTOM5'].isin(symptoms)) & (df['AGE_YRS'] >= age_range[0]) & (df['AGE_YRS'] < age_range[1])].groupby(by='SYMPTOM5')[['VAERS_ID']].count()], axis = 1).sum(axis = 1) \
                        .divide(pd.Series(data=[divisor]*5, index=symptoms), fill_value=0)
                
                for i in range(len(symptoms)):
                    new_group[symptoms[i]].append(new_data[symptoms[i]])

            new_x = [(age, symptom) for age in ages for symptom in symptoms]
            new_counts = sum(zip(new_group[symptoms[0]], new_group[symptoms[1]], new_group[symptoms[2]], new_group[symptoms[3]], new_group[symptoms[4]]), ())
            
            source.data = {'x': new_x, 'counts': new_counts}
            p.x_range.factors = new_x
            
    # Set up controls/widgets
    controls = [allergy, history, x_axis]

    for control in controls:
        control.on_change('value', lambda attr, old, new: update())

    # Set up figure
    p = figure(x_range=FactorRange(*x), width=400, height=400, title="Symptom prevalence", \
                toolbar_location=None, tools="")

    p.vbar(x='x', top='counts', source=source, width=0.9, line_color="white", \
        fill_color=factor_cmap('x', palette=['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99'], factors=symptoms, start=1, end=2))

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 'vertical'
    p.y_range.start = 0

    #########################################################################################
    # GRAPH 2
    #########################################################################################

    group2 = {'Vaccine Manufacturer': vaccines, symptoms[0]: [], symptoms[1]: [], symptoms[2]: [], symptoms[3]: [], symptoms[4]: []}

    for vax in vaccines:
        vax = vax.upper()

        divisor = data[data['VAX_MANU'] == vax].count()['VAERS_ID']

        df = pd.concat([data[(data['SYMPTOM1'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM1')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM2'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM2')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM3'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM3')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM4'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM4')[['VAERS_ID']].count(), \
                data[(data['SYMPTOM5'].isin(symptoms)) & (data['VAX_MANU'] == vax)].groupby(by='SYMPTOM5')[['VAERS_ID']].count()], axis = 1).sum(axis = 1) \
                .divide(pd.Series(data=[divisor]*5, index=symptoms), fill_value=0)

        for i in range(len(symptoms)):
            group2[symptoms[i]].append(df[symptoms[i]])

    # Create Input controls
    state = Select(title="State", value="All", options=["All", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", \
                                                        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", \
                                                        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", \
                                                        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", \
                                                        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"])
    sex = Select(title="Sex", value="All", options=["All", "Male", "Female"])
    age = RangeSlider(title="Age", start=12, end=100, value=(12, 100), step=8)
    allergy2 = TextInput(title="Allergy contains")
    history2 = TextInput(title="Medical history contains")

    # Create Column Data Source that will be used by the plot
    source2 = ColumnDataSource(data=group2)

    # Select new data
    def select_data2():
        state_val = state.value
        sex_val = sex.value
        age_val = age.value
        allergy_val = allergy2.value
        history_val = history2.value

        selected = data[(data['AGE_YRS'] >= age_val[0]) & (data['AGE_YRS'] <= age_val[1])]

        if (state_val != "All"):
            selected = selected[selected['STATE'] == state_val]

        if (sex_val != "All"):
            selected = selected[selected['SEX'] == sex_val[0]]

        if (allergy_val != ""):
            selected = selected[selected['ALLERGIES'].str.contains(allergy_val.lower()) == True]

        if (history_val != ""):
            selected = selected[selected['HISTORY'].str.contains(history_val.lower()) == True]

        return selected

    # Update data
    def update2():
        df = select_data2()

        new_group = {'Vaccine Manufacturer': vaccines, symptoms[0]: [], symptoms[1]: [], symptoms[2]: [], symptoms[3]: [], symptoms[4]: []}

        for vax in vaccines:
            vax = vax.upper()

            divisor = df[df['VAX_MANU'] == vax].count()['VAERS_ID']

            new_data = pd.concat([df[(df['SYMPTOM1'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM1')[['VAERS_ID']].count(), \
                    df[(df['SYMPTOM2'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM2')[['VAERS_ID']].count(), \
                    df[(df['SYMPTOM3'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM3')[['VAERS_ID']].count(), \
                    df[(df['SYMPTOM4'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM4')[['VAERS_ID']].count(), \
                    df[(df['SYMPTOM5'].isin(symptoms)) & (df['VAX_MANU'] == vax)].groupby(by='SYMPTOM5')[['VAERS_ID']].count()], axis = 1).sum(axis = 1) \
                    .divide(pd.Series(data=[divisor]*5, index=symptoms), fill_value=0)

            for i in range(len(symptoms)):
                new_group[symptoms[i]].append(new_data[symptoms[i]])

        source2.data = new_group

    # Set up controls/widgets
    controls2 = [state, sex, age, allergy2, history2]

    for control in controls2:
        control.on_change('value', lambda attr, old, new: update2())

    # Set up figure
    p2 = figure(x_range=vaccines, width=500, height=400, title="Symptom prevalence", \
                toolbar_location=None, tools="")

    vbar1 = p2.vbar(x=dodge('Vaccine Manufacturer', -0.28, range=p2.x_range), top=symptoms[0], source=source2, width=0.1, color='#a6cee3')
    vbar2 = p2.vbar(x=dodge('Vaccine Manufacturer', -0.14, range=p2.x_range), top=symptoms[1], source=source2, width=0.1, color='#1f78b4')
    vbar3 =  p2.vbar(x=dodge('Vaccine Manufacturer', 0.0, range=p2.x_range), top=symptoms[2], source=source2, width=0.1, color='#b2df8a')
    vbar4 = p2.vbar(x=dodge('Vaccine Manufacturer', 0.14, range=p2.x_range), top=symptoms[3], source=source2, width=0.1, color='#33a02c')
    vbar5 = p2.vbar(x=dodge('Vaccine Manufacturer', 0.28, range=p2.x_range), top=symptoms[4], source=source2, width=0.1, color='#fb9a99')
        
    p2.x_range.range_padding = 0.1
    p2.xgrid.grid_line_color = None
    p2.y_range.start = 0

    legend = Legend(items=[(symptoms[0], [vbar1]), (symptoms[1], [vbar2]), (symptoms[2], [vbar3]), (symptoms[3], [vbar4]), (symptoms[4], [vbar5])])
    p2.add_layout(legend, "right")
    # p2.legend.location = "top_right"
    # p2.legend.orientation = "horizontal"



    #########################################################################################
    # GRAPH 3
    #########################################################################################

    symp1 = data.groupby('SYMPTOM1')[['VAERS_ID']].count()
    symp1.sort_values(['VAERS_ID'], ascending=False, inplace=True)

    symp2 = data.groupby('SYMPTOM2')[['VAERS_ID']].count()
    symp2.sort_values(['VAERS_ID'], ascending=False, inplace=True)

    symp3 = data.groupby('SYMPTOM3')[['VAERS_ID']].count()
    symp3.sort_values(['VAERS_ID'], ascending=False, inplace=True)

    symp4 = data.groupby('SYMPTOM4')[['VAERS_ID']].count()
    symp4.sort_values(['VAERS_ID'], ascending=False, inplace=True)

    symp5 = data.groupby('SYMPTOM5')[['VAERS_ID']].count()
    symp5.sort_values(['VAERS_ID'], ascending=False, inplace=True)

    total = pd.concat([symp1,symp2,symp3,symp4,symp5], axis = 1).sum(axis = 1)
    total.sort_values(ascending=False, inplace=True)

    top_ten_symptoms = list(total.index)
    top_ten_symptoms = top_ten_symptoms[0:10]

    ranked_symptoms = {top_ten_symptoms[i]: i+1 for i in range(len(top_ten_symptoms))}

    us_states = data.groupby('STATE')[['VAERS_ID']].count()
    us_states_list = list(us_states.index)
    us_states_list.remove('Ca')

    state_data = {}
    for s in us_states_list:
        df_temp = data.loc[data['STATE'] == s]
        total_obs = len(df_temp)

        symp1 = df_temp.groupby('SYMPTOM1')[['VAERS_ID']].count()
        symp2 = df_temp.groupby('SYMPTOM2')[['VAERS_ID']].count()
        symp3 = df_temp.groupby('SYMPTOM3')[['VAERS_ID']].count()
        symp4 = df_temp.groupby('SYMPTOM4')[['VAERS_ID']].count()
        symp5 = df_temp.groupby('SYMPTOM5')[['VAERS_ID']].count()

        total_s = pd.concat([symp1,symp2,symp3,symp4,symp5], axis = 1).sum(axis = 1)
        total_s.sort_values(ascending=False, inplace=True)
        total_s = (total_s / total_obs)
        total_symptom = list(total_s.index)
        
        d1 = {f'symptom{i+1}': f'{total_symptom[i]} {total_s[i]:.2%}' for i in range(5)}
        d2 = {f's{i+1}': total_s[top_ten_symptoms[i]] if top_ten_symptoms[i] in total_s.index else np.nan for i in range(10)}
        d1.update(d2)
        state_data[s] = d1

    try:
        del states["HI"]
        del states["AK"]
    except:
        pass

    state_x = [s["lons"] for s in states.values()]
    state_y = [s["lats"] for s in states.values()]
    names = [a['name'] for a in states.values()]

    symptom1 = [state_data[s]['symptom1'] for s in states]
    symptom2 = [state_data[s]['symptom2'] for s in states]
    symptom3 = [state_data[s]['symptom3'] for s in states]
    symptom4 = [state_data[s]['symptom4'] for s in states]
    symptom5 = [state_data[s]['symptom5'] for s in states]

    target = [state_data[s]['s1'] for s in states]


    colors = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']

    color = LinearColorMapper(palette = colors, low = min(target), high = max(target))
    select_box = Select(title='Symptom:', value=str(top_ten_symptoms[0]), options=top_ten_symptoms)
    color_bar = ColorBar(color_mapper = color, location = (0,0), title = select_box.value)

    def update3():
        target = [state_data[s][f's{ranked_symptoms[select_box.value]}'] for s in states]
        color.low = min(target)
        color.high = max(target)
        color_bar.title = select_box.value
        new_data = dict(x=state_x, y=state_y, name=names, spt1=symptom1, spt2=symptom2, spt3=symptom3, spt4=symptom4, spt5=symptom5, ts=target)
        fig.patches('x', 'y', source = new_data, fill_alpha=1, fill_color = {'field': 'ts', 'transform': color},
            line_color="black", line_width=1, line_alpha=1)

    select_box.on_change('value', lambda attr, old, new: update3())

    data3 = dict(x=state_x, y=state_y, name=names, spt1=symptom1, spt2=symptom2, spt3=symptom3, spt4=symptom4, spt5=symptom5, ts=target)

    fig = figure(title="Top COVID-19 Vaccine Reactions by State", toolbar_location="right", x_axis_location=None, y_axis_location=None,
            tooltips = [("Name", "@name"), ("Top 5 Symptoms", ""), ("1", "@spt1"), ("2", "@spt2"), ("3", "@spt3"), ("4", "@spt4"), ("5", "@spt5")], 
            plot_width=800, plot_height=550)

    fig.patches('x', 'y', source = data3, fill_alpha=1, fill_color = {'field': 'ts', 'transform': color},
            line_color="black", line_width=1, line_alpha=1)

    fig.grid.grid_line_color = None

    fig.add_layout(color_bar, 'right')

    p3 = row(select_box, fig)



    # Set up layout
    inputs = column(*controls, width=320)
    inputs2 = column(*controls2, width=320)

    l = column(desc, p3, row(inputs, p), row(inputs2, p2), sizing_mode="scale_both")


    return doc.add_root(l)


def bokeh_cdn_resources():
    """Create script to load Bokeh resources from CDN based on
       installed bokeh version.

    Returns:
        script -- script to load resources from CDN
    """
    included_resources = [
        f"bokeh-{bokeh_release_ver}.min.js",
        f"bokeh-api-{bokeh_release_ver}.min.js",
        f"bokeh-tables-{bokeh_release_ver}.min.js",
        f"bokeh-widgets-{bokeh_release_ver}.min.js",
    ]

    resources = "\n    "
    for key, value in get_sri_hashes_for_version(bokeh_release_ver).items():
        if key in included_resources:
            resources += '<script type="text/javascript" '
            resources += f'src="{BOKEH_CDN}/{key}" '
            resources += f'integrity="sha384-{value}" '
            resources += 'crossorigin="anonymous"></script>\n    '

    resources += BOKEH_BROWSER_LOGGING
    return resources


def get_sockets():
    """bind to available socket in this system

    Returns:
        sockets, port -- sockets and port bind to
    """
    _sockets, _port = bind_sockets("0.0.0.0", 0)
    set_bokeh_port(_port)
    return _sockets, _port


def bk_worker(sockets, port):
    """Worker thread to  run Bokeh Server"""
    _bkapp = Application(FunctionHandler(bkapp))
    asyncio.set_event_loop(asyncio.new_event_loop())

    websocket_origins = [f"{BOKEH_ADDR}:{port}", f"{FLASK_ADDR}:{FLASK_PORT}"]
    bokeh_tornado = BokehTornado(
        {BOKEH_PATH: _bkapp},
        extra_websocket_origins=websocket_origins,
        **{"use_xheaders": True},
    )

    bokeh_http = HTTPServer(bokeh_tornado, xheaders=True)
    bokeh_http.add_sockets(sockets)
    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()


if __name__ == "__main__":
    bk_sockets, bk_port = get_sockets()
    t = Thread(target=bk_worker, args=[bk_sockets, bk_port], daemon=True)
    t.start()
    bokeh_url = BOKEH_URL.replace("$PORT", str(bk_port))
    log.info("Bokeh Server App Running at: %s", bokeh_url)
    while True:
        time.sleep(0.05)
