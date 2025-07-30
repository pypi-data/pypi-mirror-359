# OCR Project & Solid Figures Calculator

This project provides two main features:

1. **OCR Utilities**: Extract words and tabular data from images, PDFs, and DOCX files, with optional CSV export.
2. **Solid Figures Calculator**: Calculate volume and surface area for common 3D shapes (cube, sphere, rectangular prism, cylinder).

## Project Structure

- `src/` — All solid figure classes (Cube, Sphere, RectangularPrism, Cylinder)
- `main.py` — Entry point for solid figures calculator
- `requirements.txt` — Python dependencies
- `pyproject.toml` — Build and packaging configuration

## Usage

### Solid Figures Calculator

Run:

python main.py
uv build
```
python main.py
```

This will print example calculations for all supported solid figures.

### OCR Utilities

See previous versions of `main.py` for OCR and CSV extraction logic, or ask for a dedicated script.

## How to Build (for packaging)

- Project uses a `src` layout for modern Python packaging.
- To build:

```
uv build
```

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

---

For more features or help, just ask!
