import streamlit as st
import numpy as np
import trimesh
import pyrender
from PIL import Image
import json
import io
import zipfile

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Generador 3D VQA por Capas", layout="wide")
st.title("Generador de Benchmark 3D - Control de Profundidad")

st.sidebar.header("Parámetros del Benchmark")
num_images = st.sidebar.number_input("Cantidad de Imágenes para el ZIP", min_value=1, max_value=5000, value=10)
num_cubes = st.sidebar.slider("Número de Cubos por imagen", min_value=10, max_value=2000, value=300)

# NUEVO: Control de niveles de profundidad
depth_levels = st.sidebar.slider("Niveles de Profundidad (Capas Z)", min_value=1, max_value=5, value=3)

# Ocultamos la transparencia por defecto para igualar tu imagen de referencia, 
# pero mantenemos la opción en 0.0 por si la necesitas a futuro.
transparency_ratio = st.sidebar.slider("% de Cubos Transparentes", min_value=0.0, max_value=1.0, value=0.0)

# --- CACHÉ DE GEOMETRÍA ---
@st.cache_resource
def get_base_mesh():
    return trimesh.creation.box(extents=[0.75, 0.75, 0.75])

# --- LÓGICA DE GENERACIÓN ---
def create_scene_data(n_cubes, t_ratio, d_levels, base_box):
    # 1. CÁLCULO DE LA CUADRÍCULA POR CAPAS
    # Calculamos cuánto deben medir X e Y para que quepan todos los cubos en las capas Z elegidas
    grid_res_xy = int(np.ceil(np.sqrt(n_cubes / d_levels)))
    spacing = 1.4 # Un poco más de espacio entre cubos para que parezca la imagen de referencia
    
    # Coordenadas X e Y (Plano)
    coords_xy = np.linspace(-grid_res_xy * spacing / 2, grid_res_xy * spacing / 2, grid_res_xy)
    
    # Coordenadas Z (Profundidad controlada)
    if d_levels == 1:
        coords_z = np.array([0.0])
    else:
        coords_z = np.linspace(-(d_levels - 1) * spacing, (d_levels - 1) * spacing, d_levels)
        
    x, y, z = np.meshgrid(coords_xy, coords_xy, coords_z)
    all_positions = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
    
    # Asegurarnos de no pedir más cubos de los que caben en la cuadrícula
    n_cubes_actual = min(n_cubes, len(all_positions))
    indices = np.random.choice(len(all_positions), n_cubes_actual, replace=False)
    positions = all_positions[indices]
    
    scene = pyrender.Scene(ambient_light=[0.6, 0.6, 0.6])
    solid_count, transparent_count = 0, 0
    
    # 2. CREACIÓN DE MATERIALES SIN BRILLOS (MATE)
    for pos in positions:
        is_transparent = np.random.rand() < t_ratio
        
        if is_transparent:
            color = [0.9, 0.9, 0.95, 0.2]
            alpha_mode = 'BLEND'
            transparent_count += 1
        else:
            # Tonos pastel/sólidos aleatorios
            color = [np.random.uniform(0.2, 0.9), np.random.uniform(0.2, 0.9), np.random.uniform(0.2, 0.9), 1.0]
            alpha_mode = 'OPAQUE'
            solid_count += 1
            
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=color, 
            metallicFactor=0.0,    # 0.0 = Cero aspecto metálico (Elimina reflexiones fuertes)
            roughnessFactor=1.0,   # 1.0 = Completamente rugoso/mate (Elimina el punto de luz central)
            alphaMode=alpha_mode
        )
        
        mesh = pyrender.Mesh.from_trimesh(base_box, material=material)
        pose = np.eye(4)
        pose[:3, 3] = pos
        scene.add(mesh, pose=pose)
        
    # 3. CÁMARA ADAPTATIVA Y LUCES SUAVES
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
    cam_pose = np.eye(4)
    # Alejamos la cámara dinámicamente según lo ancha que sea la cuadrícula XY
    cam_pose[:3, 3] = [0.0, 0.0, max(grid_res_xy, d_levels * 1.5) * spacing * 1.3] 
    scene.add(camera, pose=cam_pose)
    
    # Luz frontal pero suave para mantener colores planos sin sombras extremas
    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)
    scene.add(light, pose=cam_pose)
    
    metadata = {
        "total_cubes": n_cubes_actual,
        "depth_levels": d_levels,
        "questions": [
            {"question": "How many solid, fully colored cubes are visible?", "answer": str(solid_count)},
            {"question": "What is the total number of cubes present in the image?", "answer": str(n_cubes_actual)}
        ]
    }
    
    return scene, metadata

# --- SECCIÓN DE VISTA PREVIA ---
st.subheader("1. Vista Previa")
if st.button("Generar Vista Previa Rápida"):
    with st.spinner("Renderizando vista previa..."):
        base_box = get_base_mesh()
        scene, meta = create_scene_data(num_cubes, transparency_ratio, depth_levels, base_box)
        
        r = pyrender.OffscreenRenderer(viewport_width=800, viewport_height=800)
        color_img, _ = r.render(scene)
        r.delete()
        
        st.image(color_img, caption="Vista previa adaptada a capas sin brillos especulares.", use_column_width=False, width=400)
        st.json(meta)

# --- SECCIÓN DE GENERACIÓN POR LOTES ---
st.subheader("2. Generar Dataset Completo")
if st.button(f"Generar ZIP con {num_images} imágenes"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    zip_buffer = io.BytesIO()
    base_box = get_base_mesh()
    all_metadata = []
    
    status_text.text("Iniciando motor gráfico...")
    r = pyrender.OffscreenRenderer(viewport_width=1024, viewport_height=1024)
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i in range(num_images):
            status_text.text(f"Renderizando imagen {i+1} de {num_images}...")
            
            scene, meta = create_scene_data(num_cubes, transparency_ratio, depth_levels, base_box)
            meta["image_id"] = f"scene_{i:04d}.png"
            all_metadata.append(meta)
            
            color_img, _ = r.render(scene)
            img = Image.fromarray(color_img)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            zip_file.writestr(meta["image_id"], img_byte_arr.getvalue())
            
            progress_bar.progress((i + 1) / num_images)
            
        zip_file.writestr("dataset_metadata.json", json.dumps(all_metadata, indent=4))
        
    r.delete()
    status_text.text("¡Benchmark generado exitosamente!")
    
    st.download_button(
        label="📥 Descargar Dataset.zip",
        data=zip_buffer.getvalue(),
        file_name=f"benchmark_3D_{depth_levels}_capas.zip",
        mime="application/zip"
    )