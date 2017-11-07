from ptl import get
def add_audit(domain):
    get.dgs('https://www.semrush.com/projects/')
    #ADD DOMAIN
    get.dec('s-btn -xs -primary js-add-project')
    get.dsk(domain, 'js-input-domain')
    get.dsk(domain, 'js-input-name')
    get.dec('s-btn -s -success js-save-pr')
    while not get.de('setup', clas='data-action'):
        get.sleep(get.randint(3,7))
        get.log('> Waiting for setup button')
    get.dec('setup', clas='data-action')
    while 'Audit' not in get.det('s-btn__text', index=-1):        
        get.sleep(get.randint(3,7))
        get.log('> Waiting for setup audit button')
    get.dec('s-btn__text', index=-1)
    counter=0
    max_loop=20
    try: #WAIT FOR PROGRESS BAR
        while not get.de('s-widget__progress-title'):
            get.sleep(get.randint(3,7))
            get.log('> Waiting for progress bar '+str(counter*3)+'s')
            if counter==max_loop:
                get.log('> ')
                break
            error_btn=get.de('s-btn -danger -xs')
            if error_btn:
                error_btn.click()
            counter+=1
    except: get.pe()
    return get_project_id(get.DR.current_url), counter<max_loop
def get_project_id(url):
    for part in url.split('/'):
        if part.replace('#','').isdigit():
            return part.replace('#','')
def get_error_rows(ul): 
    return [li.text.strip().replace('\n', ' | ') for li in ul.find_elements_by_tag_name('li')]
def apply_filter(rows):
    result=''
    for row in rows:
        text_bag = set(row.upper().split())
        intersect= text_bag.intersection(FILTERS)
        if intersect:
            result+=('\n'+' | '.join(list(intersect))+': \t'+ row)
    print(result)
    return result.split('\n')
def get_errors(pid):
    #GO TO ERROR PAGE AND CHECK IF THE RESULTS IS READY EVERY 10-20s
    get.sleep(get.randint(10, 20))
    get.dgs('https://www.semrush.com/siteaudit/campaign/'+pid+'/review/#issues')
    while not get.des('sa-issuesWarnings'):        
        get.sleep(get.randint(10, 20))
        get.dgs('https://www.semrush.com/siteaudit/campaign/'+pid+'/review/#issues')
    ERRORS = get_error_rows(get.des('sa-issuesErrors')[1])
    WARNINGS = get_error_rows(get.des('sa-issuesWarnings')[1])
    NOTICES = get_error_rows(get.des('sa-issuesNotices')[1])
    rs={'ALL': ERRORS+WARNINGS+NOTICES}
    rs['ERRORS']=apply_filter(ERRORS)
    rs['WARNINGS']=apply_filter(WARNINGS)
    rs['NOTICES']=apply_filter(NOTICES)
    
    for k in list(rs.keys())[1:]:
        while len(rs['ALL'])>len(rs[k]):
            rs[k].append('')
    return rs
def delete_project(pid, domain):
    #DELETE DOMAIN FROM PROJECTS LIST
    #IF THERE ARE 5 PROJECT AND THE DOMAIN IS AT #5 THEN
    #WEBDRIVER HEIGHT HAS TO >1100 OR ELSE THE DELETE BUTTON IS NOT VISIBLE = NOT CLICKABLE 
    try:
        get.log('> Deleting project: '+domain+', PID='+pid)
        get.dgs('https://www.semrush.com/projects/')
        div=get.de('s-project js-project-'+pid+' ')
        while not div:
            get.sleep(get.randint(3,7))
            get.dgs('https://www.semrush.com/projects/')
            div=get.de('s-project js-project-'+pid+' ')
        div.find_element_by_class_name('sr-infomenu').click()
        content=div.find_element_by_class_name('sr-infomenu-content')
        content.find_elements_by_tag_name('li')[1].click()
        get.dsk(domain, 'Project name', 'placeholder')
        get.dec('s-btn -s -danger js-remove')
        get.log('> Deleted project: '+domain+', PID='+pid)
        return True
    except: get.pe('Can not delete the project: '+domain+' > PID='+pid)
def login(url):
    get.dgs(url)
    get.log('> Login')
    account=get.f2l('SEMRush_account.txt')
    get.dec('header__navigation-login')
    get.dsk(account[0], 'email', 'name')
    get.dsk(account[1], 'password', 'name')
    get.dec('auth-popup__submit', clas='data-test')
    get.sleep(5)

try:
    PROJECT='SEMRushErrorsReport'
    FILTERS=set(get.f2l('filters.txt'))
    DOMAINS=get.f2l('domains.txt')
    DOMAINS=[dm[dm.index('//')+2:] if '//' in dm else dm for dm in DOMAINS]
    DOMAINS=[dm[:dm.index('/')] if '/' in dm else dm for dm in DOMAINS]
    DOMAINS=[dm for dm in DOMAINS if len(dm)>3]
    get.log('> DOMAINS: '+str(DOMAINS))
    get.log('> FILTERS: '+str(FILTERS))
    get.setup(debug=True, driver=True)
    URL='https://www.semrush.com/'
    login(URL)
    error_times=0
    error_allow=5
    error_domain=None
    for i, domain in enumerate(DOMAINS):
        get.log('> Progress: '+str(i+1)+'/'+str(len(DOMAINS))+': '+domain)
        pid, success = add_audit(domain)
        if success:
            get.log('> Add audit successed')
            get.save(get_errors(pid), PROJECT+'/'+get.START_TIME+'/'+domain)
        else:
            #Add failed domain to the DOMAINS list if fail
            if not error_domain: error_domain=domain
            elif error_domain==domain: error_times+=1
            else: error_times=0
            if error_times < error_allow:
                get.log('> Add '+domain+' back to project list '+str(error_times)+' times')
                DOMAINS.append(domain)
                error_domain=domain
        if not delete_project(pid, domain):
            get.log('> Fatal error encountered.')
            break
except: get.pe()
get.quit(PROJECT)