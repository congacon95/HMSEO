def run(url):
    from json import loads
    from requests import get
    from pandas import DataFrame
    api_url='https://www.googleapis.com/pagespeedonline/v1/runPagespeed'
    key='AIzaSyDGwAgFUs25FrsK6Rg_C7ketQ3K5jyo9og'
    desktop=get(api_url+'?url='+url+'&key='+key+'&strategy=desktop')
    mobile=get(api_url+'?url='+url+'&key='+key+'&strategy=mobile')
    desktop = loads(desktop.content.decode('utf8'))
    mobile = loads(mobile.content.decode('utf8'))
    def merge(data):
        formatstr = data['format']
        if 'args' in data.keys():
            args = data['args']
            for i, arg in enumerate(args):
                if args[i]['type']=='HYPERLINK':
                    formatstr=formatstr+'\n'+args[i]['value']
                else:
                    val = '' if 'SNAPSHOT' in args[i]['type'] else args[i]['value']
                    formatstr = formatstr.replace('$'+str(i+1), val)
        return formatstr
    def split_titled_string(_str):
        for a in _str:
            if a.isupper(): _str=_str.replace(a, ' '+a)
        return _str.strip()
    def get_issues(json_dict):        
        df=[]
        frs = json_dict['formattedResults']['ruleResults']
        for key in frs.keys():
            data={}
            data['Problem']=split_titled_string(key)
            data['Important']=round(frs[key]['ruleImpact'], 2)
            Headers=''
            for blocks in frs[key]['urlBlocks']:
                Headers = Headers+merge(blocks['header'])+'\n'
                if 'urls' in blocks.keys():
                    Details=''
                    for i in blocks['urls']:
                        Details=Details+(merge(i['result']))+'\n'
                    data['Details']=Details
            data['Headers']=Headers
            df.append(data)
        return DataFrame(df).sort_values(['Important'], ascending=False).reset_index(drop=True)
        
    return {'final_url':desktop['id'],
            'desktop_score':desktop['score'],
            'desktop_issues': get_issues(desktop),
            'mobile_score':mobile['score'],
            'mobile_issues': get_issues(mobile), }