# Welcome to My Vivino
***

## Task

The goal of this project is to collect and analyze wine data from Vivino to understand whether there is a relationship between wine prices and customer ratings.

The main challenge was collecting real-world data, cleaning it, finding useful patterns, and using statistical methods to understand the relationships between different features.

I also wanted to build a recommendation system that could suggest similar wines based on their characteristics.

## Description

I started by collecting wine data from Vivino using Python and saved it into a CSV file containing 720 wines and 13 columns.

After collecting the data, I used Pandas to check for missing values, duplicates, and incorrect data. I then used Matplotlib to create graphs showing wine prices, ratings, wine types, countries, and other features.

To investigate the relationship between price and customer rating, I used Pearson and Spearman correlation tests. The results showed a moderate positive relationship, meaning that more expensive wines generally received higher ratings in my dataset.

I also developed two content-based recommendation models using Scikit-learn.

- **Model 1:** Uses one-hot encoding and cosine similarity to recommend wines based on wine type, country, and region.
- **Model 2:** Improves the first model by assigning different weights to the features: 60% for wine type, 25% for country, and 15% for region.

I evaluated both models using all 720 wines. Model 1 achieved a 94.08% same-type recommendation rate, while Model 2 achieved 100%.

This project helped me practice web scraping, data cleaning, data visualization, statistical analysis, and machine learning techniques.

## Installation

The project was developed using Python and Jupyter Notebook.

First, clone the repository:

```bash
git clone <repository-url>
cd my_vivino
```

Install the required Python libraries:

```bash
pip install pandas numpy matplotlib scipy scikit-learn jupyter requests
```

Then start Jupyter Notebook:

```bash
jupyter notebook
```

Open the project's `.ipynb` notebook to explore the analysis and recommendation systems.

## Usage

The project is divided into two main parts: data collection and data analysis.

**1. Data Collection**

The Python scraping script collects wine information from Vivino and saves it into a CSV file called `vivino_wines.csv`.

The dataset contains information such as:

- Wine name and winery
- Wine type
- Country and region
- Price
- Average customer rating
- Number of customer ratings

**2. Data Analysis**

Open the Jupyter Notebook and run the cells in order.

The notebook will display graphs, descriptive statistics, correlation results, and the recommendation models.

**3. Wine Recommendation System**

To get five similar wines using Model 1:

```python
recommend_wines(0)
```

To get five similar wines using the improved Model 2:

```python
recommend_weighted_wines(0)
```

The number represents the index of the wine in the dataset.

Both functions return five recommended wines along with their wine type, country, region, and similarity score.

**4. Model Evaluation**

To compare the recommendation models:

```python
model_1_score = evaluate_model(recommend_wines)
model_2_score = evaluate_model(recommend_weighted_wines)

print(model_1_score)
print(model_2_score)
```

The evaluation calculates how often each model recommends wines of the same type as the original wine.

### The Core Team


<span><i>Made at <a href='https://qwasar.io'>Qwasar SV -- Software Engineering School</a></i></span>
<span><img alt='Qwasar SV -- Software Engineering School's Logo' src='https://storage.googleapis.com/qwasar-public/qwasar-logo_50x50.png' width='20px' /></span>
