"""Parameter fuer spamfilter.py"""
spf_version="[3.2]"
spf_vdate="2024-05-15"

dir_separator="\\"
dir_root="."+dir_separator
dir_results="dir.filter.results"+dir_separator
dir_input="dir.mail.input"+dir_separator
dir_nospam="dir.nospam"+dir_separator
dir_spam="dir.spam"+dir_separator
dir_output="dir.mail.output"+dir_separator

log_suffix=".log"
csv_suffix=".csv"
results_suffix=".results"
wordtable_suffix=".wordtable"
blacklist_suffix=".blacklist"
whitelist_suffix=".whitelist"

filename_prefix="spamfilter"
filename_blacklist=filename_prefix+blacklist_suffix
filename_whitelist=filename_prefix+whitelist_suffix
filename_nbwordtable=filename_prefix+wordtable_suffix
filename_results=filename_prefix+results_suffix
filename_csv=filename_prefix+csv_suffix
filename_logfile=filename_prefix+log_suffix

nb_wordtable={}               #wordtable initializing

#priority order from high to low
priorityorder="whitelist", "blacklist", "naive_bayes"

nb_spam_level = 0.67          #nb_level greater_or_equal is spam
nb_nospam_level = 0.33        #nb_level lower or equal is nospam
                              #in between is undetermined

nb_spam_class={"spam":(1.0,nb_spam_level), 
               "undetermined":(nb_spam_level,nb_nospam_level), 
               "nospam":(nb_nospam_level,0.0)}

#cleaning special characters
char_replaces={'"':' ', "\n":" ", "_":" ", ",":" ", "-":" ", 
               "+":" ", "„":" ", "’":" ", "“":" ", "%":" ", 
               ".":" ", "\t":" ", "[":" ", "]":" ", "<":" ", 
               ">":" ", "/":" ", "=":" ", "(":" ", ")":" ", 
               "ä":"ae", "ö":"oe", "ü":"ue", "Ä":"Ae", 
               "Ö":"Oe","Ü":"Ue","ß":"ss",
               "…":" ", "  ":" "}

#cleaning special words
words_ignore=["", " ", ":", "*", "#", "!", "&", "/", 
              ";", "?", "@", "|", "©", "®", "´", "·"]

CSV_Tags = ["from", "to", "betreff", "mail_probability", 
            "words_probability", "spam_probability", "spam_class"]
