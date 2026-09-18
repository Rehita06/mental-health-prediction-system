# Mental Health Prediction System

A machine learning-powered web application built with Django that predicts whether an individual is likely to seek mental health treatment based on workplace and personal survey responses.

> **Academic Project:** This application is intended for educational and research purposes only and is not a medical diagnostic or clinical decision-making tool.

---

## 📌 Overview

Mental health in the workplace is an important area of concern, particularly for people working in the technology industry.

This project uses machine learning to analyze survey responses related to workplace environment, personal background, mental health awareness, and access to support.

The trained machine learning model is integrated into a Django web application where users can:

- Create an account
- Log in securely
- Enter survey information
- Receive a machine learning prediction
- View their prediction results
- Access the application through a web interface

The project also includes Django REST Framework components and an administration interface.

---

## 🎯 Objectives

The main objectives of this project are:

1. Build a machine learning model for mental health treatment prediction.
2. Compare multiple classification algorithms.
3. Select the best-performing model using cross-validation.
4. Integrate the trained model into a Django web application.
5. Provide a simple web interface for entering survey responses.
6. Display prediction results to users.
7. Demonstrate the integration of machine learning with a full-stack web application.

---

## ✨ Features

- User registration and authentication
- Login and logout functionality
- Mental health prediction form
- Machine learning-based prediction
- Pre-trained Random Forest model
- Model metadata storage
- Django web application
- Django REST Framework integration
- Authentication token support
- Admin interface
- User prediction results
- Responsive HTML templates
- Separate machine learning training pipeline

---

## 🧠 Machine Learning

The project evaluates multiple classification algorithms:

### Models Used

- Logistic Regression
- Random Forest
- XGBoost

The models are evaluated using **3-fold stratified cross-validation** with F1-score as the model-selection metric.

The current training pipeline selected **Random Forest** as the best model based on cross-validation F1-score.

### Cross-Validation Results

| Model | F1 Score |
|---|---:|
| Logistic Regression | 72.50% |
| Random Forest | 75.03% |
| XGBoost | 73.99% |

The final model is then evaluated using a stratified train/test split.

---

## 📊 Model Performance

The current Random Forest model achieved the following test-set results:

| Metric | Score |
|---|---:|
| Accuracy | 74.60% |
| Precision | 76.67% |
| Recall | 71.88% |
| F1 Score | 74.19% |
| ROC-AUC | 81.12% |

### Confusion Matrix

```text
                  Predicted
                 Negative Positive

Actual Negative     96       28
Actual Positive     36       92
