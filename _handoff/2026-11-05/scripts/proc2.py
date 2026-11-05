import os,re,json
from PIL import Image, ImageOps
import os,sys; src=sys.argv[1] if len(sys.argv)>1 else 'photos-raw'; out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','meetings','assets','img','meetings')  # 用法：python3 proc2.py <原始照片資料夾>
items=[]
files=sorted(os.listdir(src))
for f in files:
    name=f.rsplit('.',1)[0].strip()
    m=re.match(r'(\d{4})[.\-]?(\d{2})[.\-]?(\d{2})(?:-\d{2})?(.*)',name)
    if m:
        y,mo,d,rest=m.groups(); date=f'{y}-{mo}-{d}'
    else:
        date='2025-07-01'; rest=name
    rest=rest.lstrip('-').strip()
    rest=re.sub(r'^(25|26)地區年會','地區年會',rest)
    im=ImageOps.exif_transpose(Image.open(os.path.join(src,f))).convert('RGB')
    base=f"{date.replace('-','')}-{len(items)+1:02d}"
    b=im.copy(); b.thumbnail((1400,1400)); b.save(f'{out}/{base}.webp',quality=78,method=6)
    s=im.copy(); s.thumbnail((600,600)); s.save(f'{out}/{base}-s.webp',quality=72,method=6)
    items.append(dict(date=date,label=rest,img=base,w=s.width,h=s.height,undated=not m))
json.dump(items,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'items.json'),'w'),ensure_ascii=False)
print(len(items))
