import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
import ssl

# Güvenlik sertifikası hatalarını aşmak için
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Daha güvenilir ve bot engeli olmayan RSS kaynakları
KAYNAKLAR = [
    {"ad": "BBC Azərbaycanca", "url": "https://feeds.bbci.co.uk/azeri/rss.xml"},
    {"ad": "Report.az", "url": "https://report.az/rss/"},
    {"ad": "Oxu.az", "url": "https://oxu.az/rss"}
]

tum_haberler = []

# Botun engellenmemesi için gerçek bir Chrome tarayıcı taklidi (Kamuflaj)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for kaynak in KAYNAKLAR:
    try:
        istek = urllib.request.Request(kaynak["url"], headers=headers)
        yanit = urllib.request.urlopen(istek, context=ctx, timeout=10)
        veri = yanit.read()
        
        root = ET.fromstring(veri)
        
        # Her siteden 10 haber alıyoruz
        for item in root.findall('.//item')[:10]:
            baslik = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            
            # Resim bulma mantığı
            resim_url = ""
            if item.find('enclosure') is not None:
                resim_url = item.find('enclosure').get('url', '')
                
            tum_haberler.append({
                "baslik": baslik,
                "link": link,
                "resim": resim_url,
                "kaynak": kaynak["ad"],
                "zaman": str(datetime.datetime.now())
            })
    except Exception as e:
        print(f"Hata ({kaynak['ad']}): {e}")

# Eğer siteler botu engellerse uygulaman çökmeyip bu mesajı göstersin (Güvenlik Ağı)
if not tum_haberler:
    tum_haberler.append({
        "baslik": "Sistem Hazır: Haberler Yükleniyor...",
        "link": "https://google.com",
        "resim": "https://via.placeholder.com/500x300.png?text=Haber+Bekleniyor",
        "kaynak": "Sistem Mesajı",
        "zaman": str(datetime.datetime.now())
    })

with open("haberler.json", "w", encoding="utf-8") as dosya:
    json.dump(tum_haberler, dosya, ensure_ascii=False, indent=4)
