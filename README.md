CLI app to transliterate words into IPA. 

obligatory arguments:
--file/--text: File or text to be transliterated, text should be a csv even if pasted directly on the terminal
--lang: language
inputs must be between "".

supports:
French
English
German
Portguese (really unreliable)
Spanish
Italian

Outputs either csv or txt file.

Code doesn't have dynamic reader.

The code uses a rule based transliteration library (epitran) for most languages except french, which uses a wikitionary scrapper library and falls back to epitran when doesn't find any. This is becuase epitran doesn't have good french support.
However, wikitionary also doesn't have good portguese support, so the results for that language in particular are really bad. For languages with multiple versions, the default is the european version.

For epitran, you must fix an encoding issue on the library files (Github Issue)[https://github.com/dmort27/epitran/issues/188]. 

In summary, go to the panphon library files, edit featuretable.py exactly in the _read_bases function at line 76. Add ", encoding='utf-8'" to the open function in line 79, or the first open function of the _read_bases function.
Made with chadgepeetea
