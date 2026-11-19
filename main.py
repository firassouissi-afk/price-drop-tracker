import sqlite3, re, smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup

conn=sqlite3.connect("prices.db")
conn.execute("CREATE TABLE IF NOT EXISTS prices(id INTEGER PRIMARY KEY, name TEXT, price REAL, url TEXT, seen TEXT)")

def track(name,url,selector):
    html=requests.get(url,timeout=20,headers={"User-Agent":"Mozilla/5.0"}).text
    soup=BeautifulSoup(html,"html.parser")
    el=soup.select_one(selector)
    if not el: raise RuntimeError("Price selector did not match")
    digits=re.findall(r"[\d,.]+",el.get_text(" ",strip=True))
    price=float(digits[-1].replace(",","").replace(" ","")) if digits else 0
    old=conn.execute("SELECT price FROM prices WHERE url=? ORDER BY id DESC LIMIT 1",(url,)).fetchone()
    conn.execute("INSERT INTO prices(name,price,url,seen) VALUES(?,?,?,datetime('now'))",(name,price,url))
    conn.commit()
    print(name,price,"drop" if old and price<old[0] else "")

if __name__=="__main__":
    import sys
    if len(sys.argv)!=4: raise SystemExit("Usage: python main.py 'Name' 'URL' '.price-selector'")
    track(sys.argv[1],sys.argv[2],sys.argv[3])
