"""
Visualization module for Fourier Series Classification.

This module provides functions for visualizing signals, Fourier coefficients,
and classification results.
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_signal(x, y, title="Signal", xlabel="x", ylabel="y", figsize=(10, 6)):
    """
    Plot a signal using matplotlib.
    
    Parameters
    ----------
    x : array-like
        Domain points
    y : array-like
        Signal values
    title : str
        Plot title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    return fig

def plot_signals_comparison(x, signals_dict, title="Signals Comparison", figsize=(12, 8)):
    """
    Plot multiple signals for comparison using matplotlib.
    
    Parameters
    ----------
    x : array-like
        Domain points
    signals_dict : dict
        Dictionary of signal names and values
    title : str
        Plot title
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for name, signal in signals_dict.items():
        ax.plot(x, signal, label=name)
    
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()
    
    return fig

def plot_fourier_coefficients(coeffs, title="Fourier Coefficients", figsize=(10, 6)):
    """
    Plot Fourier coefficients using matplotlib.
    
    Parameters
    ----------
    coeffs : array-like
        Fourier coefficients
    title : str
        Plot title
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    n = len(coeffs)
    k = np.linspace(-n//2, n//2, n)
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.stem(k, np.abs(coeffs), use_line_collection=True)
    ax.set_title(title)
    ax.set_xlabel("k")
    ax.set_ylabel("|c_k|")
    ax.grid(True)
    
    return fig

def plot_signal_and_fourier(x, signal, coeffs, title="Signal and Fourier Coefficients", figsize=(12, 10)):
    """
    Plot a signal and its Fourier coefficients using matplotlib.
    
    Parameters
    ----------
    x : array-like
        Domain points
    signal : array-like
        Signal values
    coeffs : array-like
        Fourier coefficients
    title : str
        Plot title
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    n = len(coeffs)
    k = np.linspace(-n//2, n//2, n)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # Plot signal
    ax1.plot(x, signal)
    ax1.set_title("Signal")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.grid(True)
    
    # Plot Fourier coefficients
    ax2.stem(k, np.abs(coeffs), use_line_collection=True)
    ax2.set_title("Fourier Coefficients")
    ax2.set_xlabel("k")
    ax2.set_ylabel("|c_k|")
    ax2.grid(True)
    
    fig.suptitle(title)
    fig.tight_layout()
    
    return fig

def plot_signal_with_jumps(x, signal, jumps, title="Signal with Jumps", figsize=(12, 10)):
    """
    Plot a signal and its jump information using matplotlib.
    
    Parameters
    ----------
    x : array-like
        Domain points
    signal : array-like
        Signal values
    jumps : array-like
        Jump function values
    title : str
        Plot title
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # Plot signal
    ax1.plot(x, signal)
    ax1.set_title("Signal")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.grid(True)
    
    # Plot jumps
    ax2.plot(x, jumps)
    ax2.set_title("Jump Function")
    ax2.set_xlabel("x")
    ax2.set_ylabel("Jump Value")
    ax2.grid(True)
    
    fig.suptitle(title)
    fig.tight_layout()
    
    return fig

def plot_confusion_matrix(confusion_matrix, class_names=None, title="Confusion Matrix", figsize=(10, 8)):
    """
    Plot a confusion matrix using matplotlib.
    
    Parameters
    ----------
    confusion_matrix : array-like
        Confusion matrix
    class_names : list of str, optional
        Names of the classes
    title : str
        Plot title
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    if class_names is None:
        class_names = [f"Class {i}" for i in range(confusion_matrix.shape[0])]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(confusion_matrix, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    # Show all ticks and label them with class names
    ax.set(xticks=np.arange(confusion_matrix.shape[1]),
           yticks=np.arange(confusion_matrix.shape[0]),
           xticklabels=class_names, yticklabels=class_names,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')
    
    # Rotate the tick labels and set their alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Loop over data dimensions and create text annotations
    fmt = 'd'
    thresh = confusion_matrix.max() / 2.
    for i in range(confusion_matrix.shape[0]):
        for j in range(confusion_matrix.shape[1]):
            ax.text(j, i, format(confusion_matrix[i, j], fmt),
                    ha="center", va="center",
                    color="white" if confusion_matrix[i, j] > thresh else "black")
    
    fig.tight_layout()
    return fig

def plot_training_history(history_list, figsize=(12, 10)):
    """
    Plot training history using matplotlib.
    
    Parameters
    ----------
    history_list : list
        List of training history objects
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object
    """
    # Combine histories
    accuracy = []
    val_accuracy = []
    loss = []
    val_loss = []
    
    for history in history_list:
        accuracy.extend(history.history['accuracy'])
        if 'val_accuracy' in history.history:
            val_accuracy.extend(history.history['val_accuracy'])
        loss.extend(history.history['loss'])
        if 'val_loss' in history.history:
            val_loss.extend(history.history['val_loss'])
    
    epochs = range(1, len(accuracy) + 1)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # Plot accuracy
    ax1.plot(epochs, accuracy, 'b', label='Training accuracy')
    if val_accuracy:
        ax1.plot(epochs, val_accuracy, 'r', label='Validation accuracy')
    ax1.set_title('Training and Validation Accuracy')
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Plot loss
    ax2.plot(epochs, loss, 'b', label='Training loss')
    if val_loss:
        ax2.plot(epochs, val_loss, 'r', label='Validation loss')
    ax2.set_title('Training and Validation Loss')
    ax2.set_xlabel('Epochs')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    fig.tight_layout()
    return fig

def plot_interactive(x, y, name="Signal", mode='lines'):
    """
    Create an interactive plot trace using Plotly.
    
    Parameters
    ----------
    x : array-like
        X-axis values
    y : array-like
        Y-axis values
    name : str
        Trace name
    mode : str
        Plot mode ('lines', 'markers', 'lines+markers')
        
    Returns
    -------
    plotly.graph_objects.Scatter
        Plotly scatter trace
    """
    return go.Scatter(x=x, y=y, mode=mode, name=name)

def create_interactive_figure(title="Interactive Plot"):
    """
    Create an interactive figure using Plotly.
    
    Parameters
    ----------
    title : str
        Figure title
        
    Returns
    -------
    plotly.graph_objects.Figure
        Plotly figure
    """
    return go.Figure(layout=dict(title=title))

def add_trace_to_figure(fig, trace):
    """
    Add a trace to a Plotly figure.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Plotly figure
    trace : plotly.graph_objects.Scatter
        Plotly scatter trace
        
    Returns
    -------
    plotly.graph_objects.Figure
        Updated Plotly figure
    """
    fig.add_trace(trace)
    return fig

def create_interactive_subplots(rows, cols, titles=None, subplot_titles=None):
    """
    Create interactive subplots using Plotly.
    
    Parameters
    ----------
    rows : int
        Number of rows
    cols : int
        Number of columns
    titles : str, optional
        Figure title
    subplot_titles : list of str, optional
        Titles for each subplot
        
    Returns
    -------
    plotly.subplots.make_subplots
        Plotly subplots
    """
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles)
    if titles:
        fig.update_layout(title_text=titles)
    return fig
