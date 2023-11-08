from comet_ml import Experiment
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
from sklearn import preprocessing
import seaborn as sn
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from xgboost import plot_importance
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report

# Load environment variables from the file
load_dotenv('/Users/Lenovo/Desktop/notebook/NHL/.env')

# Retrieve the COMET_API_KEY from the environment variables
COMET_API_KEY = os.getenv('COMET_API_KEY')
if COMET_API_KEY is None:
    raise ValueError("La clé API Comet.ml n'a pas été trouvée dans les variables d'environnement.")

# Create an experiment with the provided API key
exp = Experiment(
    api_key=COMET_API_KEY,
    project_name='ift6758',
    workspace='imenjaoua',
)


import warnings
warnings.filterwarnings("ignore")

import pandas as pd
df = pd.read_pickle('/Users/Lenovo/Desktop/notebook/NHL/concatenated_data.pkl')


FinalDf = df[['Game_time','Period','X','Y','Shot_distance','Shot_angle','Type','Previous_event_type',
               'Previous_x','Previous_y','Previous_time_since','Previous_distance' ,
       'Rebound_angle', 'Speed','Goal']]


# Étape 1 : Sélection des colonnes de type "objet" dans le DataFrame
donnees_objet = df.select_dtypes(include=['object']).copy()

# Étape 2 : Suppression des colonnes de type "objet" du DataFrame principal
donnees_numeriques = df.drop(donnees_objet.columns, axis=1)

# Étape 3 : Encodage des données catégorielles avec l'encodeur de libellé (Label Encoder)
encodeur_libelle = preprocessing.LabelEncoder()
donnees_objet_encodes = donnees_objet.apply(encodeur_libelle.fit_transform)

df=pd.concat([FinalDf,donnees_objet_encodes],axis=1)


correlation_mat = FinalDf.corr()
#sn.cubehelix_palette(as_cmap=True, reverse=True)
svm=sn.heatmap(correlation_mat, annot = True,cmap='rocket_r')

plt.savefig('correlation.png', dpi=400)

X = df.drop('Goal',axis=1)
y = df['Goal'].to_numpy()
X_train, x_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=0)
exp = Experiment(
    api_key=COMET_API_KEY,
    project_name='ift6758',
    workspace='imenjaoua',
)
exp.set_name('Question5/Q1')
X_train_q1 = X_train[['Shot_distance', 'Shot_angle']].to_numpy().reshape(-1, 2)
X_val_q1 = x_val[['Shot_distance', 'Shot_angle']].to_numpy().reshape(-1, 2)

xgb_q1= XGBClassifier().fit(X_train_q1, y_train)
# Calcul des scores d'entraînement et de validation
score_entrainement = xgb_q1.score(X_train_q1, y_train)
score_validation = xgb_q1.score(X_val_q1, y_val)

# Prédiction sur l'ensemble de validation
predictions_validation = xgb_q1.predict(X_val_q1)


# Afficher le rapport de classification
rapport_classification = classification_report(y_val, predictions_validation)
print(rapport_classification)

# Afficher les scores de précision
print(f'Précision d\'entraînement : {score_entrainement}')
print(f'Précision de validation : {score_validation}')

# Calculer et afficher le score ROC AUC
score_roc_auc = roc_auc_score(y_val, predictions_validation)
print("ROC AUC : ", score_roc_auc)


# Enregistrer les métriques dans l'expérience Comet.ml
exp.log_metrics({'Précision d\'entraînement': score_entrainement, 'Précision de validation': score_validation, 
                 'ROC AUC': score_roc_auc})

# Terminer l'expérience Comet.ml
exp.end()


#supprimer peiod
#dataPrepReport 