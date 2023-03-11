import requests
import urllib.parse


baseurl = "https://api.nal.usda.gov/fdc/v1/foods/search"
api_key = "mfcL8X8cnQx2pEmcUIB2UcNCNgz2y6UtUS2f4Ibb"

def search_usda(query: str):
    requrl = baseurl + f'?api_key={api_key}&query={urllib.parse.quote(query)}&pageSize=1'
    resp = requests.get(requrl)
    respJSON = resp.json()
    print(respJSON['foods'])



if __name__ == "__main__":
    search_usda("pork sausage")