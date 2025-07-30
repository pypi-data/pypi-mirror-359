# 관련 라이브러리 호출
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from sklearn import metrics


# 회귀 모델의 성능 지표 반환 함수
def regmetrics(y_true: np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
    '''
    이 함수는 회귀 모델의 다양한 성능 지표를 계산합니다.
    
    매개변수:
        y_true: 목표변수의 실제값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
        y_pred: 목표변수의 추정값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
    
    반환:
        회귀 모델의 다양한 성능 지표를 데이터프레임으로 반환합니다.
        실제값과 추정값이 음수일 때 RMSLE는 결측값으로 채웁니다.
    '''
    MSE = metrics.mean_squared_error(
        y_true = y_true, 
        y_pred = y_pred
    )
    
    RMSE = metrics.root_mean_squared_error(
        y_true = y_true, 
        y_pred = y_pred
    )
    
    minus_count = pd.Series(data = y_pred).lt(0).sum()
    
    if minus_count > 0:
        MSLE = None
        RMSLE = None
    else:
        MSLE = metrics.mean_squared_log_error(
            y_true = y_true, 
            y_pred = y_pred
        )
        
        RMSLE = metrics.root_mean_squared_log_error(
            y_true = y_true, 
            y_pred = y_pred
        )
    
    MAE = metrics.mean_absolute_error(
        y_true = y_true, 
        y_pred = y_pred
    )
    
    MAPE = metrics.mean_absolute_percentage_error(
        y_true = y_true, 
        y_pred = y_pred
    )
    
    result = pd.DataFrame(
        data = [MSE, RMSE, MSLE, RMSLE, MAE, MAPE], 
        index = ['MSE', 'RMSE', 'MSLE', 'RMSLE', 'MAE', 'MAPE']
    ).T
    
    return result


# 분류 모델의 성능 지표 반환 함수
def clfmetrics(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    '''
    이 함수는 분류 모델의 다양한 성능 지표를 계산합니다.
    
    매개변수:
        y_true: 목표변수의 실제값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
        y_pred: 목표변수의 추정값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
    
    반환:
        분류 모델의 다양한 성능 지표를 출력합니다.
    '''    
    print('▶ Confusion Matrix')
    
    cfm = pd.crosstab(
        index = y_pred, 
        columns = y_true, 
        margins = True
    )
    
    cfm.index.name = 'Pred'
    cfm.columns.name = 'Real'
    display(cfm)
    
    print()
    print('▶ Classification Report')
    print(
        metrics.classification_report(
            y_true = y_true, 
            y_pred = y_pred, 
            digits = 4
        )
    )


# 분류 모델의 분류 기준점별 성능 지표 계산(TPR, FPR, Matthew's Correlation coefficient)
def clfCutoffs(y_true: np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
    '''
    이 함수는 분류 모델에 대한 최적의 분류 기준점을 탐색합니다.
    
    매개변수:
        y_true: 목표변수의 실제값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
        y_pred: 목표변수의 추정값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
    
    반환:
        분류 모델의 분류 기준점별로 TPR, FPR, MCC 등을 반환합니다.
    '''
    cutoffs = np.linspace(0, 1, 101)
    sens = []
    spec = []
    prec = []
    mccs = []
    
    for cutoff in cutoffs:
        pred = np.where(y_prob >= cutoff, 1, 0)
        clfr = metrics.classification_report(
            y_true = y_true, 
            y_pred = pred, 
            output_dict = True, 
            zero_division = True
        )
        sens.append(clfr['1']['recall'])
        spec.append(clfr['0']['recall'])
        prec.append(clfr['1']['precision'])
        
        mcc = metrics.matthews_corrcoef(
            y_true = y_true, 
            y_pred = pred
        )
        mccs.append(mcc)
        
    result = pd.DataFrame(
        data = {
            'Cutoff': cutoffs, 
            'Sensitivity': sens, 
            'Specificity': spec, 
            'Precision': prec, 
            'MCC': mccs
        }
    )
    
    # The Optimal Point is the sum of Sensitivity and Specificity.
    result['Optimal'] = result['Sensitivity'] + result['Specificity']
    
    # TPR and FPR for ROC Curve.
    result['TPR'] = result['Sensitivity']
    result['FPR'] = 1 - result['Specificity']
    
    # Set Column name.
    cols = ['Cutoff', 'Sensitivity', 'Specificity', 'Optimal', \
            'Precision', 'TPR', 'FPR', 'MCC']

    # Select columns
    result = result[cols]
    
    return result


# 최적의 분류 기준점 시각화 함수
def EpiROC(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    '''
    이 함수는 분류 모델에 대한 최적의 분류 기준점을 ROC 곡선에 추가합니다.
    
    매개변수:
        y_true: 목표변수의 실제값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
        y_pred: 목표변수의 추정값을 pd.Series 또는 1차원 np.ndarray로 지정합니다.
    
    반환:
         ROC 곡선 그래프 외에 반환하는 객체는 없습니다.
    '''    
    obj = clfCutoffs(y_true, y_prob)
    
    # Draw ROC curve
    sns.lineplot(
        data = obj, 
        x = 'FPR', 
        y = 'TPR', 
        color = 'black'
    )

    # Add title
    plt.title(label = '최적의 분류 기준점 탐색', 
              fontdict = {'fontweight': 'bold'})
    
    # Draw diagonal line
    plt.plot(
        [0, 1], 
        [0, 1], 
        color = '0.5', 
        linestyle = '--', 
        linewidth = 0.5
    )
    
    # Add the Optimal Point
    opt = obj.iloc[[obj['Optimal'].argmax()]]
    
    sns.scatterplot(
        data = opt, 
        x = 'FPR', 
        y = 'TPR', 
        color = 'red'
    )
    
    # Add tangent line
    optX = opt['FPR'].iloc[0]
    optY = opt['TPR'].iloc[0]
    
    b = optY - optX
    
    plt.plot(
        [0, 1-b], 
        [b, 1], 
        color = 'red', 
        linestyle = '-.', 
        linewidth = 0.5
    )
    
    # Add text
    plt.text(
        x = opt['FPR'].values[0] - 0.01, 
        y = opt['TPR'].values[0] + 0.01, 
        s = f"Cutoff = {opt['Cutoff'].round(2).values[0]}", 
        ha = 'right', 
        va = 'bottom'
    );


## End of Document