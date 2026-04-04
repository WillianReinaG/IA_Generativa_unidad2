# Fase 2 — Fortalezas, limitaciones y riesgos éticos (EcoMarket)

## Marco orientativo (qué cubre el modelo y qué no)

En un esquema típico de **primer nivel de atención** (chat con datos verificados, como en la Fase 3 de este proyecto), el modelo propuesto está pensado para cubrir de forma automática **aproximadamente el 80 % de las consultas repetitivas** (estado de pedido, seguimiento, políticas de devolución con texto fijo). El **20 % restante** suele concentrar **casos complejos** (reclamos graves, situaciones límite, excepciones contractuales, clientes en crisis) que conviene **derivar a un humano** con empatía y criterio situacional. Esas proporciones son **referenciales** y deben validarse con métricas reales en producción.

**En el código de este repositorio** el 80/20 **no aparece como un número calculado** al responder cada chat: lo que sí existe es una **bifurcación explícita** entre (1) flujo con datos verificados de pedido/política (`build_pedido_messages`, `build_devolucion_messages`) y (2) flujo de **escalamiento** cuando el texto del cliente activa una heurística (`ecomarket/routing.py`: `clasificar_consulta_cliente`, `armar_mensajes_atencion_pedido`, `build_escalamiento_messages`). La proporción real automatizada vs escalada se mediría en **analítica de tickets**, no en una variable fija del programa.

## Fortalezas del modelo propuesto (híbrido: LLM + datos internos)

1. **Reducción del tiempo de respuesta**  
   La primera respuesta llega en segundos frente a colas de chat o correo; el cliente obtiene estado del pedido, enlace de rastreo o pasos de devolución sin esperar a un agente disponible.

2. **Disponibilidad 24/7**  
   El servicio puede atender en cualquier horario y zona, útil en picos nocturnos, fines de semana y campañas, sin ampliar turnos humanos en la primera línea.

3. **Alto volumen de consultas repetitivas (orden ~80 %)**  
   Preguntas del tipo “¿dónde está mi pedido?”, “¿cuándo llega?” o “¿puedo devolver esto?” se resuelven con **plantillas de prompts + datos de `data/` (simulando BD)** y reglas explícitas de no inventar información; es el caso de uso principal de `build_pedido_messages` y `build_devolucion_messages` en este repositorio.

4. **Escalado de volumen**  
   Absorbe picos (campañas, fechas clave) sin multiplicar de forma lineal el personal de soporte en el primer contacto.

5. **Consistencia informativa**  
   Si el **contenido factual** proviene de la BD y políticas versionadas, las respuestas pueden alinearse con las mismas reglas que ve el agente humano.

6. **Experiencia conversacional**  
   Buena capacidad para reformular, empatizar en tono y guiar pasos (por ejemplo, devoluciones) en lenguaje natural claro, siempre **acotada** a lo que digan los datos inyectados.

7. **Multicanal**  
   Mismo núcleo lógico puede alimentar chat web, app y, con adaptación, otros canales.

## Limitaciones

1. **No sustituye el trato humano en el ~20 % de casos complejos**  
   Conflictos legales, situaciones de salud ligadas a un producto, fraude, clientes en fuerte distrés o negociaciones excepcionales requieren **empatía profunda, juicio situacional e intervención humana**; el modelo puede parecer empático, pero **no** tiene responsabilidad profesional ni autoridad para resolver esos casos.

2. **Respuestas incorrectas si la información de la base de datos (o del JSON de ejemplo) es errónea**  
   El LLM **no valida** la verdad en almacén: si el pedido figura mal, la fecha es incorrecta o la política está desactualizada, tenderá a **justificar y verbalizar ese error** como si fuera cierto. Mitigación: calidad de datos, auditorías, y mensajes del tipo “según nuestro sistema en este momento…” cuando proceda.

3. **Dependencia de la calidad del contexto inyectado**  
   Si la consulta a BD falla, está desactualizada o el prompt no incluye los campos correctos, la respuesta puede ser incompleta o genérica (aunque en este proyecto se instruye a no inventar y a ofrecer escalamiento).

4. **Límites de conocimiento y alucinaciones residuales**  
   Incluso con RAG, puede **extrapolar** o **mezclar** políticas si el prompt es ambiguo o si se mezclan fuentes sin control.

5. **Coste y latencia**  
   Modelos más capaces o contextos muy largos aumentan coste y tiempo de respuesta; hace falta **caché**, **enrutado** (modelo pequeño vs grande) y límites de tokens.

6. **Integración operativa**  
   Requiere monitoreo, versionado de prompts, pruebas de regresión y trazabilidad de incidencias (no es “configurar y olvidar”).

## Riesgos éticos y mitigaciones orientativas

### 1. Alucinaciones (respuestas incorrectas o inventadas)

- **Riesgo:** Inventar un número de seguimiento, una fecha de entrega o una política que no existe.  
- **Mitigación:** **No** pedir al modelo que adivine datos; solo usar valores devueltos por la API/BD. Instrucciones explícitas del tipo: “Si un dato no está en el contexto, dilo y ofrece canal humano”. Revisión humana en casos de reclamación o alto valor.

### 2. Sesgos en los datos de entrenamiento

- **Riesgo:** Estereotipos en el lenguaje, trato desigual sugerido o contenido ofensivo.  
- **Mitigación:** Políticas de uso, filtros de salida, diversidad en pruebas, revisión periódica de conversaciones muestreadas y ajuste de instrucciones.

### 3. Privacidad de datos sensibles de clientes

- **Riesgo:** Filtrar datos de un cliente a otro, o enviar PII innecesaria al proveedor del modelo.  
- **Mitigación:** Autenticación/autorización estricta en backend, **minimización de datos** en el prompt, anonimización cuando sea posible, acuerdos (DPA) con el proveedor, opción de **retención cero** o regiones según normativa, logs sin datos sensibles en claro.

### 4. Impacto laboral en agentes de servicio al cliente

- **Riesgo:** Presión por productividad, desvalorización del trabajo humano o despidos mal gestionados.  
- **Mitigación:** Reposicionar al equipo hacia **casos complejos**, **calidad**, **escalamientos** y **supervisión del sistema**; formación en IA; transparencia interna; negociación según marco laboral aplicable.

---

*Proyecto: IA Generativa — Unidad 2 — EcoMarket*
