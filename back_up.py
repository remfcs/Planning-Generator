import os
import shutil


def backup(Data):
    try:
        # Construction du nom de fichier pour la sauvegarde en ajoutant un préfixe "backup_" au nom du fichier de base de données
        name = "backup_" + os.path.splitext(os.path.basename(Data))[0]
        rename_data = os.path.join(os.path.dirname(Data), name) + ".sqlite3"
        # Copie du fichier de base de données vers la sauvegarde
        shutil.copy2(Data, rename_data)
    except FileNotFoundError:
        # Gestion de l'erreur si le fichier source n'existe pas
        print("Le fichier source n'existe pas.")
    except PermissionError:
        # Gestion de l'erreur si la permission est refusée pour copier ou renommer le fichier
        print("Permission refusée pour copier ou renommer le fichier.")
    except Exception as e:
        # Gestion de toutes les autres erreurs possibles
        print(f"Une erreur s'est produite : {e}")
        
def restor_backup(Data):
    try:
        # Construction du nom de fichier de la sauvegarde en ajoutant un préfixe "backup_" au nom du fichier de base de données
        name = "backup_" + os.path.splitext(os.path.basename(Data))[0]
        rename_data = os.path.join(os.path.dirname(Data), name) + ".sqlite3"
        print(rename_data)
        # Vérification de l'existence de la sauvegarde
        if os.path.exists(rename_data):
            # Suppression du fichier de base de données actuel
            os.remove(Data)
            # Renommage de la sauvegarde pour restaurer le fichier de base de données
            os.rename(rename_data, Data)
        else:
            # Affichage d'un message d'erreur si aucune sauvegarde n'est trouvée
            print(f"Impossible, there is no backup.")
            return False
    except FileNotFoundError:
        # Gestion de l'erreur si le fichier source n'existe pas
        print("Le fichier n'existe pas.")
    except PermissionError:
        # Gestion de l'erreur si la permission est refusée pour supprimer ou renommer le fichier
        print("Permission refusée pour supprimer le fichier.")
    except Exception as e:
        # Gestion de toutes les autres erreurs possibles
        print(f"Une erreur s'est produite : {e}")