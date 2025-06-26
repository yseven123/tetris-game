import rasterio
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
import argparse # For command-line arguments

# --- Configuration ---
# Default paths can be overridden by command-line arguments.

def read_image(image_path):
    """Reads a remote sensing image using rasterio."""
    try:
        with rasterio.open(image_path) as src:
            print(f"Image opened successfully: {image_path}")
            print(f"Number of bands: {src.count}")
            print(f"Image width: {src.width}, height: {src.height}")
            print(f"Coordinate Reference System (CRS): {src.crs}")
            return src.read(), src.meta.copy() # Read all bands and copy metadata
    except rasterio.errors.RasterioIOError as e:
        print(f"Error opening image {image_path}: {e}")
        print("Please ensure the image path is correct and the file is a valid raster format.")
        print("If using the rasterio sample, ensure rasterio is correctly installed with its sample data.")
        return None, None

def main(args):
    """Main function to process the image."""

    image_path_to_use = args.input_file
    output_filename = args.output_file

    if image_path_to_use is None:
        # If no input file is specified via command line, try to use the rasterio sample.
        # Note: rasterio.sample.get_path might not be available in all versions or distributions.
        # A more robust approach for testing without user input would be to bundle a small sample GeoTIFF.
        print("No input file specified via --input_file.")
        try:
            # Attempt to locate a common path for rasterio sample data if it exists
            # This is a guess and might not work on all systems or rasterio versions.
            # A truly robust solution would require a known sample file or a different approach.
            import os
            import rasterio as rio
            rasterio_dir = os.path.dirname(rio.__file__)
            # Common locations for sample data in older versions or specific installs
            possible_sample_paths = [
                os.path.join(rasterio_dir, 'sample', 'data', 'RGB.byte.tif'), # Common structure
                os.path.join(rasterio_dir, 'tests', 'data', 'RGB.byte.tif'), # Sometimes in tests
                # Add other potential relative paths if known
            ]

            found_sample = False
            for p in possible_sample_paths:
                if os.path.exists(p):
                    image_path_to_use = p
                    print(f"Attempting to use rasterio sample image: {image_path_to_use}")
                    found_sample = True
                    break

            if not found_sample:
                # Fallback if rasterio.sample module or get_path() is not available/working
                # or if the direct path guesses fail.
                print("Could not automatically find a rasterio sample image (e.g., RGB.byte.tif).")
                print("Please provide an input image using the --input_file argument.")
                print("If you intended to use a sample, ensure rasterio's sample data is installed and accessible,")
                print("or modify the script to point to a known sample GeoTIFF file.")
                return # Exit if no sample and no user input

        except (ImportError, AttributeError, FileNotFoundError) as e:
            print(f"Error trying to access rasterio sample image: {e}")
            print("Please provide an input image using the --input_file argument.")
            return # Exit if no sample and no user input
    else:
        print(f"Using input image: {image_path_to_use}")


    data, meta = read_image(image_path_to_use)

    if data is not None:
        print("Image data read successfully.")
        original_image_name = image_path_to_use.split("/")[-1].split("\\")[-1] # Get filename
        # For now, just show the first band if it's a multi-band image, or the image itself.
        # More processing steps will be added later.
        # if data.ndim == 3 and data.shape[0] > 0:
        #     # Display the first band
        #     show(data[0], cmap='viridis', title=f'Band 1 of {image_path.split("/")[-1]}')
        # elif data.ndim == 2:
        #     # Display the single band image
        #     show(data, cmap='viridis', title=f'{image_path.split("/")[-1]}')
        # else:
        #     print("Image data has unexpected dimensions.")
        #
        # plt.show() # We will show the processed image later

        # --- Basic Image Processing: NDVI Calculation ---
        # NDVI = (NIR - Red) / (NIR + Red)
        # The rasterio sample 'RGB.byte.tif' is a 3-band RGB image.
        # Band 1: Red, Band 2: Green, Band 3: Blue.
        # It does not have a Near Infrared (NIR) band, which is required for NDVI.
        # For demonstration, let's assume:
        # Red band is data[0]
        # NIR band is data[2] (using Blue band as a proxy for NIR for this example)
        # IMPORTANT: For actual NDVI, you need a multispectral image with Red and NIR bands.

        if data.shape[0] >= 3: # Check if there are at least 3 bands
            red = data[0].astype(float)
            nir = data[2].astype(float) # Using Blue as NIR proxy

            # Avoid division by zero by adding a small epsilon where (nir + red) is zero
            ndvi_denominator = nir + red
            epsilon = 1e-8

            # Calculate NDVI
            # Handle potential RuntimeWarning for invalid value encountered in true_divide
            # by masking out areas where the denominator is zero (or very close to it)
            ndvi = np.zeros_like(red, dtype=float)
            valid_mask = np.abs(ndvi_denominator) > epsilon
            ndvi[valid_mask] = (nir[valid_mask] - red[valid_mask]) / ndvi_denominator[valid_mask]

            # NDVI values range from -1 to 1.
            # Areas with no vegetation are often close to 0 or negative.
            # Sparse vegetation might be 0.2-0.4. Dense vegetation > 0.5.
            print("NDVI calculated (using Band 3 as NIR proxy).")

            # We will display and save NDVI in subsequent steps.
            # For now, let's store it. We'll need 'meta' for saving later.
            processed_image_data = ndvi
            processed_image_meta = meta.copy()
            processed_image_meta.update(dtype=rasterio.float32, count=1, driver='GTiff')

        else:
            print("Image does not have enough bands for NDVI calculation (Red and NIR proxy).")
            print("Skipping NDVI calculation.")
            processed_image_data = None # No processing done
            processed_image_meta = None

        # --- Display Processed Image (NDVI) ---
        if processed_image_data is not None:
            print("Displaying processed NDVI image...")
            plt.figure(figsize=(8, 8))
            # Using a colormap suitable for NDVI (e.g., 'RdYlGn' or 'viridis')
            # 'RdYlGn' (Red-Yellow-Green) is often used for NDVI, where green indicates healthy vegetation.
            img_display = plt.imshow(processed_image_data, cmap='RdYlGn', vmin=-1, vmax=1)
            plt.colorbar(img_display, label='NDVI')
            plt.title(f'NDVI of {original_image_name} (Band 3 as NIR proxy)')
            plt.xlabel('Column #')
            plt.ylabel('Row #')
            if not args.no_display:
                plt.show()
                print("NDVI image display window closed.")
            else:
                print("Display skipped due to --no_display flag.")
        else:
            print("No processed image data to display.")

        # --- Save Processed Image (NDVI) ---
        if processed_image_data is not None and processed_image_meta is not None:
            # output_filename is now set from args
            try:
                # Ensure the data type is float32 for NDVI
                processed_image_data_to_save = processed_image_data.astype(rasterio.float32)

                # Update metadata for the output file
                # 'count' should be 1 for a single-band NDVI image
                # 'dtype' should be float32
                # 'driver' should be 'GTiff' for GeoTIFF format
                # 'nodata' can be set if you have specific no-data values, e.g. if areas outside valid_mask should be no-data
                # For simplicity, we are not setting a specific nodata value here, but in real applications, it's important.
                # meta was copied and updated during NDVI calculation.

                with rasterio.open(output_filename, 'w', **processed_image_meta) as dst:
                    dst.write(processed_image_data_to_save, 1) # Write to the first band
                print(f"Processed NDVI image saved as {output_filename}")
            except Exception as e:
                print(f"Error saving processed image: {e}")
        else:
            print("No processed image data to save.")

        print("Script finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a remote sensing image to calculate NDVI.")
    parser.add_argument('--input_file', type=str,
                        help='Path to the input GeoTIFF image file. If not provided, a sample RGB image from rasterio will be used (if available).')
    parser.add_argument('--output_file', type=str, default='ndvi_processed_output.tif',
                        help='Path to save the processed NDVI GeoTIFF image. (default: ndvi_processed_output.tif)')
    parser.add_argument('--no_display', action='store_true',
                        help='If set, the script will not display the NDVI image using matplotlib.')

    parsed_args = parser.parse_args()
    main(parsed_args)
