"""
Signal operations module for Fourier Series Classification.

This module provides functions for signal operations such as adding noise
and extracting jump information from signals.
"""

import numpy as np

def add_noise(y, noise_param, x):
    """
    Add Gaussian noise to a signal.
    
    Parameters
    ----------
    y : array-like
        Signal values
    noise_param : float
        Noise level parameter
    x : array-like
        Domain points (used for determining the size)
        
    Returns
    -------
    array-like
        Signal with added noise
    """
    return y + (np.random.normal(0, noise_param, len(x)))

def extract_jump(x, y, a):
    """
    Extract jump information from a signal.
    
    Parameters
    ----------
    x : array-like
        Domain points
    y : array-like
        Signal values
    a : float
        Jump location parameter
        
    Returns
    -------
    array-like
        Jump function values
    """
    fk = np.zeros(len(x))
    h = x[1] - x[0]
    
    # Find jump locations
    jumpsx = x[np.abs(x+a) <= h/2][0], x[np.abs(x-a) <= h/2][0]
    
    # Get values to the left and right of jumps
    lefty = {}
    righty = {}
    lefty[jumpsx[0]] = y[np.abs(x-(jumpsx[0]-h)) < h/2][0]
    lefty[jumpsx[1]] = y[np.abs(x-(jumpsx[1]-h)) < h/2][0]
    righty[jumpsx[0]] = y[np.abs(x-(jumpsx[0]+h)) < h/2][0]
    righty[jumpsx[1]] = y[np.abs(x-(jumpsx[1]+h)) < h/2][0]
    
    # Determine jump values
    jL = righty[jumpsx[0]]
    jR = righty[jumpsx[1]]
    
    if np.abs(lefty[jumpsx[0]]) > np.abs(righty[jumpsx[0]]):
        jL = lefty[jumpsx[0]] * -1
    if np.abs(lefty[jumpsx[1]]) > np.abs(righty[jumpsx[1]]):
        jR = lefty[jumpsx[1]] * -1
    
    # Set jump values in output array
    if len(x[np.abs(x-a) <= h/2]) == 1:
        fk[np.abs(x+a) <= h/2] = jL
        fk[np.abs(x-a) <= h/2] = jR
    else:
        fk[np.abs(x+a) <= h/2][0] = jL
        fk[np.abs(x-a) <= h/2][0] = jR
    
    return fk
