# Mejoras al Módulo de Ingestion de Artículos

## Resumen de Cambios

Se ha mejorado significativamente la extracción de campos estructurados de artículos de phishing/smishing. Los cambios se enfocaron en **reducir ruido** y **mejorar precisión** en todos los campos extraídos.

---

## 1. **Mejoras en Limpieza de Texto** (`_clean_text()`)

### Cambios:
- **Filtrado de navegación mejorado**: Ahora elimina "anterior", "siguiente", "volver", etc.
- **Eliminación de metadata**: Elimina fechas de publicación, información de autor
- **Filtrado de interacciones sociales**: Elimina referencias a comentarios, likes, shares
- **Preservación de contenido relevante**: Solo elimina ruido real, no frases válidas

### Impacto:
Reduce significativamente el "basura" que termina en los campos finales.

---

## 2. **Mejoras en Extracción de Párrafos** (`_extract_paragraph_text()`)

### Cambios:
- **Eliminación de comentarios HTML**: `<!-- ... -->` se elimina completamente
- **Descarte de navegación y sidebars**: Busca y elimina elementos con clases como "sidebar", "widget", "nav", "footer", "ads"
- **Soporte para `<main>`**: Si no hay `<article>`, intenta extraer desde `<main>`
- **Filtrado de párrafos cortos**: Elimina párrafos < 15 caracteres (ruido puro)
- **Límite de párrafos**: Procesa máximo 50 párrafos para evitar sobrecarga

### Impacto:
- El contenido extraído es mucho más relevante (solo texto principal)
- Menos navegación y publicidad contaminando el resultado

---

## 3. **Función Nueva: Detección de Genéricos** (`_is_generic_sentence()`)

### Qué hace:
Detecta y filtra frases genéricas que NO aportan información sobre el ataque:
- "Es importante..."
- "Se debe tener cuidado..."
- "En conclusión..."
- Frases muy cortas (< 20 caracteres)

### Impacto:
Evita capturar "relleno" que no tiene valor.

---

## 4. **Función Nueva: Similitud entre Strings** (`_calculate_string_similarity()`)

### Qué hace:
Calcula qué tan similares son dos strings:
- Si uno contiene al otro → 90% similitud
- Basado en palabras comunes (Jaccard similarity)

### Impacto:
Evita duplicados y frases muy parecidas en los campos extraídos.

---

## 5. **Palabras Clave Expandidas**

### Acciones de Atacantes (+20 variantes):
- "cambio de contraseña", "solicita datos", "pide datos", "introduce datos"
- "acceso no autorizado", "completa formulario", etc.

### Operaciones de Phishing/Smishing (+30 variantes):
- "campaña de phishing", "fraude electrónico", "ciberdelincuentes"
- "estafadores en línea", "ofertas falsas", "promoción falsa", etc.

### Origen del Ataque (+15 variantes):
- "actores cibernéticos", "banda de", "organización criminal"
- "grupo criminal", "delincuentes", etc.

### Objetivo del Ataque (+15 variantes):
- "personas afectadas", "trabajadores de", "empresarios"
- "adultos mayores", "ciudadanos de", etc.

### Recomendaciones de Seguridad (+40 variantes):
- "se aconseja", "no hacer clic", "cambiar contraseña"
- "2fa", "configurar", "actualizar", "cuidadoso", etc.

### Objetos Técnicos Maliciosos (+45 variantes):
- "código QR malicioso", "sitio malicioso", "formulario falso"
- "certificado falso", "app falsa", "extensión maliciosa", etc.

### Patrones de Flujo de Ataque (+10 variantes):
- "primero... después", "paso 1, paso 2, etc"
- "en este orden", "llamadas consecutivas", etc.

### Palabras Clave de Paraguay (+20 variantes):
- "asunción", "banco central", "DINAC", "ADUANA", "gobierno paraguayo"

---

## 6. **Mejoras en Extracción de Contexto** (`_extract_attack_context()`)

### Cambios principales:
1. **Deduplicación de oraciones**: Usa `_is_too_similar()` para evitar capturas duplicadas (similitud ≥ 80%)
2. **Filtrado de genéricos**: Rechaza frases que no aportan valor
3. **Aumento de límites**: 
   - Proceso: 4 → 6 oraciones
   - Secuencia: 4 → 5 oraciones
   - Recomendaciones: 4 → 10 oraciones (más ricas)
   - Ejemplos: 4 → 6 oraciones
4. **Tail más corto**: Captura 2 oraciones después de recomendación (era 3)
5. **Mejor filtrado de cola**: Verifica si es genérica antes de añadir a la "cola"

### Impacto:
- Menos repeticiones
- Más información relevante capturada
- Menor ruido en los resultados

---

## 7. **Mejoras en Extracción de Listas HTML** (`_extract_list_items_from_html()`)

### Cambios:
- **Decodificación HTML mejorada**: Maneja `&lt;`, `&gt;`, `&quot;`, `&#039;`
- **Filtrado de items cortos**: Rechaza items < 10 caracteres
- **Mejor limpieza**: Colapsa espacios y trimea correctamente

### Impacto:
Las listas extraídas del HTML son más limpias y relevantes.

---

## 8. **Función Auxiliar Interna: `_is_too_similar()`**

Usada dentro de `_extract_attack_context()` para evitar capturar oraciones demasiado parecidas (80%+ similitud).

---

## Resultados Esperados

### Antes:
- Campos llenos de ruido, navegación, fechas
- Muchas repeticiones
- Oraciones genéricas sin valor
- Contenido irrelevante

### Después:
- ✅ Campos enfocados en contenido real del ataque
- ✅ Sin repeticiones (deduplicación)
- ✅ Sin frases genéricas
- ✅ Mejor separación entre contenido principal y navegación
- ✅ Más variantes de palabras clave capturadas
- ✅ Mejor detección de flujos de ataque

---

## Archivos

- **ingestion.py** - Versión mejorada (actual)
- **ingestion_backup.py** - Versión original (para comparación)

## Testing Recomendado

1. Comparar extracciones antes/después con URLs reales
2. Verificar que los campos no tengan:
   - Navegación ("siguiente", "anterior")
   - Metadata de publicación
   - HTML residual
   - Oraciones genéricas
3. Verificar que SI contengan:
   - Descripción clara del ataque
   - Pasos específicos
   - Recomendaciones accionables
   - Objetos técnicos mencionados

---

## Cambios de Configuración

| Parámetro | Antes | Después | Razón |
|-----------|-------|---------|-------|
| Min. longitud de oración | 12 | 15 | Filtrar más ruido |
| Min. longitud de párrafo | - | 14 | Evitar párrafos vacíos |
| Max items proceso | 4 | 6 | Más cobertura |
| Max items secuencia | 4 | 5 | Más pasos capturados |
| Max items recomendaciones | 4 | 10 | Mejor cobertura |
| Max items ejemplos | 4 | 6 | Más técnicos mencionados |
| Tail de recomendación | 3 | 2 | Menos ruido después |
| Similitud para dedup | - | 0.8 | Evitar repeticiones |
| Min items lista HTML | - | 10 | Evitar items vacíos |

