from openai import AsyncOpenAI
import os
from dotenv import load_dotenv


load_dotenv()


OPEN_AI_KEY = os.getenv("OPEN_AI")

client = AsyncOpenAI(
    api_key=OPEN_AI_KEY,
    base_url="https://openrouter.ai/api/v1",
    timeout=60.0,
    max_retries=2
)


async def identify_image(
    base64_image: str,
    model: str = "google/gemini-2.5-flash",
    image_format: str = "jpeg"
):

    prompt = """Ты - экспертный определитель объектов. Рассмотри изображение и определи, что на нем.

Требования к ответу:
1. Назови объект максимально конкретно (порода собаки, вид птицы, модель машины, сорт растения)
2. Если уверен менее чем на 90% - укажи несколько вариантов с вероятностями
3. Формат ответа: "Объект: [название]\nУверенность: [%]\nПояснение: [почему так решил]"
4. Если объект не удается точно идентифицировать, напиши "Не удалось определить точно" и дай общую категорию

Примеры:
- Для птицы: "Обыкновенная лазоревка (Cyanistes caeruleus)"
- Для растения: "Ромашка аптечная (Matricaria chamomilla)"
- Для машины: "Toyota Camry XV70 2018 года"

Что на изображении?"""
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Ошибка: {str(e)}"