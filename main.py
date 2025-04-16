import pandas as pd
import numpy as np
import random
import genanki as gk
import code
from openai import OpenAI as ai
from data.apikey import API_KEY
from datetime import datetime as dt

def deepseek_gloss(words, batch_size = 40):
    cl = ai(api_key=API_KEY, base_url="https://api.deepseek.com")
    latin = []

    for i in range(0, len(words), batch_size):
        print("\r{}/{} items done...".format(i,len(words)),end="",flush=True)
        start = i
        end = i + batch_size if (i + batch_size) < len(words) else len(words)
        messages = [{"role" : "user", "content" : "I am going to give you a list of ancient greek words. I want you to return that word translated into latin with the long vowels marked by macrons. If a tense doesn't exist, say the aorist, use the closest equivalent in latin and mark it as such, for example (aorist, middle, etc). Greek loan words into latin should never be used unless a native latin equivalent doesn't exist. The words should be separated by a semi-colon. do not include any other information than what is asked. This list will be parsed programatically. Thanks:\n {}".format(words.iloc[start:end])}]

        response = cl.chat.completions.create(model="deepseek-chat", messages=messages)
        latin += response.choices[0].message.content.split(';')

    #code.interact(local=locals())
    return pd.Series(latin).astype(str).str.strip()

def deepseek_verb_conjugate(words, batch_size = 5):
    cl = ai(api_key=API_KEY, base_url="https://api.deepseek.com")
    verb = []

    for i in range(0, len(words), batch_size):
        print("\r{}/{} items done...".format(i,len(words)),end="",flush=True)
        start = i
        end = i + batch_size if (i + batch_size) < len(words) else len(words)
        messages = [{"role" : "user", "content" : "I am going to give you a list of ancient greek verbs. For each word in the list, randomly choose either a conjugation or participle and write that in a list. Each entry should only contain the conjugated verb or participle. Each list entry is separated by a ; . There must at least be one participle. The response will be parsed, so do not add anything else. Limit the conjugations to the following: {} The verbs are: {}".format("present indicative active and middle voice, the active present infinitive and the participles", words.iloc[start:end])}]

        response = cl.chat.completions.create(model="deepseek-chat", messages=messages)
        v = response.choices[0].message.content

        verb += v.split(";")

        if len(v.split(";")) > batch_size:
            code.interact(local=locals())

        #code.interact(local=locals())

    #code.interact(local=locals())
    return pd.Series(verb).astype(str).str.strip()


def deepseek_verb_parse(words, batch_size = 5):
    cl = ai(api_key=API_KEY, base_url="https://api.deepseek.com")
    conj = []

    for i in range(0, len(words), batch_size):
        print("\r{}/{} items done...".format(i,len(words)),end="",flush=True)
        start = i
        end = i + batch_size if (i + batch_size) < len(words) else len(words)

        messages = [{"role" : "user", "content" : "I am going to give you a list of ancient greek verbs. Parse each verb, listing the person, number, tense, etc. Do not include the original verb. Each entry is separated by a ;  and nothing more. The response must be on a single line, no '\n' or numbering. The response will be parsed, so do not add anything else. The verbs are: {}".format(words)}]

        response1 = cl.chat.completions.create(model="deepseek-chat", messages=messages)
        c = response1.choices[0].message.content

        conj += c.split(";")

        #code.interact(local=locals())

    #code.interact(local=locals())
    return pd.Series(conj).astype(str).str.strip()

def deepseek_noun_parse(words, batch_size = 5):
    cl = ai(api_key=API_KEY, base_url="https://api.deepseek.com")
    noun = []

    for i in range(0, len(words), batch_size):
        print("\r{}/{} items done...".format(i,len(words)),end="",flush=True)
        start = i
        end = i + batch_size if (i + batch_size) < len(words) else len(words)

        messages = [{"role" : "user", "content" : "I am going to give you a list of ancient greek nouns. Parse each noun, listing the person, case etc. Do not include the original noun. Each entry is separated by a ;  and nothing more. The response must be on a single line, no '\n' or numbering. The response will be parsed, so do not add anything else. The verbs are: {}".format(words)}]

        response1 = cl.chat.completions.create(model="deepseek-chat", messages=messages)
        n = response1.choices[0].message.content

        noun += n.split(";")

        #code.interact(local=locals())

    #code.interact(local=locals())
    return pd.Series(noun).astype(str).str.strip()

def deepseek_noun_decline(words, batch_size = 5):
    cl = ai(api_key=API_KEY, base_url="https://api.deepseek.com")
    noun = []

    for i in range(0, len(words), batch_size):
        print("\r{}/{} items done...".format(i,len(words)),end="",flush=True)
        start = i
        end = i + batch_size if (i + batch_size) < len(words) else len(words)
        messages = [{"role" : "user", "content" : "I am going to give you a list of ancient greek nouns. For each word in the list, decline it for a random case and number and write the declined noun in a list. Each entry should only contain the declined noun. Each list entry is separated by a ; and on a single line. This response will be parsed, so do not include extraneous details. The nouns are: {}".format(words.iloc[start:end])}]

        response = cl.chat.completions.create(model="deepseek-chat", messages=messages)
        n = response.choices[0].message.content

        noun += n.split(";")

    #code.interact(local=locals())
    return pd.Series(noun).astype(str).str.strip()

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


def gen_final_csv():
    df = get_df()
    
    verbs = df[df["Part of Speech"] == "vērbum"]
    nouns = df[df["Part of Speech"] == "nōmen"]
    others = df[~(df["Part of Speech"] == "nōmen" ) & ~(df["Part of Speech"] == "vērbum")]


    verbs_sample = verbs.sample(n=20,random_state=random.randint(0,19))
    nouns_sample = nouns.sample(n=20,random_state=random.randint(0,19))

    v = deepseek_verb_conjugate(verbs_sample["Lexical Form"])
    n = deepseek_noun_decline(nouns_sample["Lexical Form"])

    all_verbs = pd.concat([verbs["Lexical Form"],v], ignore_index=True)
    all_nouns = pd.concat([nouns["Lexical Form"],n], ignore_index=True)

    parsed_v = deepseek_verb_parse(all_verbs)
    parsed_n = deepseek_verb_parse(all_nouns)
    parsed_o = pd.Series([np.nan] * len(others))

    # Greek Type Chapter Parsed Latin
    greek = pd.concat([others["Lexical Form"],all_verbs,all_nouns], ignore_index=True)
    chapters = pd.concat([others["Chapter(s)"],verbs["Chapter(s)"],verbs_sample["Chapter(s)"],nouns["Chapter(s)"],nouns_sample["Chapter(s)"]], ignore_index=True)
    types = pd.concat([others["Part of Speech"],verbs["Part of Speech"],verbs_sample["Part of Speech"],nouns["Part of Speech"],nouns_sample["Part of Speech"]], ignore_index=True)
    parsed = pd.concat([parsed_o,parsed_v,parsed_n],ignore_index=True)
    latin = deepseek_gloss(greek)

    out_df = pd.DataFrame({"Greek" : greek, "Parsed" : parsed, "Type" : types, "Latin" : latin, "Chapters" : chapters})
    out_df.to_csv("data/AG_Final_{}.csv".format(dt.now().strftime("%Y_%m_%d")),index=False)
    return 

def get_final_df(file_path):
    df = pd.read_csv(file_path)
    df["Gloss"] = df["Gloss"].astype(str).str.replace(",",";")
    return df

def main():

    gen_final_csv()
    return 

    df = get_final_df("")

    #TODO: make the cards


if __name__ == "__main__":
    main()
