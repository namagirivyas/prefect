# To run the file in terminal type > python workflow.py 
# Has to connect with Prefect cloud -> https://app.prefect.cloud/
# Prefect Login [Prefect Cloud] - https://www.prefect.io/opensource  -> get started

# Step 1: Import Required Libraries
import pandas as pd
from prefect import flow, task
from sklearn.preprocessing import MinMaxScaler

# Step 2: Load the Dataset
@task
def load_dataset():
    # Load the dataset
    #url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    df = pd.read_csv("../data/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    # column_names = ['preg', 'plas', 'pres', 'skin', 'test', 'mass', 'pedi', 'age', 'Attrition']
    return df;
    # return pd.read_csv(url, names=column_names)

# Step 3: Data Preprocessing
@task(log_prints=True)
def preprocess_data(df):
    # Print columns with missing values and their count
    missing_values = df.isna().sum()
    columns_with_missing = missing_values[missing_values > 0]
    print("Columns with missing values: ")
    print(columns_with_missing)

    # Replace with Median value
    df.fillna(df.median(), inplace=True)

    # Normalize using Min-Max Scaling
    scaler = MinMaxScaler()
    features = df.drop('Attrition', axis=1)  # Exclude the target variable
    df_normalized = pd.DataFrame(scaler.fit_transform(features), columns=features.columns)
    df_normalized['Attrition'] = df['Attrition']  # Add the target variable back to the dataframe

    # Print the normalized dataframe
    print("Normalized DataFrame:")
    print(df_normalized.head())  # Printing only the first few rows for brevity

    return df_normalized

# Step 4: Model Training
@task
def train_model(df):
    # Train your machine learning model with Logistic Regression
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    
    X = df.drop('Attrition', axis=1)
    y = df['Attrition']

    # As per requirement it should be train - 70% and test - 30%
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return accuracy

# Step 5: Define Prefect Flow
@flow(log_prints=True)
def workflow_employee_attrition():
    # step 1 = loading data
    data = load_dataset()
    # step 2 = preprocessing
    preprocessed_data = preprocess_data(data)
    # step 3 = data modeling
    accuracy = train_model(preprocessed_data)

    print("Accuracy: ", accuracy)
   
# Step 6: Run the Prefect Flow
if __name__ == "__main__":
    workflow_employee_attrition.serve(name="employee-attrition-analysis-workflow",
                      tags=["first workflow"],
                      parameters={},
                      interval=120)