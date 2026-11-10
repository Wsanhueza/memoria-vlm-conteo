import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
import json
import zipfile
import os
import random
import tempfile
import math

RANDOM_SEED = 42
# --- 1. CONFIGURACIÓN Y UTILIDADES VECTORIZADAS ---

COLORS = {
    "rojo": (255, 0, 0), "azul": (0, 0, 255), "verde": (0, 255, 0),
    "amarillo": (255, 255, 0), "morado": (128, 0, 128), "naranjo": (255, 140, 0),
    "rosado": (255, 105, 180), "celeste": (0, 200, 255)
}
SHAPES = ["cuadrado", "circulo", "triangulo", "rombo"]

def create_rect_mask(w, h, x, y, size):
    mask = np.zeros((h, w), dtype=bool)
    x1, y1 = max(0, int(x)), max(0, int(y))
    x2, y2 = min(w, int(x+size)), min(h, int(y+size))
    if x1 < x2 and y1 < y2:
        mask[y1:y2, x1:x2] = True
    return mask

def create_circle_mask(w, h, cx, cy, r):
    Y, X = np.ogrid[:h, :w]
    dist_sq = (X - cx)**2 + (Y - cy)**2
    return dist_sq <= r**2

# --- helper nuevo, agrégalo junto a create_circle_mask ---
def create_polygon_mask(w, h, points):
    mask_img = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask_img).polygon(points, fill=1)
    return np.array(mask_img, dtype=bool)

def get_triangle_points(x, y, size):
    return [(x + size/2, y), (x, y + size), (x + size, y + size)]

def get_rombo_points(x, y, size):
    return [(x + size/2, y), (x + size, y + size/2), (x + size/2, y + size), (x, y + size/2)]

# --- 2. MOTOR DE GENERACIÓN DE IMÁGENES ---

def generate_image(width, height, num_shapes, max_overlap_pct, requested_size, border_width):
    bg_color = (200, 200, 200) 
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    global_mask = np.zeros((height, width), dtype=bool)
    metadata = {"total": 0, "por_forma": {s: 0 for s in SHAPES}, "por_color": {c: 0 for c in COLORS}}
    metadata["objetos"] = []
    # --- CÁLCULO DE LÍMITE DE SEGURIDAD PARA EL TAMAÑO ---
    # Calculamos el área máxima que puede ocupar cada figura considerando la resolución y el solapamiento
    max_possible_area = (width * height * (1.0 + max_overlap_pct)) / num_shapes
    # El factor 0.75 es por "eficiencia de empaquetado" (las figuras no encajan perfectamente)
    max_safe_size = int(math.sqrt(max_possible_area) * 0.75) 
    
    # Limitamos el tamaño al máximo seguro para evitar figuras invisibles o bucles infinitos
    actual_size = min(requested_size, max_safe_size)
    actual_size = max(5, actual_size) # Tamaño mínimo de 5 píxeles por seguridad
    
    max_attempts = 150 # Incrementamos los intentos por el tamaño fijo
    
    for _ in range(num_shapes):
        shape_type = random.choice(SHAPES)
        color_name = random.choice(list(COLORS.keys()))
        color_rgb = COLORS[color_name]
        
        placed = False
        for _ in range(max_attempts):
            x = random.randint(0, width - actual_size)
            y = random.randint(0, height - actual_size)
            
            if shape_type == "cuadrado":
                shape_mask = create_rect_mask(width, height, x, y, actual_size)
            elif shape_type == "circulo":
                r = actual_size // 2
                shape_mask = create_circle_mask(width, height, x + r, y + r, r)
            elif shape_type == "triangulo":
                shape_mask = create_polygon_mask(width, height, get_triangle_points(x, y, actual_size))
            else:  # rombo
                shape_mask = create_polygon_mask(width, height, get_rombo_points(x, y, actual_size))
            
            shape_area = np.sum(shape_mask)
            if shape_area == 0: continue
            
            overlap_area = np.sum(global_mask & shape_mask)
            overlap_ratio = overlap_area / shape_area
            
            if overlap_ratio <= max_overlap_pct:
                global_mask |= shape_mask

                # --- DIBUJADO CON BORDES ---
                outline_color = (30, 30, 30)  # Borde gris muy oscuro/negro
                if shape_type == "cuadrado":
                    draw.rectangle([x, y, x+actual_size, y+actual_size], fill=color_rgb, outline=outline_color, width=border_width)
                elif shape_type == "circulo":
                    draw.ellipse([x, y, x+actual_size, y+actual_size], fill=color_rgb, outline=outline_color, width=border_width)
                elif shape_type == "triangulo":
                    draw.polygon(get_triangle_points(x, y, actual_size), fill=color_rgb, outline=outline_color, width=border_width)
                else:  # rombo
                    draw.polygon(get_rombo_points(x, y, actual_size), fill=color_rgb, outline=outline_color, width=border_width)
                
                metadata["total"] += 1
                metadata["por_forma"][shape_type] += 1
                metadata["por_color"][color_name] += 1
                metadata["objetos"].append({
                    "forma": shape_type, "color": color_name,
                    "x": x, "y": y, "tamano": actual_size
                })
                placed = True
                break
                
    metadata["tamano_usado"] = actual_size # Guardar el tamaño final usado para trazabilidad
    return img, metadata

# --- 3. GENERADOR DE PREGUNTAS (QA BUILDER) ---
# (Se mantiene igual, puedes añadir más preguntas aquí)

SHAPE_EN = {"cuadrado": "square", "circulo": "circle", "triangulo": "triangle", "rombo": "diamond"}
COLOR_EN = {
    "rojo": "red", "azul": "blue", "verde": "green", "amarillo": "yellow",
    "morado": "purple", "naranjo": "orange", "rosado": "pink", "celeste": "light blue"
}

def generate_qa_pairs(metadata, img_filename):
    questions = []
    questions.append({
        "image": img_filename,
        "question": "How many shapes are there in total in the image?",
        "answer": str(metadata["total"]),
        "type": "conteo_general"
    })

    target_shape = random.choice(SHAPES)
    questions.append({
        "image": img_filename,
        "question": f"How many {SHAPE_EN[target_shape]}s are there in the image?",
        "answer": str(metadata["por_forma"][target_shape]),
        "type": "conteo_forma"
    })

    target_color = random.choice(list(COLORS.keys()))
    count_color = sum(1 for o in metadata["objetos"] if o["color"] == target_color)
    questions.append({
        "image": img_filename,
        "question": f"How many {COLOR_EN[target_color]} shapes are there in the image?",
        "answer": str(count_color),
        "type": "conteo_color"
    })

    target_shape2 = random.choice(SHAPES)
    target_color2 = random.choice(list(COLORS.keys()))
    count_comb = sum(1 for o in metadata["objetos"] if o["forma"] == target_shape2 and o["color"] == target_color2)
    questions.append({
        "image": img_filename,
        "question": f"How many {COLOR_EN[target_color2]} {SHAPE_EN[target_shape2]}s are there in the image?",
        "answer": str(count_comb),
        "type": "conteo_combinado"
    })
    return questions

# --- 4. PIPELINE Y EMPAQUETADO ---

def run_pipeline(num_images, num_shapes, max_overlap, res, req_size, border_w, progress=gr.Progress()):
    max_overlap_pct = max_overlap / 100.0 
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "benchmark_2d_sintetico.zip")
    
    all_qa_pairs = []
    tamano_final = req_size
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Barra de progreso integrada
        for i in progress.tqdm(range(num_images), desc="Renderizando dataset"):
            random.seed(RANDOM_SEED + i)  # Semilla para reproducibilidad por imagen
            img, metadata = generate_image(res, res, num_shapes, max_overlap_pct, req_size, border_w)
            tamano_final = metadata["tamano_usado"] # Capturamos el tamaño ajustado
            
            img_filename = f"escena_{i:04d}.png"
            img_path = os.path.join(temp_dir, img_filename)
            img.save(img_path)
            zipf.write(img_path, arcname=f"images/{img_filename}")
            
            qa_pairs = generate_qa_pairs(metadata, img_filename)
            all_qa_pairs.extend(qa_pairs)
            
        json_path = os.path.join(temp_dir, "dataset.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_qa_pairs, f, indent=4, ensure_ascii=False)
        zipf.write(json_path, arcname="dataset.json")
        
    return zip_path, tamano_final

def run_pipeline_por_lotes(figuras_min, figuras_max, paso, imgs_por_lote,
                            max_overlap, res, req_size, border_w, progress=gr.Progress()):
    """Genera el dataset variando num_shapes progresivamente: para cada conteo
    en [figuras_min, figuras_max] (paso 'paso') genera 'imgs_por_lote' imagenes.
    Pensado para poder estudiar despues como cambia el desempeño del modelo
    a medida que aumenta la dificultad (cantidad de figuras) de forma controlada."""
    max_overlap_pct = max_overlap / 100.0
    lista_conteos = list(range(int(figuras_min), int(figuras_max) + 1, int(paso)))

    plan = []
    for n in lista_conteos:
        plan.extend([n] * int(imgs_por_lote))
    # "plan" es la lista completa: cuantas figuras tendra cada imagen, en orden

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "benchmark_2d_sintetico_lotes.zip")
    all_qa_pairs = []

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img_idx, num_shapes in enumerate(progress.tqdm(plan, desc="Renderizando dataset por lotes")):
            random.seed(RANDOM_SEED + img_idx)
            img, metadata = generate_image(res, res, num_shapes, max_overlap_pct, req_size, border_w)

            img_filename = f"escena_{img_idx:04d}_n{num_shapes:03d}.png"
            img_path = os.path.join(temp_dir, img_filename)
            img.save(img_path)
            zipf.write(img_path, arcname=f"images/{img_filename}")

            qa_pairs = generate_qa_pairs(metadata, img_filename)
            all_qa_pairs.extend(qa_pairs)

        json_path = os.path.join(temp_dir, "dataset.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_qa_pairs, f, indent=4, ensure_ascii=False)
        zipf.write(json_path, arcname="dataset.json")

    return zip_path, len(plan), lista_conteos

# --- 5. INTERFAZ GRÁFICA (GRADIO) ---

def interface_logic(num_images, shapes, overlap, res, req_size, border_w, progress=gr.Progress()):
    zip_file, final_size = run_pipeline(int(num_images), int(shapes), float(overlap), int(res), int(req_size), int(border_w), progress)

    mensaje = f"¡Benchmark generado con éxito!\nImágenes generadas: {int(num_images)}\nFiguras por imagen: {int(shapes)}"
    if final_size < req_size:
        mensaje += f"\n⚠️ NOTA: El tamaño se redujo automáticamente de {req_size}px a {final_size}px para evitar que el lienzo se sature y respetar el límite de solapamiento."
    else:
        mensaje += f"\nTamaño de figura: {final_size}px (Sin reducción requerida)."

    return zip_file, mensaje

def interface_logic_lotes(fmin, fmax, paso, lote, overlap, res, req_size, border_w, progress=gr.Progress()):
    zip_file, total_imgs, conteos = run_pipeline_por_lotes(
        int(fmin), int(fmax), int(paso), int(lote),
        float(overlap), int(res), int(req_size), int(border_w), progress
    )
    mensaje = (f"¡Benchmark por lotes generado con éxito!\n"
               f"Conteos de figuras usados: {conteos}\n"
               f"Imágenes por cada conteo: {int(lote)}\n"
               f"Total de imágenes generadas: {total_imgs}")
    return zip_file, mensaje

with gr.Blocks(title="Generador de Benchmark 2D para VLM") as app:
    gr.Markdown("# Generador Sintético 2D (Con Bordes y Tamaño Fijo)")

    with gr.Tabs():
        with gr.Tab("Modo Fijo"):
            with gr.Row():
                with gr.Column():
                    num_img_slider = gr.Slider(1, 1000, value=10, step=1, label="Cantidad de Imágenes")
                    num_shapes_slider = gr.Slider(1, 1000, value=50, step=1, label="Figuras por Imagen")
                    overlap_slider = gr.Slider(0, 90, value=30, step=5, label="Solapamiento Máximo Permitido (%)")
                    res_slider = gr.Slider(256, 2048, value=1024, step=128, label="Resolución (Píxeles)")

                    gr.Markdown("### Control de Estilo")
                    size_slider = gr.Slider(10, 300, value=50, step=5, label="Tamaño Fijo Solicitado (Píxeles)")
                    border_slider = gr.Slider(0, 10, value=2, step=1, label="Grosor del Borde (0 = sin borde)")

                    generate_btn = gr.Button("Generar Dataset (.zip)", variant="primary")

                with gr.Column():
                    output_msg = gr.Textbox(label="Estado / Log del proceso", lines=4)
                    output_file = gr.File(label="Descargar Benchmark")

            generate_btn.click(
                fn=interface_logic,
                inputs=[num_img_slider, num_shapes_slider, overlap_slider, res_slider, size_slider, border_slider],
                outputs=[output_file, output_msg]
            )

        with gr.Tab("Modo por Lotes (dificultad progresiva)"):
            gr.Markdown(
                "Genera el dataset variando la cantidad de figuras en un rango, "
                "con la misma cantidad de imágenes por cada conteo. "
                "Ej: min=1, max=10, paso=1, imágenes por conteo=10 → 10 imágenes con 1 figura, "
                "10 con 2, ... hasta 10 con 10 figuras (100 imágenes en total)."
            )
            with gr.Row():
                with gr.Column():
                    min_slider = gr.Slider(1, 500, value=1, step=1, label="Mínimo de Figuras")
                    max_slider = gr.Slider(1, 500, value=10, step=1, label="Máximo de Figuras")
                    paso_slider = gr.Slider(1, 50, value=1, step=1, label="Paso")
                    lote_slider = gr.Slider(1, 200, value=10, step=1, label="Imágenes por cada Conteo")
                    overlap_slider2 = gr.Slider(0, 90, value=30, step=5, label="Solapamiento Máximo Permitido (%)")
                    res_slider2 = gr.Slider(256, 2048, value=1024, step=128, label="Resolución (Píxeles)")

                    gr.Markdown("### Control de Estilo")
                    size_slider2 = gr.Slider(10, 300, value=50, step=5, label="Tamaño Fijo Solicitado (Píxeles)")
                    border_slider2 = gr.Slider(0, 10, value=2, step=1, label="Grosor del Borde (0 = sin borde)")

                    generate_btn2 = gr.Button("Generar Dataset por Lotes (.zip)", variant="primary")

                with gr.Column():
                    output_msg2 = gr.Textbox(label="Estado / Log del proceso", lines=4)
                    output_file2 = gr.File(label="Descargar Benchmark")

            generate_btn2.click(
                fn=interface_logic_lotes,
                inputs=[min_slider, max_slider, paso_slider, lote_slider,
                        overlap_slider2, res_slider2, size_slider2, border_slider2],
                outputs=[output_file2, output_msg2]
            )

if __name__ == "__main__":
    app.launch()