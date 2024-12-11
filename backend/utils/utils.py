import numpy as np
import base64
import io

def binary_array_to_base64(arr:np.ndarray) -> str:
    """
    Converts a numpy array of 0's and 1's (uint8 type) to a Base64-encoded string.
    
    Parameters:
    arr (np.ndarray): Numpy array with dtype `np.uint8` containing only 0's and 1's.
    
    Returns:
    str: Base64-encoded string.
    """
    if not isinstance(arr, np.ndarray) or arr.dtype != np.uint8 or not np.all((arr == 0) | (arr == 1)):
        raise ValueError("Input must be a numpy array of uint8 with only 0 and 1 values")
    binary_string = ''.join(str(bit) for bit in arr)
    padding_length = (8 - len(binary_string) % 8) % 8
    binary_string = '0' * padding_length + binary_string
    byte_array = bytearray()
    for i in range(0, len(binary_string), 8):
        byte_array.append(int(binary_string[i:i+8], 2))
    base64_encoded = base64.b64encode(byte_array).decode('utf-8')
    return base64_encoded

def base64_to_binary_array(base64_str: str) -> np.ndarray:
    """
    Converts a Base64-encoded string back to a numpy array of 0's and 1's (uint8 type).
    
    Parameters:
    base64_str (str): Base64-encoded string.
    
    Returns:
    np.ndarray: Numpy array with dtype `np.uint8` containing 0's and 1's.
    """
    byte_array = base64.b64decode(base64_str)
    binary_string = ''.join(format(byte, '08b') for byte in byte_array)
    binary_array = np.array([int(bit) for bit in binary_string], dtype=np.uint8)
    return binary_array


def binary_quantized(embedding: np.ndarray) ->np.ndarray:
    """
    Quantizes the input embedding array into binary values (0 or 1) based on a threshold of 0.
        
    Parameters:
    embedding (np.ndarray): Input array of floats to be quantized. Values can be positive or negative.

    Returns:
    np.ndarray: A binary quantized version of the input array, with dtype uint8.
    """
    binary_array = (embedding > 0).astype(np.uint8)
    return binary_array

def scalar_quantized(embedding: np.ndarray, quantile: float = 0.99) -> np.ndarray:
    """
    WARNING: has not been tested
    Quantizes a float32 embedding array into int8 using scalar quantization.
    
    Parameters:
        embedding (np.ndarray): The input float32 embedding array.
        quantile (float): The quantile value to determine the scaling factor (default is 0.99).

    Returns:
        np.ndarray: The quantized int8 embedding array.
    """
    if embedding.dtype != np.float32:
        raise ValueError("Input embedding must be of type float32.")
    
    # Calculate the quantile value for scaling
    scale = np.quantile(np.abs(embedding), quantile)
    if scale == 0:
        raise ValueError("Quantile scale is zero, cannot quantize.")

    # Normalize the embedding by the scale and clip values to int8 range
    normalized = np.clip(embedding / scale, -1.0, 1.0)

    # Convert normalized values to int8
    quantized = (normalized * 127).astype(np.int8)
    
    return quantized

def base64_to_float32_vector(base64_str: str) -> np.ndarray:
    """
    Convert a base64-encoded string to a numpy array of dtype=np.float32.

    Args:
        base64_str (str): The base64-encoded string representing the array.

    Returns:
        np.ndarray: A 1D numpy array of dtype=np.float32.
    """
    byte_data = base64.b64decode(base64_str)
    
    return np.frombuffer(byte_data, dtype=np.float32)

def float32_vector_to_base64(vector: np.ndarray) -> str:
    """
    Convert a numpy array of dtype=np.float32 to a base64-encoded string.

    Args:
        vector (np.ndarray): A 1D numpy array of dtype=np.float32.

    Returns:
        str: The base64-encoded string representing the array.
    """
    if vector.dtype != np.float32:
        raise ValueError("Input array must have dtype=np.float32")
    
    byte_data = vector.tobytes()
    
    return base64.b64encode(byte_data).decode('utf-8')

