from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import tempfile
from nudenet import NudeDetector

app = Flask(__name__)
CORS(app)

forbiddens=["ANUS EXPOSED","BUTTOCKS_EXPOSED","FEMALE_BREAST_EXPOSED","MALE_GENITALIA_EXPOSED","FEMALE_GENITALIA_EXPOSED"]

@app.route('/detect-nudity', methods=['POST'])
def detect_nudity():

    tempData = {
        'url': str,
        'isExplicit': bool,
        'assurance': 0,
        'kind': str
    }
    # Check if request contains image URL
    if 'image_url' not in request.json:
        return jsonify({"error": "Image URL not provided"}), 400
    
    # Get the image URL from the request
    image_url = request.json['image_url']

    # Make an HTTP GET request to fetch the image data
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the image data
        image_data = response.content
        
        # Save the image data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
        
        # Initialize the NudeDetector object
        detector = NudeDetector()
        
        # Use the detect() method to perform nudity detection
        result = detector.detect(temp_file_path)
        
        # Process the result
        if result:
            for forbidden in forbiddens:
                if result[0]['class'] == forbidden:
                    tempData['url'] = image_url
                    tempData['isExplicit'] = True
                    tempData['assurance'] = result[0]['score']
            
            return jsonify({'url': image_url, 'isExplicit': True, 'assurance': result[0]['score'], 'kind': result[0]['class']})
        # else:
        #     return jsonify({"result": "The image does not contain nudity."})
    else:
        return jsonify({"error": f"Failed to fetch image: HTTP status code {response.status_code}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
