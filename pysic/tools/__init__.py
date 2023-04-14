def version2int(version):
    version = str(version)
    if version == '1.2M':
        version = '1.2.22'
    version_int = [int(v) for v in version.split('.')]
    if len(version_int) < 3:
        version_int.append(0)
    return version_int


def inverse_dict(_dict):
    """
    return the inverse of a dictionnary with non-unique values
    :param _dict: dictionnary
    :return inv_map: dictionnary
    """
    revdict = {}
    for k, v in _dict.items():
        if isinstance(v, list):
            for _v in v:
                revdict.setdefault(_v, k)
        elif isinstance(v, dict):
            for _v in v:
                revdict[_v] = k
        else:
            revdict.setdefault(v, k)
    return revdict


def parse_datetimetz(c_date_v, c_hour_v, c_tz_v):
    """
    :param c_date_v:
        string, value of date cell
    :param c_hour_v:
        string, value of hour cell
    :param c_tz_v:
        string, value of timezone cell
    :return:
        datetime.date or datetime.datetime (aware or naive) as function of the input
    """
    import logging
    import pandas as pd
    import datetime as dt
    import dateutil
    import pytz

    logger = logging.getLogger(__name__)

    if isinstance(pd.to_datetime(c_date_v, format='%Y-%m-%d').date(), dt.date):
        _d = pd.to_datetime(c_date_v)
        _d = _d.date()

        # time
        if pd.to_datetime(c_hour_v, format='%H:%M:%S') is None:
            logger.info("\ttime and timezone unavailable")
            return _d
        elif isinstance(pd.to_datetime(c_hour_v, format='%H:%M:%S').time(), dt.time):
            _t = pd.to_datetime(c_hour_v, format='%H:%M:%S').time()
            _dt = dt.datetime.combine(_d, _t)
        else:
            logger.info("\ttime and timezone unavailable")
            return _d

        # timezone
        if c_tz_v is not None:
            # format 'Country/City'
            if c_tz_v in pytz.all_timezones:
                _tz = c_tz_v
                _dt.replace(tzinfo=dateutil.tz.gettz(_tz))
            elif c_tz_v.split(' ')[0] in pytz.all_timezones:
                _tz = pytz.all_timezones
                _dt.replace(tzinfo=dateutil.tz.gettz(_tz))
            elif c_tz_v.startswith('UTC'):
                _tz = c_tz_v.split(' ')[0]
                _utc_offset = _tz.split('UTC')[-1]
                # convert +HHMM or +HH:MM to timeoffset
                if ':' in _utc_offset:
                    _tz_h = int(_utc_offset.split(':')[0])
                    _tz_m = int(_utc_offset.split(':')[1])
                elif len(_utc_offset[1:]) == 4:
                    _tz_h = int(_utc_offset[0:3])
                    _tz_m = int(_utc_offset[3:])
                elif len(_utc_offset[1:]) == 3:
                    _tz_h = int(_utc_offset[0:2])
                    _tz_m = int(_utc_offset[2:])
                else:
                    _tz_h = int(_utc_offset[0:2])
                    _tz_m = 0
                _utc_offset = dt.timedelta(hours=_tz_h, minutes=_tz_m)
                _tz = dt.timezone(_utc_offset, name=_tz)

                # offset is in seconds
                _dt = _dt.replace(tzinfo=_tz)
            else:
                _tz = None
                # TODO: guess timezone base of date and location
                logger.info("\t Timezone unavailable.")
        else:
            _tz = None
            # TODO: guess timezone base of date and location
            logger.info("\tTimezone unavailable.")
    else:
        logger.warning("\tDate unavailable")
        _dt = None
    return _dt


def parse_coordinate(v_cell_deg, v_cell_min, v_cell_sec):
    """
    :param v_cell_deg:
        float or int, value of degree cell
    :param v_cell_min:
        float or int, value of minute cell
    :param v_cell_sec:
        float or int, value of second cell
    :return:
        float, coordinate in degree
    """
    import numpy as np

    if isfloat(v_cell_deg):
        degree = float(v_cell_deg)
        if isfloat(v_cell_min):
            minute = float(v_cell_min)
            if isfloat(v_cell_sec):
                second = float(v_cell_sec)
            else:
                second = 0
        else:
            minute = 0
            second = 0
        coordinate = degree + minute / 60 + second / 3600
    else:
        coordinate = np.nan
    return coordinate


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

