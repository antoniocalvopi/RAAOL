from django.shortcuts import render
import requests, os
from rest_framework.views import APIView
from rest_framework.response import Response
from dotenv import load_dotenv
from django.http import HttpResponse, StreamingHttpResponse

load_dotenv('.config')
BASE = os.getenv("SERVICE_BASE")


class PipelineRunView(APIView):
    """ Vista de API que ejecuta pipeline para análisis de anuncios.
    Retorna el resultado final (HTML). """
    def post(self, request):
        url = request.data.get("url")
        if not url:
            return Response({"error": "Falta el parámetro 'url'"}, status=400)

        try:
            # Paso 1: Crawling
            crawling_resp = requests.post(
                f"{BASE}{os.getenv('CRAWLING_URL')}/check-url/",
                json={"url": url}
            )
            crawling_resp.raise_for_status()
            platform = crawling_resp.json().get("plataforma")

            # Paso 2: Collection
            collection_resp = requests.get(
                f"{BASE}{os.getenv('COLLECTION_URL')}/scrape?plat={platform}&url={url}" 
            )
            collection_resp.raise_for_status()
            html = collection_resp.json().get("html")
            images = collection_resp.json().get("images")
            
            # Paso 3: Cleaning
            cleaning_resp = requests.post(
                f"{BASE}{os.getenv('CLEANING_URL')}/clean/",
                json={"html": html, "plat": platform, "images": images}
            )
            cleaning_resp.raise_for_status()
            resp_json = cleaning_resp.json()
            ide = resp_json.get("result", {}).get("ide")
            
            # Paso 4: Classifying
            classifying_resp = requests.post(
                f"{BASE}{os.getenv('CLASSIFYING_URL')}/{ide}/"
            )
            classifying_resp.raise_for_status()
            
            # Paso 5: Delivering (HTML)
            response = requests.get(
                f"{BASE}{os.getenv('DELIVER_URL')}/{ide}/"
            )

            if response.ok:
                return HttpResponse(response.text)
            else:
                print(f"Error al entregar para {ide}: {response.status_code} - {response.text}")
                return Response(f"Error en el delivering: {response.text}", status=500)

        except requests.RequestException as e:
            return Response({"error": f"Error en la pipeline: {str(e)}"}, status=500)


class PipelineStreamView(APIView):
    """Vista que ejecuta pipeline mostrando logs en tiempo real."""
    def get(self, request):
        url = request.GET.get("url")
        if not url:
            return StreamingHttpResponse(iter(["Falta el parámetro 'url'\n"]), content_type="text/plain")

        def event_stream():
            try:
                # Paso 1
                yield ">> [1/5] Crawling...\n"
                crawling_resp = requests.post(
                    f"{BASE}{os.getenv('CRAWLING_URL')}/check-url/",
                    json={"url": url}
                )
                crawling_resp.raise_for_status()
                platform = crawling_resp.json().get("plataforma")
                yield "   ✓ Crawling completado\n"

                # Paso 2
                yield ">> [2/5] Collection...\n"
                collection_resp = requests.get(
                    f"{BASE}{os.getenv('COLLECTION_URL')}/scrape?plat={platform}&url={url}" 
                )
                collection_resp.raise_for_status()
                html = collection_resp.json().get("html")
                images = collection_resp.json().get("images")
                yield "   ✓ Collection completado\n"

                # Paso 3
                yield ">> [3/5] Cleaning...\n"
                cleaning_resp = requests.post(
                    f"{BASE}{os.getenv('CLEANING_URL')}/clean/",
                    json={"html": html, "plat": platform, "images": images}
                )
                cleaning_resp.raise_for_status()
                resp_json = cleaning_resp.json()
                ide = resp_json.get("result", {}).get("ide")
                yield "   ✓ Cleaning completado\n"

                # Paso 4
                yield ">> [4/5] Classifying...\n"
                classifying_resp = requests.post(
                    f"{BASE}{os.getenv('CLASSIFYING_URL')}/{ide}/"
                )
                classifying_resp.raise_for_status()
                yield "   ✓ Classifying completado\n"

                # Paso 5
                yield ">> [5/5] Delivering...\n"
                resultados_url = f"{BASE}{os.getenv('DELIVER_URL')}/{ide}/"
                yield f"Resultados generados:{resultados_url}\n"

            except requests.RequestException as e:
                yield f"!! Error en la pipeline: {str(e)}\n"

        return StreamingHttpResponse(event_stream(), content_type="text/plain")


def main_view(request):
    return render(request, "main.html")