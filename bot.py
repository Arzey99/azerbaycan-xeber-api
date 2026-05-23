import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime

# Azerbaycan haber sitelerinin standart RSS bağlantıları (Legal kaynaklar)
KAYNAKLAR = [
    {"ad": "Oxu.az", "url": "https://oxu.az/rss"},
    {"ad": "Qafqazinfo", "url": "https://qafqazinfo.az/rss"},
    {"ad": "Report.az", "url": "https://report.az/rss"}
]

tum_haberler = []

for kaynak in KAYNAKLAR:
    try:
        # Siteye bağlanıp veriyi çekiyoruz (Kendimizi normal bir tarayıcı gibi tanıtıyoruz)
        istek = urllib.request.Request(kaynak["url"], headers={'User-Agent': 'Mozilla/5.0'})
        yanit = urllib.request.urlopen(istek)
        veri = yanit.read()
        
        # XML (RSS) formatını okuyoruz
        root = ET.fromstring(veri)
        
        # Sunucuyu yormamak için her siteden en yeni 15 haberi alıyoruz
        for item in root.findall('.//item')[:15]:
            baslik = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            
            # Tarih ve resim etiketleri
            resim_url = ""
            enclosure = item.find('enclosure')
            if enclosure is not None:
                resim_url = enclosure.get('url', '')
                
            tum_haberler.append({
                "baslik": baslik,
                "link": link,
                "resim": resim_url,
                "kaynak": kaynak["ad"],
                "zaman": str(datetime.datetime.now())
            })
    except Exception as e:
        print(f"Hata oluştu ({kaynak['ad']}): {e}")

# Verileri JSON dosyasına kaydediyoruz (Mobil uygulamamızın ücretsiz veritabanı formatı)
with open("haberler.json", "w", encoding="utf-8") as dosya:
    json.dump(tum_haberler, dosya, ensure_ascii=False, indent=4)

print("Haberler başarıyla çekildi ve JSON dosyasına kaydedildi!")
