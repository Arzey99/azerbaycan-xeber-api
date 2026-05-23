import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
import ssl
import email.utils # Tarihleri sıralamak için yeni eklendi

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

KAYNAKLAR = [
    {"ad": "BBC Azərbaycanca", "url": "https://feeds.bbci.co.uk/azeri/rss.xml"},
    {"ad": "Report.az", "url": "https://report.az/rss/"},
    {"ad": "Oxu.az", "url": "https://oxu.az/rss"}
]

tum_haberler = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
    'Accept-Language': 'az,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}

for kaynak in KAYNAKLAR:
    try:
        istek = urllib.request.Request(kaynak["url"], headers=headers)
        yanit = urllib.request.urlopen(istek, context=ctx, timeout=10)
        veri = yanit.read()
        
        root = ET.fromstring(veri)
        
        for item in root.findall('.//item')[:10]:
            baslik = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            
            gercek_tarih = item.find('pubDate').text if item.find('pubDate') is not None else str(datetime.datetime.now())
            
            resim_url = ""
            if item.find('enclosure') is not None:
                resim_url = item.find('enclosure').get('url', '')
                
            tum_haberler.append({
                "baslik": baslik,
                "link": link,
                "resim": resim_url,
                "kaynak": kaynak["ad"],
                "zaman": gercek_tarih 
            })
    except Exception as e:
        print(f"Hata ({kaynak['ad']}): {e}")

if not tum_haberler:
    tum_haberler.append({
        "baslik": "Sistem Hazır: Haberler Yükleniyor...",
        "link": "https://google.com",
        "resim": "https://via.placeholder.com/500x300.png?text=Haber+Bekleniyor",
        "kaynak": "Sistem Mesajı",
        "zaman": str(datetime.datetime.now())
    })

# --- HABERLERİ ZAMANA GÖRE SIRALAMA BÖLÜMÜ ---
def tarih_cevir(haber):
    try:
        # Metin halindeki RSS tarihini bilgisayarın anlayacağı zamana çevirir
        return email.utils.parsedate_to_datetime(haber['zaman'])
    except:
        return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

# Listeyi en yeni tarihten en eskiye (reverse=True) doğru sıralıyoruz
tum_haberler.sort(key=tarih_cevir, reverse=True)
# ---------------------------------------------

with open("haberler.json", "w", encoding="utf-8") as dosya:
    json.dump(tum_haberler, dosya, ensure_ascii=False, indent=4)