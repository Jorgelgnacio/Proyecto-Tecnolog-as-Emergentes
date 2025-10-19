import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.gridspec import GridSpec
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Admisión 2025-I",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2e86ab;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .sub-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .header-image {
        text-align: center;
        margin-bottom: 1rem;
    }
    .header-image img {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 100%;
        height: auto;
    }
</style>
""", unsafe_allow_html=True)

# Header con imagen
# Ruta de la imagen local
IMAGEN_LOCAL = "Logotipo.png"  # Cambia por el nombre de tu archivo

# Header con imagen local
if os.path.exists(IMAGEN_LOCAL):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(IMAGEN_LOCAL, 
                 use_column_width=True,
                 caption="Universidad Nacional Agraria La Molina - Proceso de Admisión")
else:
    st.warning("⚠️ No se encontró la imagen local. Usando imagen por defecto.")
    # Opcional: Usar imagen online como respaldo
    st.image("http://oade.lamolina.edu.pe:99/dist/Unalm/img/Logotipo-color.png", 
             use_column_width=True,
             caption="Universidad Nacional Agraria La Molina - Proceso de Admisión")




def convertir_a_escala_20(dataframe):
    """Convierte las calificaciones a escala de 0 a 20"""
    df_convertido = dataframe.copy()
    
    # Definir los máximos posibles para cada área
    maximos = {
        'RV': 25, 'RM': 25, 'Arit': 5, 'Alg': 5, 'Geo': 4, 'Trig': 4,
        'Bio': 6, 'Qui': 6, 'Fis': 6, 'Eco': 4, 'Geog': 5, 'His': 5, 'Final': 100
    }
    
    # Lista de columnas de calificaciones
    columnas_calificaciones = ['RV', 'RM', 'Arit', 'Alg', 'Geo', 'Trig', 'Bio', 'Qui', 'Fis', 'Eco', 'Geog', 'His', 'Final']
    
    # Convertir SOLO las columnas de calificaciones a escala 0-20
    for col in columnas_calificaciones:
        if col in df_convertido.columns and col in maximos:
            df_convertido[col] = (df_convertido[col] / maximos[col]) * 20
    
    # Redondear SOLO las columnas convertidas
    df_convertido[columnas_calificaciones] = df_convertido[columnas_calificaciones].round(2)
    
    return df_convertido

def analisis_materias(dataframe):
    """Función para el análisis específico por materias"""
    
    st.markdown('<div class="section-header">📚 Análisis Detallado por Materias</div>', unsafe_allow_html=True)
    
    df_plot = dataframe
    columnas_sin_final = ['RV', 'RM', 'Arit', 'Alg', 'Geo', 'Trig', 'Bio', 'Qui', 'Fis', 'Eco', 'Geog', 'His']
    columnas_calificaciones = ['RV', 'RM', 'Arit', 'Alg', 'Geo', 'Trig', 'Bio', 'Qui', 'Fis', 'Eco', 'Geog', 'His', 'Final']
    
    # Métricas rápidas de materias
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mejor_materia = df_plot[columnas_sin_final].mean().idxmax()
        mejor_promedio = df_plot[columnas_sin_final].mean().max()
        st.metric("Mejor rendimiento", f"{mejor_materia}", f"{mejor_promedio:.1f}")
    
    with col2:
        peor_materia = df_plot[columnas_sin_final].mean().idxmin()
        peor_promedio = df_plot[columnas_sin_final].mean().min()
        st.metric("Menor rendimiento", f"{peor_materia}", f"{peor_promedio:.1f}")
    
    with col3:
        mayor_variabilidad = df_plot[columnas_sin_final].std().idxmax()
        mayor_std = df_plot[columnas_sin_final].std().max()
        st.metric("Mayor variabilidad", f"{mayor_variabilidad}", f"{mayor_std:.1f}")
    
    with col4:
        mejor_correlacion = df_plot[columnas_calificaciones].corr()['Final'].drop('Final').idxmax()
        correlacion_valor = df_plot[columnas_calificaciones].corr()['Final'].drop('Final').max()
        st.metric("Mejor correlación con Final", f"{mejor_correlacion}", f"{correlacion_valor:.3f}")

    # 1. GRÁFICO DE BARRAS COMPARATIVO CON RADAR
    st.markdown("#### 1. Comparativa de Rendimiento por Materia")
    
    fig = plt.figure(figsize=(20, 8))
    gs = GridSpec(1, 2, figure=fig)

    # Subplot 1: Radar chart
    ax1 = fig.add_subplot(gs[0, 0], polar=True)
    promedios = [df_plot[materia].mean() for materia in columnas_sin_final]
    angles = np.linspace(0, 2*np.pi, len(promedios), endpoint=False).tolist()
    angles += angles[:1]
    promedios_radar = promedios + [promedios[0]]

    ax1.plot(angles, promedios_radar, 'o-', linewidth=2, label='Promedio', color='blue', markersize=8)
    ax1.fill(angles, promedios_radar, alpha=0.25, color='blue')
    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(columnas_sin_final)
    ax1.set_ylim(0, 20)
    ax1.set_yticks([0, 5, 10, 15, 20])
    ax1.grid(True)
    ax1.set_title('Perfil Académico Promedio - Gráfico Radar', fontsize=14, fontweight='bold', pad=20)

    # Subplot 2: Barras comparativas
    ax2 = fig.add_subplot(gs[0, 1])
    colors = plt.cm.Set3(np.linspace(0, 1, len(columnas_sin_final)))
    bars = ax2.bar(range(len(promedios)), promedios, color=colors, alpha=0.7, edgecolor='black')

    ax2.set_xticks(range(len(promedios)))
    ax2.set_xticklabels(columnas_sin_final, rotation=45)
    ax2.set_ylabel('Calificación (0-20)')
    ax2.set_ylim(0, 20)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_title('Calificaciones Promedio por Materia', fontsize=14, fontweight='bold')

    # Añadir valores en las barras
    for bar, valor in zip(bars, promedios):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{valor:.1f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # 2. MATRIZ DE CORRELACIÓN (SOLO calificaciones)
    st.markdown("#### 2. Matriz de Correlación entre Materias")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    correlaciones = df_plot[columnas_calificaciones].corr()

    im = ax.imshow(correlaciones, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)

    ax.set_xticks(range(len(columnas_calificaciones)))
    ax.set_yticks(range(len(columnas_calificaciones)))
    ax.set_xticklabels(columnas_calificaciones, rotation=45, ha='right')
    ax.set_yticklabels(columnas_calificaciones)

    # Añadir valores en las celdas
    for i in range(len(columnas_calificaciones)):
        for j in range(len(columnas_calificaciones)):
            color = 'white' if abs(correlaciones.iloc[i, j]) > 0.5 else 'black'
            ax.text(j, i, f'{correlaciones.iloc[i, j]:.2f}', 
                    ha="center", va="center", color=color, fontweight='bold', fontsize=8)

    ax.set_title('Matriz de Correlación entre Materias', fontsize=16, fontweight='bold')
    plt.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # 3. ANÁLISIS POR GÉNERO (si existe la columna SEXO)
    if 'SEXO' in df_plot.columns:
        st.markdown("#### 3. Análisis de Rendimiento por Género")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
        
        # Boxplot por género para el puntaje final
        generos = df_plot['SEXO'].unique()
        for i, genero in enumerate(generos):
            data_genero = df_plot[df_plot['SEXO'] == genero]['Final']
            positions = [i + 1]
            box = ax1.boxplot([data_genero], positions=positions, widths=0.6, 
                            patch_artist=True, labels=[genero])
            for patch in box['boxes']:
                patch.set_facecolor(plt.cm.Pastel1(i))
        
        ax1.set_ylabel('Puntaje Final (0-20)')
        ax1.set_ylim(0, 20)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_title('Puntaje Final por Género', fontsize=14, fontweight='bold')
        
        # Promedio por género para cada materia
        if len(generos) > 0:
            promedio_genero_materia = df_plot.groupby('SEXO')[columnas_sin_final].mean().T
            
            for genero in promedio_genero_materia.columns:
                ax2.plot(range(len(columnas_sin_final)), promedio_genero_materia[genero], 
                        'o-', label=genero, linewidth=2, markersize=6)
            
            ax2.set_xticks(range(len(columnas_sin_final)))
            ax2.set_xticklabels(columnas_sin_final, rotation=45)
            ax2.set_ylabel('Calificación Promedio (0-20)')
            ax2.set_ylim(0, 20)
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            ax2.set_title('Rendimiento por Género y Materia', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # 4. HISTOGRAMAS ACUMULADOS PARA LAS PRINCIPALES MATERIAS
    st.markdown("#### 4. Distribución de Calificaciones por Materia")
    
    fig, axes = plt.subplots(3, 4, figsize=(20, 12))
    axes = axes.ravel()

    # Seleccionar las primeras 12 materias para los histogramas
    materias_histograma = columnas_sin_final[:12]
    colors = plt.cm.Set3(np.linspace(0, 1, len(materias_histograma)))

    for i, materia in enumerate(materias_histograma):
        if i < len(axes):
            axes[i].hist(df_plot[materia], bins=15, alpha=0.7, color=colors[i], edgecolor='black')
            axes[i].set_xlim(0, 20)
            axes[i].set_xlabel('Calificación')
            axes[i].set_ylabel('Frecuencia')
            axes[i].set_title(f'{materia}\n(μ={df_plot[materia].mean():.1f}, σ={df_plot[materia].std():.1f})')
            axes[i].grid(True, alpha=0.3)

    # Ocultar ejes vacíos
    for i in range(len(materias_histograma), len(axes)):
        axes[i].set_visible(False)

    plt.suptitle('Distribución de Calificaciones por Materia', fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # 5. ESTADÍSTICAS RESUMEN
    st.markdown("#### 5. Estadísticas Resumen Detalladas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 PUNTAJE FINAL:**")
        st.write(f"- Promedio: {df_plot['Final'].mean():.2f}")
        st.write(f"- Máximo: {df_plot['Final'].max():.2f}")
        st.write(f"- Mínimo: {df_plot['Final'].min():.2f}")
        st.write(f"- Desviación estándar: {df_plot['Final'].std():.2f}")
        
        st.markdown("**🎯 TOP 5 MATERIAS CON MEJOR RENDIMIENTO:**")
        mejores_materias = df_plot[columnas_sin_final].mean().sort_values(ascending=False)
        for i, (materia, promedio) in enumerate(mejores_materias.head(5).items(), 1):
            st.write(f"{i}. {materia}: {promedio:.2f}")
    
    with col2:
        st.markdown("**⚠️ TOP 5 MATERIAS CON MAYOR VARIABILIDAD:**")
        materias_variabilidad = df_plot[columnas_sin_final].std().sort_values(ascending=False)
        for i, (materia, std) in enumerate(materias_variabilidad.head(5).items(), 1):
            st.write(f"{i}. {materia}: {std:.2f}")
        
        st.markdown("**🔗 TOP 5 CORRELACIONES CON PUNTAJE FINAL:**")
        correlaciones_final = df_plot[columnas_calificaciones].corr()['Final'].sort_values(ascending=False)
        for i, (materia, corr) in enumerate(correlaciones_final.head(6).items(), 1):
            if materia != 'Final' and i <= 5:
                st.write(f"{materia}: {corr:.3f}")

    # 6. TABLA DE ESTADÍSTICAS COMPLETA
    st.markdown("#### 6. Tabla Completa de Estadísticas por Materia")
    
    stats_df = pd.DataFrame({
        'Materia': columnas_sin_final,
        'Promedio': [df_plot[materia].mean() for materia in columnas_sin_final],
        'Mediana': [df_plot[materia].median() for materia in columnas_sin_final],
        'Desviación Estándar': [df_plot[materia].std() for materia in columnas_sin_final],
        'Máximo': [df_plot[materia].max() for materia in columnas_sin_final],
        'Mínimo': [df_plot[materia].min() for materia in columnas_sin_final],
        'Correlación con Final': [df_plot[columnas_calificaciones].corr()['Final'][materia] for materia in columnas_sin_final]
    }).round(3)
    
    st.dataframe(stats_df.sort_values('Promedio', ascending=False), use_container_width=True)


    
def generar_todas_graficas(dataframe):
    """Función para generar todas las gráficas en Streamlit"""
    
    df_plot = dataframe
    
    # Header principal
    st.markdown('<div class="main-header">📊 Dashboard de Análisis - Proceso de Admisión 2025-I</div>', unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Postulantes", len(df_plot))
    with col2:
        st.metric("Edad Promedio", f"{df_plot['EDAD'].mean():.1f} años")
    with col3:
        st.metric("Puntaje Promedio", f"{df_plot['Final'].mean():.2f}")
    with col4:
        coincidencia = (df_plot['OPCION.1'] == df_plot['Especialidad']).mean() * 100
        st.metric("Coincidencia 1ra Opción", f"{coincidencia:.1f}%")
    
    # 1. Distribución de edades
    st.markdown('<div class="section-header">1. Distribución de Edades</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df_plot['EDAD'], bins=8, color='cornflowerblue', edgecolor='black', alpha=0.7)
    ax.set_title("Distribución de edades de postulantes", fontsize=14, fontweight='bold')
    ax.set_xlabel("Edad", fontsize=12)
    ax.set_ylabel("Frecuencia", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)
    plt.close()
    
    # 2. Distribución por sexo
    # 2. Distribución por sexo
    st.markdown('<div class="section-header">2. Distribución por Sexo</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Obtener los conteos y ordenarlos consistentemente
        sexo_counts = df_plot['SEXO'].value_counts()
        
        # Definir colores según el sexo (coherentes con las métricas)
        colors = []
        labels = []
        for sexo in sexo_counts.index:
            if sexo.lower() == 'femenino':
                colors.append('#E75480')  # Rosa igual que las métricas
                labels.append(sexo)
            elif sexo.lower() == 'masculino':
                colors.append('#0074D9')  # Azul igual que las métricas
                labels.append(sexo)
            else:
                colors.append('lightgray')  # Color por defecto
                labels.append(sexo)
        
        # Crear el gráfico pie con colores personalizados
        wedges, texts, autotexts = ax.pie(sexo_counts.values, labels=labels, autopct='%1.1f%%',
                                        colors=colors, startangle=90, explode=(0.05, 0) if len(sexo_counts) == 2 else (0,))
        
        # Personalizar el texto de los porcentajes
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        # Personalizar las etiquetas
        for text in texts:
            text.set_fontweight('bold')
            text.set_fontsize(12)
        
        ax.set_title('Distribución de Postulantes por Sexo', fontsize=14, fontweight='bold')
        ax.set_ylabel('')
        st.pyplot(fig)
        plt.close()

    with col2:
        sexo_counts = df_plot['SEXO'].value_counts()
        for sexo, count in sexo_counts.items():
            # Definir colores según el sexo (coherentes con el pie chart)
            if sexo.lower() == 'femenino':
                color = '#E75480'  # Rosa
            elif sexo.lower() == 'masculino':
                color = '#0074D9'  # Azul
            else:
                color = 'gray'  # Color por defecto para otros casos
            
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: {color}; font-weight: bold;">{sexo}</h4>
                <h3 style="color: {color}; font-weight: bold;">{count}</h3>
                <p style="color: {color}; font-weight: bold;">({count/len(df_plot)*100:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)


    # 3. Distribución por nacionalidad
    # 3. Distribución por nacionalidad
    st.markdown('<div class="section-header">3. Distribución por Nacionalidad</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    nationality_counts = df_plot['NACIONALIDAD'].value_counts()
    bars = ax.bar(nationality_counts.index, nationality_counts.values, 
                color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_title('Distribución de Postulantes por Nacionalidad', fontsize=14, fontweight='bold')
    ax.set_xlabel('Nacionalidad', fontsize=12)
    ax.set_ylabel('Número de Postulantes', fontsize=12)
    ax.tick_params(axis='x', rotation=45)

    # Calcular límite Y dinámicamente
    max_valor = nationality_counts.max()
    y_upper_limit = max_valor + (max_valor * 0.12)  # 12% de margen superior
    ax.set_ylim(0, y_upper_limit)

    for bar in bars:
        height = bar.get_height()
        # Posicionar texto dentro del gráfico con margen
        text_y_pos = min(height + (max_valor * 0.01), y_upper_limit - (max_valor * 0.005))
        ax.text(bar.get_x() + bar.get_width()/2., text_y_pos,
                f'{int(height)}', ha='center', va='bottom', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # 4. Distribución por departamento de domicilio
    # 4. Distribución por departamento de domicilio
    st.markdown('<div class="section-header">4. Distribución por Departamento de Domicilio</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    dep_counts = df_plot['DEP..DOM.'].value_counts().sort_values(ascending=True)
    bars = ax.barh(dep_counts.index, dep_counts.values, 
                color='steelblue', alpha=0.7, edgecolor='black')
    ax.set_title('Distribución de Postulantes por Departamento de Domicilio', fontsize=14, fontweight='bold')
    ax.set_xlabel('Número de Postulantes', fontsize=12)
    ax.set_ylabel('Departamento', fontsize=12)

    # Calcular límite X dinámicamente
    max_valor = dep_counts.max()
    x_upper_limit = max_valor + (max_valor * 0.15)  # 15% de margen superior
    ax.set_xlim(0, x_upper_limit)

    for bar in bars:
        width = bar.get_width()
        # Posicionar texto dentro del gráfico con margen
        text_x_pos = min(width + (max_valor * 0.01), x_upper_limit - (max_valor * 0.02))
        ax.text(text_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontsize=10)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # 5. Tipo de Institución vs Gestión
    st.markdown('<div class="section-header">5. Tipo de Institución y Gestión Educativa</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        tipo_counts = df_plot['TIPO.INSTITUCIÓN'].value_counts()
        colors_circle = ['lightblue', 'lightcoral', 'lightgreen']
        wedges, texts, autotexts = ax.pie(tipo_counts.values, labels=None, autopct='%1.1f%%',
                                         startangle=90, colors=colors_circle)
        ax.legend(wedges, [f'{label} ({count})' for label, count in zip(tipo_counts.index, tipo_counts.values)],
                 title="Tipo de Institución", loc="center")
        ax.set_title('Distribución por Tipo de Institución Educativa', fontsize=14, fontweight='bold')
        st.pyplot(fig)
        plt.close()
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        gestion_counts = df_plot['GESTIÓN'].value_counts().sort_values(ascending=True)
        colors_bars = ['lightcoral', 'lightgreen', 'lightblue']
        bars = ax.barh(gestion_counts.index, gestion_counts.values, 
                    color=colors_bars, alpha=0.8, edgecolor='black')
        
        # Calcular límite X dinámicamente
        max_valor = gestion_counts.max()
        x_upper_limit = max_valor + (max_valor * 0.22)  # 18% de margen superior para texto más largo
        ax.set_xlim(0, x_upper_limit)
        
        for bar in bars:
            width = bar.get_width()
            # Posicionar texto dentro del gráfico con margen
            text_x_pos = min(width + (max_valor * 0.02), x_upper_limit - (max_valor * 0.03))
            ax.text(text_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{int(width)} ({width/len(df_plot)*100:.1f}%)', 
                ha='left', va='center', fontsize=10, fontweight='bold')
        ax.set_title('Distribución por Tipo de Gestión Educativa', fontsize=14, fontweight='bold')
        ax.set_xlabel('Número de Postulantes', fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # 6. Distribución por modalidad
    # 6. Distribución por modalidad
    st.markdown('<div class="section-header">6. Distribución por Modalidad</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    modalidad_counts = df_plot['MODALIDAD'].value_counts().sort_values(ascending=True)
    bars = ax.barh(modalidad_counts.index, modalidad_counts.values, 
                color='lightsteelblue', alpha=0.8, edgecolor='navy', linewidth=0.5)
    ax.set_title('Distribución de Postulantes por Modalidad', fontsize=14, fontweight='bold')
    ax.set_xlabel('Número de Postulantes', fontsize=12)
    ax.set_ylabel('Modalidad', fontsize=12)

    # Calcular límite X dinámicamente
    max_valor = modalidad_counts.max()
    x_upper_limit = max_valor + (max_valor * 0.22)  # 15% de margen superior
    ax.set_xlim(0, x_upper_limit)

    for bar in bars:
        width = bar.get_width()
        # Posicionar texto dentro del gráfico con margen
        text_x_pos = min(width + (max_valor * 0.01), x_upper_limit - (max_valor * 0.02))
        ax.text(text_x_pos, bar.get_y() + bar.get_height()/2, 
            f'{int(width)} ({width/len(df_plot)*100:.2f}%)', 
            ha='left', va='center', fontsize=10, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


    # 7. Boxplots modalidad vs edad y puntaje
    st.markdown('<div class="section-header">7. Comparación por Modalidad</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        df_plot.boxplot(column='EDAD', by='MODALIDAD', ax=ax, vert=False)
        ax.set_title('Distribución de Edades por Modalidad', fontsize=12, fontweight='bold')
        ax.set_xlabel('Edad', fontsize=10)
        ax.set_ylabel('Modalidad', fontsize=10)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        df_plot.boxplot(column='Final', by='MODALIDAD', ax=ax, vert=False)
        ax.set_title('Distribución de Puntajes por Modalidad', fontsize=12, fontweight='bold')
        ax.set_xlabel('Puntaje Final', fontsize=10)
        ax.set_ylabel('Modalidad', fontsize=10)
        st.pyplot(fig)
        plt.close()
    
    # 8. Coincidencia opción 1 vs especialidad
    # 8. Coincidencia opción 1 vs especialidad
    st.markdown('<div class="section-header">8. Coincidencia Primera Opción vs Especialidad</div>', unsafe_allow_html=True)

    coincidencias = (df_plot['OPCION.1'] == df_plot['Especialidad']).value_counts()
    porcentajes = (coincidencias / len(df_plot)) * 100

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        labels_ordenados = ['No Coincide', 'Coincide']
        valores_ordenados = [coincidencias.get(False, 0), coincidencias.get(True, 0)]
        porcentajes_ordenados = [porcentajes.get(False, 0), porcentajes.get(True, 0)]
        
        bars = ax.bar(labels_ordenados, valores_ordenados, 
                    color=['lightcoral', 'lightgreen'], alpha=0.8, edgecolor='black')
        ax.set_title('Coincidencia entre Primera Opción y Especialidad Asignada', fontsize=14, fontweight='bold')
        ax.set_ylabel('Número de Postulantes', fontsize=12)
        
        # Calcular límite Y dinámicamente
        max_valor = max(valores_ordenados)
        y_upper_limit = max_valor + (max_valor * 0.15)  # 15% de margen superior
        ax.set_ylim(0, y_upper_limit)
        
        for i, bar in enumerate(bars):
            height = bar.get_height()
            # Posicionar texto dentro del gráfico con margen
            text_y_pos = min(height + (max_valor * 0.02), y_upper_limit - (max_valor * 0.01))
            ax.text(bar.get_x() + bar.get_width()/2., text_y_pos,
                f'{int(height)} postulantes\n({porcentajes_ordenados[i]:.1f}%)', 
                ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("### Resumen de Coincidencia")
        st.metric("Ingresaron a 1ra Opción", 
                 f"{coincidencias.get(True, 0)}", 
                 f"{porcentajes.get(True, 0):.1f}%")
        st.metric("No ingresaron a 1ra Opción", 
                 f"{coincidencias.get(False, 0)}", 
                 f"{porcentajes.get(False, 0):.1f}%")
    
    # 9. Boxplot puntaje final por especialidad
    # 9. Boxplot puntaje final por especialidad
    st.markdown('<div class="section-header">9. Puntaje Final por Especialidad</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(14, 8))
    especialidad_puntaje_median = df_plot.groupby('Especialidad')['Final'].median().sort_values(ascending=False)
    especialidades_ordenadas = especialidad_puntaje_median.index
    puntaje_data = [df_plot[df_plot['Especialidad'] == esp]['Final'] for esp in especialidades_ordenadas]

    box_plot = ax.boxplot(puntaje_data, labels=especialidades_ordenadas, patch_artist=True, vert=True)
    colors = plt.cm.Set3(np.linspace(0, 1, len(especialidades_ordenadas)))
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)

    # Calcular el límite Y dinámicamente
    max_puntaje_global = df_plot['Final'].max()
    min_puntaje_global = df_plot['Final'].min()
    rango_puntaje = max_puntaje_global - min_puntaje_global

    # Establecer límites del eje Y con margen para las etiquetas
    y_upper_limit = max_puntaje_global + (rango_puntaje * 0.08)  # 8% de margen superior
    y_lower_limit = max(0, min_puntaje_global - (rango_puntaje * 0.02))  # 2% de margen inferior, mínimo 0

    ax.set_ylim(y_lower_limit, y_upper_limit)

    for i, especialidad in enumerate(especialidades_ordenadas):
        datos_especialidad = df_plot[df_plot['Especialidad'] == especialidad]['Final']
        max_puntaje = datos_especialidad.max()
        
        # Verificar que la etiqueta esté dentro del límite Y
        y_pos = min(max_puntaje + 0.3, y_upper_limit - 0.1)  # Asegurar que esté dentro del gráfico
        
        ax.text(i + 1, y_pos, f'{max_puntaje:.1f}', 
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="yellow", alpha=0.7, edgecolor='black'))

    ax.set_title('Distribución de Puntaje Final por Especialidad Asignada', fontsize=14, fontweight='bold')
    ax.set_ylabel('Puntaje Final', fontsize=12)
    ax.set_xlabel('Especialidad', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    promedio_general = df_plot['Final'].mean()
    ax.axhline(y=promedio_general, color='red', linestyle='--', linewidth=2, 
            label=f'Promedio General: {promedio_general:.2f}')
    ax.legend()

    # Ajustar diseño automáticamente
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Mostrar resumen estadístico con máximos
    st.markdown("#### Resumen Estadístico por Especialidad")

    # Crear DataFrame con estadísticas
    stats_especialidades = []
    for especialidad in especialidades_ordenadas:
        datos = df_plot[df_plot['Especialidad'] == especialidad]['Final']
        stats_especialidades.append({
            'Especialidad': especialidad,
            'Postulantes': len(datos),
            'Mediana': datos.median(),
            'Promedio': datos.mean(),
            'Mínimo': datos.min(),
            'Máximo': datos.max(),
            'Desviación Estándar': datos.std()
        })

    df_stats = pd.DataFrame(stats_especialidades).round(2)

    # Mostrar en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 Estadísticas Detalladas:**")
        st.dataframe(df_stats, use_container_width=True)

    with col2:
        st.markdown("**🎯 Puntos Destacados:**")
        
        # Especialidad con máximo puntaje absoluto
        mayor_maximo = df_stats.loc[df_stats['Máximo'].idxmax()]
        st.metric(
            "Máximo puntaje", 
            f"{mayor_maximo['Especialidad']}", 
            f"{mayor_maximo['Máximo']:.2f}"
        )
        
        # Especialidad con minimo puntaje absoluto
        mayor_maximo = df_stats.loc[df_stats['Mínimo'].idxmax()]
        st.metric(
            "Mínimo puntaje", 
            f"{mayor_maximo['Especialidad']}", 
            f"{mayor_maximo['Mínimo']:.2f}"
        )
        
        # Especialidad con más postulantes
        mas_postulantes = df_stats.loc[df_stats['Postulantes'].idxmax()]
        st.metric(
            "Más postulantes", 
            f"{mas_postulantes['Especialidad']}", 
            f"{mas_postulantes['Postulantes']}"
        )

    # Mostrar tabla expandible con todos los datos
    with st.expander("📋 Ver resumen estadístico completo por especialidad"):
        st.markdown("**RESUMEN ESTADÍSTICO POR ESPECIALIDAD:**")
        st.markdown("="*50)
        
        for idx, row in df_stats.iterrows():
            st.markdown(f"**{row['Especialidad']}:**")
            st.markdown(f"- **Postulantes:** {row['Postulantes']}")
            st.markdown(f"- **Mediana:** {row['Mediana']:.2f}")
            st.markdown(f"- **Promedio:** {row['Promedio']:.2f}")
            st.markdown(f"- **Mínimo:** {row['Mínimo']:.2f}")
            st.markdown(f"- **Máximo:** {row['Máximo']:.2f} ★")
            st.markdown(f"- **Desviación Estándar:** {row['Desviación Estándar']:.2f}")
            st.markdown("")
    
    # 10. Frecuencia opción 1 vs opción 2
    # 10. Frecuencia opción 1 vs opción 2
    st.markdown('<div class="section-header">10. Frecuencia de Carreras por Opción</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(10, 8))
        op1_counts = df_plot['OPCION.1'].value_counts().sort_values(ascending=True)
        bars1 = ax.barh(op1_counts.index, op1_counts.values, 
                    color='lightblue', alpha=0.8, edgecolor='darkblue', linewidth=0.5)
        ax.set_title('Frecuencia - Primera Opción', fontsize=12, fontweight='bold')
        ax.set_xlabel('Número de Postulantes', fontsize=10)
        
        # Calcular límite X dinámicamente para Opción 1
        max_valor_op1 = op1_counts.max()
        x_upper_limit_op1 = max_valor_op1 + (max_valor_op1 * 0.12)  # 12% de margen superior
        ax.set_xlim(0, x_upper_limit_op1)
        
        for bar in bars1:
            width = bar.get_width()
            porcentaje = (width / len(df_plot)) * 100
            # Posicionar texto dentro del gráfico con margen
            text_x_pos = min(width + (max_valor_op1 * 0.01), x_upper_limit_op1 - (max_valor_op1 * 0.02))
            ax.text(text_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{int(width)} ({porcentaje:.1f}%)', 
                ha='left', va='center', fontsize=8, fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(10, 8))
        op2_counts = df_plot['OPCION.2'].dropna().value_counts().sort_values(ascending=True)
        bars2 = ax.barh(op2_counts.index, op2_counts.values, 
                    color='lightcoral', alpha=0.8, edgecolor='darkred', linewidth=0.5)
        ax.set_title('Frecuencia - Segunda Opción', fontsize=12, fontweight='bold')
        ax.set_xlabel('Número de Postulantes', fontsize=10)
        
        # Calcular límite X dinámicamente para Opción 2
        max_valor_op2 = op2_counts.max()
        x_upper_limit_op2 = max_valor_op2 + (max_valor_op2 * 0.12)  # 12% de margen superior
        ax.set_xlim(0, x_upper_limit_op2)
        
        for bar in bars2:
            width = bar.get_width()
            porcentaje = (width / len(df_plot['OPCION.2'].dropna())) * 100
            # Posicionar texto dentro del gráfico con margen
            text_x_pos = min(width + (max_valor_op2 * 0.01), x_upper_limit_op2 - (max_valor_op2 * 0.02))
            ax.text(text_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{int(width)} ({porcentaje:.1f}%)', 
                ha='left', va='center', fontsize=8, fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        st.pyplot(fig)
        plt.close()


    # Análisis comparativo
    st.markdown("#### 📊 Análisis Comparativo: Opción 1 vs Opción 2")

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Opción 1", 
            f"{len(df_plot)}",
            "100%"
        )

    with col2:
        op2_count = len(df_plot['OPCION.2'].dropna())
        st.metric(
            "Total Opción 2", 
            f"{op2_count}",
            f"{op2_count/len(df_plot)*100:.1f}%"
        )

    with col3:
        sin_op2 = df_plot['OPCION.2'].isna().sum()
        st.metric(
            "Sin Opción 2", 
            f"{sin_op2}",
            f"{sin_op2/len(df_plot)*100:.1f}%"
        )

    with col4:
        carreras_comunes = set(df_plot['OPCION.1']).intersection(set(df_plot['OPCION.2'].dropna()))
        st.metric(
            "Carreras en ambas opciones", 
            f"{len(carreras_comunes)}"
        )

    # Top carreras en dos columnas
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**🏆 TOP 5 CARRERAS MÁS ELEGIDAS - OPCIÓN 1:**")
        top5_op1 = df_plot['OPCION.1'].value_counts().head()
        top1_df = pd.DataFrame({
            'Carrera': top5_op1.index,
            'Postulantes': top5_op1.values,
            'Porcentaje': (top5_op1.values / len(df_plot)) * 100
        }).round(2)
        
        for idx, row in top1_df.iterrows():
            st.write(f"{idx+1}. **{row['Carrera']}**: {row['Postulantes']} postulantes ({row['Porcentaje']:.1f}%)")

    with col_right:
        st.markdown("**🏆 TOP 5 CARRERAS MÁS ELEGIDAS - OPCIÓN 2:**")
        top5_op2 = df_plot['OPCION.2'].value_counts().head()
        top2_df = pd.DataFrame({
            'Carrera': top5_op2.index,
            'Postulantes': top5_op2.values,
            'Porcentaje': (top5_op2.values / len(df_plot['OPCION.2'].dropna())) * 100
        }).round(2)
        
        for idx, row in top2_df.iterrows():
            st.write(f"{idx+1}. **{row['Carrera']}**: {row['Postulantes']} postulantes ({row['Porcentaje']:.1f}%)")

    # Carreras comunes
    st.markdown("**🔄 CARRERAS QUE APARECEN EN AMBAS OPCIONES:**")
    if carreras_comunes:
        # Mostrar en varias columnas para mejor visualización
        carreras_ordenadas = sorted(carreras_comunes)
        n_cols = 3
        carreras_por_columna = len(carreras_ordenadas) // n_cols + 1
        
        cols = st.columns(n_cols)
        for i, carrera in enumerate(carreras_ordenadas):
            col_idx = i % n_cols
            with cols[col_idx]:
                count_op1 = len(df_plot[df_plot['OPCION.1'] == carrera])
                count_op2 = len(df_plot[df_plot['OPCION.2'] == carrera])
                st.write(f"• **{carrera}**")
                st.write(f"  - Op1: {count_op1} | Op2: {count_op2}")
    else:
        st.write("No hay carreras comunes entre ambas opciones")


    
    # 11. Relación puntaje final vs orden de mérito
    # 11. Relación puntaje final vs orden de mérito
    st.markdown('<div class="section-header">11. Relación Puntaje Final vs Orden de Mérito</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df_plot['OM'], df_plot['Final'], alpha=0.6, color='steelblue', s=50)
    ax.set_title('Relación entre Puntaje Final y Orden de Mérito', fontsize=14, fontweight='bold')
    ax.set_xlabel('Orden de Mérito (OM)', fontsize=12)
    ax.set_ylabel('Puntaje Final', fontsize=12)
    ax.grid(True, alpha=0.3)

    z = np.polyfit(df_plot['OM'], df_plot['Final'], 1)
    p = np.poly1d(z)
    ax.plot(df_plot['OM'], p(df_plot['OM']), "r--", alpha=0.8, linewidth=2, 
            label=f'Tendencia: y = {z[0]:.3f}x + {z[1]:.3f}')

    correlacion = df_plot['OM'].corr(df_plot['Final'])
    ax.text(0.05, 0.95, f'Correlación: {correlacion:.3f}', 
            transform=ax.transAxes, fontsize=12,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
    ax.legend()
    st.pyplot(fig)
    plt.close()

    # Análisis adicional
    st.markdown("#### 📊 Análisis: Relación Puntaje Final vs Orden de Mérito")

    # Métricas principales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Correlación",
            f"{correlacion:.3f}",
            help="Coeficiente de correlación de Pearson"
        )

    with col2:
        st.metric(
            "Pendiente",
            f"{z[0]:.3f}",
            help="Pendiente de la línea de tendencia"
        )

    with col3:
        st.metric(
            "Intercepto", 
            f"{z[1]:.3f}",
            help="Punto de intersección con el eje Y"
        )

    # Analizar rangos específicos
    st.markdown("#### 🔍 Análisis por Rangos de Orden de Mérito")

    rangos_om = [
        (1, 10, "Top 10"),
        (11, 50, "Top 11-50"),
        (51, 100, "Top 51-100"),
        (101, 500, "Top 101-500"),
        (501, 1000, "Top 501-1000"),
        (1001, 2000, "Resto (1001-2000)"),
        (2001, df_plot['OM'].max(), f"Resto (2001-{int(df_plot['OM'].max())})")
    ]

    # Crear DataFrame para los rangos
    rangos_data = []
    for rango_min, rango_max, etiqueta in rangos_om:
        datos_rango = df_plot[(df_plot['OM'] >= rango_min) & (df_plot['OM'] <= rango_max)]
        if len(datos_rango) > 0:
            rangos_data.append({
                'Rango OM': etiqueta,
                'Postulantes': len(datos_rango),
                'Puntaje Promedio': datos_rango['Final'].mean(),
                'Puntaje Mínimo': datos_rango['Final'].min(),
                'Puntaje Máximo': datos_rango['Final'].max(),
                'Rango Puntajes': f"{datos_rango['Final'].min():.1f} - {datos_rango['Final'].max():.1f}"
            })

    df_rangos = pd.DataFrame(rangos_data).round(2)

    # Mostrar tabla de rangos
    st.dataframe(df_rangos, use_container_width=True)

    # Gráfica adicional: Boxplot por rangos
    st.markdown("#### 📦 Distribución de Puntajes por Rango de Mérito")

    # Crear columna de rangos para el boxplot
    df_rangos_plot = df_plot.copy()
    condiciones = [
        (df_rangos_plot['OM'] <= 10),
        (df_rangos_plot['OM'] <= 50) & (df_rangos_plot['OM'] > 10),
        (df_rangos_plot['OM'] <= 100) & (df_rangos_plot['OM'] > 50),
        (df_rangos_plot['OM'] <= 500) & (df_rangos_plot['OM'] > 100),
        (df_rangos_plot['OM'] <= 1000) & (df_rangos_plot['OM'] > 500),
        (df_rangos_plot['OM'] > 1000)
    ]

    categorias = ['Top 10', 'Top 11-50', 'Top 51-100', 'Top 101-500', 'Top 501-1000', 'Resto (>1000)']
    df_rangos_plot['Rango_Merito'] = np.select(condiciones, categorias, default='Otros')

    # Ordenar los rangos correctamente
    orden_rangos = ['Top 10', 'Top 11-50', 'Top 51-100', 'Top 101-500', 'Top 501-1000', 'Resto (>1000)']
    df_rangos_plot['Rango_Merito'] = pd.Categorical(df_rangos_plot['Rango_Merito'], categories=orden_rangos, ordered=True)

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    box_data = [df_rangos_plot[df_rangos_plot['Rango_Merito'] == rango]['Final'] for rango in orden_rangos]

    box_plot = ax2.boxplot(box_data, labels=orden_rangos, patch_artist=True, vert=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(orden_rangos)))
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)

    ax2.set_title('Distribución de Puntajes Finales por Rango de Orden de Mérito', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Puntaje Final', fontsize=12)
    ax2.set_xlabel('Rango de Orden de Mérito', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', linestyle='--', alpha=0.3)

    # Añadir línea del promedio general
    promedio_general = df_plot['Final'].mean()
    ax2.axhline(y=promedio_general, color='red', linestyle='--', linewidth=2, 
            label=f'Promedio General: {promedio_general:.2f}')
    ax2.legend()

    st.pyplot(fig2)
    plt.close()

    # Análisis expandible adicional
    with st.expander("📈 Ver análisis estadístico detallado"):
        st.markdown("**ESTADÍSTICAS DETALLADAS POR RANGO:**")
        
        for rango in rangos_data:
            st.markdown(f"**{rango['Rango OM']}:**")
            st.write(f"- Postulantes: {rango['Postulantes']}")
            st.write(f"- Puntaje promedio: {rango['Puntaje Promedio']:.2f}")
            st.write(f"- Puntaje mínimo: {rango['Puntaje Mínimo']:.2f}")
            st.write(f"- Puntaje máximo: {rango['Puntaje Máximo']:.2f}")
            st.write(f"- Rango completo: {rango['Rango Puntajes']}")
            st.write("")
        
        # Análisis de la correlación
        st.markdown("**INTERPRETACIÓN DE LA CORRELACIÓN:**")
        if correlacion < -0.7:
            st.write("- 🔥 **Correlación fuerte negativa**: El orden de mérito es un excelente predictor del puntaje")
        elif correlacion < -0.5:
            st.write("- ✅ **Correlación moderada negativa**: Relación evidente entre mérito y puntaje")
        elif correlacion < -0.3:
            st.write("- 📊 **Correlación débil negativa**: Existe relación pero no muy marcada")
        else:
            st.write("- 🔍 **Correlación muy débil**: Poca relación lineal entre las variables")
        
        st.write(f"- **Interpretación**: Por cada posición que empeora el orden de mérito, el puntaje disminuye aproximadamente {abs(z[0]):.3f} puntos")

    # Métricas adicionales
    st.markdown("#### 🎯 Puntos Clave Destacados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mejor_puntaje = df_plot.loc[df_plot['Final'].idxmax()]
        st.metric(
            "Mejor puntaje absoluto",
            f"{mejor_puntaje['Final']:.2f}",
            f"OM: {int(mejor_puntaje['OM'])}"
        )

    with col2:
        peor_puntaje_top10 = df_plot[df_plot['OM'] <= 10]['Final'].min()
        st.metric(
            "Peor puntaje en Top 10",
            f"{peor_puntaje_top10:.2f}",
            "Mínimo del top"
        )

    with col3:
        mejor_puntaje_ultimos = df_plot[df_plot['OM'] > 1000]['Final'].max()
        st.metric(
            "Mejor puntaje fuera del top 1000",
            f"{mejor_puntaje_ultimos:.2f}",
            "Máximo del resto"
        )

    with col4:
        diferencia_promedio_top_vs_resto = (
            df_plot[df_plot['OM'] <= 100]['Final'].mean() - 
            df_plot[df_plot['OM'] > 1000]['Final'].mean()
        )
        st.metric(
            "Diferencia promedio Top 100 vs Resto",
            f"{diferencia_promedio_top_vs_resto:.2f}",
            "Puntos de ventaja"
        )
    


    # 12. Demanda vs Selectividad
    # 12. Demanda vs Selectividad
    st.markdown('<div class="section-header">12. Demanda vs Selectividad por Carrera</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    demanda = df_plot['OPCION.1'].value_counts()
    selectividad = df_plot.groupby('Especialidad')['Final'].mean()

    carreras_comunes = list(set(demanda.index) & set(selectividad.index))
    demanda_selectividad = pd.DataFrame({
        'Demanda': [demanda[c] for c in carreras_comunes],
        'Selectividad': [selectividad[c] for c in carreras_comunes]
    }, index=carreras_comunes)

    # Definir cuadrantes para colores
    promedio_demanda = demanda_selectividad['Demanda'].mean()
    promedio_selectividad = demanda_selectividad['Selectividad'].mean()

    alto_demanda = demanda_selectividad['Demanda'] > promedio_demanda
    alta_selectividad = demanda_selectividad['Selectividad'] > promedio_selectividad

    # Asignar colores por cuadrante
    colores = []
    for carrera in demanda_selectividad.index:
        if alto_demanda[carrera] and alta_selectividad[carrera]:
            colores.append('blue')  # Alto-Alto
        elif alto_demanda[carrera] and not alta_selectividad[carrera]:
            colores.append('orange')  # Alto-Bajo
        elif not alto_demanda[carrera] and alta_selectividad[carrera]:
            colores.append('green')  # Bajo-Alto
        else:
            colores.append('red')  # Bajo-Bajo

    scatter = ax.scatter(demanda_selectividad['Demanda'], demanda_selectividad['Selectividad'], 
            s=100, alpha=0.7, c=colores, edgecolors='black')
    ax.set_title('Relación entre Demanda y Selectividad por Carrera', fontsize=14, fontweight='bold')
    ax.set_xlabel('Demanda (Número de postulantes como Opción 1)', fontsize=12)
    ax.set_ylabel('Selectividad (Puntaje Promedio de Ingreso)', fontsize=12)
    ax.grid(True, alpha=0.3)

    for carrera in demanda_selectividad.index:
        ax.annotate(carrera, 
                (demanda_selectividad.loc[carrera, 'Demanda'], 
                    demanda_selectividad.loc[carrera, 'Selectividad']),
                xytext=(5, 5), textcoords='offset points', 
                fontsize=9, alpha=0.8)

    correlacion = demanda_selectividad['Demanda'].corr(demanda_selectividad['Selectividad'])
    ax.text(0.05, 0.95, f'Correlación: {correlacion:.3f}', 
            transform=ax.transAxes, fontsize=12,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    ax.axhline(y=promedio_selectividad, color='red', linestyle='--', alpha=0.7, 
            label=f'Promedio Selectividad: {promedio_selectividad:.1f}')
    ax.axvline(x=promedio_demanda, color='green', linestyle='--', alpha=0.7,
            label=f'Promedio Demanda: {promedio_demanda:.1f}')

    # Añadir leyenda de cuadrantes
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Alta Demanda + Alta Selectividad'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Alta Demanda + Baja Selectividad'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Baja Demanda + Alta Selectividad'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Baja Demanda + Baja Selectividad')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    st.pyplot(fig)
    plt.close()

    # Análisis de cuadrantes
    st.markdown("#### 📊 Análisis por Cuadrantes: Demanda vs Selectividad")

    # Métricas principales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Correlación global",
            f"{correlacion:.3f}",
            help="Correlación entre demanda y selectividad"
        )

    with col2:
        st.metric(
            "Promedio demanda",
            f"{promedio_demanda:.1f}",
            "postulantes"
        )

    with col3:
        st.metric(
            "Promedio selectividad",
            f"{promedio_selectividad:.1f}",
            "puntaje"
        )

    # Mostrar análisis por cuadrantes en pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔷 Alto-Alto", "🔶 Alto-Bajo", "🟩 Bajo-Alto", "🟥 Bajo-Bajo"
    ])

    with tab1:
        st.markdown("**🔷 CUADRANTE ALTO-ALTO (Alta Demanda + Alta Selectividad)**")
        st.write("Carreras muy populares y muy exigentes")
        
        cuadrante_alto_alto = demanda_selectividad[alto_demanda & alta_selectividad]
        if not cuadrante_alto_alto.empty:
            for carrera in cuadrante_alto_alto.index:
                demanda_val = cuadrante_alto_alto.loc[carrera, 'Demanda']
                selectividad_val = cuadrante_alto_alto.loc[carrera, 'Selectividad']
                st.write(f"• **{carrera}**: Demanda={demanda_val}, Selectividad={selectividad_val:.1f}")
            
            st.metric(
                "Carreras en este cuadrante",
                f"{len(cuadrante_alto_alto)}",
                f"{len(cuadrante_alto_alto)/len(demanda_selectividad)*100:.1f}% del total"
            )
        else:
            st.write("No hay carreras en este cuadrante")

    with tab2:
        st.markdown("**🔶 CUADRANTE ALTO-BAJO (Alta Demanda + Baja Selectividad)**")
        st.write("Carreras populares pero menos exigentes")
        
        cuadrante_alto_bajo = demanda_selectividad[alto_demanda & ~alta_selectividad]
        if not cuadrante_alto_bajo.empty:
            for carrera in cuadrante_alto_bajo.index:
                demanda_val = cuadrante_alto_bajo.loc[carrera, 'Demanda']
                selectividad_val = cuadrante_alto_bajo.loc[carrera, 'Selectividad']
                st.write(f"• **{carrera}**: Demanda={demanda_val}, Selectividad={selectividad_val:.1f}")
            
            st.metric(
                "Carreras en este cuadrante",
                f"{len(cuadrante_alto_bajo)}",
                f"{len(cuadrante_alto_bajo)/len(demanda_selectividad)*100:.1f}% del total"
            )
        else:
            st.write("No hay carreras en este cuadrante")

    with tab3:
        st.markdown("**🟩 CUADRANTE BAJO-ALTO (Baja Demanda + Alta Selectividad)**")
        st.write("Carreras nicho pero muy exigentes")
        
        cuadrante_bajo_alto = demanda_selectividad[~alto_demanda & alta_selectividad]
        if not cuadrante_bajo_alto.empty:
            for carrera in cuadrante_bajo_alto.index:
                demanda_val = cuadrante_bajo_alto.loc[carrera, 'Demanda']
                selectividad_val = cuadrante_bajo_alto.loc[carrera, 'Selectividad']
                st.write(f"• **{carrera}**: Demanda={demanda_val}, Selectividad={selectividad_val:.1f}")
            
            st.metric(
                "Carreras en este cuadrante",
                f"{len(cuadrante_bajo_alto)}",
                f"{len(cuadrante_bajo_alto)/len(demanda_selectividad)*100:.1f}% del total"
            )
        else:
            st.write("No hay carreras en este cuadrante")

    with tab4:
        st.markdown("**🟥 CUADRANTE BAJO-BAJO (Baja Demanda + Baja Selectividad)**")
        st.write("Carreras con menor popularidad y menos exigentes")
        
        cuadrante_bajo_bajo = demanda_selectividad[~alto_demanda & ~alta_selectividad]
        if not cuadrante_bajo_bajo.empty:
            for carrera in cuadrante_bajo_bajo.index:
                demanda_val = cuadrante_bajo_bajo.loc[carrera, 'Demanda']
                selectividad_val = cuadrante_bajo_bajo.loc[carrera, 'Selectividad']
                st.write(f"• **{carrera}**: Demanda={demanda_val}, Selectividad={selectividad_val:.1f}")
            
            st.metric(
                "Carreras en este cuadrante",
                f"{len(cuadrante_bajo_bajo)}",
                f"{len(cuadrante_bajo_bajo)/len(demanda_selectividad)*100:.1f}% del total"
            )
        else:
            st.write("No hay carreras en este cuadrante")

    # Resumen estadístico
    st.markdown("#### 📈 Resumen Estadístico por Cuadrante")

    # Calcular estadísticas por cuadrante
    resumen_cuadrantes = []
    for nombre, cuadrante in [
        ("Alto-Alto", cuadrante_alto_alto),
        ("Alto-Bajo", cuadrante_alto_bajo),
        ("Bajo-Alto", cuadrante_bajo_alto),
        ("Bajo-Bajo", cuadrante_bajo_bajo)
    ]:
        if not cuadrante.empty:
            resumen_cuadrantes.append({
                'Cuadrante': nombre,
                'Carreras': len(cuadrante),
                '% Total': f"{(len(cuadrante)/len(demanda_selectividad)*100):.1f}%",
                'Demanda Promedio': cuadrante['Demanda'].mean(),
                'Selectividad Promedio': cuadrante['Selectividad'].mean(),
                'Demanda Total': cuadrante['Demanda'].sum()
            })

    df_resumen = pd.DataFrame(resumen_cuadrantes).round(2)
    st.dataframe(df_resumen, use_container_width=True)

    # Análisis expandible adicional
    with st.expander("🔍 Ver análisis estratégico"):
        st.markdown("**ESTRATEGIAS POR TIPO DE CARRERA:**")
        
        st.markdown("**🔷 ALTO-ALTO (Carreras Estrella):**")
        st.write("- Estrategia: Mantener excelencia y reputación")
        st.write("- Desafío: Alta competencia por vacantes")
        st.write("- Oportunidad: Atraer a los mejores estudiantes")
        
        st.markdown("**🔶 ALTO-BAJO (Carreras Masivas):**")
        st.write("- Estrategia: Mejorar calidad manteniendo acceso")
        st.write("- Desafío: Gestionar grandes volúmenes de estudiantes")
        st.write("- Oportunidad: Democratizar educación de calidad")
        
        st.markdown("**🟩 BAJO-ALTO (Carreras Élite):**")
        st.write("- Estrategia: Especialización y nicho de mercado")
        st.write("- Desafío: Atraer postulantes calificados")
        st.write("- Oportunidad: Liderazgo en áreas específicas")
        
        st.markdown("**🟥 BAJO-BAJO (Carreras Emergentes):**")
        st.write("- Estrategia: Difusión y desarrollo de mercado")
        st.write("- Desafío: Aumentar visibilidad y demanda")
        st.write("- Oportunidad: Crecimiento potencial")

    # Puntos clave destacados
    st.markdown("#### 🎯 Puntos Clave Destacados")

    col1, col2, col3 = st.columns(3)

    with col1:
        carrera_mas_demandada = demanda_selectividad.loc[demanda_selectividad['Demanda'].idxmax()]
        st.metric(
            "Carrera más demandada",
            f"{demanda_selectividad['Demanda'].idxmax()}",
            f"{carrera_mas_demandada['Demanda']} postulantes"
        )

    with col2:
        carrera_mas_selectiva = demanda_selectividad.loc[demanda_selectividad['Selectividad'].idxmax()]
        st.metric(
            "Carrera más selectiva",
            f"{demanda_selectividad['Selectividad'].idxmax()}",
            f"{carrera_mas_selectiva['Selectividad']:.1f} puntos"
        )

    with col3:
        if not cuadrante_alto_alto.empty:
            mejor_balance = cuadrante_alto_alto.loc[
                (cuadrante_alto_alto['Demanda'] / cuadrante_alto_alto['Selectividad']).idxmin()
            ]
            st.metric(
                "Mejor balance demanda/selectividad",
                f"{(cuadrante_alto_alto['Demanda'] / cuadrante_alto_alto['Selectividad']).idxmin()}",
                "Alto-Alto equilibrado"
            )
    
    # 13. Probabilidad empírica de ingreso
    # 13. Probabilidad empírica de ingreso
    st.markdown('<div class="section-header">13. Probabilidad Empírica de Ingreso por Carrera</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    probabilidades = {}
    for carrera in df_plot['OPCION.1'].unique():
        total_op1 = len(df_plot[df_plot['OPCION.1'] == carrera])
        ingresaron_op1 = len(df_plot[(df_plot['OPCION.1'] == carrera) & (df_plot['Especialidad'] == carrera)])
        probabilidad = (ingresaron_op1 / total_op1 * 100) if total_op1 > 0 else 0
        probabilidades[carrera] = probabilidad

    df_probabilidades = pd.DataFrame.from_dict(probabilidades, orient='index', columns=['Probabilidad'])
    df_probabilidades = df_probabilidades.sort_values('Probabilidad', ascending=True)

    bars = ax.barh(df_probabilidades.index, df_probabilidades['Probabilidad'], 
                color='lightcoral', alpha=0.8, edgecolor='darkred')
    ax.set_title('Probabilidad Empírica de Ingresar a la Primera Opción por Carrera', fontsize=14, fontweight='bold')
    ax.set_xlabel('Probabilidad de Ingreso (%)', fontsize=12)
    ax.set_ylabel('Carrera (Primera Opción)', fontsize=12)

    # Calcular límite X dinámicamente (máximo 100% pero con margen para etiquetas)
    max_probabilidad = df_probabilidades['Probabilidad'].max()
    x_upper_limit = min(100 + 8, max_probabilidad + (max_probabilidad * 0.15))  # Máximo 108% o 15% de margen
    ax.set_xlim(0, x_upper_limit)

    for bar in bars:
        width = bar.get_width()
        carrera = df_probabilidades.index[bars.index(bar)]
        total_op1 = len(df_plot[df_plot['OPCION.1'] == carrera])
        ingresaron_op1 = len(df_plot[(df_plot['OPCION.1'] == carrera) & (df_plot['Especialidad'] == carrera)])
        
        # Posicionar texto dentro del gráfico con margen
        text_x_pos = min(width + 1, x_upper_limit - 3)  # Margen de 3 unidades del borde
        ax.text(text_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}%\n({ingresaron_op1}/{total_op1})', 
                ha='left', va='center', fontsize=9, fontweight='bold')

    prob_promedio_global = (df_plot['OPCION.1'] == df_plot['Especialidad']).mean() * 100
    ax.axvline(x=prob_promedio_global, color='blue', linestyle='--', linewidth=2,
            label=f'Probabilidad Promedio Global: {prob_promedio_global:.1f}%')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Análisis detallado
    st.markdown("#### 📊 Análisis de Probabilidades de Ingreso por Carrera")

    # Métricas principales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Probabilidad promedio global",
            f"{prob_promedio_global:.1f}%",
            help="Porcentaje promedio de postulantes que ingresan a su primera opción"
        )

    with col2:
        # Correlación con selectividad
        selectividad_carreras = df_plot.groupby('Especialidad')['Final'].mean()
        correlacion_prob_select = df_probabilidades['Probabilidad'].corr(
            selectividad_carreras[df_probabilidades.index]
        )
        st.metric(
            "Correlación Probabilidad-Selectividad",
            f"{correlacion_prob_select:.3f}",
            help="Relación entre probabilidad de ingreso y puntaje requerido"
        )

    with col3:
        carreras_sobre_promedio = len(df_probabilidades[df_probabilidades['Probabilidad'] > prob_promedio_global])
        st.metric(
            "Carreras sobre el promedio",
            f"{carreras_sobre_promedio}",
            f"{carreras_sobre_promedio/len(df_probabilidades)*100:.1f}%"
        )

    # Top carreras en dos columnas
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**🎯 CARRERAS CON MAYOR PROBABILIDAD DE INGRESO (Top 5):**")
        top5_alta = df_probabilidades.nlargest(5, 'Probabilidad')
        
        top_alta_data = []
        for carrera, prob in top5_alta.iterrows():
            total_op1 = len(df_plot[df_plot['OPCION.1'] == carrera])
            ingresaron_op1 = len(df_plot[(df_plot['OPCION.1'] == carrera) & (df_plot['Especialidad'] == carrera)])
            top_alta_data.append({
                'Carrera': carrera,
                'Probabilidad': prob['Probabilidad'],
                'Ingresaron': ingresaron_op1,
                'Total': total_op1,
                'Ratio': f"{ingresaron_op1}/{total_op1}"
            })
        
        for i, data in enumerate(top_alta_data, 1):
            st.write(f"{i}. **{data['Carrera']}**: {data['Probabilidad']:.1f}% ({data['Ratio']})")

    with col_right:
        st.markdown("**⚠️ CARRERAS CON MENOR PROBABILIDAD DE INGRESO (Top 5):**")
        top5_baja = df_probabilidades.nsmallest(5, 'Probabilidad')
        
        top_baja_data = []
        for carrera, prob in top5_baja.iterrows():
            total_op1 = len(df_plot[df_plot['OPCION.1'] == carrera])
            ingresaron_op1 = len(df_plot[(df_plot['OPCION.1'] == carrera) & (df_plot['Especialidad'] == carrera)])
            top_baja_data.append({
                'Carrera': carrera,
                'Probabilidad': prob['Probabilidad'],
                'Ingresaron': ingresaron_op1,
                'Total': total_op1,
                'Ratio': f"{ingresaron_op1}/{total_op1}"
            })
        
        for i, data in enumerate(top_baja_data, 1):
            st.write(f"{i}. **{data['Carrera']}**: {data['Probabilidad']:.1f}% ({data['Ratio']})")

    # Análisis de correlación expandible
    with st.expander("📈 Ver análisis de correlación con selectividad"):
        st.markdown("**RELACIÓN ENTRE PROBABILIDAD DE INGRESO Y SELECTIVIDAD:**")
        
        # Crear gráfica de correlación
        fig_corr, ax_corr = plt.subplots(figsize=(10, 6))
        
        # Preparar datos para correlación
        datos_correlacion = pd.DataFrame({
            'Probabilidad': df_probabilidades['Probabilidad'],
            'Selectividad': selectividad_carreras[df_probabilidades.index]
        }).dropna()
        
        scatter = ax_corr.scatter(datos_correlacion['Selectividad'], datos_correlacion['Probabilidad'],
                                alpha=0.7, s=80, color='purple', edgecolors='black')
        
        # Añadir etiquetas
        for carrera in datos_correlacion.index:
            ax_corr.annotate(carrera, 
                            (datos_correlacion.loc[carrera, 'Selectividad'], 
                            datos_correlacion.loc[carrera, 'Probabilidad']),
                            xytext=(5, 5), textcoords='offset points', 
                            fontsize=8, alpha=0.8)
        
        ax_corr.set_xlabel('Selectividad (Puntaje Promedio de Ingreso)', fontsize=12)
        ax_corr.set_ylabel('Probabilidad de Ingreso (%)', fontsize=12)
        ax_corr.set_title('Relación entre Probabilidad de Ingreso y Selectividad', fontsize=14, fontweight='bold')
        ax_corr.grid(True, alpha=0.3)
        
        # Línea de tendencia
        if len(datos_correlacion) > 1:
            z_corr = np.polyfit(datos_correlacion['Selectividad'], datos_correlacion['Probabilidad'], 1)
            p_corr = np.poly1d(z_corr)
            ax_corr.plot(datos_correlacion['Selectividad'], p_corr(datos_correlacion['Selectividad']), 
                        "r--", alpha=0.8, linewidth=2)
        
        ax_corr.text(0.05, 0.95, f'Correlación: {correlacion_prob_select:.3f}', 
                    transform=ax_corr.transAxes, fontsize=12,
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
        
        st.pyplot(fig_corr)
        plt.close()
        
        # Interpretación de la correlación
        st.markdown("**INTERPRETACIÓN DE LA CORRELACIÓN:**")
        if correlacion_prob_select < -0.5:
            st.write("- 🔥 **Correlación negativa fuerte**: Las carreras más selectivas tienen menor probabilidad de ingreso")
        elif correlacion_prob_select < -0.3:
            st.write("- 📉 **Correlación negativa moderada**: Tendencia a menor probabilidad en carreras más exigentes")
        elif correlacion_prob_select < 0:
            st.write("- 🔍 **Correlación negativa débil**: Ligera tendencia inversa")
        elif correlacion_prob_select == 0:
            st.write("- ➖ **Sin correlación**: No hay relación lineal entre las variables")
        else:
            st.write("- 📈 **Correlación positiva**: Las carreras más selectivas tienen mayor probabilidad de ingreso")

    # Tabla completa de probabilidades
    st.markdown("#### 📋 Tabla Completa de Probabilidades por Carrera")

    # Crear DataFrame completo para la tabla
    tabla_completa = []
    for carrera in df_probabilidades.index:
        total_op1 = len(df_plot[df_plot['OPCION.1'] == carrera])
        ingresaron_op1 = len(df_plot[(df_plot['OPCION.1'] == carrera) & (df_plot['Especialidad'] == carrera)])
        selectividad_val = selectividad_carreras.get(carrera, 0)
        
        tabla_completa.append({
            'Carrera': carrera,
            'Probabilidad (%)': df_probabilidades.loc[carrera, 'Probabilidad'],
            'Ingresaron': ingresaron_op1,
            'Total Opción 1': total_op1,
            'Ratio': f"{ingresaron_op1}/{total_op1}",
            'Selectividad': selectividad_val,
            'Sobre Promedio': '✅' if df_probabilidades.loc[carrera, 'Probabilidad'] > prob_promedio_global else '❌'
        })

    df_tabla_completa = pd.DataFrame(tabla_completa).sort_values('Probabilidad (%)', ascending=False).round(2)
    st.dataframe(df_tabla_completa, use_container_width=True)

    # Puntos clave destacados
    st.markdown("#### 🎯 Puntos Clave Destacados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        carrera_mayor_prob = df_probabilidades['Probabilidad'].idxmax()
        mayor_prob_val = df_probabilidades['Probabilidad'].max()
        st.metric(
            "Mayor probabilidad",
            f"{carrera_mayor_prob}",
            f"{mayor_prob_val:.1f}%"
        )

    with col2:
        carrera_menor_prob = df_probabilidades['Probabilidad'].idxmin()
        menor_prob_val = df_probabilidades['Probabilidad'].min()
        st.metric(
            "Menor probabilidad",
            f"{carrera_menor_prob}",
            f"{menor_prob_val:.1f}%"
        )

    with col3:
        carrera_mas_postulantes = max([(carrera, len(df_plot[df_plot['OPCION.1'] == carrera])) 
                                    for carrera in df_probabilidades.index], 
                                    key=lambda x: x[1])[0]
        postulantes_count = len(df_plot[df_plot['OPCION.1'] == carrera_mas_postulantes])
        st.metric(
            "Más postulantes Op1",
            f"{carrera_mas_postulantes}",
            f"{postulantes_count} postulantes"
        )

    with col4:
        diferencia_extremos = mayor_prob_val - menor_prob_val
        st.metric(
            "Diferencia extremos",
            f"{diferencia_extremos:.1f}%",
            "brecha de probabilidad"
        )

    # Análisis estratégico
    with st.expander("💡 Recomendaciones Estratégicas"):
        st.markdown("**RECOMENDACIONES BASADAS EN EL ANÁLISIS:**")
        
        st.markdown("**🎯 Para carreras con alta probabilidad de ingreso:**")
        st.write("- Mantener y comunicar la alta tasa de ingreso como ventaja competitiva")
        st.write("- Evaluar capacidad de absorción vs demanda real")
        st.write("- Considerar aumentar requisitos si la calidad se ve comprometida")
        
        st.markdown("**⚠️ Para carreras con baja probabilidad de ingreso:**")
        st.write("- Analizar causas: alta demanda, pocas vacantes, alta selectividad")
        st.write("- Comunicar claramente las expectativas a postulantes")
        st.write("- Considerar programas de nivelación o rutas alternativas")
        
        st.markdown("**📊 Para orientación de postulantes:**")
        st.write("- Usar estas probabilidades como referencia realista")
        st.write("- Considerar carreras con buen balance demanda/probabilidad")
        st.write("- Incluir segunda opción con probabilidades complementarias")
    
    # 14. Correlación áreas vs puntaje final
    # 14. Correlación áreas vs puntaje final
    st.markdown('<div class="section-header">14. Correlación Áreas Académicas vs Puntaje Final</div>', unsafe_allow_html=True)

    areas = ['RV', 'RM', 'Arit', 'Alg', 'Geo', 'Trig', 'Bio', 'Qui', 'Fis', 'Eco', 'Geog', 'His']
    correlaciones = df_plot[areas + ['Final']].corr()['Final'].drop('Final')
    correlaciones_ordenadas = correlaciones.sort_values(ascending=False).round(3)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(correlaciones_ordenadas.index, correlaciones_ordenadas.values,
                color=['green' if x > 0.5 else 'orange' if x > 0.3 else 'red' for x in correlaciones_ordenadas.values],
                alpha=0.7, edgecolor='black')
    ax.set_title('Correlación entre Áreas Académicas y Puntaje Final', fontsize=14, fontweight='bold')
    ax.set_xlabel('Áreas Académicas', fontsize=12)
    ax.set_ylabel('Coeficiente de Correlación', fontsize=12)
    ax.set_ylim(-0.1, 1.0)
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Correlación fuerte (0.5)')
    ax.axhline(y=0.3, color='orange', linestyle='--', alpha=0.5, label='Correlación moderada (0.3)')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    st.pyplot(fig)
    plt.close()

    # Interpretación cualitativa
    st.markdown("#### 📊 Interpretación Cualitativa de Correlaciones")

    # Definir categorías de correlación
    def clasificar_correlacion(valor):
        if valor >= 0.7:
            return "🔴 Muy fuerte", "Las áreas con correlación muy fuerte son determinantes clave para el éxito en el examen"
        elif valor >= 0.5:
            return "🟠 Fuerte", "Áreas importantes que influyen significativamente en el puntaje final"
        elif valor >= 0.3:
            return "🟡 Moderada", "Áreas con influencia notable pero no determinante"
        elif valor >= 0.1:
            return "🟢 Débil", "Áreas con poca influencia directa en el resultado final"
        else:
            return "⚪ Muy débil", "Áreas con influencia prácticamente nula en el puntaje final"

    # Mostrar interpretación en columnas
    st.markdown("**ESCALA DE INTERPRETACIÓN DE CORRELACIONES:**")
    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        st.markdown("**Valor**")
        st.write("> 0.7")
        st.write("0.5 - 0.7")
        st.write("0.3 - 0.5")
        st.write("0.1 - 0.3")
        st.write("< 0.1")

    with col2:
        st.markdown("**Interpretación**")
        st.write("🔴 Muy fuerte")
        st.write("🟠 Fuerte")
        st.write("🟡 Moderada")
        st.write("🟢 Débil")
        st.write("⚪ Muy débil")

    with col3:
        st.markdown("**Significado**")
        st.write("Determinante clave")
        st.write("Influencia significativa")
        st.write("Influencia notable")
        st.write("Poca influencia")
        st.write("Influencia nula")

    # Análisis por áreas
    st.markdown("#### 🎯 Análisis Detallado por Área Académica")

    # Crear DataFrame con análisis
    analisis_areas = []
    for area in correlaciones_ordenadas.index:
        clasificacion, significado = clasificar_correlacion(correlaciones_ordenadas[area])
        analisis_areas.append({
            'Área': area,
            'Correlación': correlaciones_ordenadas[area],
            'Clasificación': clasificacion,
            'Interpretación': significado,
            #'Peso Relativo': f"{(correlaciones_ordenadas[area]/correlaciones_ordenadas.max()*100):.1f}%"
        })

    df_analisis = pd.DataFrame(analisis_areas)
    st.dataframe(df_analisis, use_container_width=True)

    # Puntos clave destacados
    st.markdown("#### 📈 Puntos Clave Destacados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        area_mayor_corr = correlaciones_ordenadas.index[0]
        mayor_corr_val = correlaciones_ordenadas.iloc[0]
        st.metric(
            "Mayor correlación",
            f"{area_mayor_corr}",
            f"{mayor_corr_val:.3f}"
        )

    with col2:
        area_menor_corr = correlaciones_ordenadas.index[-1]
        menor_corr_val = correlaciones_ordenadas.iloc[-1]
        st.metric(
            "Menor correlación",
            f"{area_menor_corr}",
            f"{menor_corr_val:.3f}"
        )

    with col3:
        areas_fuertes = len([x for x in correlaciones_ordenadas if x >= 0.5])
        st.metric(
            "Áreas fuertes (≥0.5)",
            f"{areas_fuertes}",
            f"{areas_fuertes/len(correlaciones_ordenadas)*100:.1f}%"
        )

    with col4:
        areas_moderadas = len([x for x in correlaciones_ordenadas if 0.3 <= x < 0.5])
        st.metric(
            "Áreas moderadas (0.3-0.5)",
            f"{areas_moderadas}",
            f"{areas_moderadas/len(correlaciones_ordenadas)*100:.1f}%"
        )

    # Análisis por grupos de áreas
    st.markdown("#### 📚 Análisis por Grupos de Áreas")

    # Definir grupos de áreas
    grupos_areas = {
        "Matemáticas": ['RV', 'RM', 'Arit', 'Alg', 'Geo', 'Trig'],
        "Ciencias": ['Bio', 'Qui', 'Fis'],
        "Humanidades": ['Eco', 'Geog', 'His']
    }

    # Calcular promedios por grupo
    analisis_grupos = []
    for grupo, areas_grupo in grupos_areas.items():
        correlaciones_grupo = [correlaciones_ordenadas[area] for area in areas_grupo if area in correlaciones_ordenadas]
        if correlaciones_grupo:
            analisis_grupos.append({
                'Grupo': grupo,
                'Áreas Incluidas': ', '.join(areas_grupo),
                'Correlación Promedio': np.mean(correlaciones_grupo),
                'Correlación Máxima': max(correlaciones_grupo),
                'Correlación Mínima': min(correlaciones_grupo),
                'Número de Áreas': len(correlaciones_grupo)
            })

    df_grupos = pd.DataFrame(analisis_grupos).round(3)
    st.dataframe(df_grupos, use_container_width=True)

    # Recomendaciones estratégicas
    with st.expander("💡 Recomendaciones Estratégicas Basadas en el Análisis"):
        st.markdown("**RECOMENDACIONES PARA POSTULANTES:**")
        
        # Áreas con mayor correlación
        st.markdown("**🎯 Enfocar esfuerzos en áreas de alta correlación:**")
        areas_top3 = correlaciones_ordenadas.head(3)
        for i, (area, corr) in enumerate(areas_top3.items(), 1):
            st.write(f"{i}. **{area}** (correlación: {corr:.3f}) - Priorizar en preparación")
        
        st.markdown("**⚖️ Balancear preparación:**")
        st.write("- No descuidar áreas con correlación moderada")
        st.write("- Las áreas con baja correlación pueden ser diferenciadoras")
        st.write("- Desarrollar fortalezas en áreas clave del grupo de interés")
        
        st.markdown("**📊 Estrategia por grupos:**")
        for grupo in analisis_grupos:
            st.write(f"- **{grupo['Grupo']}**: Correlación promedio {grupo['Correlación Promedio']:.3f}")
            if grupo['Correlación Promedio'] > 0.4:
                st.write("  → Grupo de alta importancia para la preparación general")
            else:
                st.write("  → Grupo de importancia específica según carrera objetivo")


    # Análisis final resumen
    st.markdown("#### 📋 Resumen")

    st.markdown("**CONCLUSIONES PRINCIPALES:**")
    st.write("1. **Áreas críticas**: Las áreas con correlación > 0.5 son determinantes para el éxito")
    st.write("2. **Estrategia de estudio**: Enfocar preparación en áreas de alta correlación")
    st.write("3. **Diferencial competitivo**: Áreas con correlación moderada pueden marcar diferencia")
    st.write("4. **Planificación**: Distribuir tiempo de estudio según importancia correlacional")

        
    st.success("✅ Todas las gráficas generadas exitosamente!")

# Interfaz principal de Streamlit
# Interfaz principal de Streamlit
def main():
    st.sidebar.title("📁 Carga de Datos")
    
    uploaded_file = st.sidebar.file_uploader(
        "Sube tu archivo Excel (.xlsx)", 
        type=['xlsx'],
        help="El archivo debe contener las columnas especificadas en el formato"
    )
    
    # Opción para convertir a escala 0-20
    convertir_escala = st.sidebar.checkbox(
        "Convertir calificaciones a escala 0-20", 
        value=True,
        help="Convierte RV, RM, Arit, Alg, Geo, Trig, Bio, Qui, Fis, Eco, Geog, His y Final a escala de 0 a 20"
    )
    
    # Navegación entre secciones
    st.sidebar.markdown("---")
    st.sidebar.title("🔍 Navegación")
    seccion = st.sidebar.radio(
        "Selecciona la sección a visualizar:",
        ["Análisis General", "Análisis por Materias"]
    )
    
    if uploaded_file is not None:
        try:
            # Leer el archivo Excel
            df = pd.read_excel(uploaded_file)
            
            # Validar que tenga las columnas necesarias
            columnas_requeridas = ['SEXO', 'EDAD', 'NACIONALIDAD', 'TIPO.INSTITUCIÓN', 'GESTIÓN', 
                                 'DEP..DOM.', 'MODALIDAD', 'OPCION.1', 'OPCION.2', 'Final', 'OM', 'Especialidad']
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                st.error(f"❌ Faltan las siguientes columnas en el archivo: {', '.join(columnas_faltantes)}")
                st.info("""
                **Formato requerido de columnas:**
                - orden, SEXO, EDAD, DIST..NAC., PROV..NAC., DEP..NAC., NACIONALIDAD
                - TIPO.INSTITUCIÓN, GESTIÓN, INSTITUCIÓN, DPTO..PROCEDENCIA
                - DIST..DOM., PROV..DOM., DEP..DOM., MODALIDAD
                - OPCION.1, OPCION.2
                - RV, RM, Arit, Alg, Geo, Trig, Bio, Qui, Fis, Eco, Geog, His
                - Final, OM, Especialidad
                """)
            else:
                # Convertir a escala 0-20 si está seleccionado
                if convertir_escala:
                    df_original = df.copy()
                    df = convertir_a_escala_20(df)
                    #st.sidebar.success("✅ Calificaciones convertidas a escala 0-20")
                    
                    # Mostrar comparación de escalas
                    #with st.sidebar.expander("🔍 Ver conversión escala"):
                    #    st.write("**Ejemplo de conversión:**")
                    #    columnas_calificaciones = ['RV', 'RM', 'Arit', 'Alg', 'Geo', 'Trig', 'Bio', 'Qui', 'Fis', 'Eco', 'Geog', 'His', 'Final']
                    #    columnas_disponibles = [col for col in columnas_calificaciones if col in df.columns]
                    #    
                    #    if len(columnas_disponibles) > 0:
                    #        ejemplo_original = df_original[columnas_disponibles].iloc[0]
                    #        ejemplo_convertido = df[columnas_disponibles].iloc[0]
                    #        comparacion = pd.DataFrame({
                    #            'Original': ejemplo_original,
                    #           'Escala 0-20': ejemplo_convertido
                    #        })
                    #        st.dataframe(comparacion)
                
                st.sidebar.success(f"✅ Archivo cargado correctamente: {len(df)} registros")
                
                # Mostrar información del dataset
                with st.sidebar.expander("📋 Información del Dataset"):
                    #st.write(f"**Registros:** {len(df)}")
                    #st.write(f"**Columnas:** {len(df.columns)}")
                    
                    # Estadísticas de ingreso vs no ingreso
                    no_ingreso_count = len(df[df['Especialidad'] == 'No Ingreso'])
                    si_ingreso_count = len(df[df['Especialidad'] != 'No Ingreso'])
                    st.write(f"**No ingresaron:** {no_ingreso_count} ({no_ingreso_count/len(df)*100:.1f}%)")
                    st.write(f"**Ingresaron:** {si_ingreso_count} ({si_ingreso_count/len(df)*100:.1f}%)")
                    
                    #st.write("**Primeras filas:**")
                    #st.dataframe(df.head(3))
                    
                    if convertir_escala:
                        st.write("**🔢 Escala aplicada:** 0-20")
                
                # Filtros en sidebar - CAMBIO PRINCIPAL AQUÍ
                with st.sidebar.expander("🔍 Filtros"):
                    # Filtro por estado de ingreso
                    opciones_ingreso = ['Todos', 'Solo ingresaron', 'Solo no ingresaron']
                    filtro_ingreso = st.selectbox("Filtrar por estado de ingreso:", opciones_ingreso)
                    
                    if filtro_ingreso == 'Solo ingresaron':
                        df = df[df['Especialidad'] != 'No Ingreso']
                    elif filtro_ingreso == 'Solo no ingresaron':
                        df = df[df['Especialidad'] == 'No Ingreso']
                    
                    # Filtro adicional por modalidad (opcional)
                    if 'MODALIDAD' in df.columns:
                        modalidades = ['Todos'] + list(df['MODALIDAD'].unique())
                        modalidad_seleccionada = st.selectbox("Filtrar por modalidad:", modalidades)
                        if modalidad_seleccionada != 'Todos':
                            df = df[df['MODALIDAD'] == modalidad_seleccionada]
                
                # Mostrar estadísticas del filtro aplicado
                #with st.sidebar.expander("📊 Estadísticas del Filtro"):
                #    total_filtrado = len(df)
                #    no_ingreso_filtrado = len(df[df['Especialidad'] == 'No Ingreso'])
                #    si_ingreso_filtrado = len(df[df['Especialidad'] != 'No Ingreso'])
                    
                #    st.write(f"**Total filtrado:** {total_filtrado}")
                #    if total_filtrado > 0:
                #        st.write(f"**No ingresaron:** {no_ingreso_filtrado} ({no_ingreso_filtrado/total_filtrado*100:.1f}%)")
                #        st.write(f"**Ingresaron:** {si_ingreso_filtrado} ({si_ingreso_filtrado/total_filtrado*100:.1f}%)")
                
                # Navegación entre secciones
                if seccion == "Análisis General":
                    generar_todas_graficas(df)
                else:
                    analisis_materias(df)
                
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
    else:
        # Pantalla de bienvenida (mantener igual)
        st.markdown("""
        # 🎓 Dashboard de Análisis de Admisión UNALM
        
        ## Bienvenido/a
        
        Esta aplicación te permite analizar los datos del proceso de admisión de la Universidad Nacional Agraria La Molina mediante gráficas interactivas.
        
        ### 📋 Instrucciones:
        1. **Sube tu archivo Excel** usando el panel lateral
        2. **Asegúrate** de que el archivo tenga las columnas requeridas
        3. **Usa los filtros** en el panel lateral para refinar el análisis
        4. **Explora** las diferentes secciones del dashboard
        
        ### 🎯 Características:
        - **Análisis General**: 14 tipos diferentes de análisis gráficos
        - **Análisis por Materias**: Análisis detallado del rendimiento académico
        - **Conversión automática a escala 0-20**
        - **Filtros por estado de ingreso**: Comparar ingresados vs no ingresados
        - Métricas resumidas
        - Visualización profesional
        """)
        
        st.info("""
        **🔢 Conversión a escala 0-20:**
        - RV: 25 → 20
        - RM: 25 → 20  
        - Arit: 5 → 20
        - Alg: 5 → 20
        - Geo: 4 → 20
        - Trig: 4 → 20
        - Bio: 6 → 20
        - Qui: 6 → 20
        - Fis: 6 → 20
        - Eco: 4 → 20
        - Geog: 5 → 20
        - His: 5 → 20
        - Final: 100 → 20
        """)

if __name__ == "__main__":
    main()

