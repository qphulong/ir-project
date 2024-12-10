import numpy as np
import base64

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

