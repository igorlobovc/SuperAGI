import requests
import os

def download_pdf(url, save_path):
    """Downloads a PDF from a URL and saves it locally."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Ensure the directory exists before saving
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {os.path.basename(save_path)} to {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    pdf_url = "https://www.tesourotransparente.gov.br/ckan/dataset/b74a4483-54f5-4625-8d23-e65515b075ef/resource/a387c7ae-6993-4710-9054-9e9be549b66d/download/metadadosrreo.pdf"

    # Define save path relative to the project root.
    # The agent's execution environment might differ, but this is standard practice.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else "."
    save_directory = os.path.join(project_root, "data", "raw", "siconfi")
    file_name = "siconfi_rreo_metadata.pdf"
    full_save_path = os.path.join(save_directory, file_name)

    # Create directory if it doesn't exist
    if not os.path.exists(save_directory):
        try:
            os.makedirs(save_directory)
            print(f"Created directory: {save_directory}")
        except OSError as e:
            print(f"Error creating directory {save_directory}: {e}")
            # Exit if directory cannot be created
            exit()


    if download_pdf(pdf_url, full_save_path):
        print(f"PDF ready at {full_save_path}")
    else:
        print(f"Failed to download PDF.")
