# OBBPatcher
- extract.py
- options.json
- patch.py
- README.md: this file
- versions.cfg Previous configuration file

# options.json
key | purpose
--- | ---
confirmPath | Confirm or change parsed path before conversion
DEBUG_MODE | Show full error traceback
enteredPath | Don't use hybrid paths that can be escaped
singleFile | Specify with PGSR to patch
pgsrEndswith | Only patch PGSRS ending with these strings
pgsrEndswithIgnore | Ignore the end of PGSRS
pgsrStartswith | Only patch PGSRS starting with these strings
pgsrStartswithIgnore | Ignore the start of PGSRS