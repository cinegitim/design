# Brandstudio P2 · KAIST pilot kontrol kaydı

Bu dizin **koordinatör dalı** `coord/brandstudio-p2-kaist-20261102` üzerinde tutulur. Kaynak üretim dalının commit kimliğine işaret eder, kendi kendisini üretilmiş çıktı gibi göstermeden `P1 TaskSpec` / `TaskReceipt` / `CapabilityReport` ve `P2 HandoffEnvelope` içerir.

- **Kaynak dalı:** [publish/chatgpt-chat-brandstudio-p2-kaist-20261102](https://github.com/cinegitim/design/tree/f50318d619d7a46a7b4504dd0efaefd03c1265b2/docs/instagram/brandstudio-p2-kaist-pilot-20261102/v1), commit [`f50318d619d7`](https://github.com/cinegitim/design/commit/f50318d619d7a46a7b4504dd0efaefd03c1265b2).
- **Gerçekten yapılan iş:** Bu ChatGPT sohbetinde GitHub bağlantısıyla KAIST V2 HTML kaynakları okundu; `source-audit.md` yazıldı. Source branch `f50318d619d7a46a7b4504dd0efaefd03c1265b2` commit'e ulaştı; GitHub karşılaştırma endpoint'iyle yalnız bu bir dosyanın değiştiği doğrulandı. Bu bir tasarım render testi **değildir**.
- **Kanıt sınıfı:** GitHub commit/branch için doğrulanmış; `chatgpt-chat` üretici kimliği bu sohbetin beyanı ve araç kullanımına dayanıyor; haricî model-host attestasyonu yok.
- **Sıradaki yürütücü:** `opencode` için önerilen **ayrı** dal `publish/opencode-brandstudio-p2-kaist-20261102`. Bu dal bilerek **oluşturulmadı**: gerçek OpenCode kendi bağımsız ortamında devralmalı. Work/Codex hedefi sonraki aşama, gerçek Work host kanıtı yok.
- **Kaynak original base:** `f44b775d9e52b736facf6d57706ffbf2b0e6ab69`. **Kaynak handoff base:** `f50318d619d7a46a7b4504dd0efaefd03c1265b2`. Birbirine karıştırılmamalıdır.
- `handoff-envelope.json` yalnızca `source_verified` durumundadır; **`received` değildir**. Koordinatör dalı `main` ile birleştirilmemeli veya tasarım ürününe dönüştürülmemelidir.

## Yeni OpenCode yürütücüsü için kısıtlar

Bağımsız çalışma alanı kullan, kaynak branch HEAD'ini GitHub/git'ten yeniden doğrula. Handoff base olarak tam `f50318d619d7a46a7b4504dd0efaefd03c1265b2` commit'ini kullan; source branch'e doğrudan commit atma. Seçili KAIST V2 dosyaları orijinal haliyle kalacak. Gerçek render/QA, kurum logosu SHA-256, insan onayı ve yayın eylemleri birbirinden ayrı kalacak. Yeni ücretli API veya görsel üretim yok.

**Not:** `TaskSpec` ve `CapabilityReport` işin izinli sınırını tanımlar; **bu dosyalar çalıştırılan bir ajanı ispat etmez**. OpenCode gerçekten çalıştığında gözlemlenebilir execution log / receipt oluşturulmalı. Başarısızsa `pilot-status.json` tamamlandıya dönüştürülmemeli.
