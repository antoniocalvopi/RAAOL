from bs4 import BeautifulSoup
from .models import RawData as raw_data


def clean_html(content):
    """ Limpia el contenido HTML eliminando scripts, estilos y comentarios.

    Args:
        content: HTML crudo como str.

    Returns:
        str: HTML limpio y estructurado como str.
    """
    soup = BeautifulSoup(content, "html.parser")

    # Eliminar etiquetas <script> y <style>
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Eliminar comentarios HTML
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.comment))):
        comment.extract()

    return soup.prettify()


def extract_data_from_html(cleaned_html, selectores):
    """ Extrae información específica desde el HTML limpio usando selectores CSS.

    Args:
        cleaned_html: HTML procesado y limpio.
        selectores: Diccionario donde la clave es el nombre del campo y el valor el selector de la clase CSS a buscar.

    Returns:
        dict: Diccionario con los datos extraídos. Si un valor no se encuentra, se asigna None.
    """
    soup = BeautifulSoup(cleaned_html, "html.parser")
    data = {}

    for key, css_class in selectores.items():
        element = soup.find(class_=css_class)
        data[key] = element.get_text(strip=True) if element else None

    return data


def run_cleaning_pipeline_from_html(raw_html, selectores, images):
    """ Ejecuta el pipeline de limpieza y extracción desde HTML y guarda el resultado en la base de datos.

    Args:
        raw_html: HTML sin procesar.
        selectores: Diccionario con las clases CSS objetivo.
        images: Lista de imágenes asociadas al contenido.

    Returns:
        obj: Instancia del modelo RawData guardada en la base de datos.
    """
    cleaned_html = clean_html(raw_html)
    data_vector = extract_data_from_html(cleaned_html, selectores)

    data_vector["images"] = images

    result = raw_data.objects.create(
        cleaned_html=cleaned_html,
        feature_vector=data_vector
    )

    return result