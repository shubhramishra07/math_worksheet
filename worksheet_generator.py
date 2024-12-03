import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
import openai
import requests
from io import BytesIO
from PIL import Image
from reportlab.lib.utils import ImageReader
import os
import random

def generate_theme_image(theme, api_key):
    """Generate a themed clipart image using OpenAI's DALL-E"""
    openai.api_key = api_key
    print(f"Generating image for {theme}")
    
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"Generate a clip art of {theme}.",
            size="1024x1024",
            n=1
        )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        
        return ImageReader(image)
    except Exception as e:
        print(f"Failed to generate image: {e}")
        return None

def add_header(c, width, height, worksheet_title):
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 40, worksheet_title)
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Name: ___________________________")
    c.drawString(350, height - 80, "Date: ___________________________")

def create_worksheet_from_json(json_file, worksheet_title="Math Worksheet", openai_key=os.environ["OPENAI_API_KEY"]):
    with open(json_file, "r") as file:
        data = json.load(file)

    statements = []
    answers = []
    themes = [] 
    for group in data:
        for item in group:
            statements.append(item["statement"])
            answers.append(item["reasoning"])
            themes.append(item.get("theme")) 

    c = canvas.Canvas("Math_Worksheet.pdf", pagesize=letter)
    width, height = letter

    theme_image = None

    add_header(c, width, height, worksheet_title)

    y_position = height - 120
    line_spacing = 40
    c.setFont("Helvetica", 12)
    

    for i, statement in enumerate(statements):
        create_image = random.random() < 0.4
        if create_image and openai_key:
            theme_image = generate_theme_image(themes[i], openai_key) 
        
        question = f"{i + 1}. {statement}"
        if create_image and theme_image:
            wrapped_lines = textwrap.wrap(question, width=75) 
        else:
            wrapped_lines = textwrap.wrap(question, width=90) 
        
        needed_height = (len(wrapped_lines) * 20) + 30
        
        if y_position - needed_height < 100:
            c.showPage()
            add_header(c, width, height, worksheet_title)
            y_position = height - 120
            c.setFont("Helvetica", 12)

        current_y = y_position
        for line in wrapped_lines:
            c.drawString(50, current_y, line)
            current_y -= 20

        if create_image:
            image_y = y_position - 60
            c.drawImage(theme_image, width - 130, image_y, width=80, height=80)

        answer_y = y_position - (len(wrapped_lines) * 20) - 10
        c.drawString(50, answer_y, "Answer: _______________________________")
        
        y_position = answer_y - line_spacing

    c.showPage()
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 40, "Answer Key")

    c.setFont("Helvetica", 12)

    x_position = 50  
    y_position = height - 80 
    line_spacing = 20  
    wrap_width = 95  

    for i, answer in enumerate(answers):
        wrapped_lines = textwrap.wrap(f"{i + 1}. {answer}", width=wrap_width)

        if y_position - (line_spacing * len(wrapped_lines)) < 50: 
            c.showPage() 
            c.setFont("Helvetica", 12)
            x_position = 50 
            y_position = height - 80  

        for line in wrapped_lines:
            c.drawString(x_position, y_position, line)
            y_position -= line_spacing

        y_position -= 10

    c.save()


if __name__ == "__main__":
    json_file = "2.OA.A.1.json"
    name_of_file = "Addition Practice"
    openai_key = os.environ["OPENAI_API_KEY"]
    
    create_worksheet_from_json(
        json_file, 
        name_of_file,
        openai_key
    )
