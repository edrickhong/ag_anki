import pandas as pd
import numpy as np
import ast
import random
import genanki as gk
import code
from openai import OpenAI as ai
from data.apikey import API_KEY
from datetime import datetime as dt


#cl = ai(api_key=API_KEY, base_url="https://api.deepseek.com")
cl = ai(api_key=API_KEY)

def to_batch_string(words):
    out = ""

    for i,w in enumerate(words):
        out += str(w).strip(";")

        if i != len(words) - 1:
            out += ";"


    return out

def deepseek_prompt(prompt, words, batch_size = 20):
    out = []
    i = 0
    attempts = 0

    #for i in range(0, len(words), batch_size):
    while i < len(words):


        if attempts == 5:
            print("\nbatch size {}\tn size {}\t message {}".format(batch_size,len(n),m))
            code.interact(local=locals())

        print("\r{}/{} items {} done...".format(i,len(words),"" if attempts == 0 else "(" + str(attempts) + ")"),flush=True)
        start = i
        end = i + batch_size if (i + batch_size) < len(words) else len(words)
        w = list(words.iloc[start:end])
        messages = [{"role" : "user", "content" : "Note the entries in the list I gave you is ; separated\n" + prompt.format(to_batch_string(w)) + "\n Do not terminate with a ;. Each entry in the list I gave you MUST ONLY have one corresponding entry in your response list, EVEN IF that entry contains multiple words"}]

        #response = cl.chat.completions.create(model="deepseek-chat", messages=messages)
        response = cl.chat.completions.create(model="gpt-4o", messages=messages)
        m = response.choices[0].message.content
        n = m.split(";")


        if len(n) > batch_size:
            attempts += 1
            continue

        out += n
        i += batch_size
        attempts = 0

    print("")

    return pd.Series(out).astype(str).str.strip()


#does some formatting and translates Gloss to Latin
def get_df():
    mapping = {
            "ῥῆμα": "vērbum",
            "ὄνομα": "nōmen",
            "ἀντωνυμία": "prōnōmen",
            "ἐπίθετον": "adiectīvum",
            "μόριον": "particula",
            "ἐπίρρημα": "adverbium",
            "πρόθεσις": "praepositio",
            "πρόθεσις": "praepositio",
            "σύνδεσμος": "coniunctio",
            "λόγος": "nōmen",
            "ἑρωτηματικὴ ἀντωνυμία": "prōnōmen interrogativum",
            "ἀόριστη ἀντωνυμία": "prōnōmen indefinitum",
            "αὐτοπαθὴ ἀντωνυμία": "prōnōmen reflexīvum",
            "ἐπιφώνημα": "interiectio",
            "ἐπιίθετον": "adiectīvum",
            "ἀντωνυμία": "prōnōmen",
            "ἀναφορικὴ ἀντωνυμία": "prōnōmen relativum",
            "σύνδεσμος": "coniunctio",
            "μετοχή": "participium",
            "ἀριθμητικόν": "numerālis",
            "ἐπίθετον - ὑπερθετικόν": "adiectīvum - superlativum",
            "conjunction": "coniunctio",
            "ἐπίρρημα": "adverbium"
            }

    df = pd.read_excel(pd.ExcelFile("./data/AG_0.xlsx"))
    df["Part of Speech"] = df["Part of Speech"].astype(str).map(mapping)
    df["Chapter(s)"] = df["Chapter(s)"].astype(str).str.replace(",",";")
    df["Chapter(s)"] = df["Chapter(s)"].map(lambda x : list(map(int, x.split(";"))))

    return df


prompts = {
        "gloss" : "I am going to give you a list of ancient greek words. I want you to return that word translated into latin with the long vowels marked by macrons. If a tense doesn't exist, say the aorist, use the closest equivalent in latin and mark it as such, for example (aorist, middle, etc). Greek loan words into latin should never be used unless a native latin equivalent doesn't exist. Your output for each word is considered an entry. The entries should be separated by a semi-colon. do not include any other information than what is asked. This list will be parsed programatically. Thanks:\n {}",


        "conjugate" : "I am going to give you a list of ancient greek verbs. For each word in the list, randomly choose either a conjugation or participle and write that in a list, which we call an entry. Each entry should only contain the conjugated verb or participle. Each list entry is separated by a ; . There must at least be one participle. The response will be parsed, so do not add anything else. Limit the conjugations to the following: present indicative active and middle voice, the active present infinitive and the participles. The verbs are: {}",


        "decline" : "I am going to give you a list of ancient greek nouns. For each word in the list, decline it for a random case and number and write the declined noun in a list, for which each of your responses is called an entry. Each entry should only contain the declined noun. Each list entry is separated by a ; and all of them are on the same line. This response will be parsed, so do not include extraneous details. The nouns are: {}",


        "verb-parse" : "I am going to give you a list of ancient greek verbs. Parse each verb, listing the person, number, tense, etc. All of these items are considered 1 entry, separated by a comma. Do not include the original verb. Each entry is separated by a ;  and nothing more. The response will be parsed, so do not add anything else. The verbs are: {}",


        "noun-parse" : "I am going to give you a list of ancient greek nouns. Parse each noun, listing the person, case etc. All of these items are considered one entry and are comma separated.Do not include the original noun. Each entry is separated by a ;  and nothing more. The response will be parsed, so do not add anything else. The verbs are: {}",


        }


def gen_final_csv():
    df = get_df()
    
    verbs = df[df["Part of Speech"] == "vērbum"]
    nouns = df[df["Part of Speech"] == "nōmen"]
    others = df[~(df["Part of Speech"] == "nōmen" ) & ~(df["Part of Speech"] == "vērbum")]



    verbs_sample = verbs.sample(n=20,random_state=random.randint(0,19))
    nouns_sample = nouns.sample(n=20,random_state=random.randint(0,19))

    print("Conjugating...")
    v = deepseek_prompt(prompts["conjugate"],verbs_sample["Lexical Form"])
    print("Declining...")
    n = deepseek_prompt(prompts["decline"],nouns_sample["Lexical Form"])

    all_verbs = pd.concat([verbs["Lexical Form"],v], ignore_index=True)
    all_nouns = pd.concat([nouns["Lexical Form"],n], ignore_index=True)

    print("Parsing verbs...")
    parsed_v = deepseek_prompt(prompts["verb-parse"],all_verbs)
    print("Parsing nouns...")
    parsed_n = deepseek_prompt(prompts["noun-parse"],all_nouns)
    parsed_o = pd.Series([np.nan] * len(others))

    # Greek Type Chapter Parsed Latin
    greek = pd.concat([others["Lexical Form"],all_verbs,all_nouns], ignore_index=True)
    chapters = pd.concat([others["Chapter(s)"],verbs["Chapter(s)"],verbs_sample["Chapter(s)"],nouns["Chapter(s)"],nouns_sample["Chapter(s)"]], ignore_index=True)
    types = pd.concat([others["Part of Speech"],verbs["Part of Speech"],verbs_sample["Part of Speech"],nouns["Part of Speech"],nouns_sample["Part of Speech"]], ignore_index=True)
    parsed = pd.concat([parsed_o,parsed_v,parsed_n],ignore_index=True)

    latin = deepseek_prompt(prompts["gloss"],greek,40)

    out_df = pd.DataFrame({"Greek" : greek, "Parsed" : parsed, "Type" : types, "Latin" : latin, "Chapters" : chapters})
    out_df.to_csv("data/AG_Final_{}.csv".format(dt.now().strftime("%Y_%m_%d")),index=False)

    #code.interact(local=locals())
    return 

def get_final_df(file_path):
    df = pd.read_csv(file_path)
    df["Latin"] = df["Latin"].astype(str).str.replace(",",";")
    df["Chapters"] = df["Chapters"].map(lambda x : ast.literal_eval(x))
    return df


def get_subdeck_chapter(df,model,title,start, end):
    deck = gk.Deck(random.randint(0,999999999),title)

    for i,r in df.iterrows():
        greek = r["Greek"]
        parsed = r["Parsed"]
        latin = r["Latin"]
        chapters = r["Chapters"]

        to_add = False

        for c in chapters:
            if c >=start and c <= end:
                to_add = True
                break

        if to_add == True:
            note = gk.Note(model= model, fields = [greek, latin])
            deck.add_note(note)

    return deck

def main():

    #gen_final_csv()
    #return 

    df = get_final_df("data/AG_Final_2025_04_17.csv")

    model = gk.Model(random.randint(0,99999999),"AG",fields=[{"name" : "Greek"}, {"name" : "Translation"}], templates=[{"name" : "Card 1", "qfmt" : "{{Greek}}", "afmt" : '{{FrontSide}}<hr id="answer">{{Translation}}'}])

    decks = []

    decks.append(get_subdeck_chapter(df,model,"Athenaze::I-X",1,10))


    gk.Package(decks).write_to_file("data/Athenaze.apkg")




if __name__ == "__main__":
    main()
