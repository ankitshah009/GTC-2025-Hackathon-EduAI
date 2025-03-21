import base64
import os
import mimetypes
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""**\"Generate an image of a futuristic, sustainable city on Mars, incorporating elements of both Martian geography (as currently understood) and eco-friendly architecture from Earth, with a style reminiscent of Syd Mead's concept art.\"**"""),
            ],
        ),
    ]

    response = client.generate_content(
        model=model,
        contents=contents,
        generation_config={"response_mime_type": "image/png"},
    )

    if hasattr(response, 'candidates') and len(response.candidates) > 0:
        parts = response.candidates[0].content.parts
        if len(parts) > 0 and hasattr(parts[0], 'data'):
            image_data = parts[0].data
            # Save the image
            save_binary_file("mars_city.png", image_data)
            print("Image saved as mars_city.png")
        else:
            print("No image data in response")
    else:
        print("No valid response received")


if __name__ == "__main__":
    generate()
