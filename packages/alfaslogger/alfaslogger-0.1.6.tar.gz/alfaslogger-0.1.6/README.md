# Alfaslogger WebGUI

Web arayüzü destekli bir logger modülüdür.

## Kurulum

```bash
pip install alfaslogger
```

## Kullanım

```python
from logger_app import Logger

# GUI ile birlikte logger başlat
logger = Logger(name="MyApp", level="DEBUG", gui=True)

# Handler ekle (zorunlu değil, otomatik dosya ve konsol loglaması vardır)
from logger_app import ConsoleHandler, FileHandler

logger.add_handler(ConsoleHandler(level="DEBUG"))
logger.add_handler(FileHandler("my_app", level="INFO"))

# Log yaz
logger.debug("Debug mesajı")
logger.info("Bilgilendirme mesajı")
logger.warning("Uyarı mesajı")
logger.error("Hata mesajı")
logger.critical("Kritik hata mesajı")

# Web GUI'ye erişmek için:
# http://localhost:8000
# WebSocket canlı log: ws://localhost:8001
```

## Özellikler
- Gerçek zamanlı log izleme (WebSocket ile)
- Logları konsola, dosyaya veya SQLite veritabanına yazabilme
- Web tabanlı kullanıcı arayüzü

## Lisans

MIT
