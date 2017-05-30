import pandas as pd
import numpy as np
from sklearn import model_selection
from sklearn.metrics import accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
import os 


def processing(pos): 
    workdata = pd.read_csv('dicts/' + pos + '_crossdict_ss.csv', header=None, encoding='utf-8-sig', delimiter='\t')
    X_work =  workdata._get_numeric_data()

    try:
        model_name = pos+'-model.save'
        log_reg_work(X_work, model_name, pos)        
        print('Using model:', model_name)
        
    except FileNotFoundError:
        model_name = log_reg_train(part_of_speech)        
        log_reg_work(X_work, model_name, part_of_speech)        
        print('Create model:', model_name)


def log_reg_train(pos):
    dataset =  pd.read_csv('sk-learn-'+part_of_speech+'.csv', encoding='utf-8-sig',delimiter='\t')
    X = dataset[['komi_len', 'udm_len', 'lev', 'sem_sim']]    
    y = dataset['res']    
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.25)
    
    model_lr = LogisticRegression()
    model_lr.fit(X_train,y_train)
    
    y_test_predict_proba = model_lr.predict_proba(X_test)
    y_test_predict = model_lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_test_predict)
    print('Accuracy = %.3f'%accuracy)

    model_name = pos+'-model.save'
    joblib.dump(model_lr, model_name)
    return model_name


def log_reg_work(X_work, model_name, part_of_speech):
    model_lr = joblib.load(model_name)

    y_work_predict_proba = model_lr.predict_proba(X_work)
    y_work_predict = model_lr.predict(X_work)    
    
    f_in = open('dicts/'+pos+'_crossdict_ss.csv', 'r', encoding='utf-8-sig').readlines()   
    f_out = open('dicts/'+pos+'_crossdict_res.csv', 'a', encoding='utf-8-sig')
    
    for line in f_in[:]:
        n = f_in.index(line)
        line=line.strip('\n')
        f_out.write('\t'.join([line, str(y_work_predict_proba[n][1]),str(y_work_predict[n])])+'\n')
    f_out.close()
    
