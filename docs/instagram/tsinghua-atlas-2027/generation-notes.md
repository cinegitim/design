# Üretim notları

- **İş:** Asya’da Eğitim için Tsinghua Üniversitesi hakkında yedi slaytlık 2027 lisans başvuru carousel’ı.
- **Kimlik:** Asya’da Eğitim approved identity metadata + canonical lockups; tam `brand-system.md` yok, uygulama kuralları yalnız bu kampanya için.
- **Görsel üretimi:** Bu oturumda görüntü üretme aracı yoktu; AI görsel üretimi ve AI öğrencisi/temsili fotoğraf kullanılmadı. Commons kaynaklı iki gerçek Tsinghua kampüs fotoğrafı, lisans şartlarına ve atıflara uygun biçimde kırpıldı.
- **Metin üretimi:** Türkçe editorial copy; resmî program adları İngilizce bırakıldı. Sıralama, ücret, burs, program, takvim claims `sources-and-verification.md` içinde birincil kaynaklara bağlandı.
- **Tasarım/çıktı:** Editable slide HTML’leri, CSS, Jost VF, orijinal onaylı SVG lockup kopyaları; Chrome + Playwright render; tam 1080×1350 PNG’ler, SVG ile contact sheet ve mobil gezinme önizlemesi.
- **İterasyon:** İlk contact-sheet denetiminde kapak başlığı ile P-01 lockup yakınlığı ve kapak alt satır çakışması düzeltildi. Kapanış slaytında büyük P-01 yerine uygun boyuttaki D-04/dark seçildi. Ücret kartının kapsamı “seçili” olarak netleştirildi.
- **Sınır:** Tasarım sitesi review sayfası olarak sunuluyor; Tsinghua ile partnership/endorsement iddiası, Instagram yayını, canonical template/brand-system onayı yoktur. İnsan yaratıcı incelemesi bekleniyor.
- **Render ortamı notu:** Yerel Chrome + mevcut Playwright ile yedi PNG üretildi. Son tekrar temas sayfası ekran görüntüsü, görev diskinde boş alan 118 MB’a düştüğü için kesildi; contact sheet buna karşın `rsvg-convert` ile yerel PNG’lerden yeniden üretildi.
