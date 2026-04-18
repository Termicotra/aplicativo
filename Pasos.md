# Plan de Desarrollo del Sistema de Capacitación Contra Phishing

## **Fase 0: Preparación y planificación**

**Objetivo:** tener todo listo para comenzar a programar de forma ordenada.

* Instalar herramientas:

  * Python + Django
  * PostgreSQL
  * Node.js + npm (para React después)
  * Git y repositorio
* Crear estructura inicial del proyecto en Django:

  * Carpeta `backend/`
  * Carpeta `dataset/` para almacenar artículos de ABC y CERT
* Definir **modelos iniciales**:

  * Usuario
  * Artículo (para RAG)
  * Simulación (registro de intentos y resultados)
* Crear **documento de referencia del Prompt de desarrollo**, que servirá de guía para todas las fases.

---

## **Fase 1: Django básico para probar funcionalidad**

**Objetivo:** tener un **prototipo funcional en Django** que capture la lógica principal antes de hacer frontend bonito.

1. Crear proyecto Django:

   ```bash
   django-admin startproject phishing_training
   ```
2. Crear apps esenciales:

   * `users` → manejo de usuarios, autenticación
   * `simulaciones` → registro de simulaciones de phishing
   * `articulos` → base de conocimiento para RAG
4. Crear modelos iniciales:

   * **Usuario:** username, email, password (hashed)
   * **Articulo:** titulo, contenido, fuente, url, fecha
   * **Simulacion:** usuario, articulo, resultado, feedback, fecha
5. Crear **panel admin Django** para gestionar artículos y simulaciones.
6. Crear **endpoints REST básicos** con Django REST Framework:

   * `/api/users/`
   * `/api/simulaciones/`
   * `/api/articulos/`
7. Testear que la API funciona con **Postman o curl**.
8. Crear **página Django básica** con templates para:

   * Login / registro
   * Dashboard mostrando simulaciones
   * Lista de artículos

> ✅ Esta fase asegura que **el backend funciona antes de complicarte con React y la IA**.

---

## **Fase 2: Integración inicial con IA**

**Objetivo:** probar que el sistema puede generar simulaciones y feedback usando IA.

1. Crear módulo `ai_service.py` en Django:

   * Conecta con OpenAI 
   * Recibe prompt + artículos recientes
   * Devuelve simulación y feedback
2. Crear endpoint `/api/generar_simulacion/`

   * Recibe usuario y artículo (o tipo de simulación)
   * Llama a IA y devuelve resultado JSON
3. Testear la integración:

   * Crear simulaciones desde Django shell
   * Comprobar que feedback tiene sentido y es seguro
4. Crear **scripts simples para rellenar base de datos**:

   * Ejemplo: 10 artículos de ABC y 10 alertas de CERT
   * Esto permite que RAG funcione aunque no tengas scraper aún

> ✅ Ahora tienes un backend que **puede generar simulaciones**.

---

## **Fase 3: Automatización y actualización de artículos**

**Objetivo:** que tu sistema sea **dinámico y actualizado semanalmente**.

1. Crear scripts Python para:

   * Scraper de ABC Color
   * Scraper de CERT-PY
   * Guardar artículos nuevos en la base de datos evitando duplicados
2. Configurar **cron job** para ejecución semanal

   * Ejemplo: lunes 3 AM → `python update_articles.py`
3. Probar que nuevos artículos se guardan y pueden ser usados por IA
4. Validar que sistema RAG utiliza artículos recientes correctamente

> ✅ Ahora la IA siempre tiene **información actualizada de Paraguay**.

---

## **Fase 4: Primer frontend mínimo (Django templates)**

**Objetivo:** probar interfaz básica antes de React.

1. Crear templates Django para:

   * Login / registro
   * Dashboard de simulaciones
   * Página para ver feedback
2. Usar **Bootstrap o Tailwind CDN** para estilos rápidos
3. Asegurar que todos los endpoints REST funcionan con esta interfaz
4. Validar flujo completo:

   * Usuario se registra → inicia simulación → recibe feedback

> ✅ Esta fase asegura que **todo el flujo está correcto antes de hacer frontend moderno**.

---

## **Fase 5: Migración a frontend React**

**Objetivo:** tener un frontend moderno y modular, desacoplado del backend.

1. Crear proyecto React dentro de `/frontend`:

   ```bash
   npx create-react-app frontend
   ```
2. Crear componentes:

   * Header
   * Sidebar
   * Card / Módulos de simulación
   * Dashboard
   * Footer
3. Consumir API Django con `fetch` o `axios`
4. Integrar IA y RAG:

   * React muestra la simulación generada
   * Botón para enviar respuesta del usuario → feedback
5. Estilizar con **Tailwind** o **Bootstrap**
6. Validar accesibilidad (contrast, labels, botones claros)
7. Modularizar y documentar cada componente

> ✅ Ahora tienes un sistema completo **moderno, modular y seguro**, listo para mostrar.

---

## **Fase 6: Ajustes de seguridad y pruebas finales**

**Objetivo:** asegurar que tu tesis cumpla con **buenas prácticas de seguridad**.

1. Revisar autenticación:

   * JWT o sesiones seguras
   * Hash seguro de contraseñas
2. Revisar endpoints:

   * Validación y sanitización de datos
   * Protección contra XSS, CSRF, SQL Injection
3. Probar límites de API y roles de usuario
4. Revisar uso de variables de entorno para claves de IA
5. Pruebas de integración:

   * Flujo completo: registro → simulación → feedback
   * Flujo RAG con artículos actualizados
6. Documentar todo para la tesis:

   * Arquitectura
   * Estructura de carpetas
   * Prompt de desarrollo y system prompts
   * Flujo de datos (React ↔ Django ↔ IA ↔ RAG)

---

## **Resumen gráfico de evolución**

```text
Fase 0 → Preparación
Fase 1 → Django funcional (backend + templates)
Fase 2 → Integración IA
Fase 3 → Automatización y RAG
Fase 4 → Frontend mínimo Django
Fase 5 → Frontend moderno React
Fase 6 → Seguridad y pruebas finales
```

> Cada fase incrementa complejidad **sin perder control**.
> Comienzas simple, pruebas que todo funciona, luego agregas IA, RAG y finalmente frontend moderno.

---

💡 **Siguiente paso opcional:**
Se puede generar un **plan de carpetas y módulos desde el inicio hasta React**, incluyendo **dónde van los prompts, IA, RAG y scrapers**, listo para implementarlo paso a paso.

---

Si quieres, puedo hacer eso a continuación y dejarlo en **Markdown completo**, con **estructura de carpetas y archivos sugerida** lista para tu proyecto.

¿Quieres que haga eso?
