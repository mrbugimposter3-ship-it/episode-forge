#!/usr/bin/env python3
"""Rhyme (fawasil) + opening clusters across the Quran, and 14-line sonnet-shaped sets (form only)."""
import json,re,collections
U=json.load(open('uth.json'))['data']['surahs'];T=json.load(open('tr.json'))['data']['surahs']
DIAC=re.compile('[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
def norm(s):
    s=s.replace('\u0670','ا').replace('ٱ','ا')
    s=DIAC.sub('',s); s=re.sub('[أإآ]','ا',s).replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    return re.sub('[^\u0621-\u064A ]','',s).strip()
def rkey(ar):
    w=norm(ar).split()[-1]
    last=w[-1]; prev=w[-2] if len(w)>1 else ''
    if last in 'نم' and prev in 'يو': return 'ī/ūn' if last=='ن' else 'ī/ūm'
    if last in 'ا' : # alif endings: -ā with preceding consonant group
        return 'ā(alif)'
    if prev in 'يو': return 'ī/ū'+last
    if prev=='ا': return 'ā'+last
    return last
def okey(ar):
    ws=norm(ar).split(); return ' '.join(ws[:2]) if ws else ''
def syl(t):
    t=re.sub('<[^>]+>','',t).lower()
    return len(re.findall("[aeiou]+",t))
A=[]
for s,t in zip(U,T):
    for a,b in zip(s['ayahs'],t['ayahs']):
        ar=a['text']
        if s['number']!=1 and a['numberInSurah']==1: ar=' '.join(ar.split()[4:]) if norm(ar).startswith('بسم الله') and len(ar.split())>4 else ar
        A.append(dict(ref=f"{s['number']}:{a['numberInSurah']}",s=s['number'],n=a['numberInSurah'],surah=s['name'],ar=ar,tr=re.sub('<[^>]+>','',b['text']),syl=syl(b['text']),rhyme=rkey(ar),open=okey(ar)))
R=collections.defaultdict(list);O=collections.defaultdict(list)
for x in A: R[x['rhyme']].append(x['ref']); O[x['open']].append(x['ref'])
O={k:v for k,v in O.items() if len({r.split(':')[0] for r in v})>1}
json.dump(dict(rhyme_clusters={k:dict(count=len(v),refs=v) for k,v in sorted(R.items(),key=lambda i:-len(i[1]))},
  opening_clusters={k:dict(count=len(v),refs=v) for k,v in sorted(O.items(),key=lambda i:-len(i[1]))}),open('clusters.json','w'),ensure_ascii=False,indent=1)
idx={x['ref']:x for x in A}
ex=[['105:1','105:2','1:7'],['75:1','90:1'],['73:1','74:1'],['2:3','2:4','2:6'],['107:5','107:6','114:5'],['85:1','86:1','84:1']]
cls=[]
for g in ex:
    rs={idx[r]['rhyme'] for r in g}; os_={re.sub('^(و|ف)?(ال)?','',idx[r]['open'].split()[0])[:3] for r in g}
    fam={idx[r]['rhyme'][:3] for r in g}
    cls.append(dict(refs=g,rhyme=[idx[r]['rhyme'] for r in g],open=[idx[r]['open'] for r in g],type=('ending-rhyme' if len(rs)==1 else '')+(' + ' if len(rs)==1 and len(os_)==1 else '')+('opening-match' if len(os_)==1 else '') or ('near-rhyme (same long-vowel family)' if len(fam)==1 else 'mixed: partial rhyme pairs + bridge ayah')))
THEMES=[("القيامة والبعث",[75,81,82,84,99,101,56,69]),("السماء والقسم الكوني",[85,86,91,92,93,89,77,79]),("الجنة ونعيمها",[55,56,76,83,88]),("النار والإنذار",[67,104,111,102,74,70]),("الرحمة والهداية",[1,93,94,96,97,108,110,112,113,114]),("قصص الأنبياء",[26,37,54,71]),("الليل والقيام",[73,74,76,17,51]),("آيات الخلق والطبيعة",[16,30,36,50,80,78]),("موسى وفرعون",[20,26,28,79]),("مريم وعيسى",[19,3]),("الصبر والتوكل",[103,65,94,12,39]),("التوحيد والإخلاص",[112,109,6,59,57]),("الطاغين وعاقبتهم",[89,105,106,91,69]),("الذكر والشكر",[55,87,96,62,63])]
def sonnet(name,surs,used):
    pool=[x for x in A if x['s'] in surs and x['ref'] not in used and 6<=x['syl']<=16]
    g=collections.defaultdict(list)
    seen=set()
    for x in pool:
        if norm(x['ar']) in seen: continue
        seen.add(norm(x['ar'])); g[x['rhyme']].append(x)
    keys=[]
    for k,v in g.items():
        v.sort(key=lambda x:(abs(x['syl']-10),x['s'],x['n']))
        if len(v)>=2: keys.append((sum(abs(x['syl']-10) for x in v[:2]),k))
    keys.sort()
    keys=[k for _,k in keys][:7]
    if len(keys)<2: return None
    # allow reuse of key with different ayat if fewer than 7 distinct
    pairs=[];take=collections.Counter()
    while len(pairs)<7:
        for k in keys:
            v=g[k];i=take[k]
            if i+2<=len(v) and len(pairs)<7: pairs.append((k,v[i:i+2]));take[k]+=2
        if all(take[k]+2>len(g[k]) for k in keys): break
    if len(pairs)<7: return None
    L=[]
    letters='ABCDEFG'
    for q in range(3):
        p1,p2=pairs[2*q],pairs[2*q+1]
        L+= [(letters[2*q],p1[1][0]),(letters[2*q+1],p2[1][0]),(letters[2*q],p1[1][1]),(letters[2*q+1],p2[1][1])]
    L+=[('G',pairs[6][1][0]),('G',pairs[6][1][1])]
    for _,x in L: used.add(x['ref'])
    return dict(theme=name,surahs=surs,lines=[dict(scheme=s,ref=x['ref'],surah=x['surah'],ar=x['ar'],tr=x['tr'],syllables=x['syl'],rhyme=x['rhyme']) for s,x in L])
used=set();S=[s for s in (sonnet(n,ss,used) for n,ss in THEMES) if s]
json.dump(dict(form="14 lines, ABAB CDCD EFEF GG (form only; no Shakespeare text)",sonnets=S,example_classification=cls),open('sonnets.json','w'),ensure_ascii=False,indent=1)
D='٠١٢٣٤٥٦٧٨٩';ad=lambda r:''.join(D[int(c)] if c.isdigit() else c for c in r)
with open('sonnets.md','w') as f:
    f.write('# مجموعات الفواصل المتناغمة (Rhyme Sonnets)\n\nالشكل فقط: ١٤ سطراً ABAB CDCD EFEF GG، الهدف ~١٠ مقاطع للسطر. لا نصوص شكسبير.\n\n## تصنيف أمثلة رافع\n')
    for c in cls: f.write(f"- {', '.join(c['refs'])}: **{c['type']}** — rhyme {c['rhyme']} / open {c['open']}\n")
    for i,s in enumerate(S,1):
        f.write(f"\n## {ad(str(i))}. {s['theme']}\n\n| | آية | Transliteration | ref | syl |\n|-|-|-|-|-|\n")
        for l in s['lines']: f.write(f"| {l['scheme']} | {l['ar']} | {l['tr']} | {ad(l['ref'])} | {l['syllables']} |\n")
print(len(R),'rhyme clusters',len(O),'opening clusters',len(S),'sonnets')
for c in cls: print(c)
