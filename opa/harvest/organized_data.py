from zipfile import ZipFile
from os import listdir
from os.path import isfile, join
import os



def list_file(path_dossier):
#Retourne la liste des fichiers à dezziper présent dans le repertoire indiquer dans la variable
# path_dossier
    fichiers = []
    path2 = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path2,path_dossier)
    monRepertoire = listdir(path)
    for fichier in monRepertoire:
        if fichier.find(".zip") >= 0:
            fichiers.append(fichier)

    return fichiers
    

def dezip(path_dossier,fichiers):
    path2 = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path2, path_dossier)
    for fichier in fichiers:
        file = join(path,fichier)
        print(file)
        # ouvrir le fichier zip en mode lecture
        with ZipFile(file, 'r') as zip: 
            # afficher tout le contenu du fichier zip
            zip.printdir() 
        
            # extraire tous les fichiers
            print('extraction...') 
            zip.extractall(path= join(path,"extract"))
            print('Terminé!')



