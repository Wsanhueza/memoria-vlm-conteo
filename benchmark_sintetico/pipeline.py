import json
import os
import re
import time
import argparse
import torch
from PIL import Image

# ==============================================================================
# PIPELINE DE EVALUACIÓN PARA BENCHMARK SINTÉTICO (2D)
# Optimizado para ejecución en CPU (Dell Inspiron 24GB RAM)
# ==============================================================================

def extract_number(text):
    """Extrae el primer número encontrado en el texto de respuesta."""
    nums = re.findall(r'\d+', str(text))
    return int(nums[0]) if nums else -1

def evaluate_model(dataset_path, images_dir, model_name):
    # Cargar el dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
        
    print(f"\nIniciando evaluación con el modelo: {model_name}")
    print(f"Total de preguntas a evaluar: {len(qa_data)}")
    print("Dispositivo configurado: CPU (Puede tardar entre 5 y 20 seg por imagen)\n")
    
    device = "cpu"
    model, processor = None, None
    
    # ---------------------------------------------------------
    # 1. Cargar Moondream2 (Ligero, ideal para CPU)
    # ---------------------------------------------------------
    if model_name == "moondream2":
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model_id = "vikhyatk/moondream2"
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to(device)
        processor = AutoTokenizer.from_pretrained(model_id)
        
    # ---------------------------------------------------------
    # 2. Cargar Qwen2-VL-2B
    # ---------------------------------------------------------
    elif model_name == "qwen2_vl":
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        model_id = "Qwen/Qwen2-VL-2B-Instruct"
        model = Qwen2VLForConditionalGeneration.from_pretrained(model_id, torch_dtype=torch.float32).to(device)
        processor = AutoProcessor.from_pretrained(model_id)

    # ---------------------------------------------------------
    # 3. Cargar YOLO (Usaremos YOLO-World para Zero-Shot)
    # YOLO normal solo detecta "personas, autos", YOLO-World detecta textos como "cuadrado rojo"
    # ---------------------------------------------------------
    elif model_name == "yolo_world":
        try:
            from ultralytics import YOLOWorld
        except ImportError:
            print("Error: Debes instalar ultralytics (pip install ultralytics)")
            return
        model = YOLOWorld('yolov8s-world.pt') # Modelo pequeño y rápido
        
    else:
        print("Modelo no soportado en este script todavía. (Falta PaliGemma e InternVL2)")
        return

    # ---------------------------------------------------------
    # Bucle de Evaluación
    # ---------------------------------------------------------
    correct = 0
    total = len(qa_data)
    
    for idx, item in enumerate(qa_data):
        img_path = os.path.join(images_dir, item["image"])
        question = item["question"]
        ground_truth = int(item["answer"])
        
        if not os.path.exists(img_path):
            print(f"Imagen no encontrada: {img_path}")
            continue
            
        image = Image.open(img_path).convert("RGB")
        prediction = -1
        
        start_time = time.time()
        
        try:
            # INFERENCIA MOONDREAM 2
            if model_name == "moondream2":
                enc_image = model.encode_image(image)
                answer_text = model.answer_question(enc_image, question, processor)
                prediction = extract_number(answer_text)
                
            # INFERENCIA QWEN2-VL
            elif model_name == "qwen2_vl":
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": img_path},
                            {"type": "text", "text": question}
                        ]
                    }
                ]
                text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt").to(device)
                
                # Desactivar gradientes para ahorrar memoria RAM
                with torch.no_grad():
                    generated_ids = model.generate(**inputs, max_new_tokens=20)
                    generated_ids_trimmed = [
                        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                    ]
                    answer_text = processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
                    prediction = extract_number(answer_text)
                    
            # INFERENCIA YOLO-WORLD
            elif model_name == "yolo_world":
                # YOLO no responde preguntas, así que mapeamos la pregunta a una clase
                if "cuadrado" in question.lower() and "rojo" in question.lower():
                    clase_buscar = "red square"
                elif "circulo" in question.lower() and "azul" in question.lower():
                    clase_buscar = "blue circle"
                elif "total" in question.lower():
                    clase_buscar = "shape"
                else:
                    clase_buscar = "geometric shape" # Default
                    
                model.set_classes([clase_buscar])
                results = model(img_path, verbose=False)
                # Contar cuántas cajas (bounding boxes) detectó
                prediction = len(results[0].boxes)

        except Exception as e:
            print(f"Error procesando imagen {item['image']}: {e}")
            
        elapsed = time.time() - start_time
        
        # Comparar resultado
        is_correct = (prediction == ground_truth)
        if is_correct:
            correct += 1
            
        print(f"[{idx+1}/{total}] Q: {question} | Verdad: {ground_truth} | Predicción: {prediction} | {'✅' if is_correct else '❌'} ({elapsed:.1f}s)")
        
    accuracy = (correct / total) * 100
    print(f"\n{'='*40}")
    print(f"RESULTADOS {model_name.upper()}")
    print(f"Precisión: {accuracy:.2f}% ({correct}/{total})")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluador de VLMs para Benchmark Sintético")
    parser.add_argument('--dataset', type=str, default='dataset.json', help='Ruta al archivo dataset.json')
    parser.add_argument('--images', type=str, default='images/', help='Directorio con las imágenes')
    parser.add_argument('--model', type=str, choices=['moondream2', 'qwen2_vl', 'yolo_world'], required=True, help='Modelo a evaluar')
    
    args = parser.parse_args()
    evaluate_model(args.dataset, args.images, args.model)