import json
import os

path = "./data"

prefix_ttl = '''
@prefix : <http://www.example.org/disease-ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
@prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .

:Ontology a owl:Ontology .

'''
class_ttl = '''

# Classes
:Disease a owl:Class .
:Symptom a owl:Class .
:Treatment a owl:Class .
:Patient a owl:Class .
'''

properties_ttl = '''

# Properties
:name a owl:DatatypeProperty ;
      rdfs:domain :Patient ;
      rdfs:range xsd:string .

:hasSymptom a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range :Symptom .

:hasTreatment a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range :Treatment .

:exhibitsSymptom a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Symptom .

:hasDisease a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Disease .

:receivesTreatment a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Treatment .
    
:hasDescription a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range xsd:string .

'''

disease_instances_ttl = '''

# Disease instances
:flu a :Disease ;
    :hasSymptom :fever, :cough, :sorethroat ;
    :hasTreatment :rest, :hydration, :antiviraldrugs .

:diabetes a :Disease ;
    :hasSymptom :increasedthirst, :frequenturination, :fatigue ;
    :hasTreatment :insulintherapy, :dietmodification, :exercise .

'''

simptom_instances_ttl = '''

# Symptom instances
:fever a :Symptom .
:cough a :Symptom .
:sorethroat a :Symptom .
:increasedthirst a :Symptom .
:frequenturination a :Symptom .
:fatigue a :Symptom .
'''

current_symptoms_ttl = ["fever", "cough", "sorethroat", "increasedthirst", "frequenturination", "fatigue"]


treatment_instances_ttl = '''

# Treatment instances
:rest a :Treatment .
:hydration a :Treatment .
:antiviraldrugs a :Treatment .
:insulintherapy a :Treatment .
:dietmodification a :Treatment .
:exercise a :Treatment .
'''

current_treatment_instances = ["rest", "hydration", "antiviraldrugs", "insulintherapy", "dietmodification", "exercise"]

patient_instances_ttl = '''

# Patient instances
:Patient1 a :Patient ;
    :name "Paul Harrods"
    :exhibitsSymptom :fever ;
    :exhibitsSymptom :cough ;
    :exhibitsSymptom :sorethroat .

:Patient2 a :Patient ;
    :name "Ana Montana"
    :exhibitsSymptom :increasedthirst ;
    :exhibitsSymptom :frequenturination ;
    :exhibitsSymptom :fatigue .

'''

def load_csvs(path):
    """
    Load CSV files from a given directory and return a dictionary with the file names as keys and their contents as values.

    Args:
        path (str): The path to the directory containing the CSV files.

    Returns:
        dict: A dictionary with file names as keys and their contents as values.
    """
    csvs = {}
    json_data = {}
    
    for filename in os.listdir(path):
        
        if filename.endswith('.csv'):
            with open(os.path.join(path, filename), 'r') as f:
                csvs[filename] = f.read()
                
        elif filename.endswith('.json'):
            with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                json_data[filename] = json.load(f)
    
    return csvs, json_data

def populate_symptoms(csv_file, descriptions, treatments):
    
    
    global current_symptoms_ttl, disease_instances_ttl, simptom_instances_ttl
    global treatment_instances_ttl, patient_instances_ttl
    
    diseases_and_symptoms = {}
    
    # Gathering all the symptoms from the csv file
    for line in csv_file.splitlines()[1:]:
        
        line = line.split(",")
        disease = line[0].lower()
        symptoms = line[1:]
        
        if disease not in diseases_and_symptoms.keys():
            diseases_and_symptoms[disease] = []
            diseases_and_symptoms[disease].extend(symptoms)
        else:
            for symptom in symptoms:
                if symptom.lower() not in diseases_and_symptoms[disease]:
                    diseases_and_symptoms[disease].append(symptom)
                    
    # Adding the symptoms to the ttl file
    for disease, symptoms in diseases_and_symptoms.items():
        disease = disease.replace(" ", "")
        disease = disease.lower()
        disease = disease.replace("(", "").replace(")", "")
        symptoms = [symptom.lower() for symptom in symptoms]
        
        # Check if the symptoms are already in the ttl file
        for symptom in symptoms:
            if symptom not in current_symptoms_ttl and symptom != "":
                symptom_instance = f":{symptom.replace(" ", "")} a :Symptom .\n"
                current_symptoms_ttl.append(symptom)
                simptom_instances_ttl += symptom_instance
        
        # Adding the disease instance to the ttl file with the symptoms and description
        disease_instance = f"\n:{disease} a :Disease ;\n"
        # Remove spaces in the firt letter of the symptoms and remove the empty symptoms
        symptoms = [symptom.replace(" ", "") for symptom in symptoms if symptom != ""]
        disease_instance += f"    :hasSymptom :{', :'.join(symptoms)} ;\n"
    
        if disease in descriptions.keys():
                disease_instance += f"    :hasDescription \"{descriptions[disease][1:-2]}\" ;\n"    
            
    
        if disease in treatments.keys():
            
            to_add = []
            for treatment in treatments[disease]:
                treatment = treatment.lower()
                to_add.append(treatment.replace(" ", ""))
            
            disease_instance += f"    :hasTreatment :{', :'.join(to_add)} .\n\n"
    
        disease_instances_ttl += disease_instance
             
def gather_treatments(csv_file):
    
    global current_treatment_instances, treatment_instances_ttl
    
    treatments_dict = {}
    
    # Gathering all the treatments from the csv file
    for line in csv_file.splitlines()[1:]:
        
        line = line.split(",")
        disease = line[0].lower().replace(" ", "").replace("(", "").replace(")", "")
        treatments = line[1:]
        
        for treatment in treatments:
            treatment = treatment.lower()
            if treatment not in current_treatment_instances and treatment != "":
                treatment_instance = f":{treatment.replace(" ", "")} a :Treatment .\n"
                current_treatment_instances.append(treatment)
                treatment_instances_ttl += treatment_instance
        
        if disease not in treatments_dict.keys():
            treatments_dict[disease] = []
            for t in treatments:
                t = t.lower().replace(" ", "")
                
                if t != "":
                    treatments_dict[disease].append(t)
            
            
        else:
            for treatment in treatments:
                if treatment.lower() not in treatments_dict[disease] and treatment != "":
                    treatments_dict[disease].append(treatment.lower().replace(" ", ""))
            
    return treatments_dict
                 
def gather_descriptions(csv_file):
    
    descriptions = {}
    
    # Gathering all the descriptions from the csv file
    for line in csv_file.splitlines()[1:]:
        
        line = line.split(",")
        disease = line[0].lower().replace(" ", "").replace("(", "").replace(")", "")
        description = line[1].replace(".", "")
        
        if disease not in descriptions.keys():
            descriptions[disease] = description

    return descriptions


def populate_petients(json_data):
        
        global patient_instances_ttl
        
        patients = {}
        
        # Gathering all the patients from the json file
        count = 2
        for patient in json_data:
            count += 1
            
            id = count
            
            # Get the patient data
            name = patient["nome"]
            symptoms = patient["sintomas"]   
            
            # Add the patient to the ttl
            patient_instance = f"\n:Patient{id} a :Patient ;\n"
            patient_instance += f"    :name \"{name}\" ;\n"

            for i in range(len(symptoms)):
                symptom = symptoms[i]
                symptom = symptom.lower()
                symptom = symptom.replace(" ", "")
                
                if i == len(symptoms) - 1:
                    patient_instance += f"    :exhibitsSymptom :{symptom} .\n\n"
                    break

                patient_instance += f"    :exhibitsSymptom :{symptom} ;\n"
                
            patient_instances_ttl += patient_instance

def main():

    csvs, jsons = load_csvs(path)
    
    print("\nCSV files loaded:")
    for filename in csvs.keys():
        print(f"- {filename}")
        
    print("\nJSON files loaded:")
    for filename in jsons.keys():
        print(f"- {filename}\n")
    
    descriptions = gather_descriptions(csvs["Disease_Description.csv"])
    treatments = gather_treatments(csvs["Disease_Treatment.csv"])
    populate_symptoms(csvs["Disease_Syntoms.csv"], descriptions, treatments)
    populate_petients(jsons["doentes.json"])
    
    # Joint all the ttl files into one
    ttl_file = prefix_ttl 
    ttl_file += class_ttl
    ttl_file += properties_ttl
    ttl_file += disease_instances_ttl
    ttl_file += simptom_instances_ttl
    ttl_file += treatment_instances_ttl
    ttl_file += patient_instances_ttl
    
    # Write the ttl file
    with open("med_doentes.ttl", "w") as f:
        f.write(ttl_file)
    

if __name__ == "__main__":
    main()