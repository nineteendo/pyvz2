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
AllowNan | Allow NaN, -infinity & infinity as values
AllowAllJSON | encode every file ending in JSON
BinObjclasses | Objclasses for files that have the .bin extension
CommaSeparator | Separator between values in JSON
DEBUG_MODE | Show full error traceback
DoublePointSeparator | Separator between key & value in JSON
EnsureAscii | escape non-ASCII characters
EnteredPath | use the path exactly like entered
Indent | number of spaces or text as indent, *null:* no indent
RTONExtensions | Extensions of RTON files
RTONNoExtensions | start of RTON files with no extension
RepairFiles | Repair NBT files that end abruptly
ShortNames | remove RTON extensions for JSON files
SortKeys | Sort keys in dictionary
UncachedStrings | Always use uncached strings (useful for hex editing)