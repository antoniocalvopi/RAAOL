# RAAOL - Risk Analysis and Assessment in Online Listings

Este trabajo tiene como objetivo el desarrollo de una herramienta que, mediante el uso de técnicas OSINT y web scraping, permita analizar determinados patrones y características en anuncios de alquileres con el fin de estimar su grado de fiabilidad.

Para ello, se recopilarán datos de diversas fuentes abiertas y se aplicarán criterios predefinidos para evaluar la probabilidad de que un anuncio pueda ser fraudulento. Se explorarán diferentes metodologías para la extracción, análisis y clasificación de la información, considerando tanto indicadores técnicos como patrones de comportamiento comúnmente asociados a fraudes.

El proyecto no pretende ofrecer un sistema infalible de detección de fraudes, sino proporcionar una herramienta de apoyo basada en datos para facilitar la identificación de anuncios sospechosos.

---

## Documentación

Para más información y documentación detallada, visita la [Wiki del proyecto](http://100.98.8.118:3000/x002/RAAOL/wiki/Home).

---

## Instalación

Clona el repositorio:

```bash
git clone http://100.98.8.118:3000/x002/RAAOL
cd RAAOL
````

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Configura las variables de entorno:

```bash
nvim .config
```

Ejecuta el proyecto:

```bash
cd backend
python migrate
python manage.py runserver 8001
```

---

## Estructura del Proyecto

```text
nombre-proyecto/
│
├── backend/          # Código fuente del backend
├── CONTRIBUTING.md   # Normas para contribuir al proyecto.
├── LICENSE           # Licencia que acoge el proyecto
├── requirements.txt  # Dependencias
└── README.md         # Este fichero
```

---

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor, lee el archivo [CONTRIBUTING.md](./CONTRIBUTING.md) para más detalles.

---

## Licencia

Este proyecto está licenciado bajo la [MIT License](./LICENSE).

---

## Autor

* LinkedIn: [antoniocp](https://www.linkedin.com/in/antonio-c-p-489315279/)

---

## Agradecimientos

