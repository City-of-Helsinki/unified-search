import requests


def get_page(URL):
    r = requests.get(URL)
    print(r.status_code)

    data = r.json()
    # print(data["count"])
    # print(len(data["results"]))

    for elem in data["results"]:
        print(elem["name"]["fi"], elem["id"])

    return data["next"]


def fetch():
    URL = "https://api.hel.fi/servicemap/v2/department/"

    print("Hello from {}".format(__name__))

    next = get_page(URL)
    while next:
        next = get_page(next)

    return "Fetch completed by {}".format(__name__)


def delete():
    pass
