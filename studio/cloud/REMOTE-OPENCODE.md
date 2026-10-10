# OpenCode + Work/Codex — proje bilgisayara indirilmeden çalışma

## Kısa cevap

**GitHub repo'su tek başına bir çalışma/üretim sunucusu değildir.** Standart
OpenCode tasarım, font yükleme, render, görsel işleme ve ZIP üretimi için bir
execution host ve çalışma dosyalarına ihtiyaç duyar. Bu host uzakta çalıştırılırsa
**kullanıcının bilgisayarında proje checkout'u tutmadan** tasarım yapılabilir.

Hedef mimari:

```text
Kullanıcının arayüzü ──> Uzak OpenCode sunucusu + izole çalışma alanı ──┐
                                                                  ├─> GitHub branch/PR → audit
ChatGPT Work/Codex ──> Kendi bulut çalışma alanı ────────────────────┘
                           → İnsan kabulü / açık PR merge izni → Pages
```

İki executor da üretim yapabilir. Biri diğerinin oturumunu, araçlarını, modelini
veya credential'larını miras almaz; GitHub'daki talimatları, kaynakları ve kaydedilmiş
kararları paylaşırlar. Aynı dosyayı aynı anda düzenlemeden önce PR/head kontrolü
gerekir. Her görev için ayrı checkout ve branch uzak host üzerinde oluşturulur.

## Checkout gerektirmeyen sınırlı yol

GitHub API/connector ile dosya okumak, basit SVG/HTML/metin dosyası yazmak, commit,
branch ve PR oluşturmak proje checkout'u olmadan yapılabilir. API erişimi kendi
başına Python, fontlar, Chromium veya raster/ZIP üretimi sağlamaz. Connector'ın
gerçek yeteneklerini test etmeden “tam tasarım doğrudan repoda çalışıyor” demeyin.
API modunda base SHA, açık branch hedefi ve expected-head kontrolü gerekir;
default branch'e örtük yazım yoktur. Tam toolchain için uzak workspace önerilir.

## Resmî V2 belgeleri neyi doğruluyor?

OpenCode V2 bir istemci/sunucu mimarisidir. Sunucu oturumları, entegrasyonları,
izinleri ve tool execution'ı yönetir. CLI belirli bir sunucuya bağlanabilir:

```sh
opencode --server <erişimi-korumalı-uzak-sunucu-URL>
```

Bu bir **bağlantı örneği**, kurulmuş bir endpoint değildir. Desktop uygulamasının
bu cihazda uzak sunucuya nasıl bağlanacağı ayrıca doğrulanmalıdır; CLI desteğini
desktop'ta otomatik bağlantı varmış gibi sunmayın. JS client'ın `baseUrl` ve header
desteği de resmî belgede vardır. Remote session'ın directory'si uzak sunucunun
filesystem'ini ifade eder, kullanıcının yerel klasörünü değil.

Kontrol edilen resmî V2 kaynaklar (2026-10-10):
- https://opencode.ai/v2/docs/cli — `--server`, service'in tool execution sahipliği.
- https://opencode.ai/v2/docs/build/client — uzaktaki HTTP API'ye client, `baseUrl`, headers.

## Uzak OpenCode için kabul checklist'i

1. Uzak Linux VM/container veya uygun hosted workspace hazırlayın. Bu görev
   herhangi bir ücretli VM/Codespaces hesabı oluşturmaz veya maliyet onayı varsaymaz.
2. OpenCode sunucusunu ve `.opencode/` adapterlarını uzakta kurun; repo ve her task'ın
   checkout'u uzakta dursun. Pinned Linux render tarifi gerektiğinde kullanılabilir.
3. Uzak endpoint'i kimlik doğrulaması ve dar erişimle koruyun: özel ağ/SSH tunnel
   veya güvenli HTTPS erişim sınırı. Tool server'ı auth olmadan internete açmayın.
   Credentials cloud secret alanında; tokenlar/oturum profilleri repoya yazılmaz.
4. İstemciyi uzaktaki sunucuya bağlayın. Tek bir yerel render/helper plugin'inin
   çalışması bile “tüm tool execution uzak” iddiasını bozabilir: shell, read/write,
   preview/export ve image connector'ın host'unu ayrı ayrı doğrulayın.
5. Sunucu-side `pwd`, platform ve task branch/commit'ini kaydedin; uzak test
   çıktısını kanıt olarak PR'a ekleyin, özel IP/yerel kullanıcı yolu/secret yayımlamayın.
6. Mevcut orijinallerle izole test üretimi yapın; yeni görsel model çağrısı yok.
   Hash, boyut, font ve gerçek görsel inceleme kontrolleri, GitHub audit'i ve açık PR.
   Eski teslimi üzerine yazmayın veya yeni logo onayı saymayın.
7. Kullanıcının makinesinde proje clone/export tutmadan bunun çalıştığını ve
   önemli sonuçların GitHub'a kaydedildiğini doğrulayın. Bundan sonra eski yerel
   checkout'ları kaldırmak **ayrı, açık izin** gerektirir.

## Önemli sınırlar / güncel durum

- Bu PR yalnız talimat/dokümantasyon uyumunu düzeltir; uzak OpenCode host'u
  oluşturmaz, bu mevcut yerel oturumu buluta taşımaz ve tool bağlantısını değiştirmez.
- Work/Codex'in cloud kurulumu ve native görsel araçları da gerçek oturumda test
  edilmeden hazır sayılmaz. Repo skill'leri bağlantı/credential kurulumu değildir.
- “Proje checkout'u yok” ile “bilgisayarda hiçbir veri/cache yazılmıyor” aynı şey
  değildir. Yerel istemci oturum, auth veya UI cache'i tutabilir; görsel önizleme
  görüntü verisinin istemciye ulaşmasını gerektirir. Tam sıfır-local-byte garantisi
  bu mimariyle verilmez. Hedef: proje çalışma dosyalarının ve üretimin uzakta olması.
- GitHub Actions aynı şekilde audit-only kalır. Bu altyapı/guide PR'ı da açık merge
  izni bekler; branch'teki dosyalar Pages'te canlıymış gibi sunulmaz.
