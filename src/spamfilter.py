"""
SpamFilter Team 6 

Spamfilter auf Basis von Whitelisting, Blacklisting und Naive Bayes Filter
Parameter aus params.py
"""

#----------------------------------------------
# Module laden
import os
from statistics import mean

from params import *

# Log-Datei oeffnen
logfile = open(dir_results + filename_logfile, 'w')

# Log-Header schreiben
logHeader = f"spamfilter.py {spf_version} {spf_vdate}\n"
print(logHeader)
print(logHeader, file=logfile)


#----------------------------------------------
# Funktionen allgemein

def replaceChars(text):
    """
    Ersetzt in einem Text bestimmte Zeichen durch andere, basierend auf dem "char_replaces" dictionary.

    Parameters:
        text (str): Der Text, in dem die Zeichen ersetzt werden sollen.

    Returns:
        str: Der Text mit den ersetzen Zeichen.
    """
    return ''.join(char_replaces.get(char, char) for char in text)

def wordList(text):
    """
    Zaehlt die Haeufigkeit der Woerter im uebergebenen Text.

    Parameters:
        text (str): Der Text, dessen Woerter gezaehlt werden sollen.

    Returns:
        dict: Ein Dictionary, das die Woerter als keys und ihre Haeufigkeit als Values enthaelt.
    """
    word_list = {}
    for word in text.split(' '):
        if word not in word_list:
            word_list[word] = 1
        else:
            word_list[word] += 1
    return word_list

def deleteIgnorewords(table):
    """
    Erstellt ein neues Dictionary, welches nur die Eintraege enthaelt, 
    deren Schluessel nicht in der Liste words_ignore enthalten sind.

    Parameters:
        table (dict): Ein Dictionary, das die Woerter als keys und ihre Haeufigkeit als Values enthaelt.

    Returns:
        dict: Das Dictionary ohne die Eintraege, deren Schluessel in words_ignore enthalten sind.
    """
    table = {key: value for key, value in table.items() if key not in words_ignore}
    return table

def loadMail(dateiname):
    """
    E-Mail laden und in Einzelteile zerlegen.

    Parameters:
        dateiname (str): Der Dateiname der E-Mail, die geladen werden soll.

    Returns:
        dict: Ein Dictionary, welches die Einzelteile der E-Mail enthaelt.
    """
    mailTable = {'mail': open(dateiname, 'r').read()}
    mailTable['header'] = mailTable['mail'][:mailTable['mail'].find('\n\n')]
    mailTable['body'] = mailTable['mail'][mailTable['mail'].find('\n\n'):]
    mailTable['headerlines'] = [replaceChars(e) for e in mailTable['header'].split("\n")]
    mailTable['from'] = [e[e.find(':')+2:] for e in mailTable['headerlines'] if e.find('Von:') == 0][0]
    mailTable['to'] = [e[e.find(':')+2:] for e in mailTable['headerlines'] if e.find('An:') == 0][0]
    mailTable['betreff'] = [e[e.find(':')+2:] for e in mailTable['headerlines'] if e.find('Betreff:') == 0][0]
    mailTable['betreffWordList'] = deleteIgnorewords(wordList(mailTable['betreff']))
    mailTable['bodyWordList'] = deleteIgnorewords(wordList(replaceChars(mailTable['body'])))
    return mailTable

def loadMailDirectory(pfad):
    """
    E-Mails aus Verzeichnis laden.

    Parameters:
        dateiname (str): Der Pfad des Verzeichnisses, aus dem die E-Mails geladen werden sollen.

    Returns:
        dict: Ein Dictionary, welches alle Emails aus dem Verzeichnis enthaelt.
    """
    mails = {}
    directory = [f for f in os.listdir(pfad) if os.path.isfile(os.path.join(pfad, f))]
    print(f"Maildirectory {pfad} laden:\n{directory}\n")
    print(f"Maildirectory {pfad} laden:\n{directory}\n", file=logfile)
    for fn in directory:
        mails[fn] = loadMail(os.path.join(pfad, fn))
    return mails

#----------------------------------------------
# Whitelist laden
whitelist = [line for line in open(filename_whitelist).read().split("\n") if line != ""]
print(f"Whitelist:\n{whitelist}\n")
print(f"Whitelist:\n{whitelist}\n", file=logfile)

# Blacklist laden
blacklist = [line for line in open(filename_blacklist).read().split("\n") if line != ""]
print(f"Blacklist:\n{blacklist}\n")
print(f"Blacklist:\n{blacklist}\n", file=logfile)

#----------------------------------------------
# Bewertungstabellen fuer Naive Bayes erstellen und in eigene Datei protokollieren

def updateNaiveBayes(word, anz_sp=None, anz_no=None):    
    """
    Aktualisiert die Naive-Bayes-Worttabelle mit neuen Vorkommen eines Wortes..

    Parameters:
        word (str): Das Wort, das aktualisiert werden soll.
        anz_sp (int, optional): Die Anzahl der Vorkommen des Wortes in Spam-Mails. Standardwert ist None.
        anz_no (int, optional): Die Anzahl der Vorkommen des Wortes in Nicht-Spam-Mails. Standardwert ist None.
    """
    if word == "" or word.isnumeric():
        return
    if word not in nb_wordtable:
        nb_wordtable[word] = {"spamMails": 0, "spamWords": 0, "noSpamMails": 0, "noSpamWords": 0}
    if anz_sp:
        nb_wordtable[word]["spamMails"] += 1
        nb_wordtable[word]["spamWords"] += anz_sp
    if anz_no:
        nb_wordtable[word]["noSpamMails"] += 1
        nb_wordtable[word]["noSpamWords"] += anz_no

# Spam-Mails laden und Worttabelle aktualisieren
spammails = loadMailDirectory(pfad = dir_root + dir_spam)
for m in spammails:
    for e in spammails[m]['betreffWordList']:
        updateNaiveBayes(e, anz_sp = spammails[m]['betreffWordList'][e])
    for e in spammails[m]['bodyWordList']:
        updateNaiveBayes(e, anz_sp = spammails[m]['bodyWordList'][e])

# Nicht-Spam-Mails laden und Worttabelle aktualisieren
nospammails = loadMailDirectory(pfad = dir_root + dir_nospam)
for m in nospammails:
    for e in nospammails[m]['betreffWordList']:
        updateNaiveBayes(e, anz_no = nospammails[m]['betreffWordList'][e])
    for e in nospammails[m]['bodyWordList']:
        updateNaiveBayes(e, anz_no = nospammails[m]['bodyWordList'][e])

def calcProbability(word, context, aContext):
    """
    Berechnet die Wahrscheinlichkeit eines Wortes basierend auf der Naive-Bayes-Worttabelle.

    Parameters:
        word (str): Das Wort, fuer das die Wahrscheinlichkeit berechnet werden soll.
        text (str): Der Kontext, fuer den die Haeufigkeit des Wortes berechnet wird (z.B. 'spamWords').
        n (str): Der alternative Kontext, fuer den die Haeufigkeit des Wortes berechnet wird (z.B. 'noSpamWords').

    Returns:
        float: Die berechnete Wahrscheinlichkeit, dass das Wort im angegebenen Kontext auftritt.
    """
    return float(nb_wordtable[word][context]) / (nb_wordtable[word][context] + nb_wordtable[word][aContext])

for word in nb_wordtable:
    nb_wordtable[word]["mail_probability"] = calcProbability(word, "spamMails", "noSpamMails")
    nb_wordtable[word]["words_probability"] = calcProbability(word, "spamWords", "noSpamWords")

# Naive Bayes Worttabelle in Datei schreiben
with open(dir_results + filename_nbwordtable, "w") as wtf:
    for e in sorted(nb_wordtable.keys()):
        print(e, ":", nb_wordtable[e], file = wtf)
    wtf.close()
print(f"Naive-bayes Worttabelle ({dir_results + filename_nbwordtable}): {len(nb_wordtable)} Eintraege\n")
print(f"Naive-bayes Worttabelle ({dir_results + filename_nbwordtable}): {len(nb_wordtable)} Eintraege\n", file = logfile)

#----------------------------------------------
# Mail-Input laden, bewerten, ablegen; Klassifikation: WhiteList, BlackList, NoSpam, undetermined, Spam

inputMails = loadMailDirectory(pfad = dir_root + dir_input)
print(f"Mails bearbeiten:")
print(f"Mails bearbeiten:", file = logfile)

for e in inputMails:
    mailWordTable = {}
    for word in inputMails[e]['betreffWordList']:
        if word in nb_wordtable:
            mailWordTable[word] = nb_wordtable[word]
    for word in inputMails[e]['bodyWordList']:
        if word in nb_wordtable:
            mailWordTable[word] = nb_wordtable[word]
    inputMails[e]["mail_probability"] = mean([mailWordTable[word]["mail_probability"] for word in mailWordTable])
    inputMails[e]["words_probability"] = mean([mailWordTable[word]["words_probability"] for word in mailWordTable])
    inputMails[e]["spam_probability"] = mean([inputMails[e]["mail_probability"], inputMails[e]["words_probability"]])
    inputMails[e]["spam_class"] = ""

    # Email-Klassifizierung gemaeß Prioritaeten
    def whitelist_check():
        if [word for word in whitelist if word in inputMails[e]['header']]:
            inputMails[e]["spam_class"] = "whitelist"

    def blacklist_check():
        if [word for word in blacklist if word in inputMails[e]['header']]:
            inputMails[e]["spam_class"] = "blacklist"

    def naive_bayes_classifier():
        nbsc = [i for i in nb_spam_class if (inputMails[e]["spam_probability"] <= nb_spam_class[i][0]
                                             and inputMails[e]["spam_probability"] >= nb_spam_class[i][1])][0]
        if nbsc != "undetermined" or inputMails[e]["spam_class"] == "":
            inputMails[e]["spam_class"] = nbsc

    spam_classifier = {"whitelist": whitelist_check,
                       "blacklist": blacklist_check,
                       "naive_bayes": naive_bayes_classifier}

    for po in priorityorder[::-1]:
        spam_classifier[po]()

    # Klassifizierte E-Mail in output-Verzeichnis ablegen
    with open(dir_root + dir_output + "[" + inputMails[e]["spam_class"] + "] " + e, 'w') as f:
        f.write(inputMails[e]['header'] +
                "\nXSpam: {}".format(inputMails[e]["spam_class"]) +
                "\nXSpamProbability: {}".format(inputMails[e]["spam_probability"]) +
                inputMails[e]['body']
                )
        f.close()
        print(f"[{inputMails[e]['spam_class']}] {e}")
        print(f"[{inputMails[e]['spam_class']}] {e}", file = logfile)

#----------------------------------------------
# Bewertungsuebersicht in CSV-Datei ausgeben
with open(dir_root + dir_results + filename_csv, 'w') as f:
    print(';'.join(['filename'] + CSV_Tags), file = f)

    for e in inputMails:
        CSV_Data = '"' + '";"'.join([str(inputMails[e][t]) for t in CSV_Tags]) + '"'
        print(f'"{e}";{CSV_Data}', file = f)
    f.close()

#----------------------------------------------
# Bewertungsuebersicht in Textdatei ausgeben
with open(dir_root + dir_results + filename_results, 'w') as f:
    print(logHeader +
          f"   Prioritaet: {priorityorder}\n" +
          f"   Naive Bayes Spam Klasse: {nb_spam_class}\n" +
          "=" * 80,
          file = f)
    for e in inputMails:
        print(f"\n{inputMails[e]['header']}\n------------\n",
              f"  mailProbability:  {inputMails[e]['mail_probability']}\n",
              f"  wordsProbability: {inputMails[e]['words_probability']}\n",
              f"  spamProbability:  {inputMails[e]['spam_probability']}\n",
              f"  spamClass:        {inputMails[e]['spam_class']}\n" + "=" * 80,
              file = f)
    f.close()

print(f"Bearbeitete Mails {len(inputMails)}\n")
print(f"Bearbeitete Mails {len(inputMails)}\n", file = logfile)

#----------------------------------------------
# Streams schliessen
logfile.close()