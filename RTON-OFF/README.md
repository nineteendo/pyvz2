# RTON/OFF
- fail.txt: file with the latest errors
- fast_rtons.py: simplify RTON as JSON
- jsons_to_rtons.py: convert JSON to RTON
- options.json: settings for the conversion (see below)
- README.md: this file
- rtons_to_jsons: (old converter, DON'T use)

## Usage
* Run fast_rtons.py & insert path to RTON and output path
* Edit files as JSON
* Run fast_jsons.py & insert input to JSON path and output path

# Options.json
key | purpose
--- | ---
allowAllJSON | Encode every file ending in JSON
binObjClasses | Objclasses for files that have the .bin extension
cachKeyLimit | Cached keys cap (make negative for manual editing)
cachValueLimit | Cached values cap (make negative for manual editing)
comma | Spaces between values in JSON (make negative to disable)
confirmPath | Confirm or change parsed path before conversion
datObjClasses | Objclasses for files that have the .dat extension
DEBUG_MODE | Show full error traceback
doublepoint | Spaces between key & value in JSON (make negative to disable)
enteredPath | Don't use hybrid paths that can be escaped
indent | Spaces as indent, negative for tab, *null:* no indent
RTONExtensions | Extensions of RTON files
RTONNoExtensions | Start of RTON files with no extension
repairFiles | Repair RTON files that end abruptly
shortNames | Remove RTON extensions for JSON files
sortKeys | Sort keys in object
sortValues | Sort values in array
