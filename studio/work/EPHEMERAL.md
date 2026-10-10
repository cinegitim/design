# Tek geçici alan — OpenCode + Work/Codex

**Seçilen model:** OpenCode bilgisayarda geçici üretir; Work/Codex kendi bulut
alanında üretir. Ücretli VM yok. Her host'ta bir ana geçici alan; her aktif iş için
küçük, izole bir alt alan ve yeni branch. Gerçek RAM disk değildir; klasör sayısı
token tasarrufu sağlamaz. Script rutin işlemleri ve uzun logları azaltır.

```text
OpenCode: geçici kök/tasks/iş-a ──────┐
                                    ├─ GitHub kaynak + branch/PR + kısa handoff
Codex: kendi geçici kökü/tasks/iş-b ──┘
       → exact SHA + bağımsız byte kontrolü + PR CI → yalnız iş alanını temizle
       → açık PR / insan incelemesi → ayrı merge izni → Pages
```

RAM veya sohbet hafızası paylaşılmaz. GitHub senkronizasyon/arşiv kaynağıdır;
talimatlar native görüntü araçlarını veya Codex hesabını kendiliğinden etkinleştirmez.

## Bir kez hazırlık

Python 3 + Git; tamamlamak için ayrıca GitHub CLI (`gh`) ve kullanıcının kendi
yetkilendirmesi gerekir. macOS/Linux desteklenir (`fcntl` kilidi); Windows yerel
desteklenmez. Kurulum yeni görsel üretmez, dependency install veya merge yapmaz.

Review edilen branch'teki script ile bir kez:

```sh
export BRAND_STUDIO_TEMP_ROOT="${TMPDIR:-/tmp}/brand-studio-ephemeral"
python3 studio/work/ephemeral.py init
# init, küçük bağımsız launcher'ı root/control/ içine kopyalar.
export BS="$BRAND_STUDIO_TEMP_ROOT/control/ephemeral.py"
```

Sonraki işlemler: `python3 "$BS" ...`. `--root /seçilen/geçici/alan` ile tek bir
özel kök seçilebilir. Alan mevcut ve doluysa manager onu sahiplenmez. Root özel
izinli (700) ve ownership marker'lıdır. Küçük launcher, task kayıtları ve hash
özetleri tutulur; proje kaynakları yalnız `tasks/` içinde bulunur. Bu küçük kontrol
dosyaları veya OpenCode'un global oturum/cache'leri için “sıfır yerel byte” iddiası yok.
Temp alan OS tarafından da silinebilir; bu yüzden çalışırken düzenli commit/push gerekir.
Kurulu control/ launcher, override verilmezse kendi kökünü kullanır. Scriptin yeni
sürümüne geçmek için task'lar duruyorken control/ kopyasını açıkça güncelleyin; init
eski launcher'ın üstüne sessizce yazmaz.

Codex kendi cloud workspace'inde aynı scripti kullanabilir. Mevcut platform checkout'u
manager tarafından silinmez; çalışma manager-owned ayrı clone'a alınır. Platformun
kendi checkout/cache saklama süresi onun politikasıdır, bu scriptin garantisi değildir.

## İş açma ve kaydetme

```sh
python3 "$BS" start yeni-is-20261010 --executor opencode \
  --paths studio .agents .opencode .github brands/asyada-egitim docs/instagram/launch-creative-02
# JSON'daki path'i OpenCode session directory / shell çalışma dizini olarak kullan.
```

Codex için `--executor codex`. `--paths` belirtilmezse tüm çalışma ağacı checkout
edilir. Belirtilirse cone sparse checkout: ilgili kaynaklar indirilir; eksik gerekli
dosyaları `git sparse-checkout add <directory>` ile ekleyin. Tam repo audit'i için
policy'nin gerektirdiği bütün dizinler checkout edilmiş olmalıdır. Başlangıç clone'u
shallow/partial'dır; son koruma kontrolü **tüm committed tree blob'larını** yeniden
fetch eder. Bu bant genişliği ve geçici disk kullanır; sıfır indirme değildir.

Her task bağımsız clone'dur; ortak bare repo/worktree cache'i kullanılmaz. Böylece
task silinince `.git` object store'u da silinir. Legacy worktree'leri kullanmak,
kaynakları eski ortak Git object store'unda bırakacağı için yeni modelin parçası değil.

Üretim sonrası:

1. Orijinalleri, editable source'ları, export'ları, tarif ve kısa handoff'u repo içine
   kaydedin. Hiçbir önemli dosya cache/runtime dizininde kalmasın.
2. Marka preflight/verifier, gerekli gerçek görsel inceleme ve file audit'i çalıştırın.
3. Yalnız gerekli dosyaları açıkça `git add <paths>` ve `git commit` ile kaydedin.
   Script otomatik `git add -A` yapmaz veya secret'ları güvenli ilan etmez.
4. `python3 "$BS" publish yeni-is-20261010` — yalnız temiz committed branch'i push eder.
   Network/conflict durumunda retry/force yok, dosyalar korunur.
5. `gh pr create --repo cinegitim/design --base main --head <JSON branch>`.
   PR'ın exact HEAD'inde `submitted-files` kontrolünün geçmesini bekleyin; açık bırakın.

## Güvenli tamamlamanın tek komutu

Önce diğer editörleri, build/preview süreçlerini durdurun. OpenCode oturumunu task
klasöründen **control/ veya başka güvenli alana taşıyın**, shell de task dışında olsun.
Manager kilidi script işlemlerini ayırır; başka editörleri kilitlemez. Aynı task'ta
aktif yazıcı varken cleanup çalıştırmak desteklenmez.

```sh
python3 "$BS" cleanup yeni-is-20261010 --pr 123       # dry-run; silmez
python3 "$BS" cleanup yeni-is-20261010 --pr 123 --apply
```

Bu explicit tamamlanma komutu, doğrulama sonrası temizliği otomatik yürütür; zamanlı
daemon/startup silmesi değildir. `--apply` için exact branch/SHA ile açık PR, `main`
hedefi ve passing `submitted-files` CI zorunludur. **Merge gerekmez ve yapılmaz.**

Kapı ayrıca: remote HEAD = local HEAD; bağımsız fetch + Git fsck; her blob SHA-256;
materialized dosyalarla byte/mode eşitliği; dirty/staged/untracked/**ignored** dosya
yok; stash/başka branch'te korunmamış commit/linked worktree/submodule/LFS yok.
Kontrol başarısızsa hiçbir task dosyası silinmez. LFS, submodule veya Release-only
özgün dosyalar için ek durable-object doğrulayıcı gerekir; mevcut script bunları
güvenli kabul etmez. Kontrol download'u kendi geçici verify dizininden temizlenir.

Dependency/cache istisnası isteğe bağlıdır:

```sh
python3 "$BS" publish yeni-is-20261010 --discard-runtime
python3 "$BS" cleanup yeni-is-20261010 --pr 123 --discard-runtime --apply
```

Yalnız Git tarafından ignored **`.venv`, `node_modules`, `.cache`,
`studio/cloud/node_modules`** dizinlerini açık izinle dışlar/siler. Varsayılan, bunların
içindeki ignored dosyaları da bloklar. Bu bayrak önemli orijinal/çıktıları bu dizinlerden
kurtarmaz; kullanmadan önce yalnız yeniden kurulabilir runtime olduklarını doğrulayın.
Başka ignored dosya (ör. `.env`, yeni PNG, yerel not) yine temizliği durdurur. Aynı
isimde tracked dosya varsa runtime istisnası reddedilir. Tüm-root `rm -rf`, `git clean`,
force push, branch silme, timer ve legacy cleanup yoktur. Dosya silme secure erase değildir.

## OpenCode'dan Codex'e devam

OpenCode PR'ı push edip kısa handoff'u commit eder. Kullanıcı Codex'e:

> PR #123'teki işe devam et. Handoff'u oku; aynı markanın approved kaynaklarıyla
> çalış. `--base publish/opencode-yeni-is-20261010 --executor codex` ile yeni task
> branch/clone aç. Değişiklikleri incele, yeni PR aç; eskisini ezme veya merge etme.

Codex GitHub'dan aynı bytes'ı alır, kendi yeni branch'ine yazar. Parent PR merge
edilmemişse yeni PR önceki değişiklikleri de içerir; PR body'ye dependency/supersession
yazılır. Overlapping PR'lar ayrı insan kararıyla çözülür; otomatik kapatma yok.

## Uygulama sınırı

Bu repository scripti, client/model/cache servislerine müdahale etmez. OpenCode'da
manuel “tamamla” çağrısını otomatik permission/plugin hook'una dönüştürmez. Codex
hesabında gerçek çalışma/handoff ayrıca test edilmelidir; yerel `--executor codex`
simülasyonu hesap aktivasyonu veya native görsel araç testi sayılmaz. Legacy dosyaları
kaldırmak bu görevde yetkilendirilmedi. Eski bir checkout'u yöneticiye kaydetmek yoktur.
