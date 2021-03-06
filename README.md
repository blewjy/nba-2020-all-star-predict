# Predicting the 2020 NBA All-Stars with Machine Learning

## Introduction

This personal project was done by myself in Nov 2019, as part of a Machine Learning course. The goal of this project was to predict the NBA All-Stars for the upcoming 2020 NBA All-Star game using only in-game statistics of past seasons and the current season.

This `README` will give a brief summary of this project, setup instructions for training and prediction code, and also the results. For a full report that has explanations, justifications, graphs, tables and numbers, please refer to `report.pdf` in this repo.

## Project Summary

### Target Problem

Every year, out of the 400 over NBA players across all 30 NBA teams, the top 24 players (12 per conference) will be selected to play in the annual NBA All-Star game as part of the NBA All-Star weekend festivities. These selected players are usually the best performing players for the first half of that season, and performance of these players can be determined by their in-game statistics. With Machine Learning, this project aims to use past years' data and statistics, and perform binary classification on the dataset to predict the probability of the player being an All-Star that season.

### Algorithms

Three different algorithms were used for this project, namely **Decision Trees with Boosting**, **Support Vector Machines**, and **Neural Networks**. All of the algorithms were implemented with the `scikit-learn` library. Please refer to `report.pdf` for the performance of these models and how they compare against each other. 

### Results

While **Decision Trees with Boosting** had the best performance out of the three algorithms (by a slim margin), all three of them performed relatively similar to each other. I decided to use the average (normalized) probabilities predicted by each of these algorithms for the final result:

*(Ran prediction on 31st Jan 2020)*

| **East**              |     |       | **West**           |     |       |
| --------------------- | --- | ----- | ------------------ | --- | ----- |
| **Starters:**         |     |       | **Starters:**      |     |       |
| Giannis Antetokounmpo | PF  | 1.0   | James Harden       | SG  | 0.997 |
| Trae Young            | PG  | 0.965 | Luka Dončić        | PG  | 0.994 |
| Pascal Siakam         | PF  | 0.96  | Kawhi Leonard      | SF  | 0.993 |
| Joel Embiid           | C   | 0.956 | Anthony Davis      | PF  | 0.993 |
| Bradley Beal          | SG  | 0.948 | Nikola Jokić       | C   | 0.968 |
| **Reserves:**         |     |       | **Reserves:**      |     |       |
| Jimmy Butler          | SF  | 0.921 | LeBron James       | PG  | 0.993 |
| Kyle Lowry            | PG  | 0.886 | Russell Westbrook  | PG  | 0.981 |
| Kemba Walker          | PG  | 0.883 | Damian Lillard     | PG  | 0.979 |
| Domantas Sabonis      | C   | 0.856 | Donovan Mitchell   | SG  | 0.952 |
| Jayson Tatum          | PF  | 0.842 | Paul George        | SF  | 0.858 |
| Zach LaVine           | SG  | 0.83  | Rudy Gobert        | C   | 0.834 |
| Khris Middleton       | SF  | 0.826 | Karl-Anthony Towns | C   | 0.812 |

> NOTE: These results are purely based on statistics of the players. There are many other non-statistical factors that come into play when it comes to All-Star selection, including narrative, fan-popularity, etc. These factors are very difficult to capture using numbers, and hence the results here do not tell the whole story. Nevertheless, statistics is usually a reliable reflection of the player's performance and popularity, which is convenient for us in this case. 

> [Finalized 2020 NBA All-Star Roster](https://www.nba.com/allstar/2020/roster#/)

## Running the code

### Environment 

This project was done using Python 3.7.5

I have included a `requirements.txt` which lists all the pip libraries used for this project. 

You are recommended to create a new virtual environment and install all dependencies with 

```
pip install -r requirements.txt
```

### Quick Start

If you just want to clone and run the predictions, make sure you have either setup the virtual environment as above or have already install the dependencies, and do

```
git clone https://github.com/blewjy/nba-2020-all-star-predict.git
cd nba-2020-all-star-predict
python predict.py
```

This will print out the predictions for the 2020 All-Stars with my pre-trained models in `models/`.

### Getting the data

> NOTE: You really don't have to scrap for years 2019 and before, because the stats will not change. You could scrap for 2020 to update to the latest available stats though.

All the data is obtained from *basketball-reference.com*. I wrote a basic web scraper to scrap the data required, specifically the split data for each NBA season for all players that are active before the All Star Game (ASG) of each season. 

- `data/bb_ref.py` contains all the API for the scraping.
- `data/scrap.py` is a script to scrap all data for a specific season
- `data/process_data.py` is a script to convert all the JSON scraped into csv file suitable for our training algorithms

To run the scraper for a specific year (for e.g. 2020), navigate to the `data` folder and run:

```
cd data
python scrap.py 2020
```

You should see that the latest data for the players will be saved as a JSON file in `raw/2020.json`.

Then, to convert these into appropriate csv format:

```
python process_data.py
```

The converted csv file will be in `processed/2020.csv`.

### Training the models

> NOTE: If you just want to run the predictions with my pre-trained models, skip to "Getting the predictions"

The main code for the training of the models is in `train.py`. You can perform the training (including hyperparameter tuning) with:

```
python train.py
```

Running `train.py` will run the grid search cross validation for all three methods (SVM, Decision trees with AdaBoost, and Neural Networks) one by one, and all graphs and table related to this cross validation step will be generated and saved into `figures/`.

The models themselves will be saved and exported as a `.joblib` file into `models/`

The final scores (test score, F1 score, etc) will be saved into `final_scores.json`.

> NOTE: `train.py` takes 20min to run on my 2017 MBP 13-inch.

### Getting the predictions

To predict the All-Stars for 2020, simply run:

```
python predict.py
```

The predicted 2020 All-Stars will be printed onto the console.

## Acknowledgements

This project was inspired by *dribbleanalytics.blog*, who has a lot of NBA and data analytics related content.