import cv2
import mss
import numpy as np
import pydirectinput
import time
import random
import os
import sys
import threading
from fastapi import FastAPI
import psutil

app = FastAPI()

#Fonction d'autokill (obligé du a l'utilisation de pyinstaler avec --onefile)
def check_parent():
    parent = psutil.Process(os.getpid()).parent()
    while True:
        if not parent or not parent.is_running():
            #fermeture si plus de parents détècter (l'interface a tué le parent)
            os._exit(0)
        time.sleep(3)


#Function qui récupère le chemin d'accés des fichier
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#Variable constante
lower_gold1 = np.array([14, 173, 157]) 
upper_gold1 = np.array([24, 255, 255])
lower_gold2 = np.array([0, 0, 199]) 
upper_gold2 = np.array([179, 16, 255])

monitor1 = {"top": 990, "left": 905, "width": 110, "height": 90}
monitor2 = {"top": 400, "left": 1150, "width": 200, "height": 600}

#Variable a définir
compteur = 0
dernier_appui = 0
delai_entre_appuis = 0.5

#Classe pour detecter une image
class SymbolDetector:
    def __init__(self):
        self.compteur = 0
        self.dernier_appui = 0
        self.delai_entre_appuis = 0.5

    def detec_picture(self, sct, monitor, lower_gold, upper_gold, threshold, name):
            template_img = cv2.imread(get_resource_path(name))
            template_hsv = cv2.cvtColor(template_img, cv2.COLOR_BGR2HSV)
            template_mask = cv2.inRange(template_hsv, lower_gold, upper_gold)
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            hsv_frame = cv2.cvtColor(hsv_frame, cv2.COLOR_BGR2HSV)
            
            screen_mask = cv2.inRange(hsv_frame, lower_gold, upper_gold)
            res = cv2.matchTemplate(screen_mask, template_mask, cv2.TM_CCOEFF_NORMED)
            
            loc = np.where(res >= threshold)
            
            if len(loc[0]) > 0:
                self.compteur += 1
                
                if self.compteur == 5:
                    self.compteur = 0
                    temps_actuel = time.time()
                    print(f"Symbole détecté avec succès !")
                    if temps_actuel - self.dernier_appui >= self.delai_entre_appuis:
                        print("appuyé")
                        pydirectinput.keyDown('f')
                        time.sleep(random.uniform(0.1, 0.3)) 
                        pydirectinput.keyUp('f')
                        self.delai_entre_appuis = 0.3+random.random()/2
                        self.dernier_appui = temps_actuel
            
            else:
                self.compteur = 0
#Variable qui vérifie si la détéction doit être activé           
activer = True   

#Définit la boucle de détection
def run():
    global activer
    with mss.mss() as sct:
        detecteur1 = SymbolDetector()
        detecteur2 = SymbolDetector()
        while True:
            
            if activer:
                detecteur2.detec_picture(sct, monitor2, lower_gold2, upper_gold2, 0.82, "symbol2.png")
                detecteur1.detec_picture(sct, monitor1, lower_gold1, upper_gold1, 0.60, "symbol.png")
            else:
                cv2.destroyAllWindows()
                time.sleep(0.5)
            time.sleep(0.01)

#Tourne la boucle en arrière plan
thread = threading.Thread(target=run, daemon=True)
thread.start()

#Config requete serveur           
@app.post("/activate")
async def activ():
    global activer
    if not activer:
        activer = True
    return {"message": "ok"}

@app.post("/desactivate")
async def desactiv():
    global activer
    if activer:
        activer = False
    return {"message": "ok"}  
     


#Execution serveur
if __name__ == "__main__":
    import uvicorn
    threading.Thread(target=check_parent, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)