"""Render README tool-flow diagrams. No network or third-party dependencies."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'docs/images/reference'
LABELS = {
 'en': {
  'title': 'How ICM handles an image task',
  'desc': 'The skill guides task decisions. Local tools preserve originals and prepare images. The agent or an optional native worker inspects them. Only checked, sufficient findings are reused as text; originals can be recalled.',
  'heading': 'IMAGE TASK / TOOL FLOW',
  'steps': [
   ('Identify the task', 'Agent + installed skill', 'Read text first; identify image use'),
   ('Prepare the image', 'Local ICM tools', 'Keep original, crop or compress'),
   ('Inspect and verify', 'Agent / optional visual worker', 'Host starts worker; text comes back'),
   ('Save findings', 'Local ICM tools', 'Reuse text when complete + sufficient'),
  ],
  'store': 'Originals + versions', 'keep': 'Save original', 'recall': 'Recall to recheck',
  'storage': 'Files stay local; originals remain available',
  'commands': ['skill', 'add / prepare', 'delegate (optional)', 'record / prepare'],
  'footer': 'SCHEMATIC · choices depend on task and verification',
  'frames': ['01 / 05 · Identify what this task needs', '02 / 05 · Prepare image; preserve original', '03 / 05 · Inspect image; return text findings', '04 / 05 · Save checked, sufficient findings', '05 / 05 · Need another check? Recall original'],
 },
 'zh-CN': {
  'title': 'ICM 如何处理图片任务',
  'desc': 'skill 指导 agent 判断用途，本地工具保存原图并准备图片。agent 或可选的原生看图子 agent 检查图片。只有完成并核对、足够使用的结论才能复用为文字，需要复查时取回原图。',
  'heading': '图片任务 / 工具流程',
  'steps': [
   ('判断这一步需要什么', 'agent + 已安装的 skill', '先读文字，再确定看图用途'),
   ('准备要看的图片', 'ICM 本地工具', '按需保留原图、裁剪或压缩'),
   ('看图并核对结果', 'agent / 可选看图子 agent', '宿主启动子 agent，只回传文字'),
   ('保存核对后的结论', 'ICM 本地工具', '完成且足够使用后，复用文字'),
  ],
  'store': '原图与版本', 'keep': '保存原图', 'recall': '取回原图，重新核对',
  'storage': '文件保存在本地，原图始终可取回',
  'commands': ['skill', 'add / prepare', 'delegate（可选）', 'record / prepare'],
  'footer': '流程示意 · 按任务与核验情况选择处理方式',
  'frames': ['01 / 05 · 判断本轮任务需要什么', '02 / 05 · 按需准备图片，保存原图', '03 / 05 · 看图核对，回传文字结论', '04 / 05 · 保存已核对、足够使用的结论', '05 / 05 · 需要复查时，取回原图'],
 },
}


def render(lang, dark, mobile):
    t = LABELS[lang]
    w, h = (360, 748) if mobile else (720, 422)
    bg, panel, border, dot, ink, muted, soft, accent = (
        ('#111113','#1A1A1E','#26262B','#232328','#EDEDEF','#A1A1AA','#3D3D45','#FF8A3D')
        if dark else
        ('#FBFAF7','#FFFFFF','#E6E2D9','#DDD8CD','#1B1A17','#5F5B53','#C9C3B6','#AC4808')
    )
    a = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
         '<!-- Visual conventions adapted from Browser Use; Copyright (c) 2024 Gregor Zunic; MIT; see ATTRIBUTION.md and UPSTREAM_LICENSE. ICM-specific workflow schematic, not a session recording. -->',
         f'<title id="title">{escape(t["title"])}</title><desc id="desc">{escape(t["desc"])}</desc>',
         f'''<defs><pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r=".7" fill="{dot}"/></pattern>
<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1.5L8 5L1 8.5" fill="none" stroke="#FE750E" stroke-width="1.3"/></marker></defs>
<style>.sans{{font-family:Geist,Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif}}.mono{{font-family:'Geist Mono',ui-monospace,Menlo,monospace}}.wire{{fill:none;stroke:#FE750E;stroke-width:1.4;marker-end:url(#arrow)}}.pulse{{fill:none;stroke:#FE750E;stroke-width:2;stroke-dasharray:3 16}}.frame{{display:none}}.progress{{opacity:0}}@keyframes flow{{to{{stroke-dashoffset:-38}}}}@keyframes active{{0%,18%{{stroke:#FE750E;stroke-width:2.5}}20%,100%{{stroke:{border};stroke-width:1}}}}@keyframes visible{{0%,19.8%{{opacity:1}}19.9%,100%{{opacity:0}}}}@keyframes progress{{0%{{stroke-dashoffset:100;opacity:1}}18%{{stroke-dashoffset:0;opacity:1}}20%,100%{{stroke-dashoffset:100;opacity:0}}}}@media(prefers-reduced-motion:no-preference){{.stage{{animation:active 12s linear infinite;animation-delay:var(--delay)}}.pulse{{animation:flow 2.4s linear infinite,visible 12s steps(1,end) infinite;animation-delay:0s,var(--delay)}}.progress{{animation:progress 12s linear infinite;animation-delay:var(--delay)}}.frame{{display:block;animation:visible 12s steps(1,end) infinite;animation-delay:var(--delay)}}.static-caption{{display:none}}}}</style>''',
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="{bg}" stroke="{border}"/>',
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#dots)"/>']
    def text(x,y,s,size=13,color=ink,weight=400,cls='sans',anchor='start'):
        a.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>')
    def delay(phase):
        return f'{-((5-phase)%5)*2.4:g}s'
    def wire(d, phase):
        a.append(f'<path d="{d}" class="wire"/>')
        a.append(f'<path d="{d}" class="pulse" style="--delay:{delay(phase)}"/>')
    def progress(x,y,width,phase):
        a.append(f'<path d="M{x} {y}h{width}" pathLength="100" stroke="#FE750E" stroke-width="3" stroke-linecap="round" stroke-dasharray="100" class="progress" style="--delay:{delay(phase)}"/>')
    def caption(y):
        text(24,y,t['footer'],10,muted,cls='sans static-caption')
        for phase,label in enumerate(t['frames']):
            a.append(f'<g class="frame" style="--delay:{delay(phase)}">')
            text(24,y,label,10,accent,weight=600)
            a.append('</g>')
    def icon(x,y,kind):
        # Small isometric base, matching the existing reference-diagram vocabulary.
        a.append(f'<g transform="translate({x} {y})" fill="none" stroke="{muted}" stroke-width="1.1" stroke-linejoin="round">')
        a.append(f'<path d="M0 15L20 26L40 15V21L20 32L0 21Z" fill="{bg}" stroke="{soft}"/><path d="M0 15L20 4L40 15L20 26Z" fill="{panel}"/>')
        if kind==0: a.append('<path d="M11 12L20 7L29 12L20 17Z M14 15V21L20 18" stroke="#FE750E"/>')
        elif kind==1: a.append('<path d="M11 9V19H29 M15 5V15H33 M18 16L22 12L28 15" stroke="#FE750E"/>')
        elif kind==2: a.append('<path d="M9 15Q20 4 31 15Q20 26 9 15Z"/><circle cx="20" cy="15" r="3" stroke="#FE750E"/>')
        else: a.append('<path d="M12 11L18 14L28 9 M12 17L24 23 M18 16L30 22" stroke="#FE750E"/>')
        a.append('</g>')
    text(24,28,'FIG 1.0',10,muted,cls='mono')
    text(w-24,28,t['heading'],10,muted,cls='mono',anchor='end')
    if mobile:
        for i,(title,owner,detail) in enumerate(t['steps']):
            y=52+i*138
            a.append(f'<rect x="26" y="{y}" width="308" height="110" rx="10" fill="{panel}" stroke="{border}" class="stage" style="--delay:{delay(i)}"/>')
            icon(40,y+12,i)
            text(94,y+26,f'0{i+1}',11,accent,cls='mono')
            text(94,y+48,title,16,weight=600)
            text(42,y+76,owner,13,muted)
            text(42,y+96,detail,12,muted)
            progress(42,y+105,276,i)
            if i<3: wire(f'M180 {y+112}V{y+134}',i)
        y=634
        a.append(f'<rect x="26" y="{y}" width="308" height="70" rx="10" fill="{panel}" stroke="{soft}" stroke-dasharray="4 3" class="stage" style="--delay:{delay(4)}"/>')
        text(42,y+25,t['store'],16,weight=600)
        text(42,y+49,t['storage'],12,muted)
        # Save and recall are a separate file-management loop, not history deletion.
        wire('M334 236H346V652H336',1)
        wire('M26 662H12V262H24',4)
        text(26,622,t['recall'],12,accent)
        text(334,622,t['keep'],12,accent,anchor='end')
        caption(730)
    else:
        for i,(title,owner,detail) in enumerate(t['steps']):
            x=24+i*174
            a.append(f'<rect x="{x}" y="74" width="150" height="176" rx="10" fill="{panel}" stroke="{border}" class="stage" style="--delay:{delay(i)}"/>')
            icon(x+18,91,i)
            text(x+126,108,f'0{i+1}',11,accent,cls='mono',anchor='end')
            text(x+12,147,title,13,weight=600)
            # English copy is split to retain the source diagram's compact labels.
            if lang=='en':
                ownerlines=[['Agent + skill'],['Local ICM tools'],['Agent / visual worker'],['Local ICM tools']][i]
                detaillines=[['Read text first;', 'identify image use'],['Original, crop', 'or compression'],['Optional native worker;', 'returns text only'],['Reuse text after checks:', 'complete + sufficient']][i]
            else:
                ownerlines=[owner]
                detaillines=['由当前 agent 启动', '只回传文字'] if i==2 else [detail]
            for j,line in enumerate(ownerlines): text(x+12,170+j*16,line,11,muted)
            for j,line in enumerate(detaillines): text(x+12,194+j*16,line,10 if lang=='zh-CN' else 11,muted)
            text(x+12,234,t['commands'][i],10,accent,cls='mono')
            progress(x+12,244,126,i)
            if i<3: wire(f'M{x+152} 158H{x+170}',i)
        a.append(f'<rect x="24" y="310" width="672" height="68" rx="10" fill="{panel}" stroke="{soft}" stroke-dasharray="4 3" class="stage" style="--delay:{delay(4)}"/>')
        text(42,337,t['store'],15,weight=600)
        text(42,359,t['storage'],12,muted)
        wire('M240 252V308',1)
        text(230,284,t['keep'],11,accent,anchor='end')
        wire('M620 308V280H294V252',4)
        text(460,274,t['recall'],11,accent,anchor='middle')
        caption(402)
    a.append('</svg>')
    return '\n'.join(a)+'\n'


def main():
    for lang in LABELS:
        for dark in (False,True):
            for mobile in (False,True):
                name=f'tool-workflow-{lang}-'+('dark' if dark else 'light')+('-mobile' if mobile else '')+'.svg'
                (OUT/name).write_text(render(lang,dark,mobile))

if __name__=='__main__': main()
