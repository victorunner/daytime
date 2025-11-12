from bokeh.models import (
    CustomJSHover,
    CustomJSTickFormatter,
    DatetimeTickFormatter,
    NumeralTickFormatter,
)

day_axis_formatter = DatetimeTickFormatter(
    days='%d',
    # months='%b=%m',
    months='%b',
    years='%Y',
    context=DatetimeTickFormatter(days='%b', months='%Y'),
    context_which='all',
)

daylight_duration_axis_formatter = NumeralTickFormatter(format='00:00:00')

daytime_axis_formatter = CustomJSTickFormatter(
    code="""
        if (tick==12*60*60) {return 'midday'}
        if (tick==24*60*60) {return '24:00'}
        return new Date(tick*1000).toISOString().slice(11, 16)
    """
)

day_hover_formatter = CustomJSHover(
    code="""
        const { snap_x, name} = special_vars
        return new Date(snap_x).toUTCString().slice(5, 11)
    """
)

time_hover_formatter = CustomJSHover(
    code="""
        const { snap_y } = special_vars
        const end = format === 'include_sec' ? 19 : 16
        return new Date(snap_y*1000).toISOString().slice(11, end)
    """
)
