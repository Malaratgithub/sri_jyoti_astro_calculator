"""Image/PDF prediction report. Uses exact supplied header and footer pixel artwork."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from io import BytesIO
import textwrap
ROOT=Path(__file__).parent
W=1122; PURPLE='#3f0655'; GOLD='#dc990b'; CREAM='#fffdf1'; INK='#21143b'
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
CELLS=[(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(3,2),(3,1),(3,0),(2,0),(1,0),(0,0)]
ABBR={'Ascendant':'As','Sun':'Su','Moon':'Mo','Mars':'Ma','Mercury':'Me','Jupiter':'Ju','Venus':'Ve','Saturn':'Sa','Rahu':'Ra','Ketu':'Ke','Uranus':'Ur','Neptune':'Ne','Pluto':'Pl'}
COLORS={'Sun':'#e63211','Moon':'#7667ec','Mars':'#db2d27','Mercury':'#168136','Jupiter':'#a96f0e','Venus':'#ca26ba','Saturn':'#283bb1','Rahu':'#df19bd','Ketu':'#e55b08','Ascendant':'#b11c1c'}

def font(sz,bold=False):
    """Use genuine Arial on Windows for all generated report text.

    Liberation Sans is a metrically compatible fallback only for Linux preview/tests.
    The supplied master header/footer are fixed raster artwork and are not re-typeset.
    """
    windows = (['C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/Arialbd.ttf']
               if bold else ['C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/Arial.ttf'])
    linux = (['/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
              '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'] if bold
             else ['/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
                   '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'])
    for candidate in windows + linux:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate,sz)
    raise RuntimeError('Arial font is required for reports on Windows; Arial-compatible font not found.')

def center(draw,text,y,f,color=INK):
    b=draw.textbbox((0,0),text,font=f);draw.text(((W-(b[2]-b[0]))/2,y),text,font=f,fill=color)

def title(draw,text,y,x1=38,x2=1084):
    draw.rounded_rectangle((x1,y,x2,y+34),radius=15,fill=PURPLE,outline=GOLD,width=3)
    b=draw.textbbox((0,0),text,font=font(24,True));draw.text(((x1+x2-(b[2]-b[0]))/2,y+2),text,fill='white',font=font(24,True))

def wrap(d,text,f,width):
    out=[]
    for p in text.split('\n'):
        if not p.strip():out.append('');continue
        line=''
        for word in p.split():
            trial=(line+' '+word).strip()
            if d.textbbox((0,0),trial,font=f)[2] <=width: line=trial
            else:
                if line:out.append(line)
                line=word
        if line:out.append(line)
    return out

def chart(draw, data, x=378, y=260, size=365):
    """Render report chart at its final resolution, without downscaling Arial labels.

    The PDF uses 140 DPI; an Arial 19-pixel font is ~9.8 pt in the exported PDF.
    Whole degrees appear here; seconds stay available in the planetary table.
    """
    step = size / 4
    chart_font = font(19, True)  # 9.77 pt when exported at 140 DPI
    draw.rounded_rectangle((x-5,y-5,x+size+5,y+size+5),radius=10,outline=GOLD,width=3)
    draw.rectangle((x,y,x+size,y+size),outline='black',width=2)
    for i in range(1,4):
        k=x+i*step
        draw.line((k,y,k,y+size),fill='black',width=2)
        draw.line((x,y+i*step,x+size,y+i*step),fill='black',width=2)
    draw.rectangle((x+step,y+step,x+3*step,y+3*step),fill=CREAM,outline='black',width=2)
    entries=[f'DOB: {data.get("date", "")}',f'Time: {data.get("time", "")}',
             f'Place: {data.get("place", "").split(",")[0][:22]}']
    for ii,t in enumerate(entries):
        f=font(16 if ii==2 else 18,True)
        bb=draw.textbbox((0,0),t,font=f)
        draw.text((x+size/2-(bb[2]-bb[0])/2,y+step*1.45+ii*29),t,fill=INK,font=f)
    groups=[[] for _ in range(12)]
    bodies={'Ascendant':data['ascendant'],**data['planets']}
    for name,p in bodies.items():
        s=p.get('sign_index',0)
        deg=int(float(p.get('degrees_in_sign',0)))
        groups[s].append((name,ABBR.get(name,name[:2])+('*' if p.get('retrograde') else '')+f' {deg:02}°'))
    for s,arr in enumerate(groups):
        r,c=CELLS[s];left=x+c*step;top=y+r*step
        if any(n=='Ascendant' for n,_ in arr):
            draw.line((left+step-22,top+2,left+step-3,top+21),fill='#d82727',width=3)
        placements=[item for item in arr if item[0]!='Ascendant']
        # Single-column labels avoid overlapping abbreviated planetary degrees.
        for j,(name,label) in enumerate(placements):
            f=chart_font
            if draw.textbbox((0,0),label,font=f)[2] > step-7:
                f=font(17,True)
            draw.text((left+4,top+4+j*21),label,font=f,fill=COLORS.get(name,INK))

def table(draw,x,y,width,header,rows,heights=26):
    cw=[width*p for p in ([.24,.21,.21,.34] if len(header)==4 else [ .25,.375,.375 ])]
    widths=[int(q) for q in cw];widths[-1]=width-sum(widths[:-1])
    draw.rounded_rectangle((x,y,x+width,y+30+len(rows)*heights),radius=8,fill='#fff9e4',outline=GOLD,width=2)
    draw.rectangle((x,y,x+width,y+30),fill='#ffe7a6')
    hfont=font(15,True);bfont=font(14)
    yy=y
    for i,row in enumerate([header]+rows):
        ht=30 if i==0 else heights
        cur=x
        for col,cell in enumerate(row):
            if col:draw.line((cur,yy,cur,yy+ht),fill='#cfb681',width=1)
            val=str(cell)
            while draw.textbbox((0,0),val,font=hfont if i==0 else bfont)[2]>widths[col]-7 and len(val)>4:val=val[:-2]+'…'
            draw.text((cur+5,yy+5),val,font=hfont if i==0 else bfont,fill=INK)
            cur+=widths[col]
        yy+=ht;draw.line((x,yy,x+width,yy),fill='#cdb585',width=1)

def make_page(data,text,continuation=0):
    img=Image.new('RGB',(W,1402),CREAM);d=ImageDraw.Draw(img)
    header=Image.open(ROOT/'assets/master_header.png').convert('RGB');img.paste(header,(0,0))
    footer=Image.open(ROOT/'assets/master_footer.png').convert('RGB');img.paste(footer,(0,1250))
    d.rectangle((0,1215,W,1249),fill=CREAM)
    if not continuation:
        title(d,'Lagna Chart',219)
        # Draw directly at output size so PDF and PNG chart text remains legible.
        chart(d,data,x=378,y=260,size=365)
        title(d,'Planetary Positions',638,561,1085)
        v=data.get('vimshottari',{});periods=v.get('periods',[])
        from datetime import datetime
        date=data.get('date','')
        def get_active():
            for p in periods:
                if p.get('start','')<=date<p.get('end',''):return p
            return next((p for p in periods if p.get('lord')=='Rahu'),periods[0] if periods else {})
        # Default to current-period Mahadasha (on today's date, not client's birth date).
        today=datetime.now().strftime('%Y-%m-%d');active=next((p for p in periods if p.get('start','')<=today<p.get('end','')), periods[-1] if periods else {})
        ds=active.get('children',[])
        def human(s):
            bits=s.split('-');return '-'.join(reversed(bits)) if len(bits)==3 else s
        drows=[[p.get('lord',''),human(p.get('start','')),human(p.get('end',''))] for p in ds]
        title(d,f"Antar Dasha ({active.get('lord','')} Dasha)",638,37,545)
        table(d,38,677,505,['Planet','Start','End'],drows,20)
        bodies={'Ascendant':data['ascendant'],**data['planets']}
        prow=[]
        for k,v in bodies.items():
            deg=float(v.get('degrees_in_sign',0));degree=int(deg);m=int((deg-degree)*60);sec=round((((deg-degree)*60)-m)*60)
            if sec==60:sec=0;m+=1
            if m==60:m=0;degree+=1
            prow.append([k, v.get('sign',''),f'{degree:02}:{m:02}:{sec:02}',str(v.get('nakshatra',''))[:11]+f"({v.get('pada','')})"])
        table(d,562,677,521,['Planets','Sign','Degree','Nakshatra'],prow,20)
        title(d,'Predictions and Analysis',979)
        region=(44,1024,1034,1240)
    else:
        title(d,'Predictions and Analysis (continued)',219)
        region=(44,271,1034,1237)
    return img,region

def render(data,body):
    if not body.strip():body='Prediction text to be entered by the astrologer.'
    pages=[];remaining=body.strip().replace('\r','')
    for n in range(30):
        im,area=make_page(data,remaining,n)
        d=ImageDraw.Draw(im)
        f=font(20)
        lines=wrap(d,remaining,f,area[2]-area[0]);line_h=28;max_lines=int((area[3]-area[1])//line_h)
        first=lines[:max_lines]
        for k,line in enumerate(first):d.text((area[0],area[1]+k*line_h),line,font=f,fill=INK)
        pages.append(im)
        if len(lines)<=max_lines:break
        remaining='\n'.join(lines[max_lines:])
    return pages

def export(data,prediction,format):
    imgs=render(data,prediction)
    output=BytesIO()
    if format=='pdf':
        imgs[0].save(output,format='PDF',resolution=140,save_all=True,append_images=imgs[1:]);return output.getvalue(),'application/pdf','pdf'
    # For a long report combine consecutive pages into a single PNG.
    if len(imgs)==1:result=imgs[0]
    else:
        result=Image.new('RGB',(W,1402*len(imgs)),CREAM)
        for i,im in enumerate(imgs):result.paste(im,(0,i*1402))
    result.save(output,format='PNG');return output.getvalue(),'image/png','png'
