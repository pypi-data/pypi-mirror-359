"""
Models module for Fourier Series Classification.

This module provides neural network models for classifying signals
based on their Fourier coefficients or raw signal values.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam

def create_feed_forward_model(input_shape, num_classes=5, hidden_layers=None):
    """
    Create a feed-forward neural network model for signal classification.
    
    Parameters
    ----------
    input_shape : tuple
        Shape of the input data
    num_classes : int
        Number of signal classes to classify
    hidden_layers : list of int, optional
        List of neurons in each hidden layer
        
    Returns
    -------
    tensorflow.keras.models.Sequential
        Compiled feed-forward neural network model
    """
    if hidden_layers is None:
        hidden_layers = [512, 256, 128]
    
    model = Sequential()
    
    # Input layer
    model.add(Input(shape=input_shape))
    
    # Hidden layers
    for units in hidden_layers:
        model.add(Dense(units, activation='relu'))
        model.add(Dropout(0.2))
    
    # Output layer
    model.add(Dense(num_classes, activation='softmax'))
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model(model, x_train, y_train, x_val=None, y_val=None, 
                epochs=100, batch_size=32, verbose=1, target_accuracy=0.999,
                max_iterations=10000):
    """
    Train a neural network model for signal classification.
    
    Parameters
    ----------
    model : tensorflow.keras.models.Model
        Model to train
    x_train : array-like
        Training data
    y_train : array-like
        Training labels
    x_val : array-like, optional
        Validation data
    y_val : array-like, optional
        Validation labels
    epochs : int
        Number of epochs per iteration
    batch_size : int
        Batch size for training
    verbose : int
        Verbosity level
    target_accuracy : float
        Target accuracy to stop training
    max_iterations : int
        Maximum number of iterations
        
    Returns
    -------
    tuple
        Trained model and training history
    """
    # Convert labels to one-hot encoding if needed
    if len(y_train.shape) == 1:
        y_train = tf.keras.utils.to_categorical(y_train, num_classes=model.output_shape[-1])
    
    if x_val is not None and y_val is not None:
        if len(y_val.shape) == 1:
            y_val = tf.keras.utils.to_categorical(y_val, num_classes=model.output_shape[-1])
        validation_data = (x_val, y_val)
    else:
        validation_data = None
    
    # Train until target accuracy or max iterations
    iteration = 0
    history_list = []
    current_accuracy = 0
    
    while current_accuracy < target_accuracy and iteration < max_iterations:
        history = model.fit(
            x_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            verbose=verbose
        )
        
        history_list.append(history)
        
        # Check current accuracy
        _, current_accuracy = model.evaluate(x_train, y_train, verbose=0)
        
        iteration += 1
        if verbose > 0:
            print(f"Iteration {iteration}, Current accuracy: {current_accuracy:.4f}")
    
    return model, history_list

def evaluate_model(model, x_test, y_test, class_names=None):
    """
    Evaluate a trained model on test data.
    
    Parameters
    ----------
    model : tensorflow.keras.models.Model
        Trained model to evaluate
    x_test : array-like
        Test data
    y_test : array-like
        Test labels
    class_names : list of str, optional
        Names of the classes
        
    Returns
    -------
    dict
        Evaluation metrics
    """
    # Convert labels to one-hot encoding if needed
    if len(y_test.shape) == 1:
        y_test_categorical = tf.keras.utils.to_categorical(y_test, num_classes=model.output_shape[-1])
    else:
        y_test_categorical = y_test
        y_test = np.argmax(y_test, axis=1)
    
    # Evaluate model
    loss, accuracy = model.evaluate(x_test, y_test_categorical, verbose=0)
    
    # Get predictions
    y_pred_proba = model.predict(x_test)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Calculate confusion matrix
    confusion_matrix = tf.math.confusion_matrix(y_test, y_pred).numpy()
    
    # Calculate per-class accuracy
    per_class_accuracy = {}
    for i in range(confusion_matrix.shape[0]):
        class_name = class_names[i] if class_names is not None else f"Class {i}"
        per_class_accuracy[class_name] = confusion_matrix[i, i] / np.sum(confusion_matrix[i])
    
    return {
        'loss': loss,
        'accuracy': accuracy,
        'confusion_matrix': confusion_matrix,
        'per_class_accuracy': per_class_accuracy
    }

def prepare_data_for_model_a(signals, labels, test_size=0.2, random_state=42):
    """
    Prepare data for Model A (physical space signal data).
    
    Parameters
    ----------
    signals : array-like
        Signal data
    labels : array-like
        Signal labels
    test_size : float
        Proportion of data to use for testing
    random_state : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        Training and testing data and labels
    """
    from sklearn.model_selection import train_test_split
    
    # Reshape signals if needed
    if len(signals.shape) == 2:
        signals = signals.reshape(signals.shape[0], signals.shape[1], 1)
    
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(
        signals, labels, test_size=test_size, random_state=random_state, stratify=labels
    )
    
    return x_train, x_test, y_train, y_test

def prepare_data_for_model_b(fourier_coeffs, labels, test_size=0.2, random_state=42):
    """
    Prepare data for Model B (Fourier data).
    
    Parameters
    ----------
    fourier_coeffs : array-like
        Fourier coefficients
    labels : array-like
        Signal labels
    test_size : float
        Proportion of data to use for testing
    random_state : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        Training and testing data and labels
    """
    from sklearn.model_selection import train_test_split
    
    # Reshape coefficients if needed
    if len(fourier_coeffs.shape) == 2:
        fourier_coeffs = fourier_coeffs.reshape(fourier_coeffs.shape[0], fourier_coeffs.shape[1], 1)
    
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(
        fourier_coeffs, labels, test_size=test_size, random_state=random_state, stratify=labels
    )
    
    return x_train, x_test, y_train, y_test

def prepare_data_for_model_c(signals, jumps, labels, test_size=0.2, random_state=42):
    """
    Prepare data for Model C (signal data with jump information).
    
    Parameters
    ----------
    signals : array-like
        Signal data
    jumps : array-like
        Jump information
    labels : array-like
        Signal labels
    test_size : float
        Proportion of data to use for testing
    random_state : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        Training and testing data and labels
    """
    from sklearn.model_selection import train_test_split
    
    # Reshape signals and jumps if needed
    if len(signals.shape) == 2:
        signals = signals.reshape(signals.shape[0], signals.shape[1], 1)
    if len(jumps.shape) == 2:
        jumps = jumps.reshape(jumps.shape[0], jumps.shape[1], 1)
    
    # Combine signals and jumps
    combined_data = np.concatenate([signals, jumps], axis=2)
    
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(
        combined_data, labels, test_size=test_size, random_state=random_state, stratify=labels
    )
    
    return x_train, x_test, y_train, y_test
