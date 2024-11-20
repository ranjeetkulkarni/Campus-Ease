import os
import requests
import PyPDF2
from gtts import gTTS

# Replace with your API2Convert API key
API_KEY = '0e9129d40968b9e3740ef0493022b752'

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyPDF2."""
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()  # Extract text from each page
    return text

def convert_text_to_mp3(text, mp3_path):
    """Convert text to MP3 using gTTS."""
    tts = gTTS(text, lang='en')
    tts.save(mp3_path)
    print(f"MP3 saved as {mp3_path}")

def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    """Convert MP3 to WAV using API2Convert."""
    # API2Convert endpoint for file conversion
    url = 'https://api.api2convert.com/v1/convert'
    
    # Open the MP3 file to upload
    with open(mp3_file_path, 'rb') as file:
        files = {
            'file': file
        }
        
        # Prepare the payload for the API request
        data = {
            'apikey': API_KEY,
            'output_format': 'wav'  # Set output format to WAV
        }
        
        # Make the request to the API2Convert service
        response = requests.post(url, files=files, data=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                download_url = result['download_url']
                print(f"Conversion successful! Downloading WAV file from: {download_url}")
                
                # Download the converted WAV file
                download_response = requests.get(download_url)
                if download_response.status_code == 200:
                    # Save the downloaded WAV file to the specified path
                    with open(wav_file_path, 'wb') as output_file:
                        output_file.write(download_response.content)
                    print(f"File saved as: {wav_file_path}")
                else:
                    print("Failed to download the WAV file.")
            else:
                print(f"Conversion failed: {result.get('error_message')}")
        else:
            print(f"Failed to convert file. HTTP Status Code: {response.status_code}")
            print(response.json())

def main(pdf_path, mp3_path, wav_path):
    """Main function to handle PDF extraction and file conversion."""
    # Step 1: Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Convert the extracted text to MP3
    if text:
        convert_text_to_mp3(text, mp3_path)
        # Step 3: Convert MP3 to WAV using API2Convert
        convert_mp3_to_wav(mp3_path, wav_path)
    else:
        print("No text found in the PDF.")

if __name__ == "__main__":
    # Input and output file paths
    pdf_file_path = "C:\\Users\\Personal\\Desktop\\Wav Files\\Lecture_9.pdf"  # Replace with your PDF file path
    mp3_file_path = "transcript.mp3"  # Intermediate MP3 output path
    wav_file_path = "output.wav"  # Final WAV output path

    main(pdf_file_path, mp3_file_path, wav_file_path)
