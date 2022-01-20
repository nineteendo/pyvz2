# NBTeditor
- fail.txt: file with the latest errors
- jsons_to_rtons.py: convert JSON to RTON
- options.json: settings for the conversion (see below)
- README.md: this file
- rtons_to_jsons.py: simplify RTON as JSON

## Usage
* Run rtons_to_jsons.py & insert path to RTON and output path
* Edit files as JSON
* Run jsons_to_rtons.py & insert input to JSON path and output path

# Options.json
key | purpose
--- | ---
allowNan | Allow NaN, -infinity & infinity as values
allowAllJSON | Encode every file ending in JSON
binObjClasses | Objclasses for files that have the .bin extension
cachLimit | Cached strings cap (negative for manual editing, don't set too high)
commaSeparator | Separator between values in JSON
confirmPath | Confirm or change parsed path before conversion
datObjClasses | Objclasses for files that have the .dat extension
DEBUG_MODE | Show full error traceback
doublePointSeparator | Separator between key & value in JSON
ensureAscii | Escape non-ASCII characters
enteredPath | Don't use hybrid paths that can be escaped
indent | Number of spaces or text as indent, *null:* no indent
RTONExtensions | Extensions of RTON files
RTONNoExtensions | Start of RTON files with no extension
repairFiles | Repair NBT files that end abruptly
shortNames | Remove RTON extensions for JSON files
sortKeys | Sort keys in dictionary