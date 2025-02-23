
from PIL import Image
import os
import io

def compress_image(input_path, target_size_mb=1, output_path=None, quality_start=95):

    """
    Compress an image to a target file size in 1/2/3 MB.
    
    Args:
        input_path (str): Path to the input image file
        target_size_mb (int, optional): Target size in MB (1, 2, or 3). Defaults to 1.
        output_path (str, optional): Path to save the compressed image. If None, will use input filename with '_compressed' suffix.
        quality_start (int, optional): Initial JPEG quality to try. Defaults to 95.
    
    Returns:
        str: Path to the compressed image
        float: Final file size in MB
        int: Final quality setting used

    """


    # validate target size
    if target_size_mb not in [1, 2, 3]:
        raise ValueError("Target size must be 1, 2, or 3 MB")
    
    # convert target size to bytes
    target_size_bytes = target_size_mb * 1024 * 1024
    
    # set output path if not provided
    if output_path is None:
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}_compressed{ext}"
    
    img = Image.open(input_path)
    
    # Convert to RGB if in RGBA mode (remove alpha channel)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Binary search approach for finding the optimal quality
    quality_min = 5
    quality_max = quality_start
    quality = quality_max
    best_quality = None
    best_data = None
    
    while quality_min <= quality_max:

        # Save image to memory buffer to check size
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        current_size = buffer.tell()
        
        # Check if we're close enough to target size
        if current_size <= target_size_bytes:
            # works - save it and try a higher quality
            best_quality = quality
            best_data = buffer.getvalue()
            quality_min = quality + 1
        else:
            # too large - try a lower quality
            quality_max = quality - 1
        
        # Update quality for next iteration
        quality = (quality_min + quality_max) // 2
    
    # When find a suitable quality, save the image
    if best_quality is not None:
        with open(output_path, 'wb') as f:
            f.write(best_data)
        final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        return output_path, final_size_mb, best_quality
    else:
        # If no suitable quality found, save with lowest quality
        img.save(output_path, format='JPEG', quality=quality_min, optimize=True)
        final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        return output_path, final_size_mb, quality_min