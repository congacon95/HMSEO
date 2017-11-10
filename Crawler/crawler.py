import sys
if 'E:\\jupyter_notebook\\HomemadeSEO_Phil\\' not in sys.path:
    sys.path.append('E:\\jupyter_notebook\\HomemadeSEO_Phil\\')
from ptl import get
get.setup(debug=True, driver=False)
import numpy
get.N_FAIL_REQUEST=1

def check_length_status(_len, tag):
    if tag=='title':
        if _len == 0:  return 'BAD, MISSING '+tag.upper()
        if _len > 90: return 'TOO LONG'
        if _len > 70:  return 'LONG'
        if _len < 50:  return 'SHORT'
        if _len < 30:  return 'TOO SHORT'
        return 'GOOD'
    if tag=='description':
        if _len == 0:  return 'BAD, MISSING '+tag.upper()
        if _len > 160: return "TOO LONG"
        if _len < 40:  return 'TOO SHORT'
        return 'GOOD'
def check_img(row):
    try:
        imgs=row['SOUP'].findAll('img')
        imgs_alt_tag=[img['alt'] for img in imgs if img.has_attr('alt')]
        row['Number of images'.upper()] = len(imgs)
        row['Number of with alt-tag'.upper()] = len(imgs_alt_tag)
        row['Number of without alt-tag'.upper()] = len(imgs) - len(imgs_alt_tag)
        alt_tags=numpy.array([len(img) for img in imgs_alt_tag])
        if len(alt_tags)>0:
            row['alt-tag Minimum length'.upper()] = alt_tags.min()
            row['alt-tag Average length'.upper()] = alt_tags.mean()
            row['alt-tag Maximum length'.upper()] = alt_tags.max()
        df = get.DataFrame(imgs_alt_tag)
        row['Number of Alt-Tags that are duplicated'.upper()] = len(df[df.duplicated])       
    except: get.pe()
def check_meta(row):
    try:
        for i, meta in enumerate(row['SOUP'].findAll('meta')):
            if not meta.has_attr('name') or not meta.has_attr('content'): continue
            key = meta['name'].lower()
            if key!='description' and key!='keywords': continue
            key='META '+key.upper()
            row[key] = meta['content']
            _len = len(row[key])
            row[key+' LENGTH'] = _len
            #if key=='keywords':
                #row[key+' STATUS'] = check_length_status(_len, 'keywords')
            if key=='description':
                row[key+' STATUS'] = check_length_status(_len, 'description')       
    except: get.pe(str(meta))
def check_canonical_link(row):
    try:
        for i, link in enumerate(row['SOUP'].findAll('link')):
            if not link.has_attr('rel'): continue
            for i in link['rel']:
                if i.lower()=='canonical': 
                    key=i.upper()
                    row[key] = link['href']
                    row[key+' LENGTH'] = len(row[key])
                    break
            if 'CANONICAL' not in row:
                row['CANONICAL']='None'
                row['CANONICAL LENGTH']=''       
    except: get.pe(str(link))
def check(tag, row):
    try:
        for i, _tag in enumerate(row['SOUP'].findAll(tag)):
            key=tag.upper()
            if 'h' in tag: key=key+'-'+str(i+1)
            row[key]=_tag.text
            _len = len(row[key])
            row[key+' LENGTH'] = _len
            row[key+' STATUS'] = check_length_status(_len, tag)       
    except: get.pe(str(_tag))
def soups(rows, folder, t_id):
    for row in rows:
        try:    
            get.log('> GET '+row['URL'])
            rq = get.get(row['URL'])
            folders=row['URL'].split('//')[1].split('/')[:-1]
            for i, folder in enumerate(folders):
                if i==0: continue
                row['FOLDER LEVEL '+str(i)]=folder
            row['DEPTH'] = len(folders)
            row['FINAL URL']=rq.url
            row['FINAL URL LENGTH']=len(rq.url)
            row['HEADERS']=rq.headers
            row['CONTENT TYPE']=rq.headers['Content-Type'] if 'Content-Type' in rq.headers else ''
            #row['CONTENT LENGTH']=rq.headers['Content-Length'] if 'Content-Length' in rq.headers else ''
            #row['SERVER']=rq.headers['Server']
            row['DATE']=rq.headers['Date']
            #row['ENCODE']=rq.encoding
            row['RESPONSE TIME (MS)']=rq.elapsed.microseconds/1000
            row['REDIRECT TYPE']='NONE' if not rq.is_redirect else 'PERMANENT' if rq.is_permanent_redirect else 'TEMPERARY'
            row['REDIRECT']=rq.is_redirect
            row['STATUS']=rq.reason
            row['STATUS CODE']=rq.status_code
            row['HTTP/HTTPS']='HTTPS' if 'https' in rq.url[:10] else 'HTTP'
            row['SOUP'] = get.bs(rq.content, 'html.parser')
            check('title', row)
            check('h1', row)
            check('h2', row)
            check_meta(row)
            check_img(row)
            check_canonical_link(row)
        except: get.pe()
def distinct(alist):
    return list(dict.fromkeys(alist))

def has(a, alist):
    for item in alist:
        if item in a: return False
    return True
def get_hrefs(stack, url):
    hrefs=[]
    ROOT = get.dmr(url).split('/')[-1]
    filters=[' ', '?', 'javascript', 'tel:','fax:','mailto:', '.jpg', '.png']
    for row in stack:
        if 'SOUP' in row and row['SOUP']:
            _hrefs=[a['href']
                    for a in get.bes(None, div='a', pr=row['SOUP']) 
                    if a.has_attr('href')]
            _hrefs=[a
                    for a in _hrefs
                    if len(a)>3
                    and has(a, filters)]
            for a in _hrefs:
                if 'http' not in a:
                    _hrefs[_hrefs.index(a)]=(url+a)
            _hrefs=[a.replace('//','/').replace(':/', '://')
                    for a in _hrefs
                   if ROOT in a]
            hrefs=hrefs+distinct(_hrefs)
    return hrefs
def check_dp(df, output, col):
    try:
        if col in df.keys():
            dps=list(df[df.duplicated(col)].groupby(col))
            if len(dps)>0:
                for i, dp in enumerate(dps):
                    row_text, _dp = dp
                    _dp = df[df[col]==row_text]
                    row={}
                    row['TAG']=col
                    row['DUPLICATION TEXT'] = row_text
                    row['NUMBER OF DUPLICATION'] = len(_dp)
                    row['URL'] = '#\n'+'\n'.join(list(_dp['URL']))
                    output.append(row)
    except: get.pe(col)
def reformat_dp(dp, rows_text):
    dp = get.DataFrame(dp).sort_values(['TAG',
                                        'NUMBER OF DUPLICATION'],
                                    ascending=False)
    rs=get.DataFrame()
    for tag in rows_text:
        rs = get.concat([rs, dp[dp['TAG']==tag]])
    return rs
if __name__=='__main__':
    try:
        sites = [line for line in get.f2l(get.argv[1]) if len(line)>0]
        get.log('> All sites:'+ str(sites))
        for site in sites:
            URL=site
            DOMAIN = get.dmn(URL)
            DOWNLOADED=[]
            try:
                robots = get.get(URL+'robots.txt')
                if not robots:
                    get.log('> robots.txt not found')
                    DOWNLOADED.append({'URL': URL+'robots.txt', 'TITLE': 'Missing Robots.txt'})
                else:
                    DOWNLOADED.append({'URL': URL+'robots.txt', 'TITLE': 'Found Robots.txt'})
            except: 
                get.log('> robots.txt not found')
                get.pe()
            VISISTED=[]
            STACK=[URL]
            N_THREADS= 5
            THRESHOLD= 3 
            ITER=1
            while len(STACK)!=0:
                get.log('> Iteration:  '+str(ITER)+', stack size: '+str(len(STACK)))
                get.log('> Downloaded: '+str(len(DOWNLOADED)))
                stack=[{'URL':url} for url in STACK if '.pdf' not in url and '/members/' not in url]
                #print('> test'+str(get.split(STACK, N_THREADS)))
                if len(stack)/N_THREADS > THRESHOLD:
                    N_THREADS=get.ceil(len(stack)/THRESHOLD)
                get.log('> Getting content')
                #soups(stack, '', '')
                get.run_threads(get.split(stack, N_THREADS), soups, folder='nodriver')
                VISISTED=VISISTED+STACK
                hrefs = get_hrefs(stack, URL)
                get.log('> New links:  '+str(len(hrefs)))
                DOWNLOADED=DOWNLOADED+stack
                STACK = list(set(hrefs)-set(hrefs).intersection(set(VISISTED)))
                get.log('> New stack: '+str(len(STACK)))
                #STACK = STACK[:3]
                ITER+=1
                #if ITER==3: break
            get.log('> Finished after '+str(ITER)+' iterations')
            DOWNLOADED=get.DataFrame(DOWNLOADED).sort_values('TITLE LENGTH', ascending=False)
            columns=['URL',
                    'FINAL URL',
                    'FINAL URL LENGTH',
                    'CANONICAL',
                    'CANONICAL LENGTH',
                    'TITLE',
                    'TITLE LENGTH',
                    'TITLE STATUS',
                    'H1-1',
                    'H1-1 LENGTH',
                    'H1-1 STATUS',
                    'META DESCRIPTION',
                    'META DESCRIPTION LENGTH',
                    'META DESCRIPTION STATUS',
                    'META KEYWORDS',
                    'META KEYWORDS LENGTH',
                    'H2-1',
                    'H2-1 LENGTH',
                    'H2-1 STATUS',
                    'NUMBER OF IMAGES',
                    'NUMBER OF WITH ALT-TAG',
                    'NUMBER OF WITHOUT ALT-TAG',
                    'ALT-TAG AVERAGE LENGTH',
                    'ALT-TAG MAXIMUM LENGTH',
                    'ALT-TAG MINIMUM LENGTH',
                    'NUMBER OF ALT-TAGS THAT ARE DUPLICATED',
                    'CONTENT TYPE',
                    'DATE',
                    'HTTP/HTTPS',
                    'REDIRECT',
                    'REDIRECT TYPE',
                    'RESPONSE TIME (MS)',
                    'STATUS',
                    'STATUS CODE',
                    'DEPTH',
                    'FOLDER LEVEL 1',
                    'FOLDER LEVEL 2',
                    'FOLDER LEVEL 3',]
            get.save(DOWNLOADED, DOMAIN+'/crawl', columns=columns)
            DUPLICATIONS=[]
            check_dp(DOWNLOADED, DUPLICATIONS, 'TITLE')
            check_dp(DOWNLOADED, DUPLICATIONS, 'H1-1')
            check_dp(DOWNLOADED, DUPLICATIONS, 'META DESCRIPTION')
            check_dp(DOWNLOADED, DUPLICATIONS, 'H2-1')
            get.save(reformat_dp(DUPLICATIONS, 
                                ['TITLE', 'H1-1', 'META DESCRIPTION', 'H2-1']), 
                    DOMAIN+'/duplications',
                    columns=['TAG', 
                            'DUPLICATION TEXT',
                            'NUMBER OF DUPLICATION', 
                            'URL', ])
            get.log('> Start time:'+get.START_TIME)
            get.log('> Finish time:'+get.dtn())
    except: get.pe()
get.quit()