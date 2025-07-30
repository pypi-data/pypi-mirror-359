import os
import sys

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

from typing import Union, Literal

sys.path.append(os.path.abspath('..'))
from graphmodex import plotlymodex


__all__ = [
    'frequency'
]


def frequency(df:pd.DataFrame, x:str, covariate:str=None, bin_size:int=1, colors:Union[list, str]=None,
              histnorm:Literal[None, 'probability density']='probability density', categorical:bool=None,
              show_curve:bool=True, show_hist:bool=True, show_rug:bool=False, opacity:float=0.8,
              min_max:bool=True, sort_x:bool=True, layout_kwargs:dict=None, bar_kwargs:dict=None, marker_kwargs:dict=None) -> go.Figure:
    
    if df is None:
        raise ValueError("DataFrame cannot be None")
    df = df.copy()
    
    if x not in df.columns:
        raise ValueError(f"Column '{x}' not found in DataFrame")
    
    if (covariate is not None) and (covariate not in df.columns):
        raise ValueError(f"Covariate '{covariate}' not found in DataFrame")

    categorical = pd.api.types.is_object_dtype(df[x]) or \
                  isinstance(df[x], pd.CategoricalDtype)

    if categorical:
        try:
            sorted_categories = sorted(df[x].dropna().unique().tolist())
            df[x] = pd.Categorical(df[x], categories=sorted_categories, ordered=True)
            df = df.sort_values(by=x)
        except Exception as e:
            ...
            
        # This is used in case of categorical with covariates
        if (covariate is not None):
            grouped = df.groupby([x, covariate], observed=False).size().reset_index(name='count')
            fig = go.Figure()

            for i, group in enumerate(grouped[covariate].unique()):
                sub_data = grouped[grouped[covariate] == group]
                fig.add_trace(go.Bar(
                    x=sub_data[x], y=sub_data['count'],
                    name=str(group), marker_color=colors[i] if colors and i < len(colors) else None,
                    marker=marker_kwargs, **(bar_kwargs or {})
                ))
                
        # This is used in case of categorical without covariates
        else:
            counts = df[x].value_counts().reset_index()
            if sort_x:
                counts = counts.sort_values(by=f'{x}')
            counts.columns = [x, 'count']
            fig = go.Figure(data=[go.Bar(
                x=counts[x], y=counts['count'],
                name='freq',
                marker_color=colors[0] if colors else 'rgba(0, 0, 0, 0.9)',
                marker=marker_kwargs, **(bar_kwargs or {})
            )])
            fig.update_layout(showlegend=False)

        plotlymodex.main_layout(fig, y='frequency', x=f'{x}', title=f'Frequency of {x}', barcornerradius=10, **(layout_kwargs or {}))

        for trace in fig.data:
            trace.marker.opacity = opacity

        return fig

    else:
        # This is used in case of continuous with covariates
        if (covariate is not None):
            group_labels = df[f'{covariate}'].unique().tolist()
            grouped_data = [df[df[f'{covariate}'] == cov][f'{x}'] for cov in group_labels]
            if min_max:
                for idx in range(len(grouped_data)):
                    grouped_data[idx] = pd.concat([grouped_data[idx], pd.Series([df[f'{x}'].min(), df[f'{x}'].max()])])
        # This is used in case of continuous without covariates
        else:
            group_labels = [x]
            grouped_data = [df[f'{x}']]
        
        if isinstance(colors, str):
            colors = [colors]
        if covariate is not None and isinstance(colors, list):
            if (len(colors) < len(covariate)):
                colors = colors + px.colors.qualitative.D3[:len(group_labels)]

        fig = ff.create_distplot(
            hist_data=grouped_data, group_labels=group_labels, bin_size=bin_size, 
            colors=colors, histnorm=histnorm,
            show_curve=show_curve, show_hist=show_hist, show_rug=show_rug
        )

        plotlymodex.main_layout(fig, y='frequency', x=f'{x}', title=f'Frequency of {x}', **(layout_kwargs or {}))

        for trace in fig.data:
            trace.marker.opacity = opacity

        # This is used in case of continuous without covariates
        if covariate is None:
            fig.layout.showlegend = False
            for trace in fig.data:
                if colors is None:
                    trace.marker.color = 'black'

        return fig