# kcolours

Extracts a colour palette from an image in the terminal using [k-means clustering](https://en.wikipedia.org/wiki/K-means_clustering).

---
## Example

|                      |                                                                                 |
| -------------------- | ------------------------------------------------------------------------------- |
| ![](https://raw.githubusercontent.com/chlofisher/kcolours/main/demo/demo.gif) | ![*The Great Wave off Kanagawa*, Katsushika Hokusa (1831)](https://raw.githubusercontent.com/chlofisher/kcolours/main/demo/kanagawa.jpg) |

--- 
## Installation & Usage

### Option 1: using `uv` (recommended)
Run without installing using `uvx`
```bash
uvx kcolours example.png
```
or install locally 
```bash
uv tool install kcolours
kcolours example.png
```

### Option 2: using `pipx`
```bash
pipx install kcolours
kcolours example.png
```

### Option 3: using `pip` in a virtual environment
```bash
pip install kcolours
python -m kcolours example.png
```

