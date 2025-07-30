"""
Signal generation module for Fourier Series Classification.

This module provides functions for generating various types of 1D signals:
- Box/Rectangular
- Sawtooth/Ramp
- Exponential
- Sinusoidal
- Gaussian

Each function can generate either the raw signal or its Fourier coefficients,
with options for normalization, jump detection, and noise addition.
"""

import numpy as np
from fourier_classification.fourier import fourier_series
from fourier_classification.operations import add_noise, extract_jump

# Signal type dictionary for reference
SIGNAL_TYPES = {
    'Box': 1,
    'Saw': 2,
    'Exp': 3,
    'Sin': 4,
    'Gaus': 5
}

def box_signal(x, a=2, b=5, normalized=True, jump=False, type_name='Trig', 
               noise=False, noise_parameter=0.1, fourier=False, n_modes=40):
    """
    Generate a box/rectangular signal.
    
    Parameters
    ----------
    x : array-like
        Domain points where the signal is evaluated
    a : float
        Width parameter (half-width of the box)
    b : float
        Height parameter
    normalized : bool
        Whether to normalize the signal to [-1, 1]
    jump : bool
        Whether to return jump information
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
    noise : bool
        Whether to add noise to the signal
    noise_parameter : float
        Noise level parameter
    fourier : bool
        Whether to return Fourier coefficients instead of signal values
    n_modes : int
        Number of Fourier modes to use
        
    Returns
    -------
    array-like or tuple
        Signal values or Fourier coefficients, with jump information if requested
    """
    if fourier:
        k = np.linspace(int((-n_modes/2)), int((n_modes/2)), n_modes+1)
        fk_hat = np.zeros(len(k))
        fk_hat[k == 0] = (2*a*b)
        fk_hat[k != 0] = ((2*b*np.sin(a*k[k != 0]))/k[k != 0])
        y = fk_hat/(2*np.pi)

        if normalized:
            if jump:
                y = y[0:-1]/np.max(np.abs(box_signal(x, a, b, normalized=False)))
                from fourier_classification.fourier import partial_fourier_sum
                return y, partial_fourier_sum(1500, len(y), x, y, type_name)
            return y[0:-1]/np.max(np.abs(box_signal(x, a, b, normalized=False)))

        return y
    
    y = np.zeros(len(x))
    y[np.abs(x) < a] = b
    
    if noise:
        if normalized:
            y = y/np.max(abs(y))
        return add_noise(y, noise_parameter, x)
    
    if normalized:
        if jump:
            y = y / np.max(abs(y))
            fk = extract_jump(x, y, a)
            return y[0:-1], fk[0:-1]
        return y/np.max(abs(y))
    
    return y

def saw_signal(x, a=2, b=5, normalized=True, jump=False, type_name='Trig', 
               noise=False, noise_parameter=0.1, fourier=False, n_modes=40):
    """
    Generate a sawtooth/ramp signal.
    
    Parameters
    ----------
    x : array-like
        Domain points where the signal is evaluated
    a : float
        Width parameter (half-width of the sawtooth)
    b : float
        Slope parameter
    normalized : bool
        Whether to normalize the signal to [-1, 1]
    jump : bool
        Whether to return jump information
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
    noise : bool
        Whether to add noise to the signal
    noise_parameter : float
        Noise level parameter
    fourier : bool
        Whether to return Fourier coefficients instead of signal values
    n_modes : int
        Number of Fourier modes to use
        
    Returns
    -------
    array-like or tuple
        Signal values or Fourier coefficients, with jump information if requested
    """
    if fourier:
        k = np.linspace(int((-n_modes/2)), int((n_modes/2)), n_modes+1)
        fk_hat = np.zeros(len(k)).astype(complex)
        fk_hat[k == 0] = 0
        fk_hat[k != 0] = (2*1j*b*(np.sin(a*k[k != 0])-a*k[k != 0]*np.cos(a*k[k != 0])))/(k[k != 0]**2)
        y = fk_hat/(2*np.pi)

        if normalized:
            if jump:
                y = y[0:-1]/np.max(np.abs(saw_signal(x, a, b, normalized=False)))
                from fourier_classification.fourier import partial_fourier_sum
                return y, partial_fourier_sum(1500, len(y), x, y, type_name)
            return y[0:-1]/np.max(np.abs(saw_signal(x, a, b, normalized=False)))

        return y
    
    y = np.zeros(len(x))
    y[np.abs(x) < a] = -b*x[np.abs(x) < a]
    
    if noise:
        if normalized:
            y = y/np.max(abs(y))
        return add_noise(y, noise_parameter, x)
    
    if normalized:
        if jump:
            y = y / np.max(abs(y))
            fk = extract_jump(x, y, a)
            return y[0:-1], fk[0:-1]
        return y/np.max(abs(y))
    
    return y

def exp_signal(x, a=2, b=2, c=-1, normalized=True, jump=False, type_name='Trig', 
               noise=False, noise_parameter=0.1, fourier=False, n_modes=40):
    """
    Generate an exponential signal.
    
    Parameters
    ----------
    x : array-like
        Domain points where the signal is evaluated
    a : float
        Width parameter (half-width of the exponential)
    b : float
        Exponential rate parameter
    c : float
        Vertical shift parameter
    normalized : bool
        Whether to normalize the signal to [-1, 1]
    jump : bool
        Whether to return jump information
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
    noise : bool
        Whether to add noise to the signal
    noise_parameter : float
        Noise level parameter
    fourier : bool
        Whether to return Fourier coefficients instead of signal values
    n_modes : int
        Number of Fourier modes to use
        
    Returns
    -------
    array-like or tuple
        Signal values or Fourier coefficients, with jump information if requested
    """
    if fourier:
        k = np.linspace(int((-n_modes/2)), int((n_modes/2)), n_modes+1).astype(complex)
        fk_hat = np.zeros(len(k)).astype(complex)
        fk_hat[k == 0] = (2*((a*b*c)+np.sinh(a*b)))/b
        fk_hat[k != 0] = ((2*c*np.sin(a*k[k != 0]))/k[k != 0])+((2*np.sinh(a*(b+(1j*k[k != 0]))))/(b+(1j*k[k != 0])))
        y = fk_hat/(2*np.pi)

        if normalized:
            if jump:
                y = y[0:-1]/np.max(np.abs(exp_signal(x, a, b, c, normalized=False)))
                from fourier_classification.fourier import partial_fourier_sum
                return y, partial_fourier_sum(1500, len(y), x, y, type_name)
            return y[0:-1]/np.max(np.abs(exp_signal(x, a, b, c, normalized=False)))

        return y
    
    y = np.zeros(len(x))
    y[np.abs(x) < a] = c+np.e**(-b*x[np.abs(x) < a])
    
    if noise:
        if normalized:
            y = y/np.max(abs(y))
        return add_noise(y, noise_parameter, x)
    
    if normalized:
        if jump:
            y = y / np.max(abs(y))
            fk = extract_jump(x, y, a)
            return y[0:-1], fk[0:-1]
        return y/np.max(abs(y))
    
    return y

def sin_signal(x, a=2, b=2, c=-1, normalized=True, jump=False, type_name='Trig', 
               noise=False, noise_parameter=0.1, fourier=False, n_modes=40):
    """
    Generate a sinusoidal signal.
    
    Parameters
    ----------
    x : array-like
        Domain points where the signal is evaluated
    a : float
        Width parameter (half-width of the sinusoid)
    b : float
        Frequency parameter
    c : float
        Amplitude parameter
    normalized : bool
        Whether to normalize the signal to [-1, 1]
    jump : bool
        Whether to return jump information
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
    noise : bool
        Whether to add noise to the signal
    noise_parameter : float
        Noise level parameter
    fourier : bool
        Whether to return Fourier coefficients instead of signal values
    n_modes : int
        Number of Fourier modes to use
        
    Returns
    -------
    array-like or tuple
        Signal values or Fourier coefficients, with jump information if requested
    """
    if fourier:
        k = np.linspace(int((-n_modes/2)), int((n_modes/2)), n_modes+1).astype(complex)
        fk_hat = np.zeros(len(k)).astype(complex)
        fk_hat[k == b] = ((1j*c*np.sin(2*a*b))/(2*b))-(1j*a*c)
        fk_hat[k == -b] = (1/2)*1j*c*((2*a)-((np.sin(2*a*b))/b))
        mask = (k != b) & (k != 0)
        fk_hat[mask] = (2*1j*c*((b*np.cos(a*b)*np.sin(a*k[mask]))-(k[mask]*np.sin(a*b)*np.cos(a*k[mask]))))/((b**2)-(k[mask]**2))
        y = fk_hat/(2*np.pi)

        if normalized:
            if jump:
                y = y[0:-1]/np.max(np.abs(sin_signal(x, a, b, c, normalized=False)))
                from fourier_classification.fourier import partial_fourier_sum
                return y, partial_fourier_sum(1500, len(y), x, y, type_name)
            return y[0:-1]/np.max(np.abs(sin_signal(x, a, b, c, normalized=False)))

        return y
    
    y = np.zeros(len(x))
    y[np.abs(x) < a] = c*np.sin(b*x[np.abs(x) < a])
    
    if noise:
        if normalized:
            y = y/np.max(abs(y))
        return add_noise(y, noise_parameter, x)
    
    if normalized:
        if jump:
            y = y / np.max(abs(y))
            fk = extract_jump(x, y, a)
            return y[0:-1], fk[0:-1]
        return y/np.max(abs(y))
    
    return y

def gaussian_signal(x, a=2, b=2, normalized=True, jump=False, type_name='Trig', 
                    noise=False, noise_parameter=0.1, fourier=False, n_modes=40, m_modes=40):
    """
    Generate a Gaussian signal.
    
    Parameters
    ----------
    x : array-like
        Domain points where the signal is evaluated
    a : float
        Width parameter (half-width of the Gaussian)
    b : float
        Exponent parameter controlling the shape
    normalized : bool
        Whether to normalize the signal to [-1, 1]
    jump : bool
        Whether to return jump information
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
    noise : bool
        Whether to add noise to the signal
    noise_parameter : float
        Noise level parameter
    fourier : bool
        Whether to return Fourier coefficients instead of signal values
    n_modes : int
        Number of Fourier modes to use
    m_modes : int
        Number of modes for DFT calculation
        
    Returns
    -------
    array-like or tuple
        Signal values or Fourier coefficients, with jump information if requested
    """
    if fourier:
        from fourier_classification.fourier import dft
        y = ((np.dot(dft(len(x), m_modes), gaussian_signal(x, a, b)))/len(x))
        if normalized:
            if jump:
                y = y[0:-1]/np.max(np.abs(gaussian_signal(x, a, b, normalized=False)))
                from fourier_classification.fourier import partial_fourier_sum
                return y[0:-1], partial_fourier_sum(1500, len(y), x, y, type_name)
            return y[0:-1]/np.max(np.abs(gaussian_signal(x, a, b, normalized=False)))
        return y
    
    y = np.zeros(len(x))
    y[np.abs(x) < a] = np.e**(-a*(x[np.abs(x) < a]**(2*b)))
    y = np.nan_to_num(y)
    
    if noise:
        if normalized:
            y = y/np.max(abs(y))
        return add_noise(y, noise_parameter, x)
    
    if normalized:
        if jump:
            y = y / np.max(abs(y))
            fk = extract_jump(x, y, a)
            return y[0:-1], fk[0:-1]
        return y/np.max(abs(y))
    
    return y

def generate_signals(signal_type, x, amount, normalized=True, fourier=False, jump=False, 
                     n_modes=40, type_name='Trig', noise=False, noise_parameter=0.1, 
                     method='precompute', random_param=True, a=0, b=0, c=0):
    """
    Generate multiple signals of the specified type with varying parameters.
    
    Parameters
    ----------
    signal_type : str
        Type of signal to generate ('Box', 'Saw', 'Exp', 'Sin', 'Gaus')
    x : array-like
        Domain points where the signals are evaluated
    amount : int
        Number of signals to generate
    normalized : bool
        Whether to normalize the signals to [-1, 1]
    fourier : bool
        Whether to return Fourier coefficients instead of signal values
    jump : bool
        Whether to return jump information
    n_modes : int
        Number of Fourier modes to use
    type_name : str
        Type of concentration factor ('Trig', 'Poly', or 'Exp')
    noise : bool
        Whether to add noise to the signals
    noise_parameter : float
        Noise level parameter
    method : str
        Method for Fourier series calculation ('precompute', 'ifft', 'forloop')
    random_param : bool
        Whether to use random parameters for signal generation
    a, b, c : float
        Fixed parameters to use if random_param is False
        
    Returns
    -------
    list or tuple
        List of generated signals and their parameters
    """
    signal_output = []
    length = amount + 2
    
    # Select the appropriate signal generation function
    if signal_type == 'Box':
        signal_func = box_signal
        param_count = 2
    elif signal_type == 'Saw':
        signal_func = saw_signal
        param_count = 2
    elif signal_type == 'Exp':
        signal_func = exp_signal
        param_count = 3
    elif signal_type == 'Sin':
        signal_func = sin_signal
        param_count = 3
    elif signal_type == 'Gaus':
        signal_func = gaussian_signal
        param_count = 2
    else:
        raise ValueError(f"Unknown signal type: {signal_type}")
    
    # Generate random parameters if requested
    if random_param:
        if signal_type == 'Box' or signal_type == 'Saw':
            a_values = np.linspace(0.10, 2.90, length)
            b_values = np.append(np.linspace(-100, -0.01, int(length/2)), 
                                np.linspace(0.01, 100, int(length/2)))
            a_values = np.random.permutation(a_values)
            b_values = np.random.permutation(b_values)
            
        elif signal_type == 'Exp':
            a_values = np.linspace(np.pi/4, np.pi/2, length)
            b_values = np.append(np.linspace(-1, -0.1, int(length/2)), 
                               np.linspace(0.1, 1, int(length/2)))
            c_values = np.append(np.linspace(-3, -1.01, int(length/2)), 
                               np.linspace(-1.01, 1, int(length/2)))
            a_values = np.random.permutation(a_values)
            b_values = np.random.permutation(b_values)
            c_values = np.random.permutation(c_values)
            
        elif signal_type == 'Sin':
            a_values = np.linspace(np.pi/4, np.pi/2, length)
            b_values = np.append(np.linspace(-2*np.pi, -0.3, int(length/2)), 
                               np.linspace(0.3, 2*np.pi, int(length/2)))
            c_values = np.append(np.linspace(-100, -0.1, int(length/2)), 
                               np.linspace(0.1, 100, int(length/2)))
            a_values = np.random.permutation(a_values)
            b_values = np.random.permutation(b_values)
            c_values = np.random.permutation(c_values)
            
        elif signal_type == 'Gaus':
            a_values = np.linspace(np.pi/4, np.pi/2, length)
            b_values = np.linspace(1, 10, length)
            a_values = np.random.permutation(a_values)
            b_values = np.random.permutation(b_values)
    else:
        # Use fixed parameters
        a_values = np.full(amount, a)
        b_values = np.full(amount, b)
        if param_count > 2:
            c_values = np.full(amount, c)
    
    # Generate signals
    for i in range(amount):
        if signal_type in ['Box', 'Saw', 'Gaus']:
            if fourier:
                if jump:
                    if signal_type == 'Gaus':
                        result = signal_func(x, a_values[i], int(b_values[i]), normalized=normalized, 
                                           jump=True, type_name=type_name, fourier=True, n_modes=n_modes)
                    else:
                        result = signal_func(x, a_values[i], b_values[i], normalized=normalized, 
                                           jump=True, type_name=type_name, fourier=True, n_modes=n_modes)
                    cn = result[0]
                    jump_data = result[1]
                    signal_output.append([fourier_series(cn, x, method=method)[0:-1], jump_data])
                else:
                    if signal_type == 'Gaus':
                        cn = signal_func(x, a_values[i], int(b_values[i]), normalized=normalized, fourier=True, n_modes=n_modes)
                    else:
                        cn = signal_func(x, a_values[i], b_values[i], normalized=normalized, fourier=True, n_modes=n_modes)
                    signal_output.append(fourier_series(cn, x, method=method))
            elif noise:
                if signal_type == 'Gaus':
                    f = signal_func(x, a_values[i], int(b_values[i]), noise=True, normalized=normalized, 
                                  noise_parameter=noise_parameter)
                else:
                    f = signal_func(x, a_values[i], b_values[i], noise=True, normalized=normalized, 
                                  noise_parameter=noise_parameter)
                signal_output.append(f)
            else:
                if signal_type == 'Gaus':
                    f = signal_func(x, a_values[i], int(b_values[i]), jump=jump, normalized=normalized)
                else:
                    f = signal_func(x, a_values[i], b_values[i], jump=jump, normalized=normalized)
                signal_output.append(f)
                
            if param_count == 2:
                return [signal_output, a_values[0:amount], b_values[0:amount]]
                
        else:  # Exp or Sin
            if fourier:
                if jump:
                    result = signal_func(x, a_values[i], b_values[i], c_values[i], normalized=normalized, 
                                       jump=True, type_name=type_name, fourier=True, n_modes=n_modes)
                    cn = result[0]
                    jump_data = result[1]
                    signal_output.append([fourier_series(cn, x, method=method)[0:-1], jump_data])
                else:
                    cn = signal_func(x, a_values[i], b_values[i], c_values[i], normalized=normalized, 
                                   fourier=True, n_modes=n_modes)
                    signal_output.append(fourier_series(cn, x, method=method))
            elif noise:
                f = signal_func(x, a_values[i], b_values[i], c_values[i], noise=True, 
                              normalized=normalized, noise_parameter=noise_parameter)
                signal_output.append(f)
            else:
                f = signal_func(x, a_values[i], b_values[i], c_values[i], jump=jump, normalized=normalized)
                signal_output.append(f)
                
            return [signal_output, a_values[0:amount], b_values[0:amount], c_values[0:amount]]
