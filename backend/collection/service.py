import asyncio
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
import random
import logging

""" Instancia para registro de logs del módulo collections (scraper) """
logger = logging.getLogger("collection")

async def human_scroll(page, steps=3):
    """ función asincrona que simula scroll humano

    Args:
        page (Page): Instancia de la página del navegador controlada por Playwright.
        steps (int, optional): Número de desplazamientos parciales hacia abajo. Defaults a 3.

    Returns:
        None
    """
    for i in range(steps):
        await page.evaluate(f"window.scrollBy(0, window.innerHeight/{steps});")
        sleep_time = random.uniform(1.5, 3.0)
        logger.info(f"Scroll step {i+1}/{steps}, esperando {sleep_time:.2f} segundos...")
        await asyncio.sleep(sleep_time)

# --- Plataforma: Milanuncios ---
async def handle_banner_milanuncios(page):
    try:
        await page.evaluate("""
            var element = document.querySelector('#didomi-host');
            if (element) element.remove();
        """)
        logger.info("[Milanuncios] Banner de cookies eliminado.")
    except Exception as e:
        logger.error(f"[Milanuncios] Error al eliminar banner: {e}")
        
async def handle_carousel_milanuncios(page, steps=5):
    image_urls = []
    for i in range(steps):
        try:
            await page.wait_for_selector(".ma-SharedSliderArrow.ma-SharedSliderArrow--right", timeout=3000)
            button = await page.query_selector(".ma-SharedSliderArrow.ma-SharedSliderArrow--right")
            if not button:
                logger.warning("[Milanuncios] Botón carrusel no encontrado")
                break
            await button.click()
            await asyncio.sleep(random.uniform(0.8, 1.5))
            image_urls = await page.eval_on_selector_all(
                '.ma-SharedSlider-slide picture.ma-SharedImage img[src]',
                'els => els.map(e => e.src)'
            )
        except Exception as e:
            logger.error(f"[Milanuncios] Error carrusel: {e}")
            break
    return image_urls


# --- Plataforma: Idealista ---
async def handle_banner_idealista(page):
    try:
        await page.click("button#didomi-notice-agree-button", timeout=3000)
        logger.info("[Idealista] Banner aceptado con click.")
    except Exception:
        logger.info("[Idealista] No se encontró banner de cookies.")

async def handle_carousel_idealista(page, expand_first: bool = True):
    try:
        if expand_first:
            btn = await page.query_selector("a.more-photos")
            if btn:
                await btn.click()
                await page.wait_for_timeout(700)
        
        # JS para extraer todas las URLs
        js_extract = r"""
        Array.from(document.querySelectorAll('#main-multimedia img, .placeholder-multimedia img'))
            .map(n => n.getAttribute('data-service') || n.getAttribute('src') || (n.src || null))
            .filter(Boolean)
        """
        urls = await page.evaluate(js_extract)
        return urls
    except Exception as e:
        logger.error(f"[Idealista] Error extrayendo carrusel: {e}")
        return []

async def scrape(plat: str, url: str, proxy: str = None):
    """ Función asíncrona donde se implementa el scraper junto con simulación de comportamiento humano (funciones anteriores).

    Este scraper utiliza Playwright para cargar una página web, manejar banners de cookies,
    simular scroll humano y navegación en carruseles de imágenes. También permite usar un proxy
    y un User-Agent aleatorio para evitar bloqueos automatizados. 

    Args:
        url (str): URL del sitio web a scrapear.
        proxy (str, optional): Dirección del servidor proxy a utilizar (e.g., "http://127.0.0.1:8000").
            Defaults to None.

    Returns:
        tuple[str, list[str]]: Una tupla que contiene:
            - El contenido HTML de la página (`str`).
            - Una lista de URLs de imágenes extraídas del carrusel (`list[str]`).
    """
    ua = UserAgent()
    user_agent = ua.random

    playwright = await async_playwright().start()
    browser = None
    browser_args = [
        f'--user-agent={user_agent}',
        '--disable-blink-features=AutomationControlled',
    ]

    launch_options = {
        "headless": True,
        "args": browser_args,
        "ignore_default_args": ["--mute-audio"]
    }

    if proxy:
        launch_options["proxy"] = {"server": proxy} # en caso de introducir proxy

    try:
        browser = await playwright.chromium.launch(**launch_options)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        logger.info(f"Visitando {url} con User-Agent: {user_agent}")
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")


        # Banner por plataforma
        if "milanuncios" in plat:
            await handle_banner_milanuncios(page)
        elif "idealista" in plat:
            await handle_banner_idealista(page)

        await human_scroll(page, steps=5)


        await human_scroll(page, steps=5)
    
        # Carrusel por plataforma
        if "milanuncios" in plat:
            images = await handle_carousel_milanuncios(page, steps=10)
        elif "idealista" in plat:
            images = await handle_carousel_idealista(page, True)
        else:
            images = []
        
        extra_wait = random.uniform(2, 5)
        logger.info(f"Esperando {extra_wait:.2f} segundos antes de obtener contenido...")
        await asyncio.sleep(extra_wait)

        content = await page.content()
    finally:
        if browser is not None:
            await browser.close()
        await playwright.stop()

    return content, images

def run_collection_pipeline(plat: str, url: str, proxy: str = None):
    """
    Ejecuta el scraper para obtener contenido HTML en bruto e imágenes de una URL.

    Args:
        url (str): URL de la que se extraerá el contenido.
        proxy (str, optional): Dirección del servidor proxy a utilizar. Por defecto, None.

    Returns:
        Tuple[str, List[str]]: HTML en bruto y lista de URLs de imágenes obtenidas.
    """
    html, images_urls = asyncio.run(scrape(plat, url, proxy))

    if html is not None or images_urls:
        logger.info("Contenido scrapeado con éxito")
    else:
        logger.warning(f"No se pudo extraer contenido de la URL: {url}")

    return html, images_urls