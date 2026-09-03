import io, re, subprocess, sys

new = io.open('index.html', encoding='utf-8').read()
old = subprocess.run(['git', 'show', 'HEAD:index.html'],
                     capture_output=True, text=True, encoding='utf-8').stdout

V8 = '    { name:"UK Energy Atlas Grid Overlay V8", url:"./repd_grid_atlasv8/" },'
checks = [
    ("V8 sentinel occurs exactly once", new.count(V8) == 1),
    ("V8 route occurs exactly once",    new.count('./repd_grid_atlasv8/') == 1),
    ("AUTOMATION_START survives",       new.count('GRIDATLAS_V9_AUTOMATION_START') == 1),
    ("AUTOMATION_END survives",         new.count('GRIDATLAS_V9_AUTOMATION_END') == 1),
]

name_pat = re.compile('name:"([^"]*)"')
note_pat = re.compile('note:"([^"]*)"')
on, nn = name_pat.findall(old), name_pat.findall(new)
onote, nnote = note_pat.findall(old), note_pat.findall(new)

added_names   = [x for x in nn if x not in on]
removed_names = [x for x in on if x not in nn]
removed_notes = [x for x in onote if x not in nnote]

checks += [
    ("every pre-existing name: string unchanged", not removed_names),
    ("every pre-existing note: string unchanged", not removed_notes),
    ("exactly one name added",                    len(added_names) == 1),
    ("new route resolves to a real folder",       './estate_scan/202609021858/' in new),
]

print("name: strings  %d -> %d" % (len(on), len(nn)))
print("note: strings  %d -> %d" % (len(onote), len(nnote)))
print("added name   : %r" % (added_names,))
print("removed names: %r" % (removed_names,))
print("removed notes: %r" % ([x[:50] for x in removed_notes],))
print()
ok = True
for label, passed in checks:
    print(("  PASS  " if passed else "  FAIL  ") + label)
    ok = ok and passed
print()
print("RESULT:", "all checks pass" if ok else "FAILED")
sys.exit(0 if ok else 1)
