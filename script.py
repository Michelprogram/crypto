#coding:utf-8
from bs4 import BeautifulSoup
from requests import get
from pymongo import MongoClient

#l = soup.find_all("span",class_="jsx-1338272632")
#Code html formater et encoder soup.prettify(formatter="html5",encoding="utf-8")))

class Crypto_Analyse:

    def __init__(self):
        requete = get("https://courscryptomonnaies.com/")
        code_html = requete.text
        self.soup = BeautifulSoup(code_html,"html.parser")
        self.final_list = []

    def run(self):
        name_crypto = self.soup.select("span.jsx-1338272632")
        cours_crypto = self.soup.find_all(attrs={"data-title":"Cours"})
        value_crypto = self.soup.select("td[data-title='Variation (24h)']")

        name_crypto = list(map(lambda current_span : current_span.contents[1],name_crypto))
        value_crypto = list(map(lambda value : float(value.get_text()[:-2]),value_crypto))
        cours_crypto = list(map(self.__text_cours,cours_crypto))


        self.__ecriture_final_list(name_crypto, cours_crypto, value_crypto)

    def __ecriture_final_list(self,liste1,liste2,liste3):
        for i in range(len(liste1)):
            tempo_dict = {
            "name":liste1[i],
            "cours":liste2[i],
            "value":liste3[i]
            }
            self.final_list.append(tempo_dict)

    def __text_cours(self,text):
        line = str(text.span.prettify("ascii"))
        if "\\'" in line:
            line = line.replace("\\'"," ")
            line = line[20:line.index("#")-2].split()
            return float("".join(line))
        return float (line[20:line.index("#")-2])

    def tri(self,cours=False,value=False):
        if cours:
            self.final_list = sorted(self.final_list, key=lambda cours : cours["cours"],reverse=True)
        elif value:
            self.final_list = sorted(self.final_list, key=lambda cours : cours["value"],reverse=True)
        else:
            pass

    def connexion_mongodb(self):
        client = MongoClient("mongodb+srv://ID/Crypto?retryWrites=true&w=majority")
        database = client["Crypto"]
        collection = database.cryptomonnaie

        for i in range(len(self.final_list)):
            database.cryptomonnaie.find_one_and_replace({"name":self.final_list[i]["name"]},self.final_list[i])


    def ecriture(self):
        with open("table.csv","w") as table_csv:
            table_csv.write("name,cours,value(%)\n")
            for i in range(len(self.final_list)):
                table_csv.write("{},{},{}\n".format(self.final_list[i]["name"],self.final_list[i]["cours"],self.final_list[i]["value"]))


crypto = Crypto_Analyse()
crypto.run()
crypto.tri(cours=True)

crypto.connexion_mongodb()
crypto.ecriture()




#database.cryptomonnaie.insert_one(pots).inserted_id
#print(database.cryptomonnaie.find_one({"id":"350"}))
