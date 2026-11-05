import re,sys,json,subprocess,html,collections,os
locs=re.findall(r'<loc>([^<]+)</loc>',open('sitemap.xml').read())
rows=[];titles=collections.Counter();descs=collections.Counter()
os.makedirs('pages',exist_ok=True)
for u in locs:
    fn='pages/'+re.sub(r'[^a-zA-Z0-9]','_',u)[-80:]
    if not os.path.exists(fn):
        subprocess.run(['curl','-sSL','-o',fn,u])
    s=open(fn,errors='ignore').read()
    t=re.search(r'<title>(.*?)</title>',s,re.S); t=html.unescape(t.group(1).strip()) if t else ''
    d=re.search(r'<meta name="description" content="([^"]*)"',s); d=d.group(1) if d else ''
    can='rel="canonical"' in s; og='og:title' in s; ogimg='og:image' in s
    ld=re.findall(r'"@type":"(\w+)"',s)
    h1=len(re.findall(r'<h1[\s>]',s))
    faq='FAQPage' in s
    mod=re.search(r'"dateModified":"([^"]+)"',s)
    text=re.sub(r'<(script|style)[\s\S]*?</\1>','',s); text=re.sub(r'<[^>]+>',' ',text)
    imgs=re.findall(r'<img\b[^>]*>',s); noalt=sum(1 for i in imgs if 'alt=' not in i or 'alt=""' in i)
    titles[t]+=1; descs[d]+=1
    rows.append(dict(u=u.replace('https://rctsi.3481.org',''),title=t,dlen=len(d),can=can,og=og,ogimg=ogimg,ld=sorted(set(ld)),h1=h1,faq=faq,mod=mod.group(1)[:10] if mod else '',chars=len(re.sub(r'\s+','',text)),noalt=noalt,size=len(s)))
dup_t=[t for t,c in titles.items() if c>1]; dup_d=[d for d,c in descs.items() if c>1 and d]
print('pages',len(rows),'dup titles',len(dup_t),'dup desc',len(dup_d))
for k in ['can','og','ogimg','faq']: print(k, sum(r[k] for r in rows))
print('no desc',[r['u'] for r in rows if r['dlen']==0])
print('desc too long>160',[ (r['u'],r['dlen']) for r in rows if r['dlen']>160][:10])
print('h1!=1',[(r['u'],r['h1']) for r in rows if r['h1']!=1])
print('no JSON-LD',[r['u'] for r in rows if not r['ld']])
print('noalt imgs',[(r['u'],r['noalt']) for r in rows if r['noalt']][:15])
print('thin <800 chars',[(r['u'],r['chars']) for r in rows if r['chars']<800])
print('big >2MB',[r['u'] for r in rows if r['size']>2_000_000])
print('FAQ pages',[r['u'] for r in rows if r['faq']])
print('types', collections.Counter(t for r in rows for t in r['ld']).most_common())
print('dateModified', collections.Counter(r['mod'] for r in rows).most_common(5))
for t in dup_t[:5]: print('DUP T',t)
json.dump(rows,open('../audit_rows.json','w'),ensure_ascii=False)
