from bokeh.models import BoxAnnotation, FixedTicker
from bokeh.layouts import gridplot
from formatters import (
    time_hover_formatter,
    daytime_axis_formatter,
    day_hover_formatter,
    day_axis_formatter,
    daylight_duration_axis_formatter,
)
from bokeh.models import (
    HoverTool,
    PanTool,
    BoxZoomTool,
    WheelZoomTool,
    ResetTool,
    ColumnDataSource,
    CrosshairTool,
    Span,
)
from bokeh.io import curdoc
from astral.geocoder import database, lookup
from astral.sun import daylight
from bokeh.plotting import figure, show
import pendulum


curdoc().theme = 'caliber'


def calc_daylight_info(sunrise_time_utc, sunset_time_utc, timezone: str):
    sunrise_time = pendulum.instance(sunrise_time_utc).in_timezone(timezone)
    sunset_time = pendulum.instance(sunset_time_utc).in_timezone(timezone)

    daylight_duration = sunset_time.diff(sunrise_time)

    return {
        'sunrise_time_sec': sunrise_time.diff(
            sunrise_time.start_of('day')
        ).in_seconds(),
        'sunset_time_sec': sunset_time.diff(sunset_time.start_of('day')).in_seconds(),
        'daylight_duration_sec': daylight_duration.in_seconds(),
    }


def build_source(city: str, year: int | None = None):
    if year is None:
        year = pendulum.today().year

    location_info = lookup(city, database())
    tz_str = location_info.timezone

    t_start = pendulum.datetime(year, 1, 1)
    t_end = t_start.add(years=1)

    times = [t for t in pendulum.interval(t_start, t_end).range('days')]
    info_array = [
        calc_daylight_info(*daylight(location_info.observer, t.naive()), tz_str)
        for t in times
    ]

    return ColumnDataSource(
        data={
            'day': times,
            'daylight_duration_sec': [r['daylight_duration_sec'] for r in info_array],
            'sunrise_time_sec': [r['sunrise_time_sec'] for r in info_array],
            'sunset_time_sec': [r['sunset_time_sec'] for r in info_array],
        }
    )


source = build_source(city='Moscow')

width1 = Span(dimension='width', line_dash='dashed', line_width=1)
width2 = Span(dimension='width', line_dash='dashed', line_width=1)
height = Span(dimension='height', line_dash='dotted', line_width=1)


# ----------- Daylight duration -----------

daylight_duration_plot = figure(
    title='Daylight duration',
    x_axis_type='datetime',
    y_axis_label='duration',
    y_range=(6 * 60 * 60, 18 * 60 * 60),
    tools=[
        BoxZoomTool(),
        ResetTool(),
        PanTool(),
        WheelZoomTool(dimensions='width'),
    ],
)
daylight_duration_plot.xaxis[0].formatter = day_axis_formatter
daylight_duration_plot.yaxis[0].formatter = daylight_duration_axis_formatter
daylight_duration_plot.yaxis[0].ticker = FixedTicker(
    ticks=[h * 60 * 60 for h in range(0, 25, 2)]
)

daylight_duration_plot.add_tools(CrosshairTool(overlay=[width1, height]))

daylight_duration_hover = HoverTool(
    tooltips=[
        ('day', '@day{custom}'),
        ('daylight duration', '@daylight_duration_sec{include_sec}'),
    ],
    formatters={
        '@day': day_hover_formatter,
        '@daylight_duration_sec': time_hover_formatter,
    },
    mode='vline',
)
daylight_duration_plot.add_tools(daylight_duration_hover)

daylight_duration_plot.line(
    x='day',
    y='daylight_duration_sec',
    source=source,
    legend_label='duration',
    color='navy',
    line_width=1,
    name='daylight_duration_sec',
)
daylight_duration_plot.scatter(
    x='day',
    y='daylight_duration_sec',
    source=source,
    marker='circle',
    size=2,
    line_color='navy',
    fill_color='white',
)

# ----------- Sunrise/sunset -----------

sunrise_sunset_plot = figure(
    title='Sunrise & sunset time',
    x_axis_type='datetime',
    y_axis_label='time',
    y_range=(0, 24 * 60 * 60),
    tools=[
        BoxZoomTool(),
        ResetTool(),
        PanTool(),
        WheelZoomTool(dimensions='width'),
    ],
    x_range=daylight_duration_plot.x_range,
)
sunrise_sunset_plot.xaxis[0].formatter = day_axis_formatter
sunrise_sunset_plot.yaxis[0].formatter = daytime_axis_formatter
sunrise_sunset_plot.yaxis[0].ticker = FixedTicker(
    ticks=[h * 60 * 60 for h in range(0, 25, 4)]
)

sunrise_sunset_plot.line(
    x='day',
    y='sunrise_time_sec',
    source=source,
    legend_label='sunrise',
    color='red',
    line_width=1,
    name='sunrise_time_sec',
)
sunrise_sunset_plot.scatter(
    x='day',
    y='sunrise_time_sec',
    source=source,
    marker='circle',
    size=2,
    line_color='red',
    fill_color='white',
    name='sunrise_time_sec',
)

sunrise_sunset_plot.line(
    x='day',
    y='sunset_time_sec',
    source=source,
    legend_label='sunset',
    color='green',
    line_width=1,
    name='sunset_time_sec',
)
sunrise_sunset_plot.scatter(
    x='day',
    y='sunset_time_sec',
    source=source,
    marker='circle',
    size=2,
    line_color='green',
    fill_color='white',
    name='sunset_time_sec',
)

sunrise_sunset_plot.add_tools(CrosshairTool(overlay=[width2, height]))

sunrise_sunset_hover = HoverTool(
    tooltips=[
        ('name', '$name'),
        ('day', '@day{custom}'),
        ('time', '@$name{custom}'),
    ],
    formatters={
        '@day': day_hover_formatter,
        '@{sunrise_time_sec}': time_hover_formatter,
        '@{sunset_time_sec}': time_hover_formatter,
    },
    mode='vline',
)
sunrise_sunset_plot.add_tools(sunrise_sunset_hover)

before_midday_box = BoxAnnotation(
    top=12 * 60 * 60, fill_alpha=0.2, fill_color='#F0E442'
)
after_midday_box = BoxAnnotation(
    bottom=12 * 60 * 60, fill_alpha=0.2, fill_color='#009E73'
)
sunrise_sunset_plot.add_layout(before_midday_box)
sunrise_sunset_plot.add_layout(after_midday_box)

grid = gridplot(
    [daylight_duration_plot, sunrise_sunset_plot],
    ncols=1,
    sizing_mode='stretch_width',
    # width=250,
    height=350,
    merge_tools=True,
)
source = build_source(city='Moscow')
show(grid)
