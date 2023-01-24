from urllib.request import urlopen
from bs4 import BeautifulSoup

def scrapeText(html, maxlen = 4000):
    sep = "___"
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text(separator=sep)

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    splittext = [j for j in [i.replace(sep, "").strip() for i in text.split(f"{sep}\n{sep}\n{sep}\n{sep}")] if j]
    for text in splittext:
        print("----------")
        print(text)
        print("----------")