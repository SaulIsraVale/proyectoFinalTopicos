import folium
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Cargar el CSV actualizado
data_path = "C:/Users/sivv1/OneDrive/Documentos/UAEMEX/JHOVANI/proyectoFinal/tablaNueva.csv"
data = pd.read_csv(data_path)

# Cargar el GeoJSON
geojson_path = "C:/Users/sivv1/OneDrive/Documentos/UAEMEX/JHOVANI/proyectoFinal/estadosCorreg.geojson"
geojson_data = gpd.read_file(geojson_path)

# Agrupar por estado para obtener los datos requeridos
state_data = data.groupby("estado").agg(
    ingreso_total=("ingreso_total", "sum"),
    ingreso_promedio=("ingreso_total", "mean"),
    gasto_total=("gasto_total", "sum"),
    gasto_promedio=("gasto_total", "mean"),
    utilidad_total=("utilidad_total", "sum"),
    utilidad_promedio=("utilidad_total", "mean")  # Nueva columna de utilidad promedio
).reset_index()

# Crear un mapa de Folium centrado en México
m = folium.Map(location=[23.6345, -102.5528], zoom_start=5)

# Función para normalizar colores de ingreso
def get_income_color(ingreso_total, max_income):
    if ingreso_total > max_income * 0.7:
        return 'green'
    elif ingreso_total > max_income * 0.4:
        return 'orange'
    else:
        return 'red'

# Encontrar el ingreso máximo para establecer los colores
max_income = state_data['ingreso_total'].max()

# Función para crear el gráfico y devolverlo como una imagen en base64
def create_chart(estado_data):
    fig, ax = plt.subplots(figsize=(5, 3))
    labels = ['Ingreso Total', 'Ingreso Promedio', 'Gasto Total', 'Gasto Promedio', 'Utilidad Total', 'Utilidad Promedio']
    values = [
        estado_data['ingreso_total'].values[0],
        estado_data['ingreso_promedio'].values[0],
        estado_data['gasto_total'].values[0],
        estado_data['gasto_promedio'].values[0],
        estado_data['utilidad_total'].values[0],
        estado_data['utilidad_promedio'].values[0]
    ]
    ax.bar(labels, values, color=['blue', 'lightblue', 'orange', 'lightcoral', 'purple', 'mediumpurple'])
    ax.set_title('Ingresos, Gastos y Utilidades')
    ax.tick_params(axis='x', rotation=45)  # Rotar etiquetas para mayor legibilidad

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches="tight")  # Ajustar tamaño para que las barras se muestren correctamente
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    return img_base64

# Función para crear el popup con el gráfico
def create_popup(estado):
    estado_data = state_data[state_data['estado'] == estado]
    if estado_data.empty:
        html = f"""
        <h4>{estado}</h4>
        <p>No hay datos disponibles para este estado en el CSV.</p>
        """
    else:
        ingreso_total = estado_data['ingreso_total'].values[0]
        ingreso_promedio = estado_data['ingreso_promedio'].values[0]
        gasto_total = estado_data['gasto_total'].values[0]
        gasto_promedio = estado_data['gasto_promedio'].values[0]
        utilidad_total = estado_data['utilidad_total'].values[0]
        utilidad_promedio = estado_data['utilidad_promedio'].values[0]  # Nueva línea para utilidad promedio
        
        img_base64 = create_chart(estado_data)
        
        html = f"""
        <div style="width: 300px; height: 400px;">
            <h3 style="text-align: center;">{estado}</h3>
            <p><strong>Ingreso Total:</strong> ${ingreso_total:,.2f}</p>
            <p><strong>Ingreso Promedio:</strong> ${ingreso_promedio:,.2f}</p>
            <p><strong>Gasto Total:</strong> ${gasto_total:,.2f}</p>
            <p><strong>Gasto Promedio:</strong> ${gasto_promedio:,.2f}</p>
            <p><strong>Utilidad Total:</strong> ${utilidad_total:,.2f}</p>
            <p><strong>Utilidad Promedio:</strong> ${utilidad_promedio:,.2f}</p>
            <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto;"/>
        </div>
        """
    return folium.Popup(html, max_width=400)

# Agregar el GeoJSON al mapa de Folium y asignar popups con color basado en ingreso
for _, feature in geojson_data.iterrows():
    estado = feature['state_name']
    estado_data = state_data[state_data['estado'] == estado]
    
    # Determinar el color según el ingreso total
    if not estado_data.empty:
        ingreso_total = estado_data['ingreso_total'].values[0]
        color = get_income_color(ingreso_total, max_income)
    else:
        color = 'gray'  # Color para estados sin datos

    estado_popup = create_popup(estado)
    
    # Crear un GeoJson para cada estado individualmente
    folium.GeoJson(
        feature['geometry'],
        name=estado,
        style_function=lambda x, color=color: {
            'fillColor': color,
            'fillOpacity': 0.6,
            'color': 'black',
            'weight': 1
        }
    ).add_child(estado_popup).add_to(m)

# Añadir leyenda personalizada en la esquina superior derecha
legend_html = """
<div style="
    position: fixed; 
    top: 10px; right: 10px; width: 130px; height: 130px; 
    background-color: white; z-index:9999; font-size:12px;
    border:1px solid grey; border-radius:5px; padding: 8px;">
    <h4 style="text-align:center; margin:0; font-size:14px;">Leyenda</h4>
    <p style="margin:5px 0;"><i style="background:green;width:15px;height:15px;display:inline-block;margin-right:5px;"></i> Ingreso alto</p>
    <p style="margin:5px 0;"><i style="background:orange;width:15px;height:15px;display:inline-block;margin-right:5px;"></i> Ingreso medio</p>
    <p style="margin:5px 0;"><i style="background:red;width:15px;height:15px;display:inline-block;margin-right:5px;"></i> Ingreso bajo</p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Guardar el mapa como archivo HTML
output_path = "C:/Users/sivv1/OneDrive/Documentos/UAEMEX/JHOVANI/proyectoFinal/mapa_interactivo_con_popup.html"
m.save(output_path)
print(f"Mapa guardado en: {output_path}")
