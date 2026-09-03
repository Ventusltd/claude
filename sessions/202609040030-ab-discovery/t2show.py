import json,sys
for f in sys.argv[1:]:
    r=json.load(open(f,encoding='utf-8'))
    b=['### %s profile=%s mobile=%s %s  final_hidden=%s'%(f,r['profile'],r['mobile'],r['utc'],r.get('final_hidden'))]
    for s in r['transitions']:
        b.append(' t=%-6s ready=%-8s popups=%s sheet=%-5s ans_len=%-4s deep=%-9s loader=%-5s working=%-28s painted@0.78=%-24s ids=%s'%(
            s.get('t_s'),s.get('ready'),s.get('n_popups'),s.get('sheet'),s.get('answer_len'),
            s.get('deep'),s.get('loader_visible'),str(s.get('working_label'))[:28],
            s.get('painted_at_answer'),s.get('identity_repeats')))
        for p in s.get('popups') or []:
            b.append('        popup cls=%-30s rect=%-20s z=%-5s measure=%-5s | %s'%(p['cls'][:30],json.dumps(p['rect']),p['z'],p['has_measure'],p['text'][:60]))
        if s.get('search_bar'): b.append('        search_bar %s | %s'%(json.dumps(s['search_bar']['rect']),s['search_bar']['text'][:100]))
        if s.get('errs'): b.append('        errs %s'%json.dumps(s['errs'])[:180])
    b.append('')
    sys.stdout.buffer.write(('\n'.join(b)+'\n').encode('utf-8','replace'))
