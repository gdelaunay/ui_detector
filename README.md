# UI Detector
![Static Badge](https://img.shields.io/badge/Python-3.7-brightgreen)
![Static Badge](https://img.shields.io/badge/Tesseract%20OCR-4.0-olivedrab)
![Static Badge](https://img.shields.io/badge/Tensorflow-1.7.1-orange)
![Static Badge](https://img.shields.io/badge/OpenCV-4.1.0-orangered)


**UI Detector** (ou Trad'UI) est une application de **maquettage d'écran automatisé** basé sur la détection d'objet. </br>

À partir d'une image (pouvant être une capture d'écran d'un page web existante, d'une maquette fonctionnelle ou graphique, ou d'un dessin) l'application va détecter et analyser chaque élement, pour ensuite les retranscrire dans une maquette modifiable au format SVG (manipulable sous Adobe XD qui permet ensuite un export en HTML/CSS), ou dans d'autres formats de logiciels de maquettage (Balsamiq, Pencil). </br>

En pratique, l'application produisant un maquette instantanément, permet par exemple la visualisation immédiate de modifications souhaitées par un client lors d'une réunion.</br>

## Fonctionnement
Un modèle de détection d'objet utilisant **Tensorflow**, librairie open-source de machine learning, a été entraîné sur un dataset maison de 300 images d'interfaces utilisateurs web sur lesquelles sont annotés chaque élement et son type. Ce modèle va donc identifier tous les éléments de l'image fournie ainsi que leur position exacte, qui seront ensuite traités différement en fonction de leur type (image, icône, bouton, paragraphe, zone d'entrée etc).
![Capture1](https://github.com/gdelaunay/ui_detector/assets/55590623/fe94aa3f-8c54-4e19-8590-dee39e1d41d0)

La libraire **OpenCV** est utilisée ici pour ses fonctionnalités de traitement d'image. Elle nous sert à analyser les différentes propriétés de certains types d'éléments ainsi qu'à les traiter. Par exemple les élements de type "image" sont découpés et isolés pour être réstitués dans la maquette; les éléments de types "bouton" sont eux analysés pour déterminer leur couleur, si il ont une bordure et si oui sa couleur et son épaisseur, puis le texte de ce bouton est capturé sous forme d'image pour être envoyé à la fonction d'OCR de l'application (comme tous les autres éléments textuels).
![Capture2](https://github.com/gdelaunay/ui_detector/assets/55590623/6695f355-8910-4865-82ec-cd2629686768)

**Tesseract OCR** (par pytesseract) est un modèle de reconnaissance optique de caractères, qui nous sert ici à transformer un texte au format d'image en une chaîne de caractères modifiable.
![Capture3](https://github.com/gdelaunay/ui_detector/assets/55590623/84817f89-464c-4821-b157-1e1c13261a6f)

## Démo

Capture d'écran d'une page web :
![image017](https://github.com/gdelaunay/ui_detector/assets/55590623/adfc280a-cd8a-461a-bcc2-93e3a8bef696)

Maquette modifiable produite (en **< 1 minute**):
![maquetteCBIC](https://github.com/gdelaunay/ui_detector/assets/55590623/4348733b-7595-4fca-a230-a2b437ef230e)

## Installation
setup.bat

</br>
</br>

_Application au stade de prototype, non maintenue, le déploiment ne devrait pas fonctionner sur votre machine._
