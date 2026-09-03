import json,sys
for f in sys.argv[1:]:
    r=json.load(open(f,encoding='utf-8'))
    b=[]
    b.append('### %s  profile=%s mobile=%s  %s'%(f,r['profile'],r['mobile'],r['utc']))
    for s in r['samples']:
        d=s['reading']
        if not isinstance(d,dict): b.append(' t=%-3s ERROR %s'%(s['at'],str(d)[:120])); continue
        b.append(' t=%-3s hidden=%s ready=%-9s sheet=%-5s rect=%-22s answer=%-5s nearest=%-5s working=%-5s deep=%-10s popups=%d top@centre=%-22s top@0.75=%-22s ids=%s'%(
            d.get('t_s'),d.get('hidden'),d.get('ready'),d.get('sheet_present'),
            json.dumps(d.get('sheet_rect')),d.get('answer_present'),d.get('has_nearest'),
            d.get('says_working'),d.get('deep_link_state'),d.get('popup_count'),
            d.get('top_at_centre'),d.get('top_at_lower_third'),d.get('identity_repeats')))
        for p in d.get('popups') or []:
            b.append('        popup[%d] %-46s rect=%-22s z=%-6s off_below=%-5s off_any=%-5s | %s'%(
                p['i'],p['cls'][:46],json.dumps(p['rect']),p['z'],p['offscreen_below'],p['offscreen_any'],p['text'][:70]))
        if d.get('measurement_line'): b.append('        ANSWER: %s'%d['measurement_line'][:150])
        if d.get('errs'): b.append('        errs: %s'%json.dumps(d['errs'])[:200])
    b.append('')
    sys.stdout.buffer.write(('\n'.join(b)+'\n').encode('utf-8','replace'))
