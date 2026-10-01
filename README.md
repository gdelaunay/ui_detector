# UI Detector
![Static Badge](https://img.shields.io/badge/Python-3.7-brightgreen)
![Static Badge](https://img.shields.io/badge/Tesseract%20OCR-4.0-olivedrab)
![Static Badge](https://img.shields.io/badge/Tensorflow-1.7.1-orange)
![Static Badge](https://img.shields.io/badge/OpenCV-4.1.0-orangered)

UI Detector convertit une capture d'écran d'interface web en maquette modifiable. Un réseau de détection identifie chaque élément de l'interface, le traitement d'image extrait ses propriétés visuelles, l'OCR rend les textes éditables, et le résultat est exporté aux formats SVG, Balsamiq ou Pencil.

## Pipeline

```
Image → Faster R-CNN (TF) → OpenCV post-processing → Tesseract OCR → Export (.svg / .zip / .epz)
```

| Détection |
|-----------|
|![Capture1](https://github.com/gdelaunay/ui_detector/assets/55590623/fe94aa3f-8c54-4e19-8590-dee39e1d41d0)|
Un modèle Faster R-CNN (ResNet-50), entraîné sur environ 300 captures d'interfaces annotées manuellement, localise chaque composant de l'image et lui attribue une catégorie parmi les 19 classes supportées (texte, bouton, image, icône, champ de saisie, etc.).  

---
  
| Analyse |
|-----------|
|![Capture2](https://github.com/gdelaunay/ui_detector/assets/55590623/6695f355-8910-4865-82ec-cd2629686768)|
Chaque zone détectée est recadrée puis analysée avec OpenCV. On identifie les couleurs dominantes, on supprime les bordures parasites, on détermine la position exacte du texte à l'intérieur d'un bouton, et on ajuste les limites de l'élément au pixel près.  

---

| OCR |
|-----------|
|![Capture3](https://github.com/gdelaunay/ui_detector/assets/55590623/84817f89-464c-4821-b157-1e1c13261a6f)|
Les régions contenant du texte sont converties en image binaire puis passées dans Tesseract (anglais + français). Le texte reconnu remplace l'image d'origine dans la maquette, ce qui le rend directement modifiable.  

---

## Démo

| Input | Output (SVG → Adobe XD) |
|-------|------------------------|
| ![image017](https://github.com/gdelaunay/ui_detector/assets/55590623/adfc280a-cd8a-461a-bcc2-93e3a8bef696) | ![maquetteCBIC](https://github.com/gdelaunay/ui_detector/assets/55590623/4348733b-7595-4fca-a230-a2b437ef230e) |

## Formats d'export

| Format | Extension | Destiné à |
|--------|-----------|-----------|
| SVG | `.svg` | Adobe XD (export HTML/CSS ensuite) |
| Balsamiq | `.zip` (bmml + assets) | Balsamiq |
| Pencil | `.epz` | Evolus Pencil |

## Quickstart

```bash
# 1. Cloner
git clone https://github.com/gdelaunay/ui_detector && cd ui_detector

# 2. Setup (Windows, nécessite Python 3.7 + Tesseract embarqué)
setup.bat

# 3. Lancer
python index.py
# → http://localhost:89
```

Ou via Docker :
```bash
docker build -t ui-detector .
docker run -p 89:89 ui-detector
```

## Structure

```
├── index.py                 # Flask app (upload + export API)
├── prediction.py            # TF inference + NMS
├── mockup.py                # Orchestration (translate → align → export)
├── elements.py              # Classes TextElement, ImageElement, Icon
├── image_utils.py           # OpenCV/PIL: couleurs, bordures, crops
├── ocr.py                   # Tesseract wrapper
├── img2svg.py               # Générateur SVG
├── img2bmml.py              # Générateur Balsamiq
├── constants.py             # Types, tags XML, icônes b64
├── network_training.py      # Script training (TF1 legacy)
├── export_graph.py          # Export frozen graph
├── trained_graphs/          # Modèle .pb
├── dataset/                 # Images annotées + .record
├── training/                # Config pipeline + pretrained
└── misc/dataset_processing/ # xml→csv→tfrecord
```

## Processus technique

```
Capture d'écran
    │
    ▼
Faster R-CNN (ResNet-50, fine-tuné COCO)
    │  19 classes, NMS IoU 0.1, seuil confiance 0.4
    │  → boxes [ymin,xmin,ymax,xmax] + classes + scores
    ▼
translate_raw_results()
    │
    ├── TextElement (text, buttons, inputs)
    │     → crop → remove borders → detect colors (LAB ΔE)
    │     → find text position → OCR → compute size/color
    │
    ├── ImageElement (images)
    │     → crop → remove borders → base64 encode
    │
    └── Icon (search, lock, menu, etc.)
          → replace with embedded SVG vector
    ▼
align_text_elements()
    │  Y-axis snap, size/color harmonization (ΔE threshold)
    ▼
Background extraction
    │  Fill element zones with corner color → clean backdrop
    ▼
Export
    ├── SVG  → Scene(Rect, Text, Image, ButtonRect) → .svg
    ├── BMML → Sketch(Text, Button, Image) + PNG assets → .zip
    └── EPZ  → Pencil XML pages + content.xml → .epz
```

## Limitations

- Prototype non maintenu. Déploiement non garanti hors config d'origine (chemins Windows, partage réseau, TF 1.x).
- 19 classes statiques, pas de détection de conteneurs/grille.

## Licence

Prototype personnel de R&D, non maintenu. Distribué sous licence MIT — voir [LICENSE](LICENSE).
