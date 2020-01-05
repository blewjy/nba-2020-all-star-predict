import random
import time
import json
import numpy as np
from joblib import dump
from sklearn import svm, metrics
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

"""
Set seed for reproducible results
"""
np.random.seed(6969)
random.seed(6969)

"""
Training data set will be some subset of seasons.
Testing data set will be the remaining seasons.
"""
def load_data(balance=False, oversample=True):
  all_data = []
  for season in range(1985, 2020):
    if season == 1999:
      continue
    data = np.genfromtxt("./data/processed/" + str(season) + ".csv",delimiter=',',dtype=float)
    all_data.append(data)
  
  all_index = range(len(all_data))
  num_seasons_for_testing = int(len(all_data)*0.15)
  test_season_indices = random.sample(all_index, num_seasons_for_testing)
  train_season_indices = [i for i in all_index if not i in test_season_indices]
  train_seasons = [all_data[i] for i in train_season_indices]
  test_seasons = [all_data[i] for i in test_season_indices]
  train_data = np.vstack(train_seasons)
  test_data = np.vstack(test_seasons)
  train_X = train_data[:,:-1].astype(float)
  train_Y = train_data[:,-1].reshape(-1,1)
  test_X = test_data[:,:-1].astype(float)
  test_Y = test_data[:,-1].reshape(-1,1)

  train_X = np.nan_to_num(train_X)
  test_X = np.nan_to_num(test_X)
  
  as_count = 0
  non_count = 0
  for y in train_Y:
    if y == 0:
      non_count += 1
    else:
      as_count +=1
  print("Train dataset has: {} All-Stars, {} non All-Stars".format(non_count, as_count))

  as_count = 0
  non_count = 0
  for y in test_Y:
    if y == 0:
      non_count += 1
    else:
      as_count +=1  
  print("Test dataset has: {} All-Stars, {} non  All-Stars".format(non_count, as_count))

  return train_X, train_Y, test_X, test_Y

def gen_graph(results, key, x_label, y_label, filename):
  x = []
  for r in results["params"]:
    x.append(r[key])
  scores = results["mean_test_score"]

  import matplotlib.pyplot as plt

  plt.plot(x, scores)
  plt.xlabel(x_label)
  plt.ylabel(y_label)
  plt.savefig("./figures/{}".format(filename))
  plt.close()

def gen_table(results, widths, filename):
  params = results["params"]
  scores = results["mean_test_score"]
  mean_fit_time = results["mean_fit_time"]
  mean_score_time = results["mean_score_time"]
  mean_time = [sum(x) for x in zip(mean_fit_time, mean_score_time)]
  headers = list(params[0].keys()) + ["Score (Accuracy)", "Mean Time Taken per Fold (s)"]
  all_values = []
  for i, p in enumerate(params):
    s = round(scores[i],5)
    t = round(mean_time[i],5)
    values = list(p.values()) + [s, t]
    all_values.append(values)

  import matplotlib.pyplot as plt 
  from matplotlib.font_manager import FontProperties

  fig = plt.figure()
  ax = fig.add_subplot(111)

  # Draw table
  the_table = plt.table(cellText=all_values,
                        colWidths=widths,
                        rowLabels=None,
                        colLabels=headers,
                        loc='center')
  the_table.auto_set_font_size(False)
  the_table.set_fontsize(8)
  the_table.scale(1, 1)

  # Removing ticks and spines enables you to get the figure only with table
  plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
  plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
  for pos in ['right','top','bottom','left']:
    plt.gca().spines[pos].set_visible(False)
  for (row, col), cell in the_table.get_celld().items():
    if (row == 0):
        cell.set_text_props(fontproperties=FontProperties(weight='bold', size=8))
        cell.set_facecolor("lightGray")
  plt.savefig("./figures/{}".format(filename))
  plt.close()

def gen_confusion_matrix(model, test_X, test_Y, title, filename):
  import matplotlib.pyplot as plt
  np.set_printoptions(suppress=True)
  disp = metrics.plot_confusion_matrix(model, test_X, test_Y, cmap=plt.cm.Blues, normalize=None)
  disp.ax_.set_title("Confusion Matrix: {}".format(title))
  plt.savefig("./figures/{}".format(filename))
  plt.close()

def run_svm_grid_search(train_X, train_Y, test_X, test_Y, model_name):
  start = time.time()

  param_grid = {
    'C': [0.1, 1, 10, 100, 1000],  
    'gamma': [1, 0.1, 0.01, 0.001, 0.0001]
  }
    
  grid = GridSearchCV(
    svm.SVC(random_state=6969, kernel="rbf", probability=True), 
    param_grid, 
    refit=True, 
    cv=3, 
    verbose=3, 
    n_jobs=-1
  )

  # fitting the model for grid search 
  grid.fit(train_X, train_Y.ravel())

  end = time.time()
  elapsed = round(end - start, 3)

  pred_Y = grid.predict(test_X)
  print(metrics.classification_report(test_Y, pred_Y))

  # plot the table
  gen_table(grid.cv_results_, [0.2, 0.2, 0.3, 0.45], "svm_table.png")

  # save the model
  dump(grid, './models/{}.joblib'.format(model_name)) 

  # get scores
  scores = get_scores(grid, test_X, test_Y)

  # confusion matrix
  gen_confusion_matrix(grid, test_X, test_Y, "SVM", "svm_cm")

  return grid.best_params_, scores, elapsed
  
def run_adaboost_grid_search(train_X, train_Y, test_X, test_Y, model_name): 
  start = time.time()
  best_params = {}

  param_grid = {
    'n_estimators': [10, 100, 500, 1000],
    'learning_rate': [0.1, 0.01, 0.001]
  }
    
  grid = GridSearchCV(
    AdaBoostClassifier(random_state=6969, base_estimator=DecisionTreeClassifier(max_depth=5)), 
    param_grid, 
    refit=True, cv=3, verbose=3, n_jobs=-1
  )

  # fitting the model for grid search  
  grid.fit(train_X, train_Y.ravel())
  best_n_estimators = grid.best_params_["n_estimators"]
  best_learning_rate = grid.best_params_["learning_rate"]

  end = time.time()
  elapsed1 = round(end - start, 3)

  # plot the table
  gen_table(grid.cv_results_, [0.2, 0.2, 0.3, 0.45], "abc_table.png")

  # update best params
  best_params.update(grid.best_params_)

  start = time.time()

  param_grid = {
    'base_estimator__max_depth': [1, 2, 5, 8, 10, 15]
  }

  grid = GridSearchCV(
    AdaBoostClassifier(
      random_state=6969, 
      base_estimator=DecisionTreeClassifier(),
      n_estimators=best_n_estimators, 
      learning_rate=best_learning_rate
    ), 
    param_grid, 
    refit=True, cv=3, verbose=3, n_jobs=-1
  )
    
  # fitting the model for grid search 
  grid.fit(train_X, train_Y.ravel())

  end = time.time()
  elapsed2 = round(end - start, 3)

  pred_Y = grid.predict(test_X)
  print(metrics.classification_report(test_Y, pred_Y))

  # plot the graph
  gen_graph(grid.cv_results_, "base_estimator__max_depth", "Max Depth of Tree", "Cross Validation Score (Accuracy)", "abc_graph.png")

  # update best params
  best_params.update(grid.best_params_)

  # save the model
  dump(grid, './models/{}.joblib'.format(model_name)) 

  # get scores
  scores = get_scores(grid, test_X, test_Y)

  # confusion matrix
  gen_confusion_matrix(grid, test_X, test_Y, "Decision Trees with AdaBoost", "abc_cm")

  return best_params, scores, elapsed1 + elapsed2

def run_nn_grid_search(train_X, train_Y, test_X, test_Y, model_name):
  start = time.time()

  best_params = {}

  hidden_layers = [(50, 50, 50), (100, 100, 100), (200, 200, 200), (300, 300, 300), (50, 50, 50, 50), (100, 100, 100, 100), (200, 200, 200, 200), (300, 300, 300, 300)]

  param_grid = {
    'learning_rate_init': [0.1, 0.01, 0.001, 0.0001]
  }

  grid = GridSearchCV(
    MLPClassifier(random_state=6969, max_iter=1000), 
    param_grid, 
    refit=True, cv=3, verbose=3, n_jobs=-1
  )
  
  # fitting the model for grid search  
  grid.fit(train_X, train_Y.ravel())
  best_learning_rate_init = grid.best_params_["learning_rate_init"]

  end = time.time()
  elapsed1 = round(end - start, 3)

  # plot the graph
  gen_graph(grid.cv_results_, "learning_rate_init", "Learning Rate", "Cross Validation Score (Accuracy)", "nn_graph.png")

  # update best params
  best_params.update(grid.best_params_)

  start = time.time()

  param_grid = {
    'hidden_layer_sizes': hidden_layers
  }

  grid = GridSearchCV(
    MLPClassifier(random_state=6969, max_iter=1000, learning_rate_init=best_learning_rate_init), 
    param_grid, 
    refit=True, cv=3, verbose=3, n_jobs=-1
  )
  
  # fitting the model for grid search 
  grid.fit(train_X, train_Y.ravel())

  end = time.time()
  elapsed2 = round(end - start, 3)

  pred_Y = grid.predict(test_X)
  print(metrics.classification_report(test_Y, pred_Y))

  # plot the table
  gen_table(grid.cv_results_, [0.3, 0.3, 0.45], "nn_table.png")

  # update best params
  best_params.update(grid.best_params_)

  # save the model
  dump(grid, './models/{}.joblib'.format(model_name)) 

  # get scores
  scores = get_scores(grid, test_X, test_Y)

  # confusion matrix
  gen_confusion_matrix(grid, test_X, test_Y, "Neural Networks", "nn_cm")

  return best_params, scores, elapsed1 + elapsed2

def get_scores(model, test_X, test_Y):
  pred_Y = model.predict(test_X)
  
  test_acc = round(metrics.accuracy_score(test_Y, pred_Y), 3)
  recall = round(metrics.recall_score(test_Y, pred_Y), 3)
  precision = round(metrics.precision_score(test_Y, pred_Y), 3)
  f1 = round(metrics.f1_score(test_Y, pred_Y), 3)
  cv_score = cross_val_score(model, test_X, test_Y.ravel(), cv=3, scoring="accuracy")
  cv_score_mean = round(cv_score.mean(), 3)
  cv_score_ci = round(cv_score.std()*2, 3)
  
  return {
    "test_acc": test_acc,
    "recall": recall,
    "precision": precision,
    "f1": f1,
    "cv_score_mean": cv_score_mean,
    "cv_score_ci": cv_score_ci 
  }

train_X, train_Y, test_X, test_Y = load_data()

results = {}

model_name = "svm"
best_params, scores, elapsed = run_svm_grid_search(train_X, train_Y, test_X, test_Y, model_name)
results[model_name] = {
  "params": best_params, 
  "scores": scores,
  "time": elapsed
}

model_name = "abc"
best_params, scores, elapsed = run_adaboost_grid_search(train_X, train_Y, test_X, test_Y, model_name)
results[model_name] = {
  "params": best_params, 
  "scores": scores,
  "time": elapsed
}

model_name = "nn"
best_params, scores, elapsed = run_nn_grid_search(train_X, train_Y, test_X, test_Y, model_name)
results[model_name] = {
  "params": best_params, 
  "scores": scores,
  "time": elapsed
}

# Write to file
with open('final_scores.json', 'w') as fp:
  json.dump(results, fp, sort_keys=True, indent=2, separators=(',', ': '))
