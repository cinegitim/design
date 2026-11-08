# Work/Codex etkinleştirme — uzak OpenCode ayrı kurulabilir

Bu kontrol listesi özel Codex Cloud render ortamını etkinleştirmek içindir.
ChatGPT Work'te bağlı GitHub araçlarıyla repo okuma, branch/PR hazırlama ve
salt okunur denetim ayrı bir yoldur; [Work adapter](../work/README.md) ve
[2026-10-10 gözlem kaydı](../work/2026-10-10-audit.md) ile ilerleyin.
Native Work image aracı, yerel OpenCode ChatGPT credential adapter'ından ayrıdır;
bu liste ikisini etkinleştirmiş veya kotasını doğrulamış sayılmaz.

Repo dosyaları bir Codex Cloud ortamını kendiliğinden oluşturmaz. Bu oturumun
ChatGPT hesabına/Cloud ayarlarına yönetim erişimi yoktur. Aşağıdaki adımlar
hesap sahibi tarafından yapılır; ortamda başarılı test olmadan “buluta geçildi” denmez.

Bu checklist Work/Codex içindir; **OpenCode üretim yapmak için Codex'in açılmasını
beklemek zorunda değildir**. Seçilen OpenCode modeli için
[EPHEMERAL.md](../work/EPHEMERAL.md): geçici yerel üretim, doğrulama sonrası temizlik;
ücretli uzak sunucu gerekmez. Uzak execution host yalnız isteğe bağlı alternatiftir.
Her iki ortam aynı GitHub kaynaklarına ve exact-head checked-merge kurallarına bağlıdır.

1. ChatGPT Work/Codex'te **Work in → Cloud → Create environment** seçin.
2. GitHub bağlantısına `cinegitim/design` erişimi verin; güncel `main`i kullanın.
3. Python **3.12**, Node **22** ve Linux ortamı isteyin. Install script:
   `bash studio/cloud/setup.sh`. Start talimatı: `AGENTS.md` ve
   `.agents/skills/cloud-delivery/SKILL.md`i oku; `bash studio/cloud/doctor.sh` çalıştır.
4. Paket indirmeleri için internet izinlerini açın. PyPI, npm, GitHub ve
   Playwright Chromium indirme alan adlarına erişimi kurulum çıktısında doğrulayın.
   Başarısız indirmede TLS doğrulamasını kapatmayın; izin/CA zincirini düzeltin.
5. Test başarılıysa ortamı **Publish** edin. Yeni bir task açıp aşağıdaki promptu verin.
6. **Görsel üretim bağlantısı ayrı:** mevcut `.opencode/plugins/` doğrudan Codex
   connector'ı değildir. Bu göçte API anahtarı alınmıyor veya `codex-action` kurulumu
   yapılmıyor. Pollinations/ChatGPT raster bağlantısı yoksa bunu raporlayın; API'ye
   sessiz geçiş yapmayın. Mevcut orijinallerle HTML/SVG/PNG üretimi yapılabilir.

## İlk gerçek bulut testi için prompt

> Bu repoda AGENTS.md ve cloud-delivery skill'ini oku. Cloud doctor ve bağımsız
> audit'i çalıştır. Yeni görsel üretme; onaylı logo dosyalarını değiştirme.
> launch-creative-02 tarifini geçici bir çalışma kopyasında çalıştır; mevcut teslimi
> üzerine yazma. Araç sürümlerini, font yüklemesini, beş PNG ölçüsünü ve audit
> sonucunu raporla. Linux/Chromium çıktısını mevcut macOS teslimiyle gerçek görsel
> incelemeyle karşılaştır; byte-identical olduğunu varsayma. Önemli test kanıtlarını
> repoya ekleyen bir PR aç; PUBLISHING.md'deki exact-head zorunlu denetimler ve teknik
> düzeltmelerden sonra checked merge yap, yayını doğrula. Kullanılabilir görsel araçlarını açıkla.

Bu test PR'ı ve insan incelemesi tamamlandığında cutover kaydı eklenir. O zamana
kadar yerel klasörler silinmez. Bulut VM önbelleği, Actions artifact'i veya sohbet
geçmişi GitHub'daki kalıcı kaynakların yerine geçmez.

Kaynaklar (kurulum sırasında kontrol edildi):
- https://learn.chatgpt.com/docs/environments/cloud-environments
- https://developers.openai.com/codex/skills
