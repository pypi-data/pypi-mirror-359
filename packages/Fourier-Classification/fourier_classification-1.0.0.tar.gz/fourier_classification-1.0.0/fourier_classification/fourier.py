"""
Fourier transformation module for Fourier Series Classification.

This module provides functions for Fourier series calculations, transformations,
and jump detection using concentration factors.
"""

import numpy as np

# Global variables for precomputed matrices
N_GRID = 1500
IDFT_MAT_DICT = {}
XX = np.linspace(-np.pi, np.pi, N_GRID + 1)
X = XX[0:-1]

# Spectrum type dictionary
SPECTRUM_TYPES = {'Trig': 1, 'Poly': 2, 'Exp': 3}

# Supported N-modes
N_MODES = [15, 20, 40, 45, 80, 135, 160, 320, 405, 640, 1215, 1280, 1500]

# Algorithm types
ALGORITHM_TYPES = {'ifft': 1, 'forloop': 2, 'precompute': 3}

def calculate_idft_mat():
    """
    Precompute IDFT matrices for efficient Fourier series calculation.
    
    This function calculates and stores the inverse discrete Fourier transform
    matrices for various numbers of modes in the global IDFT_MAT_DICT.
    """
    for n in N_MODES:
        n_modes = n
        idft_mat = np.zeros((N_GRID, n_modes), dtype=complex)
        nn = np.linspace(-n_modes / 2, n_modes / 2, n_modes + 1)
        for i in range(N_GRID):
            for j in range(n_modes):
                idft_mat[i][j] = np.e ** (1j * X[i] * nn[j])
        IDFT_MAT_DICT[n] = idft_mat
        
        idft_mat = np.zeros((N_GRID, n_modes-1), dtype=complex)
        for i in range(N_GRID):
            for j in range(n_modes-1):
                idft_mat[i][j] = np.e ** (1j * X[i] * nn[j])
        IDFT_MAT_DICT[n-1] = idft_mat

# Initialize IDFT matrices
calculate_idft_mat()

def dft(n, m=40):
    """
    Compute the Discrete Fourier Transform matrix.
    
    Parameters
    ----------
    n : int
        Size of the signal
    m : int
        Number of modes to compute
        
    Returns
    -------
    array-like
        DFT matrix of shape (m, n)
    """
    power = np.zeros((m, n), dtype=complex)
    xj = np.linspace(-np.pi, np.pi, n)
    for i in range(m):
        for j in range(n):
            power[i][j] = -1j * (i - m/2) * xj[j]
    dft_matrix = np.e**power
    return dft_matrix

def fourier_series(cn, x, method='precompute'):
    """
    Compute the Fourier series approximation for given coefficients.
    
    Parameters
    ----------
    cn : array-like
        Fourier coefficients
    x : array-like
        Domain points where to evaluate the series
    method : str
        Calculation method ('precompute', 'forloop', or 'ifft')
        
    Returns
    -------
    array-like
        Fourier series approximation at the given points
    """
    n = len(cn)
    
    if ALGORITHM_TYPES[method] == 3:  # precompute
        return np.dot(IDFT_MAT_DICT[n], cn).real
    elif (ALGORITHM_TYPES[method] == 2) or (n % 2 == 0):  # forloop
        fx = []
        for x_val in x:
            result = 0
            for i in range(int((-n / 2)), int((n / 2))):
                result = result + cn[int(i + (n / 2))] * (np.e ** (1j * i * x_val))
            fx.append(result.real)
        return fx
    else:  # ifft
        cn_shifted = np.zeros(len(x), dtype=complex)
        cn_shifted[0] = cn[int(n/2)]
        cn_shifted[1:int(n/2)+1] = cn[int(n/2)+1:n+1]
        cn_shifted[len(x)-int(n/2):len(x)] = cn[0:int(n/2)]
        fx = len(x) * np.fft.ifftshift(np.fft.ifft(cn_shifted))
        return fx.real

def exponential_term(x, n, sign=1):
    """
    Compute the complex exponential term e^(±i*x*n).
    
    Parameters
    ----------
    x : float
        Input value
    n : int
        Frequency
    sign : int
        Sign of the exponent (1 for positive, -1 for negative)
        
    Returns
    -------
    complex
        Complex exponential value
    """
    if sign == 1:
        return np.e**(1j*x*n)
    else:
        return np.e**(-1j*x*n)

def trigonometric_signal(n):
    """
    Compute trigonometric concentration factor.
    
    Parameters
    ----------
    n : array-like
        Frequency values
        
    Returns
    -------
    array-like
        Concentration factor values
    """
    si_pi = 1.85193705198247
    sig = np.pi * np.sin((np.pi * np.abs(n)) / (np.max(n))) / si_pi
    return sig

def polynomial_signal(n):
    """
    Compute polynomial concentration factor.
    
    Parameters
    ----------
    n : array-like
        Frequency values
        
    Returns
    -------
    array-like
        Concentration factor values
    """
    sig = (np.pi * np.abs(n) / np.max(n))
    return sig

def exponential_signal(n, n_total):
    """
    Compute exponential concentration factor.
    
    Parameters
    ----------
    n : array-like
        Frequency values
    n_total : int
        Total number of frequencies
        
    Returns
    -------
    array-like
        Concentration factor values
    """
    alpha = 2
    tau = np.linspace(1/n_total, 1-(1/n_total), 1000)
    res = tau[1] - tau[0]
    const = np.pi / (res * sum(np.e**(1/(alpha*tau*(tau-1)))))
    
    normalized_n = np.abs(n) / np.max(n)
    sig = const * normalized_n * np.e**(1/(alpha*normalized_n*(normalized_n-1)))
    
    # Handle special cases
    sig[n == 0] = 0
    sig[0] = 0
    sig[-1] = 0
    
    return sig

def partial_fourier_sum(m2, m1, x, cn, type_name='Trig'):
    """
    Compute the partial Fourier sum with concentration factors.
    
    Parameters
    ----------
    m2 : int
        Number of output points
    m1 : int
        Number of input coefficients
    x : array-like
        Domain points
    cn : array-like
        Fourier coefficients
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
        
    Returns
    -------
    array-like
        Partial Fourier sum with concentration factors
    """
    type_id = SPECTRUM_TYPES[type_name]
    n = np.linspace(-m1/2, m1/2, m1)
    d2 = np.zeros((m2-1, m1), dtype=complex)
    
    for p in range(m2-1):
        for q in range(m1-1):
            d2[p][q] = exponential_term(x[p], n[q])
    
    if type_id == 1:
        sig = trigonometric_signal(n)
    elif type_id == 2:
        sig = polynomial_signal(n)
    elif type_id == 3:
        sig = exponential_signal(n, len(cn))
    
    sn = cn * (1j * np.sign(n) * sig)
    fx = np.dot(d2, sn)
    
    return fx.real
