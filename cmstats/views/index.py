from cmstats.database.schema.devices import Device
from cmstats.resources import Root
from cmstats.utils.template import number
from pyramid.view import view_config


@view_config(context=Root, renderer='index.mako')
def index(request):
    kwargs = {
            'device_count': Device.device_count(),
            'version_count': Device.version_count(),
            'total_nonkang': Device.count_nonkang(),
            'total_kang': Device.count_kang(),
            'total_last_day': Device.count_last_day(),
    }

    return kwargs

@view_config(context=Root, name='live', renderer='json', xhr=True)
def live_xhr(request):
    total = number(Device.count())
    return {'count': total}

@view_config(context=Root, name='live', renderer='live.mako')
def live(request):
    return {}
