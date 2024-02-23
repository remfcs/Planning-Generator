import pandas as pd

# Import the csv file and sort it by the grade
student_list = pd.read_csv('liste_eleve_v1.csv', skiprows=1)
print(student_list)
sorted_list = student_list.sort_values(by=student_list.columns[2])
print(sorted_list)

#def groups_lv1(list, min size, max_size):


def groups_lv13(list, min_size, max_size):
    # Initialize the groups
    groups = [[] for i in range(len(list) // min_size)]

    # Répartir les élèves dans les groupes
    for eleve in list:
        # Trouver le groupe avec le moins d'élèves
        min_groupe = min(groupes, key=len)
        # Ajouter l'élève au groupe avec le moins d'élèves
        min_groupe.append(eleve)

    # Vérifier si certains groupes sont trop petits
    for groupe in groupes:
        if len(groupe) < taille_groupe_min:
            # Distribuer les élèves excédentaires aux autres groupes
            while len(groupe) < taille_groupe_min and groupes:
                # Chercher un groupe avec un surplus
                surplus_groupe = max(groupes, key=len)
                # Déplacer un élève du groupe avec surplus au groupe actuel
                eleve_deplace = surplus_groupe.pop()
                groupe.append(eleve_deplace)
    return groups

def groups_lv12(list, min_size, max_size):
    # Initialize the variables
    groups = []
    actual_group = []
    actual_group_size = 0
    for student in list:
        # Add the students in a group if the size of the actual group is smaller than the maximum size
        if actual_group_size + len(actual_group) <= max_size:
            actual_group.append(student)
            actual_group_size += 1
        else:
            # If the size of the actual group is equal to the maximum size, this group is added to the groups list
            groups.append(actual_group)
            # The actual group is initialized again
            actual_group = [student]
            actual_group_size = 1

    # Add the last group to the groups list
    if actual_group:
        groups.append(actual_group)

    # Vérifier si les groupes sont trop petits, les fusionner si nécessaire
    for i in range(len(groups) - 1):
        if len(groups[i]) + len(groups[i + 1]) <= min_size:
            groups[i] += groups[i + 1]
            del groups[i + 1]
            break
    return groups

# Exemple d'utilisation
groups = groups_lv1(sorted_list, 15,)

def groups_lv1(df, min_size, max_size, number_classes):
    groups = pd.DataFrame(columns=["Numéro de groupe", "Prénom", "Nom", "Note"])
    class_number = 0
    number_students = math.ceil(len(df) / number_classes)
    for i in range(len(df)):
        # Vérifier si le groupe actuel existe dans la DataFrame des groupes
        if len(groups[groups["Numéro de groupe"] == class_number]) == 0:
            groups = groups.append({"Numéro de groupe": class_number, "Prénom": "", "Nom": "", "Note": ""}, ignore_index=True)
            
        # Ajouter l'étudiant au groupe actuel
        if len(groups[groups["Numéro de groupe"] == class_number]) < number_students:
            groups.loc[groups["Numéro de groupe"] == class_number, ["Prénom", "Nom", "Note"]] = df.iloc[i].values
        else:
            class_number += 1
            groups = groups.append({"Numéro de groupe": class_number, "Prénom": "", "Nom": "", "Note": ""}, ignore_index=True)
            groups.loc[groups["Numéro de groupe"] == class_number, ["Prénom", "Nom", "Note"]] = df.iloc[i].values
            
    return groups

number_classes = 2
groups = groups_lv1(sorted_list, 15, 18, number_classes)
print(groups.to_string(index=False))

for group_num, group_df in groups.groupby("Numéro de groupe"):
    print(f"Groupe {group_num}:")
    print(group_df[["Prénom", "Nom", "Note"]].to_string(index=False))
    print()
for idx, group in enumerate(groups):
    print(f"Groupe {idx + 1}: {group}")