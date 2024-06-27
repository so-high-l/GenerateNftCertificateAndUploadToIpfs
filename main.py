import requests
import json
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

# Function to generate certificate
def generate_certificate(user_name, score, qr_data, date):
    # Load the template image
    template = Image.open("certTemplate.png")

    # Create a draw object
    draw = ImageDraw.Draw(template)

    # Define font and size
    font = ImageFont.truetype("comic.ttf", 20)  # Adjust the font size and path as needed

    # Overlay the user's name
    draw.text((30, 170), user_name, fill="black", font=font)  # Adjust the position as needed

    # Overlay the score
    draw.text((300, 170), score, fill="black", font=font)  # Adjust the position as needed

    draw.text((300, 410), date, fill="black", font=font)  # Adjust the position as needed

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.convert("RGB")

    # Resize QR code to fit the certificate
    qr_img = qr_img.resize((200, 200))  # Adjust the size as needed

    # Paste the QR code onto the template image
    template.paste(qr_img, (240, 200))  # Adjust the position as needed

    # Save the generated certificate
    output_path = "output/generated_certificate.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    template.save(output_path)

    return output_path

# Function to upload file to Pinata
def upload_to_pinata(file_path, pinata_api_key, pinata_secret_api_key):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": pinata_api_key,
        "Authorization": f"Bearer {pinata_secret_api_key}",
    }
    with open(file_path, 'rb') as file:
        files = {
            'file': (os.path.basename(file_path), file)
        }
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        return response.json()["IpfsHash"]

# Example usage
def generate_and_upload_to_pinata(user_name, score, date, qr_data, pinata_api_key, pinata_secret_api_key):
    output_path = generate_certificate(user_name, score, qr_data, date)
    certificate_ipfs_hash = upload_to_pinata(output_path, pinata_api_key, pinata_secret_api_key)

    # Create metadata
    metadata = {
        "name": "Quiz Certificate NFT",
        "description": "Certificate for completing the quiz",
        "image": f"ipfs://{certificate_ipfs_hash}",
        "attributes": [
            {"trait_type": "Name", "value": user_name},
            {"trait_type": "Score", "value": score},
            {"trait_type": "Date", "value": date},
        ]
    }

    # Save metadata to a JSON file
    metadata_path = "output/metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

    # Upload metadata to Pinata
    metadata_ipfs_hash = upload_to_pinata(metadata_path, pinata_api_key, pinata_secret_api_key)

    metadata_ipfs_url = f"ipfs://{metadata_ipfs_hash}"
    print(f"Metadata IPFS URL: {metadata_ipfs_url}")

pinata_api_key = os.getenv('pinata_api_key')
pinata_secret_api_key = os.getenv('pinata_secret_api_key')
generate_and_upload_to_pinata("User test", "80/100", "06/26/2024", "http://localhost/", pinata_api_key, pinata_secret_api_key)
