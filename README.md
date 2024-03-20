# Corpdoc OCR Service
**Install Tesseract**

```bash
  https://github.com/UB-Mannheim/tesseract/wiki
```

**Install Poppler**

```bash
  https://poppler.freedesktop.org/
```

**Install Libraries**

```bash
  pip install -r requirements.txt
```

**Start OCR Server**

```bash
  uvicorn src.main:app --reload --port=9000 --host=0.0.0.0
```