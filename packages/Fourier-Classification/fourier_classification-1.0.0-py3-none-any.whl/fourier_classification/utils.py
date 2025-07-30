"""
Utility functions for Fourier Series Classification.

This module provides utility functions for data handling, preprocessing,
and other common operations.
"""

import numpy as np
import os
import pickle

def save_model(model, filepath):
    """
    Save a trained model to disk.
    
    Parameters
    ----------
    model : tensorflow.keras.models.Model
        Model to save
    filepath : str
        Path to save the model
        
    Returns
    -------
    str
        Path where the model was saved
    """
    model.save(filepath)
    return filepath

def load_model(filepath):
    """
    Load a trained model from disk.
    
    Parameters
    ----------
    filepath : str
        Path to the saved model
        
    Returns
    -------
    tensorflow.keras.models.Model
        Loaded model
    """
    from tensorflow.keras.models import load_model as tf_load_model
    return tf_load_model(filepath)

def save_data(data, filepath):
    """
    Save data to disk using pickle.
    
    Parameters
    ----------
    data : object
        Data to save
    filepath : str
        Path to save the data
        
    Returns
    -------
    str
        Path where the data was saved
    """
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    return filepath

def load_data(filepath):
    """
    Load data from disk using pickle.
    
    Parameters
    ----------
    filepath : str
        Path to the saved data
        
    Returns
    -------
    object
        Loaded data
    """
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def create_domain(start=-np.pi, end=np.pi, num_points=1500):
    """
    Create a domain array for signal generation.
    
    Parameters
    ----------
    start : float
        Start of the domain
    end : float
        End of the domain
    num_points : int
        Number of points in the domain
        
    Returns
    -------
    array-like
        Domain array
    """
    return np.linspace(start, end, num_points + 1)[:-1]

def create_labels(signal_types, num_per_type):
    """
    Create labels for generated signals.
    
    Parameters
    ----------
    signal_types : list of str
        List of signal types
    num_per_type : int
        Number of signals per type
        
    Returns
    -------
    array-like
        Labels array
    """
    labels = []
    for i, signal_type in enumerate(signal_types):
        labels.extend([i] * num_per_type)
    return np.array(labels)

def normalize_signal(signal):
    """
    Normalize a signal to the range [-1, 1].
    
    Parameters
    ----------
    signal : array-like
        Signal to normalize
        
    Returns
    -------
    array-like
        Normalized signal
    """
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        return signal / max_val
    return signal

def ensure_directory(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Parameters
    ----------
    directory : str
        Directory path
        
    Returns
    -------
    str
        Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def prepare_dataset(signal_types, num_per_type, domain, fourier=False, jump=False, 
                    n_modes=40, noise=False, noise_parameter=0.1):
    """
    Prepare a dataset of signals for classification.
    
    Parameters
    ----------
    signal_types : list of str
        List of signal types to generate
    num_per_type : int
        Number of signals per type
    domain : array-like
        Domain points for signal generation
    fourier : bool
        Whether to generate Fourier coefficients
    jump : bool
        Whether to include jump information
    n_modes : int
        Number of Fourier modes
    noise : bool
        Whether to add noise to signals
    noise_parameter : float
        Noise level parameter
        
    Returns
    -------
    tuple
        Dataset of signals and labels
    """
    from fourier_classification.signals import (
        generate_signals, SIGNAL_TYPES
    )
    
    signals = []
    labels = []
    
    for i, signal_type in enumerate(signal_types):
        if signal_type not in SIGNAL_TYPES:
            raise ValueError(f"Unknown signal type: {signal_type}")
        
        signal_data = generate_signals(
            signal_type, domain, num_per_type, 
            fourier=fourier, jump=jump, n_modes=n_modes,
            noise=noise, noise_parameter=noise_parameter
        )[0]
        
        signals.extend(signal_data)
        labels.extend([i] * num_per_type)
    
    return np.array(signals), np.array(labels)
