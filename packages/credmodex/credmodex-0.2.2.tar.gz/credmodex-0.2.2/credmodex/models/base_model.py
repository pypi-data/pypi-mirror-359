import pandas as pd
import numpy as np
import inspect
from typing import Union, Literal
import warnings
import os
from pprint import pprint, pformat

import plotly.subplots

from sklearn.linear_model import LogisticRegression
from scipy.stats import chi2_contingency

from credmodex.rating import Rating
from credmodex.discriminancy import *
from credmodex.utils import *


class BaseModel:
    """
    Base class for all models with advanced splitting functionality.
    """

    def __init__(self, model:type=None, treatment:type=None, df:pd.DataFrame=None, seed:int=42, id:str='id', doc:str=None,
                 features=None, target=None, predict_type:str=None, time_col:str=None, name:str=None, n_features:int=None):
        if (df is None):
            raise ValueError("DataFrame cannot be None. Input a DataFrame.")
            
        if (model is None):
            model = LogisticRegression(max_iter=10000, solver='saga')

        if (treatment is None):
            treatment = lambda df: df

        if isinstance(features,str):
            self.features = [features]
        else:
            self.features = features
        self.features = [f for f in features 
                         if f in df.columns 
                         and f != target 
                         and f != time_col
                         and f != 'id']

        if (n_features is None):
            self.n_features = len(self.features)
        else:
            self.n_features = n_features

        self.seed = seed
        np.random.seed(self.seed)

        self.model = model
        self.treatment = treatment
        self.df = df.copy(deep=True)
        self.doc = doc
        self.id = 'id'
        self.target = target
        self.time_col = time_col
        self.name = name
        self.predict_type = predict_type

        self.ratings = {}

        if callable(self.model):
            self.model_code = inspect.getsource(self.model)
        else:
            self.model_code = None

        if callable(self.treatment):
            self.treatment_code = inspect.getsource(self.treatment)
        else:
            self.treatment_code = None

        if callable(self.doc):
            self.doc = inspect.getsource(self.doc)
        else:
            self.doc = None

        self.train_test_()
        self.fit_predict()


    def train_test_(self):
        try:
            self.train = self.df[self.df['split'] == 'train']
            self.test = self.df[self.df['split'] == 'test']

            transformed_features = [col for col in self.df.columns if col not in ['split', self.target, self.time_col]]
            self.features = transformed_features
            self.n_features = len(transformed_features)

            self.X_train = self.df[self.df['split'] == 'train'][self.features]
            self.X_test = self.df[self.df['split'] == 'test'][self.features]
            self.y_train = self.df[self.df['split'] == 'train'][self.target]
            self.y_test = self.df[self.df['split'] == 'test'][self.target]
        except:
            if not getattr(self, 'suppress_warnings', False):
                warnings.warn(
                    'No column ["split"] was found, therefore, the whole `df` will be used in training and testing',
                    category=UserWarning
                )
            self.train = self.df
            self.test = self.df

            transformed_features = [col for col in self.df.columns if col not in ['split', self.target, self.time_col]]
            self.features = transformed_features
            self.n_features = len(transformed_features)

            self.X_train = self.df[self.features]
            self.X_test = self.df[self.features]
            self.y_train = self.df[self.target]
            self.y_test = self.df[self.target]


    def fit_predict(self):
        self.df = self.treatment(self.df).copy(deep=True)
        self.train_test_()
        predict_type = self.predict_type.lower().strip() if isinstance(self.predict_type, str) else None

        if ('func' in predict_type) or callable(self.model):
            self.df = self.model(self.df).copy(deep=True)
            return

        self.model = self.model.fit(self.X_train, self.y_train)

        if predict_type and ('prob' in predict_type):
            if hasattr(self.model, 'predict_proba'):
                self.df['score'] = self.model.predict_proba(self.df[self.features])[:,0]
                self.df['score'] = self.df['score'].apply(lambda x: round(x,6))
                return 
            elif hasattr(self.model, 'decision_function'):
                scores = self.model.decision_function(self.df[self.features])
                self.df['score'] = scores
                self.df['score'] = self.df['score'].round(6)
                return
            else:
                raise AttributeError("Model doesn't support probability prediction.")
        
        if (predict_type is None) or ('raw' in predict_type):
            if hasattr(self.model, 'predict'):
                preds = self.model.predict(self.df[self.features])
                self.df['score'] = preds
                self.df['score'] = self.df['score'].round(6)
                return
            else:
                raise AttributeError("Model doesn't support raw predictions.")

        else:
            raise SystemError('No ``predict_type`` available')
    

    def predict(self, df_):
        df_ = self.treatment(df_).copy(deep=True)
        predict_type = self.predict_type.lower().strip() if isinstance(self.predict_type, str) else None

        if ('func' in predict_type) or callable(self.model):
            df_ = self.model(df_).copy(deep=True)
            return df_

        if predict_type and ('prob' in predict_type):
            if hasattr(self.model, 'predict_proba'):
                df_['score'] = self.model.predict_proba(df_[self.features])[:,0]
                df_['score'] = df_['score'].apply(lambda x: round(x,6))
                return df_
            elif hasattr(self.model, 'decision_function'):
                scores = self.model.decision_function(df_[self.features])
                df_['score'] = scores
                df_['score'] = df_['score'].round(6)
                return df_
            else:
                raise AttributeError("Model doesn't support probability prediction.")
        
        if (predict_type is None) or ('raw' in predict_type):
            if hasattr(self.model, 'predict'):
                preds = self.model.predict(df_[self.features])
                df_['score'] = preds
                df_['score'] = df_['score'].round(6)
                return df_
            else:
                raise AttributeError("Model doesn't support raw predictions.")

        else:
            raise SystemError('No ``predict_type`` available')
    

    def add_rating(self, model:type=None, doc:str=None, type='score', optb_type:str='transform', name:str=None,
                   time_col:str=None):
        if (name is None):
            name = f'{model.__class__.__name__}_{len(self.ratings)+1}'
        if (time_col is None):
            time_col = self.time_col
        
        rating = Rating(
            model=model, df=self.df, type=type, features=['score'], target=self.target, 
            optb_type=optb_type, doc=doc, time_col=time_col, name=name
            )
        self.ratings[name] = rating
        setattr(self, name, rating)
        
        # Set the self.rating to the last one defined
        self.rating = rating
        
        return model

    def eval_goodness_of_fit(self, method:Union[str,type]='gini', rating:Union[type]=None,
                             comparison_cols:list[str]=[]):
        if rating is None:
            try: rating = self.rating
            except: raise ModuleNotFoundError('There is no model to evaluate!')
        
        if isinstance(method, str): method = method.lower().strip()

        eval_methods = {
            'iv': IV_Discriminant,
            'ks': KS_Discriminant,
            'psi': PSI_Discriminant,
            'gini': GINI_Discriminant,
            'corr': Correlation,
            'good': GoodnessFit,
        }

        # Single method execution
        if method != 'relatory':
            for key, func in eval_methods.items():
                if (key in method) or (method == func):
                    try: return func(df=rating.df, target=self.target, features=['rating'])
                    except: return func
            
        if ('relatory' in method):
            self.rating.plot_gains_per_risk_group().show()
            self.rating.plot_stability_in_time().show()
            try: KS_Discriminant(df=rating.df, target=self.target, features=['rating']).plot().show()
            except: ...
            try: PSI_Discriminant(df=rating.df, target=self.target, features=['rating']).plot().show()
            except: ...
            print('\n=== Kolmogorov Smirnov ===')
            print(KS_Discriminant(df=rating.df, target=self.target, features=['rating']+comparison_cols).table())
            print('\n=== Population Stability ===')
            print(PSI_Discriminant(df=rating.df, target=self.target, features=['rating']+comparison_cols).table())
            print('\n=== Information Value ===')
            print(IV_Discriminant(df=rating.df, target=self.target, features=['rating']+comparison_cols).table())


    def model_relatory_pdf(self, rating:Union[type]=None, add_rating:bool=True,
                           comparison_cols:list[str]=[], pdf=None, save_pdf:bool=True):
        try:
            from credmodex.utils import pdf_report
        except ImportError as e:
            raise ImportError("PDF generation requires `fpdf`. Please install it with `pip install fpdf`.") from e
        
        if (pdf is None):
            pdf = pdf_report.PDF_Report()
        else: ...

        pdf.add_page()

        try:
            ks = KS_Discriminant(df=self.df, target=self.target, features=['score'] + comparison_cols)

            pdf.chapter_title('Kolmogorov Smirnov')
            pdf.add_dataframe_split(ks.table(), chunk_size=5)

            fig = ks.plot()
            fig.update_layout(margin=dict(l=70, r=70, t=70, b=70))
            img_path = pdf.save_plotly_to_image(fig)
            pdf.add_image(img_path)
            os.remove(img_path)
        except Exception as e:
            pdf.chapter_df(f"<log> KS failed: {str(e)}")

        try:
            psi = PSI_Discriminant(df=self.df, target=self.target, features=['score'] + comparison_cols, enable_oot=True)

            pdf.chapter_title('Population Stability Index')
            pdf.add_dataframe_split(psi.table(), chunk_size=5)

            fig = psi.plot(add_min_max=[0, 1],)
            fig.update_layout(margin=dict(l=70, r=70, t=70, b=70))
            img_path = pdf.save_plotly_to_image(fig)
            pdf.add_image(img_path)
            os.remove(img_path)
        except Exception as e:
            pdf.chapter_df(f"<log> PSI failed: {str(e)}")

        try:
            gini = GINI_Discriminant(df=self.df, target=self.target, features=['score'] + comparison_cols)

            pdf.chapter_title('Gini Lorenz Coefficient and Variability')
            gini_var = GoodnessFit.gini_variance(y_pred=self.df['score'], y_true=self.df[self.target], info=True)
            pdf.chapter_df(pformat(gini_var))

            fig = gini.plot()
            fig.update_layout(margin=dict(l=70, r=70, t=70, b=70))
            img_path = pdf.save_plotly_to_image(fig)
            pdf.add_image(img_path, w=120)
            os.remove(img_path)
        except Exception as e:
            pdf.chapter_df(f"Plotting failed for {GINI_Discriminant.__name__}: {str(e)}")

        try:
            iv = IV_Discriminant(df=self.df, target=self.target, features=['score'] + comparison_cols)

            pdf.chapter_title('Information Value')
            pdf.add_dataframe_split(iv.table(), chunk_size=5)
        except Exception as e:
            pdf.chapter_df(f"IV Table failed: {str(e)}")

        try:
            hosmer = GoodnessFit.hosmer_lemeshow(y_pred=self.df['score'], y_true=self.df[self.target], info=True)
            pdf.chapter_title('Hosmer Lemeshow')
            pdf.chapter_df(pformat(hosmer))
        except Exception as e:
            pdf.chapter_df(f"Hosmer Lemeshow failed: {str(e)}")

        try:
            deviance = GoodnessFit.deviance_odds(y_pred=self.df['score'], y_true=self.df[self.target], info=True)
            deviance.pop('conclusion', None)
            pdf.chapter_title('Deviance Odds')
            pdf.chapter_df(pformat(deviance))
        except Exception as e:
            pdf.chapter_df(f"Deviance Odds failed: {str(e)}")


        if (add_rating == True) and (len(self.ratings.items()) >= 1):
                
            for key, rating in self.ratings.items():
                pdf.reference_name_page = f'{self.name} {rating.name}'
                pdf.add_chapter_rating_page(text1=rating.name, text2=self.name)
                pdf.add_page()
                pdf.main_title(f'Rating | {rating.name}')

                try:
                    pdf.chapter_title('Basic Analysis | Whole Population')
                    fig_gains = rating.plot_gains_per_risk_group(split=['train','oot','test'])['data']
                    fig_stab = rating.plot_stability_in_time(split=['train','oot','test'])['data']
                    fig_stab_ = rating.plot_stability_in_time(split=['train','oot','test'], agg_func='count', percent=False, stackgroup=True)['data']
                    fig_ks = KS_Discriminant(rating.df, target=self.target, features='rating').plot()['data']

                    fig = plotly.subplots.make_subplots(
                        rows=2, cols=2,
                        subplot_titles=(
                            'Gains por Risk Group', 
                            'Kolmogorov-Smirnov Discriminant',
                            f'Stability in Time | Metric',
                            'Stability in Time | Volumetry',
                        ),
                        vertical_spacing=0.1,
                        horizontal_spacing=0.05,
                        y_title='percent [%] | volume [*]', 
                    )
                    for fig_ in fig_gains:
                        fig_.showlegend = False 
                        fig.add_trace(fig_, row=1, col=1)
                    for fig_ in fig_ks:
                        fig.add_trace(fig_, row=1, col=2)
                    for fig_ in fig_stab:
                        fig_.showlegend = False 
                        fig.add_trace(fig_, row=2, col=1)
                    for fig_ in fig_stab_:
                        fig_.showlegend = False 
                        fig.add_trace(fig_, row=2, col=2)

                    plotly_main_subplot_layout(fig, title=f'Basic Rating Evaluation | Train+Test', height=1000)
                    fig.update_layout(margin=dict(l=70, r=70, t=70, b=70))
                    img_path = pdf.save_plotly_to_image(fig)
                    pdf.add_image(img_path, w=190)
                    os.remove(img_path)
                except Exception as e:
                    pdf.chapter_df(f"<log> gains and stability in time failed: {str(e)}")

                try:
                    psi = PSI_Discriminant(df=rating.df, target=rating.target, features=['rating'] + comparison_cols, enable_oot=True)

                    fig = psi.plot(col='rating', discrete=True, sort=True,)
                    fig.update_layout(margin=dict(l=70, r=70, t=70, b=70))
                    img_path = pdf.save_plotly_to_image(fig)
                    pdf.add_image(img_path)
                    os.remove(img_path)
                except Exception as e:
                    pdf.chapter_df(f"<log> PSI failed: {str(e)}")

                try:
                    pdf.chapter_title('Basic Analysis | Out of Time')
                    fig_gains = rating.plot_gains_per_risk_group(split=['oot'])['data']
                    fig_stab = rating.plot_stability_in_time(split=['oot'])['data']
                    fig_stab_ = rating.plot_stability_in_time(split=['oot'], agg_func='count', percent=False, stackgroup=True)['data']
                    fig_ks = KS_Discriminant(rating.df[rating.df['split'] == 'oot'], target=self.target, features='rating').plot()['data']

                    fig = plotly.subplots.make_subplots(
                        rows=2, cols=2,
                        subplot_titles=(
                            'Gains por Risk Group', 
                            'Kolmogorov-Smirnov Discriminant',
                            f'Stability in Time | Metric',
                            'Stability in Time | Volumetry',
                        ),
                        vertical_spacing=0.1,
                        horizontal_spacing=0.05,
                        y_title='percent [%] | volume [*]', 
                    )
                    for fig_ in fig_gains:
                        fig_.showlegend = False 
                        fig.add_trace(fig_, row=1, col=1)
                    for fig_ in fig_ks:
                        fig.add_trace(fig_, row=1, col=2)
                    for fig_ in fig_stab:
                        fig_.showlegend = False 
                        fig.add_trace(fig_, row=2, col=1)
                    for fig_ in fig_stab_:
                        fig_.showlegend = False 
                        fig.add_trace(fig_, row=2, col=2)

                    plotly_main_subplot_layout(fig, title=f'Basic Rating Evaluation | Out of Time', height=1000)
                    fig.update_layout(margin=dict(l=70, r=70, t=70, b=70))
                    img_path = pdf.save_plotly_to_image(fig)
                    pdf.add_image(img_path, w=190)
                    os.remove(img_path)
                except Exception as e:
                    pdf.chapter_df(f"<log> no out of time information available to use!: {str(e)}")

                try:
                    pdf.chapter_title('Information Value')
                    iv = IV_Discriminant(df=rating.df, target=rating.target, features=['rating'] + comparison_cols)

                    pdf.add_dataframe_split(iv.table(), chunk_size=5)
                except Exception as e:
                    pdf.chapter_df(f"IV Table failed: {str(e)}")

        if (save_pdf == True):
            pdf.output(f"{self.name}_report.pdf")
        else:
            return pdf
        

    def eval_best_rating(self, sort:str=None, split:Literal['train','test','oot']=None):
        
        metrics_dict = {}

        for rating_name, rating in self.ratings.items():
            if (split is not None):
                y_true = rating.df[self.df['split'] == split][rating.target]
                y_pred = rating.df[self.df['split'] == split]['rating']
                dff = rating.df[self.df['split'] == split].copy(deep=True)
            else:
                y_true = rating.df[rating.target]
                y_pred = rating.df['rating']
                dff = rating.df.copy(deep=True)

            try: iv = IV_Discriminant(dff, rating.target, ['rating']).value('rating', final_value=True)
            except: iv = np.nan
            try: ks = KS_Discriminant(dff, rating.target, ['rating']).value('rating', final_value=True)
            except: ks = np.nan
            try: psi = PSI_Discriminant(dff, rating.target, ['rating']).value('rating', final_value=True)
            except: psi = np.nan
            try: gini = GINI_Discriminant(dff, rating.target, ['rating']).value('rating', final_value=True)/100; auc = round((gini+1)/2, 4)
            except: gini = np.nan; auc = np.nan

            contingency_table = pd.crosstab(y_pred, y_true)
            chi2_stat, p_val_chi2, _, _ = chi2_contingency(contingency_table)
            if (p_val_chi2 < 0.05): chi2 = 'Significant Discr.'
            else: chi2 = 'No Significant Discr.'

            y_true = dff[rating.target]
            y_pred = dff.groupby('rating')[self.target].transform('mean')

            hosmer_lemershow = GoodnessFit.hosmer_lemeshow(y_true=y_true, y_pred=y_pred, info=True)['conclusion']
            log_likelihood = GoodnessFit.log_likelihood(y_true=y_true, y_pred=y_pred)
            aic = GoodnessFit.aic(y_true=y_true, y_pred=y_pred, n_features=self.n_features)
            bic = GoodnessFit.bic(y_true=y_true, y_pred=y_pred, n_features=self.n_features, sample_size=len(self.df))
            wald_test = GoodnessFit.wald_test(y_true=y_true, y_pred=y_pred, info=True)['conclusion']
            deviance_odds = GoodnessFit.deviance_odds(y_true=y_true, y_pred=y_pred, info=True)['power']

            metrics_dict[f'{self.name}.{rating_name}'] = {
                'iv': round(iv,4),
                'ks': round(ks,4),
                'psi': round(psi,4),
                'auc': round(auc,4),
                'gini': round(gini,4),
                'chi2': chi2,
                'wald test': wald_test,
                'log-likelihood': round(log_likelihood,1),
                'aic': round(aic,1),
                'bic': round(bic,1),
            }

        # Create DataFrame and transpose it so rating names are columns
        dff = pd.DataFrame(metrics_dict)
        dff.loc['relative likelihood',:] = GoodnessFit.relative_likelihood(aic_values=list(dff.loc['aic',:].values))
        dff = dff.loc[['relative likelihood'] + [i for i in dff.index if i != 'relative likelihood']]

        try:
            sort = sort.lower()
            if (sort is not None) and (sort in [s.lower() for s in dff.index]):
                dff = dff.T.sort_values(by=sort, ascending=False).T
        except:
            ...

        return dff
