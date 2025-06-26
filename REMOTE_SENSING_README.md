# Simple Remote Sensing Image Processor

This Python script (`process_image.py`) performs a basic remote sensing image processing task: calculating the Normalized Difference Vegetation Index (NDVI) from a GeoTIFF image. It uses the `rasterio` library for reading and writing raster data, `numpy` for numerical operations, and `matplotlib` for displaying the resulting image.

## Features

- Reads GeoTIFF images.
- Calculates NDVI.
    - **Note:** The script assumes specific band orders for Red and Near-Infrared (NIR) if a standard multi-spectral image is used. For the default rasterio sample image (`RGB.byte.tif`), which is an RGB image, it uses the Red band (Band 1) and proxies the NIR band with the Blue band (Band 3) for demonstration purposes. For accurate NDVI, ensure your input image has distinct Red and NIR bands and adjust the band indices in the script if necessary.
- Displays the calculated NDVI image.
- Saves the processed NDVI image as a new GeoTIFF file.
- Supports command-line arguments for specifying input and output files, and for suppressing image display.

## Requirements

- Python 3.x
- rasterio
- numpy
- matplotlib

## Installation

1.  **Download the `process_image.py` script.**

2.  **Install the required Python libraries:**
    It's recommended to use a virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

    Then install the packages:
    ```bash
    pip install rasterio numpy matplotlib
    ```

    **Note on `rasterio` installation:** `rasterio` has GDAL as a dependency. Depending on your system, installing `rasterio` via pip might be tricky.
    - Using Conda is often easier: `conda install -c conda-forge rasterio`
    - If you prefer pip, refer to the [rasterio installation documentation](https://rasterio.readthedocs.io/en/stable/installation.html) for platform-specific instructions, which might involve installing GDAL separately.

## Usage

Run the script from the command line:

```bash
python process_image.py [OPTIONS]
```

### Options

-   `--input_file FILE_PATH`: Path to the input GeoTIFF image file.
    If not provided, the script will attempt to use a sample RGB image from `rasterio` (`RGB.byte.tif`). If this sample is not found, an error will occur.
    Example: `python process_image.py --input_file path/to/your/image.tif`

-   `--output_file FILE_PATH`: Path to save the processed NDVI GeoTIFF image.
    (Default: `ndvi_processed_output.tif`)
    Example: `python process_image.py --output_file results/my_ndvi.tif`

-   `--no_display`: If this flag is set, the script will not display the NDVI image using `matplotlib`.
    This is useful for batch processing or running in environments without a display server.
    Example: `python process_image.py --no_display`

### Examples

1.  **Process the default sample image and save to `ndvi_processed_output.tif` (displays image):**
    ```bash
    python process_image.py
    ```

2.  **Process a specific input image and save to a custom output path (displays image):**
    ```bash
    python process_image.py --input_file /path/to/landsat_image.tif --output_file /path/to/output/landsat_ndvi.tif
    ```

3.  **Process an image without displaying it:**
    ```bash
    python process_image.py --input_file my_image.tif --no_display
    ```

## How NDVI Calculation Works (in this script)

NDVI is calculated using the formula:

`NDVI = (NIR - Red) / (NIR + Red)`

-   **Red:** Pixels values from the Red band of the image.
-   **NIR:** Pixels values from the Near-Infrared band of the image.

This script makes the following assumptions for band data from the input `data` array (read by `rasterio`):
-   `Red = data[0]` (first band)
-   `NIR = data[2]` (third band, **acting as a proxy if using the RGB sample image**)

**Important:** If you are using your own multispectral image, you might need to adjust these band indices (`data[index_for_red_band]`, `data[index_for_nir_band]`) in the `main()` function within `process_image.py` to match your image's band configuration. For example, Landsat 8 OLI/TIRS images typically have Red as Band 4 and NIR as Band 5.

## Limitations

-   The script currently performs a very basic NDVI calculation. More advanced remote sensing analyses would require more sophisticated algorithms and potentially different band combinations.
-   Error handling is basic.
-   The proxy NIR band used for the sample RGB image is for demonstration only and does not yield a scientifically accurate NDVI.
