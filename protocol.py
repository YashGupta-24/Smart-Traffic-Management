from uagents import Context, Model, Protocol
import asyncio, random, os, cv2
from ultralytics import YOLO
import google.generativeai as genai
from dotenv import load_dotenv
import openai 

# Load environment variables from .env file
load_dotenv()

class AgentCall(Model):
    display_time :int
    status: bool

class ControlRequest(Model):
    calculated_time :int

protocol = Protocol()

# Get the directory where protocol.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(current_dir, "data")
image_files = [f for f in os.listdir(data_folder) if f.endswith(('.png', '.jpg', '.jpeg','.webp'))]

model = YOLO("yolov8n.pt") 
class_names = model.names

# Configure Gemini (you'll need to set up your API key)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-pro')
# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

async def object_count(ctx: Context):
    if not image_files:
        ctx.logger.info("Error: No images found in the data folder.")
        return 0
    
    image_path = os.path.join(data_folder, random.choice(image_files))
    frame = cv2.imread(image_path)

    if frame is None:
        ctx.logger.info("Error: Could not read the image.")
        return 0
    
    results = model(frame, verbose=False)  
    class_counts = {name: 0 for name in class_names}

    for result in results:
        for box in result.boxes:
            class_name = class_names[int(box.cls.item())]
            if class_name not in class_counts:
                class_counts[class_name] = 0
            class_counts[class_name] += 1
    
    detection_summary = ", ".join(f"{count} {class_name}" for class_name, count in class_counts.items() if count > 0)
    
    ctx.logger.info(f"Detected: {detection_summary}")
    
    # Send to Gemini and get recommended time
    prompt = f"""
    Based on the following traffic detection data: {detection_summary}
    Calculate the optimal traffic signal duration in seconds to ensure smooth traffic flow.
    Please respond with only a number between 10 and 60.
    """
    
    response = await get_gemini_response(prompt)  # You'll need to implement this function
    try:
        recommended_time = int(response)
        recommended_time = max(10, min(60, recommended_time))  # Ensure time is between 10-60 seconds
        return recommended_time
    except ValueError:
        return 30  # Default fallback time

async def get_gemini_response(prompt: str) -> str:
    # response = await gemini_model.generate_content_async(prompt)
    # return response.text.strip()
    client = openai.AsyncOpenAI()  # Use AsyncOpenAI instead of OpenAI
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a traffic analysis assistant. Respond only with a number between 10 and 60."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

@protocol.on_message(model=AgentCall)
async def on_message(ctx: Context, sender: str, msg: AgentCall): 
    if msg.status == True:
        for i in range(msg.display_time, 0, -1):
            ctx.logger.info(f"{i} GO")
            await asyncio.sleep(1)
    else:
        for i in range(msg.display_time, 0, -1):
            ctx.logger.info(f"{i} STOP")
            await asyncio.sleep(1)
        ctx.logger.info("0")
        # ctx.logger.info('I am scanning for the density of vehicles')
        calculated_time = await object_count(ctx)
        # ctx.logger.info(f'Based on current traffic density, recommended signal duration: {calculated_time} seconds')
        await ctx.send(sender, ControlRequest(calculated_time=calculated_time))


