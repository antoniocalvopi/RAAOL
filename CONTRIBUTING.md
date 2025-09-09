## Cómo contribuir

Este documento explica las normas básicas para contribuir al proyecto, incluyendo cómo escribir mensajes de commit y docstrings, con el objetivo de mantener la calidad y coherencia en el código.
#### Índice
- [Cómo contribuir](#cómo-contribuir)  
- [Flujo para contribuir](#flujo-para-contribuir)  
- [Guía de Commits](#guía-de-commits)  
  - [Ejemplo](#ejemplo)  
  - [Tipos de operación](#tipos-de-operación)  
  - [Buenas prácticas para los mensajes de commit](#buenas-prácticas-para-los-mensajes-de-commit)  
- [Guía Docstrings (Google Style)](#guía-docstrings-google-style)  
  - [Estructura general](#estructura-general)  
  - [Buenas prácticas](#buenas-prácticas)  
  - [Ejemplo real](#ejemplo-real)  
- [Tests](#tests)  
- [Contacto](#contacto)


---

## Flujo para contribuir

1. Haz un fork del repositorio.
    
2. Crea una rama nueva para tu cambio:
    
    ```bash
    git checkout -b mi-rama
    ```
    
3. Realiza tus cambios siguiendo las guías de commits y docstrings. (consultar mas abajo)
    
4. Asegúrate de que el código pasa las pruebas (si aplican).
    
5. Envía un pull request describiendo los cambios.
    

---
## Guía de Commits

Para mantener el historial de commits claro y organizado, se recomienda seguir una estructura consistente que facilite entender rápidamente qué se hizo en cada cambio. La estructura utilizada es la siguiente:

```
{nombre_del_módulo}<{tipo_de_operación}>: {breve o mediana descripción}
```

### Ejemplo

```bash
git commit -m "crawling<refactor>: refactorización de script views"
```

En este ejemplo:

- **crawling** es el nombre del módulo del proyecto donde se hizo el cambio.
    
- indica el tipo de operación.
    
- La descripción explica brevemente qué se realizó.
    

### Tipos de operación

| Tipo de operación | Descripción                                                | Ejemplo de commit                                    |
| ----------------- | ---------------------------------------------------------- | ---------------------------------------------------- |
| `<feature>`       | Cuando se añade una nueva funcionalidad                    | `auth<feature>: implementación de login`             |
| `<fix>`           | Para corrección de errores o bugs                          | `api<fix>: corrección en el endpoint de usuarios`    |
| `<refactor>`      | Cambios en el código sin añadir funcionalidades            | `db<refactor>: limpieza y optimización de consultas` |
| `<docs>`          | Cambios o mejoras en la documentación                      | `readme<docs>: actualización de instrucciones`       |
| `<test>`          | Añadir o modificar pruebas                                 | `tests<test>: pruebas unitarias para auth`           |
| `<style>`         | Cambios relacionados con formato o estilo (no funcionales) | `ui<style>: mejora de indentación y espaciado`       |
| `<chore>`         | Tareas generales, configuraciones, scripts, etc.           | `build<chore>: actualización de dependencias`        |

### Buenas prácticas para los mensajes de commit

- Usar siempre la estructura `{módulo}<{tipo}>: descripción`.
    
- Ser claro y conciso en la descripción.
    
- Usar tiempo presente y forma activa.
    
- En caso de dudas, describir el "qué" y el "por qué" del cambio.
    
- Evitar mensajes genéricos como "arreglo" o "cambios".

---
## Guía Docstrings (Google Style)

Se utiliza el formato **Google-style docstring** para mantener el código limpio, legible y uniforme.

### Estructura general

```python
def nombre_funcion(param1: Tipo, param2: Tipo) -> Tipo:
    """ Breve descripción de lo que hace la función, redactada en tercera persona.

    Args:
        param1 (Tipo): Descripción clara del primer parámetro.
        param2 (Tipo): Descripción clara del segundo parámetro.

    Returns:
        Tipo: Valor que retorna la función.

    Raises:
        ExcepcionTipo: Condición bajo la cual se lanza esta excepción.
    """
```

### Buenas prácticas

- La docstring debe comenzar con una **frase breve en tercera persona**, por ejemplo: `"Verifica si..."`, `"Devuelve un..."`.
    
- Se recomienda usar las secciones `Args:`, `Returns:` y `Raises:` cuando correspondan.
    
- Aunque las funciones tengan anotaciones de tipos, es importante incluirlos también en la descripción para mayor claridad.
	Ejemplo: `param1 (str)
    
- Mantener consistencia en el uso de puntos finales: o siempre usarlos o nunca usarlos. (válido para cada función o método)
    
- No repetir información obvia, ser directo y útil.
    
- Los métodos privados (aquellos que empiezan con `_`) también deben incluir docstrings si realizan operaciones que no son triviales.
    

### Ejemplo real

```python
def check_consistency(self, tolerance: float = 0.3):
        """ Compara el precio inferido con precios de referencia para evaluar consistencia del precio.

        Args:

            tolerance (float): Porcentaje de tolerancia para considerar precios similares.

        Returns:

            dict|None: Resultado del análisis con estado y puntaje, o respuesta de error.
        """

        if (self.reference_price_m2 is None or
            self.inferred_price_m is None or
            self.reference_price_idealista is None):
            
            self.price_flag = "UNKNOWN"
            return _error_response("Faltan datos para la verificación")
```

---
## Tests

Cuando sea posible, añade o actualiza pruebas para validar que tus cambios no rompen funcionalidades existentes.

---

## Contacto

Si tienes dudas o problemas, abre un issue en el repositorio o contacta al equipo a través de [acalvopi@alumnos.unex.es](mailto:acalvopi@alumnos.unex.es).