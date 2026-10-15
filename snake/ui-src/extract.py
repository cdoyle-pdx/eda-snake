import re
h=open('nokia-snake-eda.html').read()
js=re.search(r'<script>(.*)</script>',h,re.S).group(1)
open('check-eda.js','w').write(js)
g=js.replace('"use strict";','')
g=re.sub(r'^const ','var ',g,flags=re.M); g=re.sub(r'^let ','var ',g,flags=re.M)
# The page bootstrap must not auto-run in the unit harnesses: it would start a
# second, concurrent EDA.connect() alongside the one each test awaits, which
# silently doubles token exchanges and makes call-count assertions meaningless.
# Matched by sentinel rather than exact text so editing the bootstrap body does
# not quietly stop the stripping and reintroduce that race.
pat = re.compile(r'/\* @bootstrap.*?\*/\s*\(async\(\)=>\{.*?\n\}\)\(\);', re.S)
assert len(pat.findall(g)) == 1, "bootstrap sentinel not found - check extract.py"
g = pat.sub('/* bootstrap stripped for tests */', g)
open('eda_globals.js','w').write(g)
print("eda_globals.js written, bootstrap stripped")
