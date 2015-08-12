import humanize
__author__ = 'tcezard'


def default_formatter(data, **kwargs):
    return str(data)

def format_percent(data, style='wiki', **kwargs):
    if type(data) is str:
        return data
    if style=='wiki':
        return '%.2f%%'%(float(data)*100)
    elif style=='json':
        return float(data)*100
    else:
        return default_formatter(data)

def format_float(data, style='wiki', **kwargs):
    if type(data) is str:
        return data
    if style=='wiki':
        return '%.2f'%data
    elif style=='json':
        return float(data)
    else:
        return default_formatter(data)

def format_longint(data, style='wiki', **kwargs):
    if style=='wiki':
        return humanize.intcomma(data)
    elif style=='json':
        return int(data)
    else:
        return default_formatter(data)

def link_plot(data, style='wiki', **kwargs):
    if style == 'wiki':
        return '[plot|%s]'%data
    else:
        return default_formatter(data)

def link_page(data, style='wiki', **kwargs):
    if style=='wiki':
        if type(data) == tuple:
            return '[%s|%s]'%data
        elif type(data) == list:
            return ', '.join([link_page(element,style) for element in data])
        else:
            return default_formatter(data)
    else:
        if type(data) == tuple:
            return data[0]
        elif type(data) == list:
            return ', '.join([link_page(element,style) for element in data])
        else:
            return default_formatter(data)