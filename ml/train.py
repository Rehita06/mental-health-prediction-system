# ml/train.py
import os, json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix, roc_auc_score

try:
    from xgboost import XGBClassifier
    XGB_OK = True
except Exception:
    XGB_OK = False

def build_preprocessor(X):
    num_cols = X.select_dtypes(include=['number']).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]
    num_tf = Pipeline([('imputer', SimpleImputer(strategy='median'))])
    cat_tf = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                       ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    pre = ColumnTransformer([('num', num_tf, num_cols), ('cat', cat_tf, cat_cols)])
    return pre, num_cols, cat_cols

def get_models(random_state=42):
    models = {
        'logreg': LogisticRegression(max_iter=1000),
        'rf': RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1)
    }
    if XGB_OK:
        models['xgb'] = XGBClassifier(n_estimators=200, random_state=random_state, use_label_encoder=False, eval_metric='logloss')
    return models

def evaluate(model, X_test, y_test, positive_label=None):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    try:
        p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', pos_label=positive_label)
    except Exception:
        p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    try:
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X_test)
            classes = list(model.classes_)
            if positive_label is None:
                positive_label = classes[-1]
            pos_idx = classes.index(positive_label)
            auc = roc_auc_score((y_test == positive_label).astype(int), proba[:, pos_idx])
        else:
            auc = None
    except Exception:
        auc = None
    cm = confusion_matrix(y_test, y_pred)
    return {'accuracy': acc, 'precision': p, 'recall': r, 'f1': f1, 'auc': auc, 'cm': cm.tolist()}

def train_and_save(csv_path, target='treatment', models_dir='models', random_state=42):
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found in CSV columns: {list(df.columns)}")
    y = df[target]
    X = df.drop(columns=[target])
    # Normalize y to Yes/No if strings
    # Normalize y and encode
    if y.dtype == 'O':
        y = y.fillna('Unknown')
        y = y.replace({'yes':'Yes','no':'No','Yes':'Yes','No':'No',1:'Yes',0:'No',True:'Yes',False:'No'})
        if y.nunique() > 2:
            top2 = y.value_counts().index[:2].tolist()
            y = y.where(y.isin(top2), top2[0])

    # Encode labels as 0/1
    if y.dtype == 'O' or y.dtype.name == 'category':
        label_map = {'No': 0, 'Yes': 1}
        y = y.map(label_map).fillna(0).astype(int)
        positive_label = 1
    else:
        positive_label = 1 if 1 in y.unique() else None

    pre, num_cols, cat_cols = build_preprocessor(X)
    models = get_models(random_state)
    best = None; best_name=None; best_f1=-1; results={}

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=random_state)
    for name, clf in models.items():
        pipe = Pipeline([('pre', pre), ('clf', clf)])
        f1s = []
        for tr, va in skf.split(X, y):
            pipe.fit(X.iloc[tr], y.iloc[tr])
            yhat = pipe.predict(X.iloc[va])
            try:
                _,_,f1,_ = precision_recall_fscore_support(y.iloc[va], yhat, average='binary', pos_label=positive_label)
            except Exception:
                _,_,f1,_ = precision_recall_fscore_support(y.iloc[va], yhat, average='weighted')
            f1s.append(f1)
        results[name] = {'cv_f1': float(sum(f1s)/len(f1s))}
        if sum(f1s)/len(f1s) > best_f1:
            best_f1 = sum(f1s)/len(f1s)
            best = pipe
            best_name = name

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=random_state)
    best.fit(X_tr, y_tr)
    metrics = evaluate(best, X_te, y_te, positive_label=positive_label)
    model_path = Path(models_dir)/'best_model.joblib'
    joblib.dump(best, model_path)
    meta = {'best_model': best_name, 'target': target, 'positive_label': positive_label,
            'raw_feature_names': X.columns.tolist(), 'numeric_features': num_cols, 'categorical_features': cat_cols,
            'test_metrics': metrics, 'cv_results': results}
    with open(Path(models_dir)/'metadata.json','w') as f:
        json.dump(meta,f,indent=2)
    return str(model_path), meta

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--target', default='treatment')
    ap.add_argument('--models_dir', default='models')
    args = ap.parse_args()
    p, meta = train_and_save(args.csv, target=args.target, models_dir=args.models_dir)
    print('Saved model to', p)
    print('Metadata:', meta)
