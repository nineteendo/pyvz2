# Python VS. Zombies 2 (PyVZ2)
Python3 scripts for modifying Plants VS Zombies 2

# Release 1.0.0 (24 Jun 2021)
## Master 0.1.0 (11 Jul 2020)
1. DIFF TABLE:
	* Make changelog from a specific depth of a json file
2. JSON WALKER:
	* Get depth from JSON file for DIFF TABLE
3. RTONS PARSER:
	* **Forked from RTONParser v0.01 by 1Zulu**
	* Convert .rton to .json
	* Non-command line execution
## Master 0.2.0 (18 May 2021)
1. JSONS PARSER:
	* Convert .json to .rton
2. RTONS PARSER:
	* Latin strings & duplicate keys
## Master 0.2.1 (24 May 2021)
1. JSONS PARSER:
	* Encode keys correctly (Keys could be encoded as RTID instead of strings)
## Master 0.2.2 (26 May 2021)
1. JSONS PARSER:
	* More integer types & Unicode
2. RTONS PARSER:
	* Supported unicode strings
## Master 0.2.3 (27 May 2021)
1. JSONS PARSER:
	* Disabled other integer types (The game doesn't seem to use them in the packages.)
## Master 0.2.4 (2 Jun 2021)
1. OBBPatcher:
	* **Forked from OBBPatcher v0.05b by 1Zulu**
	* Extract & Patch sections from OBBs
	* Configured untill v7.8.1
2. README:
	* Information about the tools
3. RTONS PARSER:
	* Development tool for No_backup
	* Supported RTID type 0 and 2, all negative varints
## Master 0.2.5 (3 Jun 2021)
1. JSONS PARSER:
	* More RTID types
	* Automatic .dat & .bin extensions
2. README:
	* Mardown format
## Master 0.2.6 (4 Jun 2021)
1. JSONS PARSER:
	* No Backup SHOULD be supported
	* Output file with problematic keys that are configured
## Master 0.2.7 (5 Jun 2021)
1. JSONS PARSER:
	* Reverted changes from Master 0.2.6
## Master 0.2.8 (7 Jun 2021)
1. JSONS PARSER:
	* Temporary solution for No_Backup files
2. RTONS PARSER:
	* More SilentErrors
	* Tool to check support
## Master 0.2.9 (24 Jun 2021)
1. JSONS PARSER:
	* Removed jsons.py
	* Improved consistency
	* Input file & Directory
	* Open fail.txt
	* Version Mention & Author
2. OBBPatcher:
	* Python version
	* Configured untill v8.8.1
3. RTONS PARSER:
	* Removed rtons.py
	* Input file & Directory
	* Open fail.txt
	* Version Mention & Author
# Release 1.1.0 (6 Feb 2022)
## Master 1.0.0b (26 Nov 2021)
1. RTONS PARSER:
	* **Merged with JSONS PARSER**
## Master 1.0.1 (3 Jan 2022)
1. OBBUnpacker:
	* **Forked from 1bsr pgsr v0.2.2 by Luigi Auriemma**
	* Unpack obb
	* Fixed path names
## Master 1.0.1b (4 Jan 2022)
1. OBBUnpacker:
	* Unpack multiple files
	* Fixed short paths
	* Options
## Master 1.0.2 (8 Jan 2022)
1. OBBPatcher:
	* Removed java version
	* README
2. OBBUnpacker:
	* README
3. README:
	* Added OBBUnpacker
4. RTON Converter:
	* Renamed from RTONS PARSER
	* No more manually chosen data types
	* Options
	* README
## Master 1.0.2b (8 Jan 2022)
1. DIFF TABLE:
	* Moved to DataTools
2. JSON WALKER:
	* Moved to DataTools
2. LICENSE:
	* This tools are licenced under the GPL-3.0 LICENSE
## Master 1.0.3 (20 Jan 2022)
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
## Master 1.0.3b (21 Jan 2022)
1. OBBPatcher:
	* Load options with executable
2. OBBUnpacker:
	* Removed 1bsr_pgsr.bms
	* Windows path names
	* Load options with executable
3. RTON Converter:
	* Load options with executable
## Master 1.0.4 (22 Jan 2022)
1. OBBEdit:
	* Renamed from OBBUnpacker
	* Fixed wrong size
2. RTON Converter:
	* Increased efficiency
	* Options:
		* Split up cachLimit in cachKeyLimit & cachValueLimit
	* README:
		* Split up cachLimit in cachKeyLimit & cachValueLimit
## Master 1.0.5 (29 Jan 2022)
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
## Master 1.0.5b (30 Jan 2022)
1. OBBEdit:
	* Improved error log
2. RTON Converter:
	* Improved error log
## Master 1.0.5c (31 Jan 2022)
1. RTON Converter:
	* Improved objects
## Master 1.0.5d (1 Feb 2022)
1. RTON Converter:
	* Enforce Python 3.9
	* Fixed short names
## Master 1.0.6 (2 Feb 2022)
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
## Master 1.0.6b (3 Feb 2022)
1. RTON Converter:
	* Fixed NaN & Infinity
## Master 1.0.6c (4 Feb 2022)
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
## Master 1.0.6d (6 Feb 2022)
1. RTON-OFF:
	* Renamed from RTON Converter
	* Fixed wrong encoding on Windows
# Release 1.2.0 (The future)
## Master 1.1.4 (29 Mar 2022)
### Beta 1.1.0b (12 Feb 2022)
1. OBBEdit:
	* Decoding some PTX files
### Beta 1.1.0c (16 Feb 2022)
1. OBBEdit:
	* Converting to same folder
2. RTON-OFF:
	* Converting to same folder
### Beta 1.1.0d (17 Feb 2022)
1. OBBEdit:
	* Fixed outputting invalid obbs
2. RTON-OFF:
	* Fixed RTID()
### Beta 1.1.0e (22 Feb 2022)
1. OBBEdit:
	* Fixed DEBUG MODE, import error
2. RTON-OFF:
	* Fixed DEBUG MODE
### Beta 1.1.0f (23 Feb 2022)
1. README:
	* Crediting h3x4n1um
	* Issues?
### Beta 1.1.0g (4 Mar 2022)
1. OBBEdit:
	* Disabled PTX decoding 
	* Warning for BaseExceptions
2. RTON-OFF:
	* Faster conversion
	* Fixed negative varints
	* Options:
		* Added ensureAscii
	* Warning for BaseExceptions
### Beta 1.1.0h (12 Mar 2022)
1. RTON-OFF:
	* CDN support
	* Options:
		* Removed allowAllJSON & cachKeyLimit & cachKeyLimit
	* README:
		* Removed allowAllJSON & cachKeyLimit & cachKeyLimit
### Beta 1.1.1 (15 Mar 2022)
1. OBBEdit:
	* Preparing merge with RTON-OFF
### Beta 1.1.2 (15 Mar 2022)
1. OBBEdit:
	* **Merged with RTON-OFF**
	* Unpack json from obb
### Beta 1.1.2b (17 Mar 2022)
1. OBBEdit:
	* Tweaked conversion to better match PVZ2Tool
	* README:
		* **Merged OBBEdit & RTON-OFF**
### Beta 1.1.2c (19 Mar 2022)
1. OBBEdit:
	* RTON conversion is sligthly faster
### Beta 1.1.2c (19 Mar 2022)
1. OBBEdit:
	* Synced different configurations
2. RTONCrypto:
	* **Forked RTONCrypto from SmallPea**
	* Added options
### Beta 1.1.2d (22 Mar 2022)
1. OBBEdit:
	* Compressed rsb support
2. README:
	* Creditted Small Pea
### Beta 1.1.3 (22 Mar 2022)
1. OBBEdit:
	* Preparing merge of OBBEdit & RTONCrypto
	* Unpacking decrypted files
	* Options:
		* Removed Universal options
### Beta 1.1.4 (28 Mar 2022)
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
## Master 1.1.4b (4 Apr 2022)
1. OBBEdit:
	* Creditted YingFengTingYu
	* README:
		* Fixed documentation with help of Watto Studios.
2. README:
	* Split up credits in Code & Documentation
	* Creditted YingFengTingYu & Watto Studios
### Beta 1.1.4b (6 Apr 2022)
1. OBBEdit:
	* Removed rsgp unpacking
	* Moved encryption to custom library
	* Decoding all PTX files from PVZfree
	* Improved unpacking
	* Options:
		* Removed rsgpExtensions & rsgpUnpackLevel
	* README:
		* Removed rsgpExtensions & rsgpUnpackLevel
### Beta 1.1.5 (16 Apr 2022)
1. OBBEdit:
	* Added templates to make multiple custom settings easier.
	* Moved RTON conversions to custom library
	* Writing rsb.tag.smf
	* Improved patching
	* README:
		* Split up credits in Code & Documentation
		* Creditted YingFengTingYu & Watto Studios
### Beta 1.1.6 (1 May 2022)
1. OBBEdit:
	* Added changelog
	* Resupported rsg unpacking
	* Improved templates
	* Fixed patching
	* Fixed Encryption
	* Options:
		* Added overrideDataCompression & overrideEncryption & overrideImageDataCompression
		* Added rsgExtensions & rsgUnpackLevel
	* README:
		* Fixed documentation with help of Watto Studios.
		* Added overrideDataCompression & overrideEncryption & overrideImageDataCompression
		* Added rsgExtensions & rsgUnpackLevel
		* Fixed empty rows
### Beta 1.1.6b (2 May 2022)
1. OBBEdit:
	* Improved templates
	* Fixed patching
	* Options:
		* Added smfPacked, smfUnpacked, encryptedPacked, encryptedUnpacked, encodedPacked & encodedUnpacked
		* Added rsbPacked, rsbPatched, rsbUnpacked, rsgPacked, rsgPatched & rsgUnpacked
		* renamed some options
	* README:
		* Added smfPacked, smfUnpacked, encryptedPacked, encryptedUnpacked, encodedPacked & encodedUnpacked
		* Added rsbPacked, rsbPatched, rsbUnpacked, rsgPacked, rsgPatched & rsgUnpacked
		* renamed some options
### Beta 1.1.6c (3 May 2022)
1. OBBEdit:
	* More templates
	* Warning message for unknown headers
### Beta 1.1.6d (22 May 2022)
1. OBBEdit:
	* Conversion following more closely the official data format
	* Fixed unpack everything (level 6 instead of 7)
	* More control of paths for single file conversions
	* Show preset unpack level & overrides
	* Credited TwinKleS-C
	* Link to Discord server
	* Moved custom command line input & output to custom library
	* Updated changelog format
	* Options:
		* RTON conversion more closely to PVZ2Tool
		* Override encryption for patching
	* README:
		* More accurate depiction of data format
		* Credited TwinKleS-C
### Beta 1.1.6e (28 May 2022)
1. OBBEdit:
	* Sped up JSON conversion after a report of plant16gamer on Discord
### Beta 1.1.7 (29 May 2022)
1. OBBEdit:
	* Sped up RTON conversion
### Beta 1.1.7b (9 June 2022)
1. OBBEdit:
	* Sped up RTON conversion
	* Fixed self.Infinity as number
	* README:
		* Files & Foldes
		* Templates
2. README:
	* Fixed wording choice
### Beta 1.1.7c (10 June 2022)
1. OBBEdit:
	* Sped up JSON conversion slightly
### Beta 1.1.7d (11 June 2022)
1. OBBEdit:
	* Reverted faster JSON conversion.
	* Tweaked JSON conversion
### Beta 1.1.7e (18 June 2022)
1. OBBEdit:
	* Moved more code to custom library
### Beta 1.1.7f (19 June 2022)
1. OBBEdit:
	* Fixed version check
	* Dump fail.txt to custom file when failed to edit
	* Reorganized templates
	* No case-sensite keys
	* Added https:// to invite link
### Beta 1.1.7g (23 June 2022)
1. OBBEdit:
	* Confirm relatives paths.
	* Added unused template with default encryption
	* Fixed UnboundLocalError for RTONDecoding after a report of Earth2888 on Discord.
	* Fixed TypeError for SMFCompressing
	* Fixed AttributeError for RSGUnpacking
	* Fixed 1BSR & RTON HEADER info
	* Finished "Unpacking"