# Pragma Backend

## Descripción General

**Pragma Backend** es el servidor central de una plataforma de educación emocional. Permite a los usuarios gestionar estrés y ansiedad mediante simulaciones interactivas. Funciona como intermediario entre:

- **Cliente Godot**: donde el usuario juega escenarios.
- **Base de datos cifrada**: almacenamiento seguro de datos sensibles.
- **Dashboard web**: visualización de progreso y retroalimentación.

### Qué es Pragma

Pragma simula situaciones generadoras de estrés (presentaciones, entrevistas, conflictos sociales) en un ambiente seguro. El usuario toma decisiones, recibe retroalimentación y el sistema analiza patrones de comportamiento para generar recomendaciones personalizadas.

### Características Principales

- **Autenticación JWT**: acceso seguro sin exponer credenciales.  
- **Cifrado AES-256**: protege todos los datos de sesiones.  
- **Captura automática de métricas**: tiempo, emoción, impacto por decisión.  
- **Análisis IA**: integración con N8N para insights avanzados.  
- **Dashboard personalizado**: visualización de progreso y recomendaciones.  
- **API REST**: endpoints documentados.  
- **Suite de tests**: 78 pruebas unitarias (autenticación, cifrado, métricas).  

---

## Componentes Principales

- **Módulo de Autenticación**: registro, login y tokens JWT (access 1h, refresh 7d).  
- **Módulo de Cifrado**: AES-256 para proteger savefiles y métricas.  
- **Módulo de Captura de Métricas**: analiza JSONs de Godot y calcula métricas.  
- **Módulo de Análisis**: envía datos a N8N para generar fortalezas, áreas de mejora y recomendaciones.  
- **Módulo de Dashboard**: endpoints para obtener datos de usuario en JSON y renderizar gráficos.  

---

## Inicio Rápido

### Requisitos Previos

- Python 3.12+, PostgreSQL 12+, Git, pip/virtualenv

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/LokszDev/pragma_backend.git
cd pragma_backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
