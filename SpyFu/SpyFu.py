from ptl import get
get.setup(debug=True, driver=True)
try:
    PROJECT='SpyFu'
    DOMAIN = get.argv[1]
    DOMAIN_NAME=get.dmn(DOMAIN)
    overview = 'https://www.spyfu.com/overview/domain?query='
    seo_cp = 'https://www.spyfu.com/seo/competitors/domain?rowsPerPage=2500&query='
    ppc_cp = 'https://www.spyfu.com/ppc/competitors/domain?rowsPerPage=2500&query='
    seo_kw = 'https://www.spyfu.com/seo/keywords/domain?rowsPerPage=2500&query='
    ppc_kw = 'https://www.spyfu.com/ppc/keywords/domain?rowsPerPage=2500&query='
    get.soup(overview+DOMAIN, get.DR)
    overview={}
    overview['Organic Search Keywords Count']=get.bef('organic-search-widget-keywords-count')
    overview['Organic Search Monthly Click Count']=get.bef('organic-search-widget-monthly-clicks-count')
    overview['Paid Search Keywords Count']=get.bef('paid-search-widget-keywords-count')
    overview['Paid Search Monthly Click Count']=get.bef('paid-search-widget-monthly-clicks-count')
    overview['Organic/Paid Ratio']=get.bet('domain-overview-inbound-clicks-ratio-percent')
    get.save([overview], PROJECT+'/'+DOMAIN_NAME+'_overview')
    def get_data_from_table(index=0):
        tbl = get.be('backgrid','table',index=index)
        if not tbl:
            get.log("> There is no table data")
            return
        cols = [e.text.strip() for e in tbl.thead.findAll('th')][1:] #column names
        #get.log('> Columns: '+str(cols))
        rows = []
        for tr in [tr for tr in tbl.tbody.findAll('tr')]:
            try:
                row = {}
                tds = tr.findAll('td')[1:]
                for  i, td in enumerate(tds):
                    if cols[i]=='Domain Name': #domain name column
                        row[cols[i]] = td.text
                    elif cols[i]=='Overlap': 
                        if td.a: #overlap column
                            overlap = td.a.div['style'].replace('width: ', '').replace('%', '')
                            row[cols[i]] = float(overlap)
                        else:
                            if td.i: # rank change column
                                text = td.text.split('(')
                                row['Rank']= text[0]
                                row['Rank Change']= text[1].replace(')', '') if len(text)>1 else ''
                            else:
                                row[cols[i]]=-1               
                    elif cols[i]=='Keyword':
                        keyword = get.bec(td)
                        row[cols[i]] = keyword[0].text
                        row[cols[i]+' URL'] = keyword[1].text if len(keyword)>1 else ''
                    elif cols[i]=='Ad Timeline':
                        keyword = get.bec(td)
                        row[cols[i]] = keyword[0].text                    
                    elif len(cols[i])>0: #other column
                        if '(' in td.text:
                            text=td.text.split('(')
                            row['Rank'] = int(text[0])
                            text[1] = text[1].replace(')', '')
                            row[cols[i]]= int(text[1]) if text[1].isdigit() else 0
                        else: row[cols[i]] = get.s2f(td.text) 
            except: get.pe()
            rows.append(row)
        return get.DataFrame(rows)
    get.WDW_DELAY=120
    get.soup(seo_cp+DOMAIN, get.DR, waitc='class', waitv='backgrid')
    get.save(get_data_from_table(0), PROJECT+'/'+DOMAIN_NAME+'_seo_competitors')
    get.soup(ppc_cp+DOMAIN, get.DR, waitc='class', waitv='backgrid')
    get.save(get_data_from_table(0), PROJECT+'/'+DOMAIN_NAME+'_paid_competitors')
    get.soup(seo_kw+DOMAIN, get.DR, waitc='class', waitv='backgrid')
    get.save(get_data_from_table(1), PROJECT+'/'+DOMAIN_NAME+'_seo_keywords')
    get.soup(ppc_kw+DOMAIN, get.DR, waitc='class', waitv='backgrid')
    get.save(get_data_from_table(0), PROJECT+'/'+DOMAIN_NAME+'_paid_keywords')
except: get.pe()
get.quit()