# Kalıcı yerel temel — değişmeyeni yeniden indirme

GitHub hâlâ ortak kaynak ve tarihçedir. Kullanıcının tercihi: **ortak talimatları
ve araç kaynaklarını lokalde sabitle; değişince kalibre et.** Marka arşivi lokalde
tutulmaz. Bu katman yürütmeyi buluta taşımaz veya sohbet hafızasını paylaşmaz.

## Ne kalır?

Varsayılan özel kök: `~/.local/share/brand-studio/baseline/` (izin 700).

- `owner.json`: tek repository/host ownership kaydı.
- `active.json`: main kaynak SHA'sı, seçilmiş dosyaların Git blob kimlikleri,
  SHA-256 hash'leri, dosya modları ve içerik-sürümü digest'i.
- `snapshots/<digest>/`: salt-okunur, sürümü kayıtlı ortak kaynak dosyaları.
- `ephemeral.py`: main'deki scriptin hash'i kayıtlı kalıcı launcher kopyası.

Seçim kodda sabittir: `AGENTS.md`, `README.md`, `.gitignore`, root OpenCode
JSON/JSONC ayarları; `.opencode/`, `.agents/`, `.github/`; `studio/work/`,
`studio/cloud/`, `studio/templates/`, `studio/references/`, `studio/workflow/`,
`studio/tools/` altındaki metin/kod dosyaları. Yalnız committed normal dosyalar.
JSON/lockfile/requirements **kaynakları** kalabilir; kurulu paketler kalmaz.
Marka sistemleri/logoları, `brands/`, `docs/` teslimleri, görseller, ZIP'ler,
fontlar, `.env`, private key'ler, cache/dependency klasörleri seçim dışındadır.
Bu filtre tam secret taraması değildir; kaynaklara secret commit etmek hâlâ yasaktır.

## Bir kez hazırla

Onaylı/güncel script ile geçici manager kökünü hazırlayın. OpenCode mevcut seçili
özel temp alanını kullanır; shell ortamının kalıcı olarak düzenlenmesi gerekmez:

```sh
export BRAND_STUDIO_TEMP_ROOT="${TMPDIR:-/tmp}/brand-studio-ephemeral"
python3 studio/work/ephemeral.py init
python3 studio/work/ephemeral.py calibrate
export BS="$HOME/.local/share/brand-studio/baseline/ephemeral.py"
```

`BRAND_STUDIO_BASELINE_ROOT` veya `--baseline-root` farklı **kalıcı** özel yolu
seçebilir. Baseline geçici manager kökü içine konamaz. Script başka repository
veya dolu/sahipsiz bir klasörü sahiplenmez. Global OpenCode ayarları, auth,
shell profili ve legacy `Design` checkout'u değiştirilmez.

## Yeni iş

```sh
python3 "$BS" start yeni-is --executor opencode \
  --paths studio .agents .opencode .github brands/asyada-egitim
```

Her start bağımsız shallow/partial clone'dan güncel main commit/tree metadatasını
alır. Seçili kaynak blob'larının kimlikleri değişmemişse içerik yerelden yeniden
kullanılır; yalnız yeni/değişmiş ortak kaynak blob'ları yüklenir. Sonuç JSON'u
`baseline.source_sha`, `digest`, `loaded_blobs`, `reused_blobs` ve snapshot yolunu
verir. Kaynak ve Git metadata kontrolü nedeniyle **sıfır ağ isteği** iddiası yoktur.
Server blob filtrelemesini desteklemiyorsa Git daha fazla veri indirebilir.

Snapshot dosyaları task'ın kendi Git object store'una `hash-object` ile alınır;
checkout normal ve bağımsızdır. Paylaşılan `.git`, alternates veya hardlink yoktur.
Task değişiklikleri baseline'ı değiştirmez. Task'ın `AGENTS.md` ve SHA'sı geçerli
talimattır; eski snapshot aktif task'ı veya oturumun üst öncelikli kurallarını ezmez.

`--base publish/...` explicit devam işidir: baseline güncellenmez, yalnız eski
blob'lar import edilir; Git seçili branch'in kendi blob'larını checkout eder.
`--no-baseline` eski bağımsız remote yolunu kullanır.

## Değişiklikten sonra kalibre et

Ortak kaynak değişikliğini normal branch/PR/check/merge süreciyle teslim edin.
Merge doğrulamasından sonra:

```sh
python3 "$BS" calibrate
```

Bu komut yalnız GitHub main'in committed kaynaklarını okur. Değişen içeriğe yeni
snapshot çıkarır, active kaydını ve hash'i doğrulanmış launcher'ı günceller.
Değişmeyen snapshot yeniden yazılmaz; yalnız marka/teslim değiştiyse kaynak
digest'i aynı kalır ve `loaded_blobs: 0` olur. Eski snapshot'lar küçük, sürümlü
geri izleme kayıtları olarak korunur; otomatik budama/silme yoktur.
`start` da aynı kalibrasyonu yapar; unutulmuş manuel refresh eski kural üretmez.

Snapshot veya launcher'da yerel edit, symlink, eksik/eklenmiş dosya, hash/mod
uyuşmazlığı varsa **STOP**: üzerine yazılmaz. Ağ yoksa eski temeli sessizce güncel
ilan etmek yerine iş durur. Benzersiz yerel değişikliği önce ayrı koruyun.

## Temizlik ve sınırlar

Task cleanup yalnız temporary `tasks/<iş>` clone'unu temizler; kalıcı baseline'a
dokunmaz. Son bağımsız remote-byte proof ve exact-head PR CI kapıları değişmez.
Onların fetch'i baseline'dan yapılmaz. Kurulu runtime ve kişisel credential'lar
bu source cache'in dışındadır; önemli üretim çıktıları cache'e konmaz.

Codex kendi host'unda aynı yordamı kullanabilir. Platform storage silinirse yeniden
kurulur; OpenCode'un Mac baseline'ı Codex'e otomatik aktarılmaz. Bu çalışma Codex
hesap aktivasyonu veya native görsel araç testi değildir.
