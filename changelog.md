# Python VS. Zombies 2 (PyVZ2)
Python3 scripts for modifying Plants VS Zombies 2

# Release 1.0.0 (Jun 24, 2021)
## Master 1.0.0 (Jun 24, 2021)
### Beta 0.1.0 (Jul 11, 2020)
1. DIFF TABLE:
	* ~~Make changelog from a specific depth of a json file~~ (Moved to https://github.com/Nineteendo/DataTools)
		* [Beta 1.0.2b](#beta-1.0.2b-jan-8-2022)
		* [Beta 1.0.2b](#beta-1.0.2b-\(jan-8-2022\))
		* [Beta 1.0.2b](#beta-1.0.2b-\(jan-8,-2022\))
2. JSON WALKER:
	* ~~Get depth from JSON file for DIFF TABLE~~ (Moved to https://github.com/Nineteendo/DataTools for Beta 1.0.2b)
3. RTONS PARSER:
	* **Forked from RTONParser v0.01 by 1Zulu** http://drive.google.com/file/d/0B-SMAZsDM9ERTGwxVkpoN0U0LVE (Jan 8, 2018)
	* Convert .rton to .json
	* No command line arguments
### Beta 0.2.0 (May 18, 2021)
1. JSONS PARSER:
	* Convert .json to .rton
2. RTONS PARSER:
	* Latin strings & duplicate keys
### Beta 0.2.1 (May 24, 2021)
1. JSONS PARSER:
	* Encode keys correctly (Keys could be encoded as RTID instead of strings)
### Beta 0.2.2 (May 26, 2021)
1. JSONS PARSER:
	* More integer types & Unicode
2. RTONS PARSER:
	* Supported unicode strings
### Beta 0.2.3 (May 27, 2021)
1. JSONS PARSER:
	* Disabled other integer types (The game doesn't seem to use them in the packages)
### Beta 0.2.4 (Jun 2, 2021)
1. OBBPatcher:
	* **Forked from OBBPatcher v0.05b by 1Zulu** http://drive.google.com/file/d/0B_u59SyYZBrTMExscEpLdlNFVWc (Oct 8, 2021)
	* Extract & Patch sections from OBBs
	* Configured untill PVZ2 v7.8.1
2. README:
	* Information about the tools
3. RTONS PARSER:
	* ~~Development tool for No_backup~~ (Removed in Beta 1.0.2)
	* Supported RTID type 0 and 2, all negative varints
### Beta 0.2.5 (Jun 3, 2021)
1. JSONS PARSER:
	* More RTID types
	* Automatic .dat & .bin extensions
2. README:
	* Markdown format
### Beta 0.2.6 (Jun 4, 2021)
1. JSONS PARSER:
	* ~~No Backup SHOULD be supported~~ (Reverted in Beta 0.2.7)
	* ~~Output file with problematic keys that are configured~~ (Reverted in Beta 0.2.7)
### Beta 0.2.7 (Jun 5, 2021)
1. JSONS PARSER:
	* Reverted changes from Beta 0.2.6
### Beta 0.2.8 (Jun 7, 2021)
1. JSONS PARSER:
	* Temporary solution for No_Backup files
2. RTONS PARSER:
	* More SilentErrors
	* ~~Re-RTON checker~~ (deleted in Beta 1.0.2)
### Beta 1.0.0 (Jun 24, 2021)
1. JSONS PARSER:
	* Removed jsons.py
	* Improved consistency
	* Input file & Directory
	* Open fail.txt
	* Version Mention & Author
2. OBBPatcher:
	* Python version
	* Configured untill PVZ2 v8.8.1
3. RTONS PARSER:
	* Removed rtons.py
	* Input file & Directory
	* Open fail.txt
	* Version Mention & Author
# Release 1.1.0 (Feb 6, 2022)
## Master 1.1.0 (Feb 6, 2022)
### Beta 1.0.0b (Nov 26, 2021)
1. RTONS PARSER:
	* **Merged with JSONS PARSER**
### Beta 1.0.1 (Jan 3, 2022)
1. OBBUnpacker:
	* **Forked from 1bsr pgsr v0.2.2 by Luigi Auriemma** http://aluigi.altervista.org/bms/1bsr_pgsr.bms (Jun 29, 2015)
	* Unpack obb
	* Fixed path names
### Beta 1.0.1b (Jan 4, 2022)
1. OBBUnpacker:
	* Unpack multiple files
	* Fixed short paths
	* Options
### Beta 1.0.2 (Jan 8, 2022)
1. OBBPatcher:
	* Removed java version
	* README
2. OBBUnpacker:
	* README
3. README:
	* Added OBBUnpacker
4. RTON Converter:
	* Renamed from RTONS PARSER
	* Removed Development tool for No_backup (added in Beta 0.2.4)
	* Removed re-RTON check (added in )
	* No more manually chosen data types
	* Options
	* README
### Beta 1.0.2b (Jan 8, 2022)
1. DIFF TABLE:
	* Moved to DataTools
2. JSON WALKER:
	* Moved to DataTools
2. LICENSE:
	* This tools are licenced under the GPL-3.0 LICENSE
### Beta 1.0.3 (Jan 20, 2022)
1. OBBPatcher:
	* Extracting & Patching based on OBBUnpacker
	* Better path input
	* Options
	* README
2. OBBUnpacker:
	* Improved extraction
	* Better path input
	* More Extensions
	* Options:
		* Added confirmPath
		* More extensions
		* Added pgsrEndswith & pgsrEndswithIgnore
		* Added pgsrStartswith & pgsrStartswithIgnore
	* README:
		* Added confirmPath
		* Added pgsrEndswith & pgsrEndswithIgnore
		* Added pgsrStartswith & pgsrStartswithIgnore
		* Added pgsr_extract
3. README:
	* Removed DIFF TABLE & JSON WALKER
	* **Merged JSONS_PARSER & RTONS_PARSER**
4. RTON Converter:
	* Re-enabled other integer types
	* Better path input
	* Options:
		* Added cachLimit
		* Removed UncachedStrings
	* README:
		* Removed UncachedStrings
### Beta 1.0.3b (Jan 21, 2022)
1. OBBPatcher:
	* Load options with executable
2. OBBUnpacker:
	* Removed 1bsr_pgsr.bms
	* Windows path names
	* Load options with executable
3. RTON Converter:
	* Load options with executable
### Beta 1.0.4 (Jan 22, 2022)
1. OBBEdit:
	* Renamed from OBBUnpacker
	* Fixed wrong size
2. RTON Converter:
	* Increased efficiency
	* Options:
		* Split up cachLimit in cachKeyLimit & cachValueLimit
	* README:
		* Split up cachLimit in cachKeyLimit & cachValueLimit
### Beta 1.0.5 (Jan 29, 2022)
1. OBBEdit:
	* **Merged with OBBPatcher**
	* Added patching files & sections
	* Options:
		* Split up extractRsgp in rsbUnpackLevel & rsgpUnpackLevel
		* Split up extensions in rsbExtensions & rsgpExtensions
		* Renamed some options
	* README:
		* Split up extractRsgp in rsbUnpackLevel & rsgpUnpackLevel
		* Split up extensions in rsbExtensions & rsgpExtensions
		* Renamed some options
		* rsgp_extract
2. README:
	* **Merged OBBPatcher & OBBUnpacker**
### Beta 1.0.5b (Jan 30, 2022)
1. OBBEdit:
	* Improved error log
2. RTON Converter:
	* Improved error log
### Beta 1.0.5c (Jan 31, 2022)
1. RTON Converter:
	* Improved objects
### Beta 1.0.5d (Feb 1, 2022)
1. RTON Converter:
	* Enforce Python 3.9 after a report of mutaqin-hanif on GitHub http://github.com/Nineteendo/PVZ2tools/issues/4 (Feb 1, 2022)
	* Fixed short names
### Beta 1.0.6 (Feb 2, 2022)
1. OBBEdit:
	* Options:
		* Enabled DEBUG MODE
		* Removed dumpRsgp
	* README:
		* Removed dumpRsgp
2. RTON Converter:
	* Faster conversions
	* Options:
		* Added sortValues
		* Removed allowNan & ensureAscii
		* Renamed some options
	* README:
		* Added sortValues
		* Removed allowNan & ensureAscii
		* Renamed some options
### Beta 1.0.6b (Feb 3, 2022)
1. RTON Converter:
	* Fixed NaN & Infinity
### Beta 1.0.6c (Feb 4, 2022)
1. OBBEdit:
	* Options:
		* Enabled DEBUG MODE
2. RTON Converter:
	* Increased performance
	* Options:
		* Enabled DEBUG MODE
		* Merged cachKeyLimit & cachValueLimit
	* README:
		* Merged cachKeyLimit & cachValueLimit
### Beta 1.1.0 (Feb 6, 2022)
1. RTON-OFF:
	* Renamed from RTON Converter
	* Fixed wrong encoding on Windows
# Release 1.2.0 (Jun 23, 2022)
## Master 1.1.4 (Mar 29, 2022)
### Beta 1.1.0b (Feb 12, 2022)
1. OBBEdit:
	* Decoding some PTX files after some help of YingFengTingYu on GitHub https://github.com/Nineteendo/PVZ2tools/issues/10 (Mar 3, 2022)
### Beta 1.1.0c (Feb 16, 2022)
1. OBBEdit:
	* Converting to same folder
2. RTON-OFF:
	* Converting to same folder
### Beta 1.1.0d (Feb 17, 2022)
1. OBBEdit:
	* Fixed outputting invalid obbs
2. RTON-OFF:
	* Fixed RTID-detection
### Beta 1.1.0e (Feb 22, 2022)
1. OBBEdit:
	* Fixed DEBUG MODE, import error
2. RTON-OFF:
	* Fixed DEBUG MODE
### Beta 1.1.0f (Feb 23, 2022)
1. README:
	* Credited h3x4n1um
### Beta 1.1.0g (Mar 4, 2022)
1. OBBEdit:
	* Disabled PTX decoding
	* Warning for BaseExceptions
2. RTON-OFF:
	* Faster rton conversion
	* Fixed negative varints after comparing to h3x4n1um
	* Options:
		* Added ensureAscii
	* Warning for BaseExceptions
### Beta 1.1.0h (Mar 12, 2022)
1. RTON-OFF:
	* CDN support
	* Options:
		* Removed allowAllJSON & cachKeyLimit & cachKeyLimit
	* README:
		* Removed allowAllJSON & cachKeyLimit & cachKeyLimit
### Beta 1.1.1 (Mar 15, 2022)
1. OBBEdit:
	* Preparing merge with RTON-OFF
### Beta 1.1.2 (Mar 15, 2022)
1. OBBEdit:
	* **Merged with RTON-OFF**
	* Unpack json from obb
### Beta 1.1.2b (Mar 17, 2022)
1. OBBEdit:
	~~* Tweaked conversion to better match PVZ2Tool~~ (Reverted in Beta v1.3.0)
	* README:
		* **Merged OBBEdit & RTON-OFF**
### Beta 1.1.2c (Mar 19, 2022)
1. OBBEdit:
	* RTON conversion is sligthly faster
### Beta 1.1.2c (Mar 19, 2022)
1. OBBEdit:
	* Synced different configurations
2. RTONCrypto:
	* **Forked RTONCrypto from SmallPea** http://smallpeashared.lanzoul.com/iLqI3ze9qrg (Jan 29, 2022)
	* Added options
### Beta 1.1.2d (Mar 22, 2022)
1. OBBEdit:
	* Compressed rsb support after some help of YingFengTingYu on GitHub https://github.com/Nineteendo/PVZ2tools/issues/8 (Mar 3, 2022)
2. README:
	* Creditted Small Pea
### Beta 1.1.3 (Mar 22, 2022)
1. OBBEdit:
	* Preparing merge of OBBEdit & RTONCrypto
	* Unpacking decrypted files
	* Options:
		* Removed Universal options
### Beta 1.1.4 (Mar 28, 2022)
1. OBBEdit:
	* **Merged OBBEdit & RTONCrypto**
	* Added Smf decompressing
	* Added Encryption & Decryption
	* Options:
		* Added smfExtensions & smfUnpackLevel
		* Added encryptedExtensions & encryptedUnpackLevel
		* Added encryptionKey
		* Renamed some options
	* README:
		* Removed Universal options
## Master 1.1.4b (Apr 4, 2022)
1. OBBEdit:
	* Creditted YingFengTingYu
	* README:
		* Fixed documentation with help of Watto Studios.
2. README:
	* Split up credits in Code & Documentation
	* Creditted YingFengTingYu & Watto Studios
## Master 1.2.0 (Jun 23, 2022)
### Beta 1.1.4b (Apr 6, 2022)
1. OBBEdit:
	* Removed rsgp unpacking
	* Moved encryption to PyVZ2rijndael library
	* Decoding all PTX files from PVZfree
	* Unpacking from the data & image data sections after research on PVZFree
	* Options:
		* Removed rsgpExtensions & rsgpUnpackLevel
	* README:
		* Removed rsgpExtensions & rsgpUnpackLevel
### Beta 1.1.5 (Apr 16, 2022)
1. OBBEdit:
	* Added templates to make multiple custom settings easier.
	* Moved RTON conversions to PyVZ2rton library
	* Writing rsb.tag.smf
	* patching the data & image data sections after research on PVZFree
	* README:
		* Split up credits in Code & Documentation
		* Creditted YingFengTingYu & Watto Studios
### Beta 1.1.6 (May 1, 2022)
1. OBBEdit:
	* Resupported rsg unpacking
	* Fixed template naming after a report of plant16gamer on Discord http://discord.com/channels/746965788899934320/969961310353784882/970318999550328862 (May 1, 2022)
	* Improved templates after a suggestion of suggesion of Sarah Lydia (http://discord.com/users/643026770823610381) on Discord https://discord.com/channels/746965788899934320/942096976718204929/970344887398572122 (May 1, 2022)
	* Failed to support changing file size
	* Disabled decoding PTX files
	* Fixed patching images after a report of Sarah Lydia (http://discord.com/users/643026770823610381) on Discord https://discord.com/channels/746965788899934320/942096976718204929/970348378837905418
	* Options:
		* Added overrideDataCompression & overrideEncryption & overrideImageDataCompression
		* Added rsgExtensions & rsgUnpackLevel
	* README:
		* Fixed documentation with help of Watto Studios.
		* Added overrideDataCompression & overrideEncryption & overrideImageDataCompression
		* Added rsgExtensions & rsgUnpackLevel
		* Fixed empty rows
2. CHANGELOG:
	* Added changelog for PyVZ2 Development
3. PyVZ2rijndael library
	* Fixed Encryption
### Beta 1.1.6b (May 2, 2022)
1. OBBEdit:
	* Improved templates
	* Fixed changing file size after a report of Orange Doge on Discord http://discord.com/users/954311716999671839
	* Options:
		* Added smfPacked, smfUnpacked, encryptedPacked, encryptedUnpacked, encodedPacked & encodedUnpacked
		* Added rsbPacked, rsbPatched, rsbUnpacked, rsgPacked, rsgPatched & rsgUnpacked
		* renamed some options
	* README:
		* Added smfPacked, smfUnpacked, encryptedPacked, encryptedUnpacked, encodedPacked & encodedUnpacked
		* Added rsbPacked, rsbPatched, rsbUnpacked, rsgPacked, rsgPatched & rsgUnpacked
		* renamed some options
### Beta 1.1.6c (May 3, 2022)
1. OBBEdit:
	* More templates
	* Warning message for unknown headers after a report of plant16gamer on Discord http://discord.com/users/894919287142232105
### Beta 1.1.6d (May 23, 2022)
1. OBBEdit:
	* Fixed unpacking badly formatted rgs files after a report of plant16gamer on Discord http://discord.com/users/894919287142232105
	* Conversion following more closely the official data format after a report of Sarah Lydia on Discord http://discord.com/users/643026770823610381
	* Fixed unpack everything (level 6 instead of 7)
	* More control of paths for single file conversions
	* Show preset unpack level & overrides
	* Credited TwinKleS-C
	* Link to Discord server discord.gg/CVZdcGKVSw
	* Moved custom command line input & output to PyVZ2nineteendo library
	* Options:
		* RTON conversion more closely to PVZ2Tool
		* Override encryption for patching
	* README:
		* More accurate depiction of data format
		* Credited TwinKleS-C
2. CHANGELOG:
	* Updated changelog format
### Beta 1.1.6e (May 28, 2022)
1. PyVZ2rton library:
	* Sped up JSON conversion after a report of plant16gamer on Discord http://discord.com/users/894919287142232105
### Beta 1.1.7 (May 29, 2022)
1. PyVZ2rton library:
	* Sped up RTON conversion
### Beta 1.1.7b (Jun 9, 2022)
1. OBBEdit:
	* README:
		* Files & Foldes
		* Templates
2. README:
	* Fixed wording choice
3. PyVZ2rton library:
	* Sped up RTON conversion
	* Fixed self.Infinity as number
### ~~Beta 1.1.7c (Jun 10, 2022)~~
1. ~~PyVZ2rton library~~:
	* ~~Sped up JSON conversion slightly~~
### Beta 1.1.7d (Jun 11, 2022)
1. PyVZ2rton library:
	* Reverted faster JSON conversion after a report of Icy Studio http://discord.com/users/954311716999671839
	* Tweaked JSON conversion
### Beta 1.1.7e (Jun 18, 2022)
1. OBBEdit:
	* Moved more code to PyVZ2nineteendo library
2. PyVZ2rton library:
	* Support for custom warning messages
### Beta 1.1.7f (Jun 19, 2022)
1. OBBEdit:
	* Reorganized templates
	* Added http:// to invite link http://discord.gg/CVZdcGKVSw
2. PyVZ2nineteendo library:
	* Fixed version check
	* Dump fail.txt to custom file when failed to edit
	* No case-sensite keys after a report of farhan✓ on Discord http://discord.com/users/800342098573656075
### Beta 1.2.0 (Jun 23, 2022)
1. OBBEdit:
	* Added unused template with default encryption
	* Fixed UnboundLocalError for RTONDecoding after a report of Earth2888 on Discord. http://discord.com/users/615425385231810560
	* Fixed TypeError for SMFCompressing
	* Fixed AttributeError for RSGUnpacking
	* Fixed 1BSR & RTON HEADER info
	* Finished "Unpacking"
2. PyVZ2nineteendo library:
	* Confirm relatives paths.
# Release 1.3.0 (Fut X, 20XX)
## Master 1.2.x (Fut X, 20XX)
### Beta 1.2.0b (Jul 3, 2022)
1. OBBEdit:
	* ZIP Support for unpacking
	* Repack json to encrypted rtons
	* Options:
		* Added archiveExtensions, encodedExtensions, zipExtensions, zipPacked, zipUnpacked, zipUnpackLevel
	* README:
		* Added archiveExtensions, encodedExtensions, zipExtensions, zipPacked, zipUnpacked, zipUnpackLevel
2. PyVZ2nineteendo library:
	~~*Slightly Faster makedirs()~~
	* Fixed escaped brackets in path names.
### Beta 1.2.1 (Jul 17, 2022)
1. OBBEdit:
	* Fixed patch.py
2. Savemaxer:
	* Generate pp.dat
### Beta 1.2.1b (Jul 19, 2022)
1. OBBEdit:
	* Version check after a suggestion of TheEarthIsGreenNBlue on Discord http://discord.com/users/615425385231810560
	* Extra template
2. Savemaxer:
	* Version check
	* JSON Output
3. PyVZ2nineteendo library:
	* Version check after a suggestion of TheEarthIsGreenNBlue on Discord http://discord.com/users/615425385231810560
### Beta 1.2.1c (Jul 28, 2022)
1. PyVZ2nineteendo library:
	* Progress bar after a suggestion of TheEarthIsGreenNBlue on Discord http://discord.com/users/615425385231810560
2. PyVZ2rton library:
	* Work-around for more mods (SHUTTLE?) after a report of dekiel123 on GitHub http://github.com/Nineteendo/PVZ2tools/issues/17
3. CHANGELOG:
	* Added hyperlinks
4. README:
	* Sources instead of people
### Beta 1.2.1d (Aug 15, 2022)
1. OBBEdit:
	* Include "global_save_data" files
	* Remove extension "again" when unpacking archives
2. PyVZ2nineteendo library:
	* Catch errors while getting a new update
	* Fixed TypeError & ZeroDivisionError when processing empty tasks
	* Fixed Progressbar not scrolling on Android
### Beta 1.2.2 (Aug 19, 2022)
1. OBBEdit:
	* Halved RAM usage after a report of º on YouTube http://www.youtube.com/channel/UCG84cfOS3RAC_PSPoc0FnNQ
### Beta 1.2.2b (Aug 20, 2022)
1. OBBEdit:
	* Less progressbars when not necessary
2. PyVZ2nineteendo library:
	* Get update no longer creates extra files
	* Fixed time rounding
	* Added actions
3. CHANGELOG:
	* Creditted a bunch of people
### Beta 1.2.2c (Sep 9, 2022)
1. OBBEdit:
	* Fixed patching after a report of Im 12 on Discord http://discord.com/users/849953555946405928
	* Fixed json parsing
	* Extra template for unpacking everything but with decoded jsons
3. PyVZ2nineteendo library:
	* Fixed progressbar after a report of No🅱 on Discord http://discord.com/users/615425385231810560
	* Code cleanup
4. PyVZ2rton library:
	* Slightly faster rton conversions
5. CHANGELOG:
	* Removed unnecessary spaces
	* Tracking libraries separately
### Beta 1.2.3 (Fut X, 20XX)
1. PyVZ2nineteendo library:
	* Fixed colors (cyan, invert)
	* Check update every UTC day (not after 24 hours)
2. EXPERIMENTAL:
	* **Forked XlsxWriter from John McNamara** https://pypi.org/project/XlsxWriter/ (Feb 27, 2022)
	* Get info of rsbs in xlxs files
3. CHANGELOG:
	* Added more info for reports
	* Fixed date format
	* Beta's for pre-1.0 and pre-1.1 versions.
