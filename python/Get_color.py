import cv2
import numpy as np

def nothing(x):
    pass

# Charger ton image de référence
image = cv2.imread('test2.png')
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Créer une fenêtre de contrôle
cv2.namedWindow('Controles')
cv2.resizeWindow('Controles', 640, 300)

# Créer les trackbars pour les plages HSV
cv2.createTrackbar('H Min', 'Controles', 0, 179, nothing)
cv2.createTrackbar('S Min', 'Controles', 0, 255, nothing)
cv2.createTrackbar('V Min', 'Controles', 0, 255, nothing)
cv2.createTrackbar('H Max', 'Controles', 179, 179, nothing)
cv2.createTrackbar('S Max', 'Controles', 255, 255, nothing)
cv2.createTrackbar('V Max', 'Controles', 255, 255, nothing)

while True:
    # Lire les positions actuelles des curseurs
    h_min = cv2.getTrackbarPos('H Min', 'Controles')
    s_min = cv2.getTrackbarPos('S Min', 'Controles')
    v_min = cv2.getTrackbarPos('V Min', 'Controles')
    h_max = cv2.getTrackbarPos('H Max', 'Controles')
    s_max = cv2.getTrackbarPos('S Max', 'Controles')
    v_max = cv2.getTrackbarPos('V Max', 'Controles')

    # Définir les plages
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    # Créer le masque
    mask = cv2.inRange(hsv, lower, upper)
    
    # Appliquer le masque sur l'image d'origine pour voir le résultat "réel"
    result = cv2.bitwise_and(image, image, mask=mask)

    # Afficher les fenêtres
    cv2.imshow('Masque (Noir & Blanc)', mask)
    cv2.imshow('Resultat (Couleur isolee)', result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
# Affiche les valeurs finales dans la console pour les copier-coller
print(f"Config finale : lower = [{h_min}, {s_min}, {v_min}], upper = [{h_max}, {s_max}, {v_max}]")