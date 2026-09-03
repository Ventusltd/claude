import json,glob,os,sys,collections
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
d=sys.argv[1]; rows={}
for f in sorted(glob.glob(os.path.join(d,'*.json'))):
    n=os.path.basename(f)[:-5]; o=None
    for line in open(f,encoding='utf-8',errors='replace'):
        line=line.strip()
        if line.startswith('{') and '"schema"' in line:
            try: o=json.loads(line)
            except Exception: pass
    if o: rows[n]=o
N=len(rows)
by=collections.defaultdict(lambda: collections.defaultdict(list))
for repo,o in rows.items():
    for r in o['results']: by[r['vaccine']][r['state']].append(repo)
print('repos measured: %d   immune repos: %d'%(N,sum(1 for v in rows.values() if v['status']=='immune')))
print('\nFAILING RULES - members, not cardinality (RH29). Control = repos the rule is quiet on.')
for v,st in sorted(by.items(), key=lambda kv:-len(kv[1].get('fail',[]))):
    f=st.get('fail',[])
    if not f: continue
    ctl=len(st.get('immune',[]))
    flag='' if ctl else '   <-- NO CONTROL: fires everywhere, suspect the rule'
    print('\n  %s  %d of %d   quiet on %d%s'%(v,len(f),N,ctl,flag))
    for r in sorted(f): print('      %s'%r)
warn={v:st.get('warn',[]) for v,st in by.items() if st.get('warn')}
if warn:
    print('\nWARNINGS - level: warning in the vaccine, an accepted dated allowance, NOT failures')
    for v,rs in sorted(warn.items(), key=lambda kv:-len(kv[1])):
        print('  %-28s %d of %d: %s'%(v,len(rs),N,', '.join(sorted(rs))))
skip={v:st.get('skipped',[]) for v,st in by.items() if st.get('skipped')}
if skip:
    print('\nSKIPPED - the rule declined to decide. A skip is not a pass.')
    for v,rs in sorted(skip.items()): print('  %-28s %d of %d: %s'%(v,len(rs),N,', '.join(sorted(rs))))
json.dump({v:{s:sorted(r) for s,r in st.items()} for v,st in by.items()},
          open(os.path.join(d,'_members.json'),'w',encoding='utf-8'),indent=1)
print('\nmembers written to %s'%os.path.join(d,'_members.json'))
