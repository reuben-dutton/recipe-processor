import pickle
import os
import sys

sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor

from training.metrics import pipelines
from training import utils


NUM_LAYERS = 6


ingredientMapPath = "data/mappings/map.csv"
ingredientMapDF = pd.read_csv(ingredientMapPath)
ingredientMapDF = ingredientMapDF.drop_duplicates()
ingredientMapDF['NAME'] = ingredientMapDF['ingredient'].apply(utils.normalizeTokens)

with open("models/metric/encoding/ingredient_targets.npy", 'rb') as f:
    y_train = np.load(f, allow_pickle=True)

ingr_pipeline = pipelines.get_ingr_pipeline()

x_train = ingr_pipeline.fit_transform(ingredientMapDF[['NAME']])

ingr_dim = x_train.shape[1]

with open("models/metric/encoding/ingr_preprocess_pipeline.pkl", 'wb') as p:
    pickle.dump(ingr_pipeline, p)

regressor = MLPRegressor(hidden_layer_sizes=[ingr_dim+5 for i in range(NUM_LAYERS)], verbose=False,)

regressor.fit(x_train, y_train)

with open("models/metric/space-regressor.pkl", 'wb') as p:
    pickle.dump(regressor, p)