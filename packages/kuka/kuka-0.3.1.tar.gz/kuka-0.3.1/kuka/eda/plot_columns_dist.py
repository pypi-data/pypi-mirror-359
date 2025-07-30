import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from ..utils import _input_function_validation

from ..utils.plot import _plot_text, _adjust_obj_to_ref

_input_val_dict = {
	'df' : ( pd.DataFrame, None ),
	'ncols' : ( int, 'range', [0, np.inf] ),
	'plotsize' : ( (tuple, list), 'length', 2 )
	}

@_input_function_validation(_input_val_dict)
def plot_columns_dist(
	df:pd.DataFrame,
    ncols:int = 3,
	plotsize:list = list(plt.rcParams['figure.figsize']*np.array([0.5,0.35]))
	) -> tuple[Figure, Axes]:

	'''
    Plot a grid of distributions for each column in a DataFrame.

    This function automatically detects the type of each column and chooses the appropriate plot:
    - Numerical (float-compatible) columns are displayed using histograms.
    - Non-numerical (object/categorical) columns are shown as bar plots with value counts.

    It organizes all plots into a structured subplot grid, and includes automatic font size adjustments
    and label abbreviation to avoid label overlaps, especially for categorical variables.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset. Each column will be plotted individually based on its data type.

    ncols : int, default=3
        Number of columns in the subplot grid.

    plotsize : list or array-like of length 2, optional
        Base size multiplier for each subplot. The final figure size will be:
        (plotsize[0] * ncols, plotsize[1] * nrows), where nrows is inferred from the number of columns.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The overall figure object containing all subplots.

    ax : numpy.ndarray of matplotlib.axes.Axes
        A 2D array of axes corresponding to the subplot grid.

    Example
    -------
	```python
    import pandas as pd
    from mylib.plotting import plot_columns_dist
    df = pd.read_csv("data.csv")
    fig, ax = plot_columns_dist(df, ncols=4, plotsize=[3, 2])
	```

	
	'''

	# 1 - recognize the numeric columns
	float_df_columns = []
	object_df_columns = []
	for i in df.columns:
		try:
			df[i] = df[i].astype(float)
		except ValueError:
			df[i] = df[i].astype(object)
			object_df_columns += [i] ###############
		else:
			float_df_columns += [i]

	nrows = math.ceil(len(df.columns)/ncols)
	fig, ax = plt.subplots( 
		ncols = ncols, 
		nrows = nrows,
		figsize = (plotsize[0]*ncols, plotsize[1]*nrows)
		)
	
	i, j = (0, 0) # row and col
	for col in df.columns:

		if (j==ncols): 
			i += 1
			j = 0

		axis = ax[i][j]

		if col in float_df_columns:
			axis.hist(df[col])
			axis.set_xlabel('Values')
			axis.set_ylabel('Frequency')
		else:
			axis.bar(
				df[col].value_counts().index,
				df[col].value_counts().values,
			)
			axis.set_ylabel('Frequency')
			
			# Dealing with large labels
			_adjust_obj_to_ref(
				fig,
				axis.get_xticklabels(),
				[axis],
				'w',
				steps = ['decrease_fontsize']*3 + ['reset_fontsize', 'abbreviate_or_remove_tick_labels'],
				threshold=0.8,
				tick_ax=axis,
				)

		axis.set_title(col)
		j += 1
	# clear the remaining axis
	for pos in np.arange(len(df.columns)%ncols, ncols):
		axis = ax[i][pos]
		axis.remove()

	fig.tight_layout()

	return fig, ax