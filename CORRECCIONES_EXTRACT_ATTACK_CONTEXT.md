# Correcciones: _extract_attack_context()

**Fecha**: 01/09/2026  
**Objetivo**: Eliminar duplicados y mejorar precisión de campos

---

## 🔴 PROBLEMAS IDENTIFICADOS Y SOLUCIONADOS

### PROBLEMA 1: ejemplos_ataque duplicado de proceso_ataque
**Causa**: Ambos campos usaban `PHISHING_TACTICS_KEYWORDS` con la misma lógica
```python
# ANTES (INCORRECTO):
if any(keyword in normalized for keyword in PHISHING_TACTICS_KEYWORDS) and len(process_lines) < 8:
    process_lines.append(raw)  # ← Misma lógica

if any(keyword in normalized for keyword in PHISHING_TACTICS_KEYWORDS) and len(example_lines) < 6:
    example_lines.append(raw)  # ← Captura lo mismo!
```

**Solución**: Separar la lógica
- `proceso_ataque`: Captura ACCIONES de atacante + tácticas
- `ejemplos_ataque`: Captura SOLO menciones de tácticas (sin acciones)

```python
# AHORA (CORRECTO):
# proceso_ataque: Necesita has_action
if has_action and len(process_lines) < 8:
    process_lines.append(raw)

# ejemplos_ataque: Solo tácticas, sin acciones
if has_phishing_tactic and not has_action and len(example_lines) < 6:
    example_lines.append(raw)
```

---

### PROBLEMA 2: secuencia_ataque sin marcadores de secuencia
**Causa**: Capturaba oraciones que contienen flujo pero no describían pasos ordenados

**Solución**: Diferenciar entre:
1. **Marcadores explícitos**: primero, luego, después, 1., 2., 3.
2. **Flujo de acciones**: recibe, hace clic, ingresa, es redirigido

```python
# AHORA (CORRECTO):
has_sequence_marker = any(marker in normalized for marker in sequence_markers)
if has_sequence_marker and len(sequence_lines) < 8:
    sequence_lines.append(raw)  # ← Prioridad a marcadores explícitos

# O si tiene flujo + acciones
elif has_flow and (has_action or has_phishing_tactic) and len(sequence_lines) < 8:
    sequence_lines.append(raw)  # ← Secundario: flujo con acciones
```

---

### PROBLEMA 3: origen_ataque vacío (capturaba solo 1 mención)
**Causa**: Solo capturaba la PRIMERA mención encontrada
```python
# ANTES (INCORRECTO):
if not origin_line and any(marker in normalized for marker in ORIGIN_MARKERS):
    origin_line = raw  # ← Solo 1, luego se ignora el resto
```

**Solución**: Capturar múltiples menciones
```python
# AHORA (CORRECTO):
origin_lines: list[str] = []  # ← Lista, no single
if len(origin_lines) < 3 and any(marker in normalized for marker in ORIGIN_MARKERS):
    if not _is_too_similar(raw, origin_lines, 0.8):
        origin_lines.append(raw)  # ← Múltiples menciones

# Return
'origen_ataque': ' '.join(origin_lines)[:600],  # ← Combina todas
```

---

### PROBLEMA 4: objetivo_ataque vacío (capturaba solo 1 mención)
**Solución**: Idéntica a origen_ataque - capturar múltiples menciones

---

### PROBLEMA 5: proceso_ataque desconectado del tema
**Causa**: No validaba que el contenido tenga relación con la temática

**Solución**: Requiere `has_action` (palabra de atacante)
```python
# AHORA (CORRECTO):
if has_action and len(process_lines) < 8:  # ← Necesita acción de atacante
    if not _is_too_similar(raw, process_lines, 0.8):
        process_lines.append(raw)
```

---

## 📋 RESUMEN DE CAMBIOS

| Campo | Antes | Ahora | Mejora |
|-------|-------|-------|--------|
| **proceso_ataque** | Captura con tácticas, puede ser genérico | Solo con acciones de atacante | +Específico |
| **secuencia_ataque** | Cualquier flujo | Requiere marcadores/flujo+acciones | +Ordenado |
| **ejemplos_ataque** | DUPLICADO de proceso | Solo tácticas sin acciones | +Diferenciado |
| **recomendaciones** | Sin cambios | Sin cambios | ✓ OK |
| **origen_ataque** | Solo 1 mención | Múltiples menciones (max 3) | +Completo |
| **objetivo_ataque** | Solo 1 mención | Múltiples menciones (max 3) | +Completo |

---

## ✅ VALIDACIONES APLICADAS

✓ Lógica separada por campo  
✓ Sin duplicados (proceso ≠ ejemplos)  
✓ Múltiples menciones para origen/objetivo  
✓ Secuencia requiere orden explícito o flujo+acciones  
✓ Proceso requiere acción de atacante  
✓ Ejemplos son solo tácticas (sin acciones)

---

## 🚀 PRÓXIMO PASO

Re-ejecutar ingesta con código corregido y validar que los problemas desaparecen.
