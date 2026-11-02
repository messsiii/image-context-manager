"""Regenerate the README's original SVG artwork; no external assets or fonts."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
THEMES = {
    'light': dict(bg='#f5f7fb', panel='#ffffff', ink='#141b26', muted='#617085', line='#d4dce8', blue='#315ee8', tint='#edf2ff', subdued='#f0f3f7'),
    'dark': dict(bg='#101720', panel='#192330', ink='#f1f5fc', muted='#a9b8cd', line='#39485d', blue='#87a9ff', tint='#233451', subdued='#253140'),
}
COPY = {
    'en': dict(before='Replay everything', after='Keep what is needed', count3='3 image attachments', count2='2 images + 1 reference', draft='Draft', candidate='Candidate', pending='Pending', finished='Read complete', compare='Compare', verify='To verify', reference='Draft · source + checked result', store='Originals stay stored', recall='Restore for comparison or recall', concept='Offline demo · illustrated request contents', host='Your harness', hostbody='History + trusted task state', icm='Image Context Manager', icmbody='Keep pixels or use a reference', adapter='Your provider adapter', adapterbody='Check and send the copy', foot='Canonical history stays intact.'),
    'zh-CN': dict(before='全部重发', after='只带本轮需要的像素', count3='3 张图片附件', count2='2 张图片 + 1 条引用', draft='草稿', candidate='候选稿', pending='待核验', finished='读取完成', compare='用于比较', verify='尚未确认', reference='草稿 · 来源 + 已核验结果', store='原图保存在请求之外', recall='比较或召回时恢复', concept='离线示例 · 请求内容示意', host='你的宿主', hostbody='完整历史 + 可信任务状态', icm='Image Context Manager', icmbody='保留像素，或使用引用', adapter='你的模型适配器', adapterbody='检查并发送请求副本', foot='完整原始历史保持不变。'),
}

def start(w,h,title,desc,p):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',f'<title id="title">{escape(title)}</title>',f'<desc id="desc">{escape(desc)}</desc>',f'<style>text{{font-family:Arial,Helvetica,sans-serif;fill:{p["ink"]}}}.muted{{fill:{p["muted"]}}}.label{{font-weight:700}}.blue{{fill:{p["blue"]}}}</style>']
def text(out,x,y,value,size=22,cls='',anchor='start'):
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}">{escape(value)}</text>')
def rect(out,x,y,w,h,fill,stroke='none',r=10):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
def write(name,out):
    (ROOT/name).write_text('\n'.join(out+['</svg>'])+'\n')

def brand(theme):
    p=THEMES[theme]; out=start(800,204,'Image Context Manager','Original project wordmark: an image frame and a source-bound text reference.',p)
    for x,y in [(24,33),(33,25)]: rect(out,x,y,112,112,'none',p['line'],12)
    rect(out,42,17,112,112,p['tint'],p['blue'],12)
    out.append(f'<path d="M57 103 81 76 98 92 118 65 141 103Z" fill="{p["blue"]}"/>')
    out.append(f'<circle cx="73" cy="47" r="8" fill="{p["blue"]}"/>')
    rect(out,86,113,82,34,p['panel'],p['blue'],7)
    out.append(f'<path d="M98 125 h20 m-20 10 h54 m-22 -10 h22" fill="none" stroke="{p["blue"]}" stroke-width="3"/>')
    out.append('<g font-weight="750" letter-spacing="-3">')
    text(out,198,90,'image context',90)
    text(out,198,180,'manager',90)
    out.append('</g>'); write(f'brand-{theme}.svg',out)

def thumb(out,x,y,w,h,p,index):
    # Abstract synthetic image, not a screenshot of a product or a model result.
    rect(out,x,y,w,h,p['subdued'],p['line'],6)
    colors=[p['muted'],p['blue'],p['muted']]
    out.append(f'<circle cx="{x+18}" cy="{y+19}" r="5" fill="{colors[index]}"/>')
    out.append(f'<path d="M{x+12} {y+h-16} l{w*.22} {-h*.28} {w*.16} {h*.16} {w*.25} {-h*.38} {w*.20} {h*.50}Z" fill="{colors[index]}" opacity=".38"/>')

def demo(lang,theme,mobile):
    p=THEMES[theme]; c=COPY[lang]
    w,h=(420,628) if mobile else (900,420)
    out=start(w,h,c['concept'],'Synthetic offline demo: all three images are replayed on the left/before. After eligible draft retirement the request has a draft reference and two protected images; originals stay stored.',p)
    rect(out,0,0,w,h,p['bg'],r=16)
    text(out,22,30,c['concept'],19,'muted')
    panels=[(16,48,388,224),(16,290,388,224)] if mobile else [(18,48,423,274),(459,48,423,274)]
    for n,(x,y,pw,ph) in enumerate(panels):
        rect(out,x,y,pw,ph,p['panel'],p['line'],12)
        text(out,x+20,y+34,c['before'] if n==0 else c['after'],26,'label')
        text(out,x+20,y+61,c['count3'] if n==0 else c['count2'],20,'muted')
        tw=102 if mobile else 110
        if n==0:
            for i,(label,state) in enumerate([(c['draft'],c['finished']),(c['candidate'],c['compare']),(c['pending'],c['verify'])]):
                tx=x+20+i*(tw+16); ty=y+79
                thumb(out,tx,ty,tw,70 if mobile else 110,p,i)
                text(out,tx,ty+(94 if mobile else 137),label,21,'label')
                text(out,tx,ty+(120 if mobile else 164),state,18,'muted')
        else:
            rect(out,x+20,y+78,pw-40,38,p['tint'],r=7)
            text(out,x+32,y+104,c['reference'],20,'blue')
            for i,(label,state) in enumerate([(c['candidate'],c['compare']),(c['pending'],c['verify'])]):
                tx=x+20+i*(tw+18); ty=y+130
                thumb(out,tx,ty,tw,44 if mobile else 64,p,i+1)
                text(out,tx,ty+(70 if mobile else 91),label,21,'label')
            # The shorter reference row, rather than a fictional size graph, shows the change.
    sy=538 if mobile else 345
    rect(out,18,sy,w-36,72 if mobile else 57,p['panel'],p['line'],10)
    for dx in [0,6,12]: rect(out,34+dx,sy+19-dx*.4,30,31,'none',p['blue'],3)
    text(out,90,sy+27,c['store'],20,'label')
    text(out,90,sy+51,c['recall'],19,'muted')
    write(f'demo-{lang}-{theme}{"-mobile" if mobile else ""}.svg',out)

def pipeline(lang,theme,mobile):
    p=THEMES[theme]; c=COPY[lang]
    w,h=(420,330) if mobile else (900,152)
    out=start(w,h,'Host → Image Context Manager → provider adapter','The host owns canonical history and trusted task state; the component checks a request copy; the host adapter checks and sends. No automatic task recognition or provider call is implied.',p)
    if mobile:
        for i,(head,body) in enumerate([(c['host'],c['hostbody']),(c['icm'],c['icmbody']),(c['adapter'],c['adapterbody'])]):
            y=8+i*101
            rect(out,10,y,400,81,p['tint'] if i==1 else p['bg'],p['line'],10)
            text(out,30,y+32,head,24,'label')
            text(out,30,y+60,body,22,'muted')
            if i<2: out.append(f'<path d="M210 {y+85} v12 m-5 -5 5 5 5 -5" fill="none" stroke="{p["muted"]}" stroke-width="2"/>')
    else:
        for i,(head,body) in enumerate([(c['host'],c['hostbody']),(c['icm'],c['icmbody']),(c['adapter'],c['adapterbody'])]):
            x=10+i*301
            rect(out,x,10,278,98,p['tint'] if i==1 else p['bg'],p['line'],10)
            text(out,x+18,49,head,23,'label')
            text(out,x+18,82,body,20,'muted')
            if i<2: out.append(f'<path d="M{x+282} 59 h14 m-5 -5 5 5 -5 5" fill="none" stroke="{p["muted"]}" stroke-width="2"/>')
        text(out,450,139,c['foot'],20,'muted','middle')
    write(f'pipeline-{lang}-{theme}{"-mobile" if mobile else ""}.svg',out)

for theme in THEMES:
    brand(theme)
    for lang in COPY:
        for mobile in (False,True): demo(lang,theme,mobile); pipeline(lang,theme,mobile)
