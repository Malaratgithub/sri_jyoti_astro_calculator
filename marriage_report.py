"""Branded marriage report using calculated D1 data and user-provided assessment.
Updated to exclude Dasha–Bhukti analysis and marriage-matching-considerations section.
Long PNG exports are returned as a ZIP of A4-sized PNG pages when needed.
"""
from io import BytesIO
from pathlib import Path
from datetime import date
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw
from report_render import font, chart, PURPLE, GOLD, CREAM, INK
ROOT=Path(__file__).parent
W=1122
PAGEH=1585
DARK='#8d1222'; NAVY='#15265b'; GOLD2='#c9902f'; PAPER='#fffdf7'

def center(draw,y,s,f,color=DARK):
    bbox=draw.textbbox((0,0),s,font=f)
    draw.text(((W-(bbox[2]-bbox[0]))/2,y),s,font=f,fill=color)

def label(draw,x,y,s,size=17,color=INK,bold=False):
    draw.text((x,y),str(s),font=font(size,bold),fill=color)

def wrap(d,text,f,maxw):
    lines=[]
    for p in str(text).splitlines():
        line=''
        words=p.split() or ['']
        for word in words:
            trial=(line+' '+word).strip()
            if d.textbbox((0,0),trial,font=f)[2]<=maxw:
                line=trial
            else:
                if line:
                    lines.append(line)
                line=word
        lines.append(line)
    return lines or ['']

def page(heading='Horoscope Compatibility Report'):
    image=Image.new('RGB',(W,PAGEH),PAPER)
    d=ImageDraw.Draw(image)
    d.rounded_rectangle((13,13,W-13,PAGEH-13),radius=21,outline=GOLD2,width=3)
    header=Image.open(ROOT/'assets/compatibility_header_reference.png').convert('RGB')
    image.paste(header.resize((W,144)),(0,0))
    d.rectangle((200,51,925,139),fill=PAPER)
    center(d,58,heading,font(39,True))
    d.line((270,118,850,118),fill=GOLD2,width=2)
    return image,ImageDraw.Draw(image)

def box(d,coords,fill='#fff9ec'):
    d.rounded_rectangle(coords,radius=13,fill=fill,outline=GOLD2,width=2)

def shortdate(s):
    try:return date.fromisoformat(s).strftime('%d %B %Y')
    except:return str(s)

def profile(d,x,y,label0,item):
    box(d,(x,y,x+498,y+123),'#f4f8fa' if label0=='Groom' else '#fff3f1')
    name=item['name']; c=item['calculation']
    d.text((x+20,y+9),label0+' Horoscope',font=font(19,True),fill=NAVY)
    d.text((x+20,y+37),name[:36],font=font(23,True),fill=DARK)
    d.text((x+20,y+70),shortdate(c['date'])+'  •  '+c['time'],font=font(15),fill=INK)
    d.text((x+20,y+93),c.get('place','')[:51],font=font(14),fill=INK)

def make(data):
    bride=data['bride'];groom=data['groom'];checks=data['checks']
    if len(checks)!=10:raise ValueError('Exactly ten Nakshatra checks are required')
    comments=str(data.get('comments','')).strip()[:15000]
    yes=sum(c['status']=='Matches' for c in checks)
    review=sum(c['status']=='Review' for c in checks)
    failed=sum(c['status']=='Does not match' for c in checks)
    score=f'{yes}/10' if review==0 else f'{yes}/{10-review} assessed (of 10)'

    im,d=page()
    logo=Image.open(ROOT/'assets/sri_jyoti_logo_crop.png').convert('RGB').resize((93,93))
    im.paste(logo,(46,152))
    label(d,156,160,'Sri Jyoti Astro Services',26,DARK,True)
    label(d,157,195,'Call for appointment: 6380274409   •   www.srijyotiastro.com',15,NAVY)
    profile(d,44,264,'Groom',groom)
    profile(d,580,264,'Bride',bride)
    center(d,391,'D1 Rasi Charts',font(23,True))
    box(d,(37,423,553,817))
    box(d,(571,423,1085,817))
    label(d,167,431,"Groom's Kundli",21,DARK,True)
    label(d,701,431,"Bride's Kundli",21,DARK,True)
    chart(d,groom['calculation'],x=100,y=471,size=350)
    chart(d,bride['calculation'],x=634,y=471,size=350)

    box(d,(41,837,1081,1191))
    center(d,846,'Nakshatra Porutham — 10 Checks',font(23,True))
    X=[56,338,557,1070]
    for a,b in zip(X[:-1],X[1:]):
        d.rectangle((a,887,b,916),fill='#f5e0ae',outline='#be904d',width=1)
    label(d,67,892,'Porutham',16,NAVY,True)
    label(d,350,892,'Result',16,NAVY,True)
    label(d,568,892,'Assessment / reference',16,NAVY,True)
    for i,c in enumerate(checks):
        y=916+i*25
        d.rectangle((56,y,1070,y+25),outline='#d7b980',width=1)
        label(d,66,y+3,c['label'],14,INK,True)
        label(d,346,y+3,c['status'],13,'#1e784c' if c['status']=='Matches' else DARK if c['status']=='Does not match' else '#896719')
        desc=c.get('detail','')
        while d.textbbox((0,0),desc,font=font(12))[2]>491 and len(desc)>4:
            desc=desc[:-2]+'…'
        label(d,568,y+3,desc,12)

    center(d,1214,'Nakshatra Matching Score: '+score,font(25,True))
    label(d,50,1265,f'{yes} match  |  {failed} do not match  |  {review} require astrologer review',16,NAVY)
    box(d,(39,1304,1084,1510))
    label(d,55,1316,'Astrological Compatibility Assessment',20,DARK,True)
    all_lines=wrap(d,comments if comments else 'Not entered. Astrologer review is required.',font(15),995)
    first_page_capacity=8
    for i,line in enumerate(all_lines[:first_page_capacity]):
        label(d,59,1352+i*19,line,15)
    label(d,50,1533,'Sri Jyoti Astro Services  •  6380274409  •  www.srijyotiastro.com',14,NAVY)
    pages=[im]

    rest=all_lines[first_page_capacity:]
    while rest:
        pi,dd=page('Astrological Compatibility Assessment Continued')
        box(dd,(39,170,1084,1460))
        label(dd,55,185,'Astrological Compatibility Assessment',20,DARK,True)
        page_lines=rest[:47]
        for i,line in enumerate(page_lines):
            label(dd,58,225+i*25,line,17)
        rest=rest[47:]
        label(dd,50,1486,'Sri Jyoti Astro Services  •  6380274409  •  www.srijyotiastro.com',15,NAVY)
        pages.append(pi)
    return pages

def export_marriage(data,fmt):
    pages=make(data)
    if fmt=='pdf':
        stream=BytesIO()
        pages[0].save(stream,format='PDF',resolution=140,save_all=True,append_images=pages[1:])
        return stream.getvalue(),'application/pdf','pdf'
    if fmt!='png':
        raise ValueError('Unsupported export format')
    if len(pages)==1:
        stream=BytesIO()
        pages[0].save(stream,format='PNG')
        return stream.getvalue(),'image/png','png'
    zip_stream=BytesIO()
    with ZipFile(zip_stream,'w',ZIP_DEFLATED) as zf:
        for i,p in enumerate(pages,1):
            img=BytesIO()
            p.save(img,format='PNG')
            zf.writestr(f'Sri_Jyoti_Marriage_Matching_Page_{i}.png',img.getvalue())
    return zip_stream.getvalue(),'application/zip','zip'
