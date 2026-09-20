# Nuevos Endpoints para el Sistema de Evaluaciones

## Resumen de Cambios

El sistema de evaluaciones ha sido mejorado para:
- ✅ Mostrar solo evaluaciones pendientes
- ✅ Detectar correctamente el progreso con estadísticas detalladas
- ✅ Permitir resetear respuestas para empezar de nuevo
- ✅ Mostrar automáticamente nuevas evaluaciones si se agregan mientras está en progreso

---

## Nuevos Endpoints

### 1. **GET `/api/evaluaciones/pendientes/`**
Obtiene solo los ejercicios que el usuario **aún no ha respondido**.

**Request:**
```bash
curl -H "Authorization: Bearer <token>" \
  https://treck-7759cedc445f.herokuapp.com/api/evaluaciones/pendientes/
```

**Response:**
```json
{
  "pendientes": [
    {
      "id": 1,
      "tema": "Phishing",
      "pregunta": "¿Qué indicador sugiere...",
      "concepto": "El phishing usa suplantacion...",
      "ejemplo": "Un correo pide verificar..."
    }
  ],
  "total_pendientes": 3,
  "total_ejercicios": 4
}
```

**Uso en Frontend:**
```javascript
// Cuando el usuario entra a evaluaciones
const response = await fetch('/api/evaluaciones/pendientes/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

if (data.total_pendientes === 0) {
  // Mostrar pantalla de progreso (no más evaluaciones)
  mostrarPantalaProgreso();
} else {
  // Mostrar ejercicios pendientes
  mostrarEjercicios(data.pendientes);
}
```

---

### 2. **GET `/api/evaluaciones/estadisticas/`**
Obtiene **estadísticas completas** del progreso del usuario.

**Request:**
```bash
curl -H "Authorization: Bearer <token>" \
  https://treck-7759cedc445f.herokuapp.com/api/evaluaciones/estadisticas/
```

**Response:**
```json
{
  "total_respuestas": 5,
  "respuestas_correctas": 4,
  "porcentaje_aciertos": 80.0,
  "total_ejercicios": 4,
  "ejercicios_respondidos": 4,
  "ejercicios_pendientes": 0,
  "completado": true,
  "estadisticas_por_tema": [
    {
      "tema": "Phishing",
      "total": 2,
      "correctas": 2,
      "porcentaje": 100.0
    },
    {
      "tema": "Smishing",
      "total": 1,
      "correctas": 0,
      "porcentaje": 0.0
    },
    {
      "tema": "Ingenieria social",
      "total": 1,
      "correctas": 1,
      "porcentaje": 100.0
    },
    {
      "tema": "Seguridad en Codigos QR",
      "total": 1,
      "correctas": 1,
      "porcentaje": 100.0
    }
  ]
}
```

**Uso en Frontend:**
```javascript
// En la pantalla de progreso
const response = await fetch('/api/evaluaciones/estadisticas/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const stats = await response.json();

// Mostrar progreso
console.log(`Aciertos: ${stats.respuestas_correctas}/${stats.total_respuestas}`);
console.log(`Porcentaje: ${stats.porcentaje_aciertos}%`);
console.log(`Ejercicios completados: ${stats.ejercicios_respondidos}/${stats.total_ejercicios}`);

// Mostrar desglose por tema
stats.estadisticas_por_tema.forEach(tema => {
  console.log(`${tema.tema}: ${tema.correctas}/${tema.total} (${tema.porcentaje}%)`);
});
```

---

### 3. **POST `/api/evaluaciones/resetear/`**
**Elimina todas las respuestas del usuario** para empezar de nuevo.

**Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  https://treck-7759cedc445f.herokuapp.com/api/evaluaciones/resetear/
```

**Response:**
```json
{
  "status": "success",
  "message": "Se eliminaron 5 respuestas",
  "respuestas_eliminadas": 5
}
```

**Uso en Frontend:**
```javascript
// Botón "Empezar de nuevo"
async function empezarDeNuevo() {
  const response = await fetch('/api/evaluaciones/resetear/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.ok) {
    // Recargar evaluaciones pendientes
    const pendientes = await fetch('/api/evaluaciones/pendientes/', {...});
    mostrarEjercicios(pendientes.data.pendientes);
  }
}
```

---

## Flujo Recomendado en el Frontend

### Componente Principal (Evaluaciones)

```javascript
import { useState, useEffect } from 'react';

export default function EvaluacionesPage() {
  const [estado, setEstado] = useState('cargando'); // cargando, mostrar-ejercicios, mostrar-progreso
  const [ejerciciosPendientes, setEjercicios] = useState([]);
  const [estadisticas, setEstadisticas] = useState(null);
  const [ejercicioActual, setEjercicioActual] = useState(null);

  // Cargar datos al iniciar
  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const pendientes = await fetch('/api/evaluaciones/pendientes/').then(r => r.json());
    
    if (pendientes.total_pendientes === 0) {
      // Sin ejercicios pendientes: mostrar progreso
      const stats = await fetch('/api/evaluaciones/estadisticas/').then(r => r.json());
      setEstadisticas(stats);
      setEstado('mostrar-progreso');
    } else {
      // Ejercicios pendientes: mostrar primero
      setEjercicios(pendientes.pendientes);
      setEjercicioActual(pendientes.pendientes[0]);
      setEstado('mostrar-ejercicios');
    }
  }

  async function responderEjercicio(ejercicioId, opcionId) {
    // Enviar respuesta
    const response = await fetch('/api/evaluaciones/responder/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ejercicio_id: ejercicioId,
        opcion_id: opcionId
      })
    }).then(r => r.json());

    // Verificar si quedan ejercicios pendientes
    const pendientes = await fetch('/api/evaluaciones/pendientes/').then(r => r.json());
    
    if (pendientes.total_pendientes === 0) {
      // Se completaron todos: mostrar progreso
      const stats = await fetch('/api/evaluaciones/estadisticas/').then(r => r.json());
      setEstadisticas(stats);
      setEstado('mostrar-progreso');
    } else {
      // Pasar al siguiente ejercicio
      setEjercicioActual(pendientes.pendientes[0]);
    }
  }

  async function empezarDeNuevo() {
    await fetch('/api/evaluaciones/resetear/', { method: 'POST' });
    cargarDatos(); // Recargar desde el inicio
  }

  // Renderizado
  if (estado === 'cargando') {
    return <div>Cargando evaluaciones...</div>;
  }

  if (estado === 'mostrar-ejercicios') {
    return (
      <EjercicioComponent 
        ejercicio={ejercicioActual}
        onRespuesta={responderEjercicio}
      />
    );
  }

  if (estado === 'mostrar-progreso') {
    return (
      <ProgresoComponent
        estadisticas={estadisticas}
        onEmpezarDeNuevo={empezarDeNuevo}
      />
    );
  }
}
```

### Componente de Progreso

```javascript
export function ProgresoComponent({ estadisticas, onEmpezarDeNuevo }) {
  return (
    <div className="progreso-container">
      <h2>Tu Progreso en Evaluaciones</h2>
      
      {/* Progreso General */}
      <div className="progreso-general">
        <h3>Aciertos</h3>
        <div className="stat">
          <span>{estadisticas.respuestas_correctas}/{estadisticas.total_respuestas}</span>
          <div className="progress-bar">
            <div 
              style={{ width: `${estadisticas.porcentaje_aciertos}%` }}
            >
              {estadisticas.porcentaje_aciertos}%
            </div>
          </div>
        </div>
      </div>

      {/* Desglose por Tema */}
      <div className="desglose-temas">
        <h3>Progreso por Tema</h3>
        {estadisticas.estadisticas_por_tema.map(tema => (
          <div key={tema.tema} className="tema-stat">
            <h4>{tema.tema}</h4>
            <p>{tema.correctas}/{tema.total} ({tema.porcentaje}%)</p>
            <div className="progress-bar">
              <div style={{ width: `${tema.porcentaje}%` }}></div>
            </div>
          </div>
        ))}
      </div>

      {/* Botón Empezar de Nuevo */}
      <button onClick={onEmpezarDeNuevo} className="btn-empezar">
        Empezar de Nuevo
      </button>

      {/* Información */}
      {estadisticas.completado && (
        <div className="mensaje-completado">
          ¡Has completado todas las evaluaciones disponibles!
          {estadisticas.ejercicios_pendientes > 0 && (
            <p>Hay {estadisticas.ejercicios_pendientes} nuevas evaluaciones disponibles.</p>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Diferencias con la Anterior Implementación

| Aspecto | Antes | Ahora |
|--------|-------|-------|
| **Mostrar ejercicios** | Todos los ejercicios | Solo pendientes |
| **Detectar progreso** | Problema con `/respuestas/` | Endpoint `/estadisticas/` correcto |
| **Reset** | No disponible | `POST /resetear/` elimina respuestas |
| **Nuevas evaluaciones** | No se detactaban | Se muestran automáticamente |
| **Pantalla progreso** | No persistía bien | Persiste hasta resetear |

---

## Testing Local

```bash
# 1. Obtener token (login)
TOKEN=$(curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"federico","password":"tu_password"}' | jq .access)

# 2. Ver evaluaciones pendientes
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/evaluaciones/pendientes/

# 3. Ver estadísticas
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/evaluaciones/estadisticas/

# 4. Resetear
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/evaluaciones/resetear/
```

---

## Resumen

✅ **Evaluaciones pendientes**: Solo se muestran ejercicios no respondidos  
✅ **Estadísticas**: Corregido para detectar correctamente respuestas y aciertos  
✅ **Reset**: Permite empezar de nuevo eliminando respuestas  
✅ **Nuevas evaluaciones**: Se muestran automáticamente si se agregan  
✅ **Persistencia**: La pantalla de progreso se queda hasta resetear  
