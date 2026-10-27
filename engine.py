"""Sri Jyoti Astro private calculation engine. Requires pyswisseph."""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import math
import swisseph as swe

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAK = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
BODIES = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN,'Uranus':swe.URANUS,'Neptune':swe.NEPTUNE,'Pluto':swe.PLUTO}
AYANAMSAS = {'lahiri':swe.SIDM_LAHIRI,'raman':swe.SIDM_RAMAN,'krishnamurti':swe.SIDM_KRISHNAMURTI}

def details(longitude):
    lon = longitude % 360
    sign = int(lon // 30)
    within = lon % 30
    nak_index = min(26, int(lon // (360/27)))
    pada = min(4, int(((lon % (360/27)) + 1e-11) / (360/108))+1)
    nav_index = (sign * 9 + min(8,int((within + 1e-11) / (30/9)))) % 12
    return {'longitude':round(lon,8),'sign':SIGNS[sign],'sign_index':sign,
            'degrees_in_sign':round(within,8),'nakshatra':NAK[nak_index],
            'pada':pada,'navamsa_sign':SIGNS[nav_index], 'navamsa_index':nav_index}

def vimshottari_birth_balance(moon_longitude):
    """Moon-nakshatra based birth-dasha balance; 360-day savana year convention."""
    lords = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
    years = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
    nak_len = 360 / 27
    nak_i = int((moon_longitude % 360) / nak_len)
    lord = lords[nak_i % 9]
    remaining = ((nak_i + 1) * nak_len - (moon_longitude % 360)) / nak_len * years[lord]
    total_days = round(remaining * 360)
    yy, remainder = divmod(total_days, 360)
    mm, dd = divmod(remainder, 30)
    return {'lord':lord,'years':yy,'months':mm,'days':dd, 'year_length_days':360,'remaining_years':round(remaining,8)}

# Vimshottari periods: lengths are proportional to the standard 120-year cycle.
DASHA_ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}

def vimshottari_periods(moon_longitude, birth_local, year_days=365.25):
    """Construct nested Mahadasha/Bhukti/Antara intervals from Moon longitude.

    Boundary convention: continuous year_days-day years, date-only display in
    the local birthplace civil timezone. Different panchangas use different
    savana/solar year lengths and rounding rules; these dates are not claimed
    to be identical to another vendor's proprietary algorithm.
    """
    if not 350 <= year_days <= 366:
        raise ValueError('Unsupported Vimshottari year length.')
    moon = moon_longitude % 360
    nak_i = int(moon / (360/27))
    initial_lord = DASHA_ORDER[nak_i%9]
    portion_elapsed = (moon/(360/27))-nak_i
    # Cross-platform UTC epoch arithmetic: Windows fromtimestamp() can fail for pre-1970 Dasha dates.
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    birth_jd = (birth_local.astimezone(timezone.utc) - epoch).total_seconds()/86400.0 + 2440587.5
    elapsed_days = portion_elapsed * DASHA_YEARS[initial_lord] * year_days
    initial_begin = birth_jd - elapsed_days
    def date_of(jd):
        # Local civil date; periods are calculated as instants, not rounded daily.
        instant_utc = epoch + timedelta(days=jd-2440587.5)
        return instant_utc.astimezone(birth_local.tzinfo).date().isoformat()
    def split(start,end,lord,level):
        idx=DASHA_ORDER.index(lord)
        duration=end-start
        cursor=start
        out=[]
        for n in range(9):
            sublord=DASHA_ORDER[(idx+n)%9]
            finish=end if n==8 else start+duration*sum(DASHA_YEARS[DASHA_ORDER[(idx+j)%9]] for j in range(n+1))/120
            rec={'lord':sublord,'start':date_of(cursor),'end':date_of(finish),'start_jd':round(cursor,8),'end_jd':round(finish,8)}
            if level<3:
                rec['children']=split(cursor,finish,sublord,level+1)
            out.append(rec)
            cursor=finish
        return out
    periods=[]
    idx=DASHA_ORDER.index(initial_lord)
    cursor=initial_begin
    # 2 cycles handle birth dates at the outer boundary of a cycle.
    for n in range(18):
        lord=DASHA_ORDER[(idx+n)%9]
        end=cursor+DASHA_YEARS[lord]*year_days
        if end>=birth_jd-1 and cursor<=birth_jd+120*year_days:
            periods.append({'lord':lord,'start':date_of(cursor),'end':date_of(end),
                            'start_jd':round(cursor,8),'end_jd':round(end,8),
                            'children':split(cursor,end,lord,2)})
        cursor=end
    return {'year_length_days':year_days,'year_convention':'Continuous solar year (365.25 days); civil-date display. Some astrology software uses other year conventions.',
            'birth_lord':initial_lord,'periods':periods}

def calculate(data):
    date = str(data['date'])
    time = str(data['time'])
    lat = float(data['latitude']); lon = float(data['longitude'])
    if not (-66 <= lat <= 66):
        raise ValueError('Phase 1 supports latitudes from -66° to +66° for the selected house calculation.')
    if not (-180 <= lon <= 180): raise ValueError('Longitude must be between -180 and 180.')
    tzname = str(data['timezone'])
    zone = ZoneInfo(tzname)
    local = datetime.fromisoformat(date+'T'+time)
    if not (1800 <= local.year <= 2100): raise ValueError('Phase 1 supports years 1800 to 2100.')
    aware = local.replace(tzinfo=zone)
    # Reject nonexistent spring-forward wall times and ambiguous autumn times.
    back = aware.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)
    if back != local: raise ValueError('This local time does not exist in the selected timezone.')
    if aware.replace(fold=0).utcoffset() != aware.replace(fold=1).utcoffset():
        raise ValueError('Ambiguous DST time: use an unambiguous local time or consult the historic timezone offset.')
    utc = aware.astimezone(timezone.utc)
    hour = utc.hour + utc.minute/60 + (utc.second+utc.microsecond/1e6)/3600
    jd = swe.julday(utc.year,utc.month,utc.day,hour,swe.GREG_CAL)
    ay = str(data.get('ayanamsa','lahiri')).lower()
    if ay not in AYANAMSAS: raise ValueError('Unsupported ayanamsha.')
    swe.set_sid_mode(AYANAMSAS[ay])
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    planets = {}
    modes = set()
    for name,pid in BODIES.items():
        xx, used = swe.calc_ut(jd,pid,flags)
        modes.add('Swiss files' if used & swe.FLG_SWIEPH else ('Moshier fallback' if used & swe.FLG_MOSEPH else 'Other'))
        planets[name] = {**details(xx[0]),'retrograde':xx[3]<0, 'speed_longitude':round(xx[3],8)}
    nodeid = swe.TRUE_NODE if str(data.get('node','mean')).lower() == 'true' else swe.MEAN_NODE
    xx,used=swe.calc_ut(jd,nodeid,flags)
    modes.add('Swiss files' if used & swe.FLG_SWIEPH else ('Moshier fallback' if used & swe.FLG_MOSEPH else 'Other'))
    planets['Rahu']={**details(xx[0]),'retrograde':xx[3]<0, 'speed_longitude':round(xx[3],8)}
    planets['Ketu']={**details((xx[0]+180)%360),'retrograde':xx[3]<0,'speed_longitude':round(xx[3],8)}
    _, ascmc=swe.houses_ex(jd,lat,lon,b'P',swe.FLG_SIDEREAL)
    asc=details(ascmc[0])
    asc['retrograde']=False
    return {'name':str(data.get('name','')).strip(),'date':date,'time':time,'place':str(data.get('place','')).strip(),
            'latitude':lat,'longitude':lon,'timezone':tzname,'utc':utc.isoformat(),
            'julian_day_ut':round(jd,8),'ayanamsa':ay,
            'ayanamsa_degrees':round(swe.get_ayanamsa_ut(jd),8),
            'node':str(data.get('node','mean')).lower(),'ascendant':asc,'planets':planets,
            'birth_dasha_balance':vimshottari_birth_balance(planets['Moon']['longitude']),
            'vimshottari':vimshottari_periods(planets['Moon']['longitude'],aware),
            'ephemeris_mode':', '.join(sorted(modes)),'calculation_note':'Sidereal ecliptic longitudes; geocentric planetary positions, topocentric ascendant; D9 from sidereal longitudes; Placidus function used solely to obtain ascendant angle.'}
