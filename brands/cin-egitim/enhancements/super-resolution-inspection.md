# Görsel denetim — süper çözünürlük adayı

Girişler gerçekten görsel olarak okundu: kilitli kaynak, iki model sonucu, tam işaret karşılaştırması ve pagoda detay karşılaştırması.

- Önceki LANCZOS + keskinleştirmeye göre pagoda çevresindeki renkli benekler, bulanık hale ve yüzey gürültüsü azaldı.
- Pagoda çatıları ve iç boşluklar daha belirgin; sonuç yalnız daha büyük piksel ızgarası değildir.
- Fırça halkasının ana açık yapısı, sağ üstteki ayrık darbeler, iki katlı pagoda ve alttaki mürekkep süpürmesi aynı görsel organizasyonu koruyor.
- İnce çizgiler/kenarlar tahmin edilmiştir; dokunun küçük bir kısmı yumuşamış, bazı kenarlara yerel model yorumu gelmiştir. **Birebir ayrıntı sadakati veya eksik detayın gerçekten geri kazanımı iddia edilmiyor.**
- `x4plus-anime` daha sert, düzleştirilmiş ve kabartma hissi veren kenarlar nedeniyle geçici test olarak bırakıldı. Genel `x4plus` daha az stilizasyon nedeniyle tercih edildi.
- Hedef kilidi değişmedi. SVG ve tipografi yok. Çıktı yalnız kullanıcının kalite değerlendirmesine sunulan raster adaydır.
