import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
import ssl
import email.utils

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 5 Dev Kaynaklı Azerbaycan Haber Ağı
KAYNAKLAR = [
    {"ad": "BBC Azərbaycanca", "url": "https://feeds.bbci.co.uk/azeri/rss.xml"},
    {"ad": "Report.az", "url": "https://report.az/rss/"},
    {"ad": "APA", "url": "https://apa.az/rss"},
    {"ad": "Azərtac", "url": "https://azertag.az/rss"},
    {"ad": "Trend", "url": "https://az.trend.az/rss"}
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
            
            gercek_tarih = item.find('pubDate').text if item.find('pubDate') is not None else email.utils.format_datetime(datetime.datetime.now())
            
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

# Önce haberleri zamana göre kusursuzca sıralıyoruz
def tarih_cevir(haber):
    try:
        dt = email.utils.parsedate_to_datetime(haber['zaman'])
        return dt.timestamp()
    except:
        return 0.0

tum_haberler.sort(key=tarih_cevir, reverse=True)

# SAAT VE TARİH DÜZENLEME BÖLÜMÜ
# Sıralama bittikten sonra tarihleri telefon ekranında şık duracak şekilde formatlıyoruz
for haber in tum_haberler:
    try:
        dt = email.utils.parsedate_to_datetime(haber['zaman'])
        # Uygulamada "24.05.2026 | 14:30" şeklinde görünecek
        haber['zaman'] = dt.strftime("%d.%m.%Y | %H:%M")
    except:
        pass

with open("haberler.json", "w", encoding="utf-8") as dosya:
    json.dump(tum_haberler, dosya, ensure_ascii=False, indent=4)