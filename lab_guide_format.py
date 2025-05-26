"""
Lab Guide Format Module

This module defines the structure and formatting for laboratory guides,
including functions to format the content and clean markdown formatting.
"""

def get_lab_guide_structure() -> dict:
    """
    Returns the standard structure for laboratory guides.
    
    Returns:
        dict: A dictionary containing the sections and subsections of the lab guide.
    """
    return {
        "header": {
            "institution": "Universidad Cooperativa de Colombia",
            "faculty": "Facultad o Escuela",
            "subject": "Nombre de la asignatura",
            "lab_name": "Nombre del laboratorio",
            "snies_code": "Código SNIES del programa",
            "professor": "Nombre del docente",
            "semester": "Semestre / Periodo académico"
        },
        "sections": [
            {
                "title": "Título del experimento",
                "type": "text"
            },
            {
                "title": "Objetivos",
                "subsections": [
                    {"title": "General", "type": "text"},
                    {"title": "Específicos", "type": "list"}
                ]
            },
            {
                "title": "Competencias a desarrollar",
                "subsections": [
                    {"title": "Cognitivas", "type": "list"},
                    {"title": "Procedimentales", "type": "list"},
                    {"title": "Actitudinales", "type": "list"}
                ]
            },
            {
                "title": "Fundamento teórico",
                "subsections": [
                    {"title": "Conceptos claves con base en bibliografía académica", "type": "text"},
                    {"title": "Enlace a resultados de aprendizaje del programa", "type": "text"}
                ]
            },
            {
                "title": "Materiales y equipos",
                "subsections": [
                    {"title": "Detallados, incluyendo normas de seguridad y sostenibilidad", "type": "list"}
                ]
            },
            {
                "title": "Procedimiento paso a paso",
                "subsections": [
                    {"title": "Instrucciones precisas", "type": "list"},
                    {"title": "Esquemas o diagramas si aplica", "type": "text"}
                ]
            },
            {
                "title": "Actividades previas al laboratorio",
                "subsections": [
                    {"title": "Cuestionario diagnóstico o lectura dirigida", "type": "text"}
                ]
            },
            {
                "title": "Actividades durante el laboratorio",
                "subsections": [
                    {"title": "Registro de observaciones", "type": "text"},
                    {"title": "Recolección de datos", "type": "text"}
                ]
            },
            {
                "title": "Análisis de resultados",
                "subsections": [
                    {"title": "Preguntas orientadoras", "type": "list"},
                    {"title": "Cálculos si aplica", "type": "text"},
                    {"title": "Comparación con teoría", "type": "text"}
                ]
            },
            {
                "title": "Conclusiones",
                "subsections": [
                    {"title": "Relación con los objetivos y competencias", "type": "text"}
                ]
            },
            {
                "title": "Recomendaciones y normas de bioseguridad",
                "type": "text"
            },
            {
                "title": "Referencias",
                "subsections": [
                    {"title": "Normas APA (u otra que use tu institución)", "type": "list"}
                ]
            }
        ]
    }

def clean_markdown_formatting(content: str) -> str:
    """
    Cleans markdown formatting from the content while preserving the structure.
    
    Args:
        content (str): The markdown formatted content
        
    Returns:
        str: Cleaned content with proper HTML formatting
    """
    # First, handle headers with proper HTML structure
    lines = content.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        # Handle headers
        if line.startswith('# '):
            formatted_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            formatted_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            formatted_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            formatted_lines.append(f'<h4>{line[5:]}</h4>')
        # Handle lists
        elif line.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            formatted_lines.append(f'<li>{line[2:]}</li>')
        # Handle empty lines and end of lists
        elif line.strip() == '':
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('<br>')
        # Handle regular text
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<p>{line}</p>')
    
    # Close any open list
    if in_list:
        formatted_lines.append('</ul>')
    
    # Join all lines and clean up any double line breaks
    content = '\n'.join(formatted_lines)
    content = content.replace('<br><br>', '<br>')
    
    # Handle any remaining markdown formatting
    content = content.replace('**', '<strong>').replace('**', '</strong>')
    content = content.replace('*', '<em>').replace('*', '</em>')
    content = content.replace('`', '<code>').replace('`', '</code>')
    
    # Handle code blocks
    content = content.replace('```', '<pre><code>').replace('```', '</code></pre>')
    
    # Handle links
    import re
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    
    return content

def format_lab_guide_content(content: str, professor_name: str, institution_info: dict) -> str:
    """
    Formats the lab guide content with the institutional header and proper structure.
    
    Args:
        content (str): The main content of the lab guide
        professor_name (str): Name of the professor
        institution_info (dict): Dictionary containing institution information
        
    Returns:
        str: Formatted lab guide content
    """
    # Create the institutional header
    header = f"""
    <div class="institutional-header">
        <h1>{institution_info.get('institution', 'Nombre de la institución')}</h1>
        <h2>{institution_info.get('faculty', 'Facultad o Escuela')}</h2>
        <p><strong>Programa académico:</strong> {institution_info.get('academic_program', 'Programa académico')}</p>
        <p><strong>Asignatura:</strong> {institution_info.get('subject', 'Nombre de la asignatura')}</p>
        <p><strong>Laboratorio:</strong> {institution_info.get('lab_name', 'Nombre del laboratorio')}</p>
        <p><strong>Código SNIES:</strong> {institution_info.get('snies_code', 'Código SNIES')}</p>
        <p><strong>Docente:</strong> {professor_name}</p>
        <p><strong>Semestre:</strong> {institution_info.get('semester', 'Semestre actual')}</p>
    </div>
    <hr>
    """
    
    # Clean and format the main content
    formatted_content = clean_markdown_formatting(content)
    
    # Combine header and content
    return header + formatted_content 