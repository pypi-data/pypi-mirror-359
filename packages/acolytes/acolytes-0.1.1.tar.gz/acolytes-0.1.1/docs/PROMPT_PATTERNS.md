## 🔨 Patrones de Persistencia (Base de Datos)

### DatabaseManager - Gestión de Conexiones SQLite

**Dónde se usa**: `/core/database.py`, todos los servicios

**Ejemplo del código real**:

```python
# Singleton pattern para BD
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obtiene la instancia singleton de DatabaseManager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Thread safety con check_same_thread=False
self._connection = sqlite3.connect(
    self.db_path,
    check_same_thread=False  # Seguro por serialización con lock
)

# Serialización con asyncio.Lock para queries
async with self._lock:
    result = await loop.run_in_executor(None, _execute)
```

**Por qué se usa así**:

- Singleton evita múltiples conexiones en sistema mono-usuario
- `check_same_thread=False` es seguro porque serializamos con Lock
- `run_in_executor` evita bloquear el event loop con queries SQL

**Consideraciones futuras**:

- Mantener el patrón singleton para consistencia
- Lock sigue siendo necesario para operaciones concurrentes

### Clasificación de Errores SQLite

**Dónde se usa**: `/core/database.py`

**Ejemplo del código real**:

```python
def _classify_sqlite_error(sqlite_error: sqlite3.Error) -> DatabaseError:
    error_code = getattr(sqlite_error, 'sqlite_errorcode', None)

    if error_code == 5 or 'database is locked' in error_msg.lower():
        # SQLITE_BUSY: BD bloqueada (común en escrituras concurrentes)
        exc = SQLiteBusyError("Database temporarily locked")
        exc.add_suggestion("Reintentar automáticamente con backoff exponencial")
        return exc

    elif error_code == 11 or 'corrupt' in error_msg.lower():
        # SQLITE_CORRUPT: BD corrupta (requiere intervención manual)
        exc = SQLiteCorruptError("Database corruption detected")
        exc.add_suggestion("Restaurar desde backup más reciente")
        return exc
```

**Por qué se usa así**:

- Diferentes errores SQLite requieren diferentes estrategias
- BUSY errors son reintentables, CORRUPT no
- Sugerencias contextuales ayudan al usuario

**Consideraciones**:

- Los códigos de error son específicos de SQLite
- Para otras bases de datos, adaptar la clasificación

### Patrón execute_async con FetchType

**Dónde se usa**: Todos los servicios que acceden a BD

**Ejemplo del código real**:

```python
# Enum para tipos de fetch
class FetchType(Enum):
    ONE = "one"    # fetchone()
    ALL = "all"    # fetchall()
    NONE = "none"  # Solo execute, sin fetch

# Uso en servicios
result = await self.db.execute_async(
    "SELECT * FROM conversations WHERE session_id = ?",
    (session_id,),
    FetchType.ONE
)

if result.data:
    session = cast(Dict[str, Any], result.data)
```

**Por qué se usa así**:

- Type safety con enum explícito
- Evita errores de "fetchone() on INSERT"
- Resultado estructurado con QueryResult

### Retry Logic para Operaciones de BD

**Dónde se usa**: `/services/conversation_service.py`

**Ejemplo del código real**:

```python
async def _execute_with_retry(
    self,
    operation_name: str,
    db_operation: Any,
    *args: Any,
    max_attempts: int = 3,
    **kwargs: Any
) -> Any:
    for attempt in range(max_attempts):
        try:
            result = await db_operation(*args, **kwargs)
            if attempt > 0:
                self.metrics.increment("services.conversation_service.db_retries_successful")
            return result

        except DatabaseError as e:
            if e.is_retryable() and attempt < max_attempts - 1:
                backoff_time = 0.5 * (2**attempt)  # 0.5s, 1s, 2s
                await asyncio.sleep(backoff_time)
                continue
            else:
                raise
```

**Por qué se usa así**:

- SQLite puede tener locks temporales
- Backoff exponencial evita "thundering herd"
- Métricas para monitorear retries

### Transacciones con Context Manager

**Dónde se usa**: `/core/database.py`

**Ejemplo del código real**:

```python
@contextmanager
def transaction(self, isolation_level: str = "DEFERRED"):
    """
    Context manager para transacciones seguras.

    Niveles:
    - DEFERRED: Default, locks al escribir
    - IMMEDIATE: Lock al inicio
    - EXCLUSIVE: Lock exclusivo total
    """
    conn = self._get_connection()
    old_isolation = conn.isolation_level

    try:
        conn.isolation_level = isolation_level
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise _classify_sqlite_error(e)
    finally:
        conn.isolation_level = old_isolation
```

### InsightStore - Compresión zlib

**Dónde se usa**: `/core/database.py`

**Ejemplo del código real**:

```python
# Comprimir entities y code_references
entities_json = json.dumps(insight.get("entities", []))
entities_compressed = zlib.compress(entities_json.encode(), level=9)

query = """
    INSERT INTO dream_insights (
        id, session_id, insight_type, title, description,
        entities_involved, code_references, confidence, impact
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
```

**Por qué se usa así**:

- Arrays JSON pueden ser grandes
- zlib nivel 9 máxima compresión
- SQLite maneja BLOB eficientemente

## 🔍 Patrones de Búsqueda Vectorial (Weaviate)

### HybridSearch - Búsqueda 70/30

**Dónde se usa**: `/rag/retrieval/hybrid_search.py`

**Ejemplo del código real**:

```python
# Búsqueda semántica con embeddings
query_builder = (
    self.weaviate_client.query.get(
        "CodeChunk",
        ["content", "file_path", "chunk_type", "start_line", "end_line"]
    )
    .with_near_vector({
        "vector": query_vector,
        "certainty": 0.7  # Threshold mínimo
    })
    .with_limit(limit)
    .with_additional(["certainty"])  # Score de similitud
)

# Búsqueda léxica con BM25
query_builder = (
    self.weaviate_client.query.get("CodeChunk", [...])
    .with_bm25(
        query=variation,
        properties=["content", "file_path"],  # Campos de búsqueda
    )
    .with_additional(["score"])  # Score BM25
)
```

**Por qué se usa así**:

- Semántica captura conceptos similares
- Léxica encuentra matches exactos
- 70/30 balance óptimo encontrado empíricamente

### Fuzzy Query Expansion

**Dónde se usa**: `/rag/retrieval/hybrid_search.py`

**Ejemplo del código real**:

```python
# Expandir query con variaciones
fuzzy_matcher = get_fuzzy_matcher()
query_variations = fuzzy_matcher.expand_query(query)

for i, variation in enumerate(query_variations):
    # Reducir peso para variaciones
    variation_weight = 1.0 if i == 0 else 0.8

    # BM25 search con cada variación
    results = weaviate_search_with_variation(variation)
```

**Por qué se usa así**:

- Captura diferentes convenciones de nombres
- camelCase, snake_case, kebab-case
- Peso reducido evita ruido

### Filtros en Weaviate Queries

**Dónde se usa**: Todo search en Weaviate

**Ejemplo del código real**:

```python
where_conditions = []

if filters.file_path:
    where_conditions.append({
        "path": ["file_path"],
        "operator": "Equal",
        "valueString": filters.file_path,
    })

if filters.chunk_types:
    where_conditions.append({
        "path": ["chunk_type"],
        "operator": "In",
        "valueStringArray": [ct.upper() for ct in filters.chunk_types],
    })

# Combinar condiciones
if len(where_conditions) > 1:
    where_clause = {"operator": "And", "operands": where_conditions}
else:
    where_clause = where_conditions[0]

query_builder = query_builder.with_where(where_clause)
```

### Normalización de Scores

**Dónde se usa**: `/rag/retrieval/hybrid_search.py`

**Ejemplo del código real**:

```python
def _normalize_scores(self, results: List[ScoredChunk]) -> List[ScoredChunk]:
    if not results:
        return results

    scores = [r.score for r in results]
    max_score = max(scores)
    min_score = min(scores)

    # Si todos los scores son iguales
    if max_score == min_score:
        return [ScoredChunk(chunk=r.chunk, score=1.0) for r in results]

    # Normalizar a [0, 1]
    for result in results:
        normalized_score = (result.score - min_score) / (max_score - min_score)
        # ...
```

### Graph Expansion para Búsqueda

**Dónde se usa**: `/rag/retrieval/hybrid_search.py`

**Ejemplo del código real**:

```python
async def search_with_graph_expansion(self, query: str, expansion_depth: int = 2):
    # 1. Búsqueda inicial para "semillas"
    initial_results = await self.search(query, max_results // 3)

    # 2. Expandir via grafo neuronal
    graph = NeuralGraph()
    for scored_chunk in initial_results[:5]:  # Top 5 como semillas
        related_nodes = await graph.find_related(
            node=file_path,
            max_distance=expansion_depth,
            min_strength=0.3
        )

    # 3. Re-rankear por relevancia
    reranked = await self._rerank_by_relevance(query, all_chunks)
```

## 🚀 Patrones de Performance (Cache)

### LRU Cache con TTL

**Dónde se usa**: `/rag/retrieval/cache.py`

**Ejemplo del código real**:

```python
class SearchCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: OrderedDict[str, Tuple[List[Chunk], float]] = OrderedDict()

    def get(self, query: str, filters: Optional[Dict] = None):
        key = self._hash_query(query, filters)

        if key in self.cache:
            results, timestamp = self.cache[key]

            # Check TTL
            if time.time() - timestamp > self.ttl:
                del self.cache[key]
                return None

            # Move to end (LRU)
            self.cache.move_to_end(key)
            return results
```

**Por qué se usa así**:

- OrderedDict mantiene orden de inserción
- move_to_end() implementa LRU eficientemente
- TTL evita resultados obsoletos

### Cache Key Hashing

**Dónde se usa**: Todos los caches

**Ejemplo del código real**:

```python
def _hash_query(self, query: str, filters: Optional[Dict] = None) -> str:
    cache_input = f"{query}"
    if filters:
        # Sort keys para hashing consistente
        sorted_filters = sorted(filters.items())
        cache_input += f"|{sorted_filters}"

    return hashlib.md5(cache_input.encode()).hexdigest()
```

**Por qué se usa así**:

- MD5 rápido para keys de cache
- Sorted filters = hash determinístico
- No criptográfico, solo unicidad

### Invalidación por Patrón

**Dónde se usa**: Cache invalidation

**Ejemplo del código real**:

```python
def invalidate_by_file(self, file_path: str):
    keys_to_remove = []

    for key, (chunks, _) in self.cache.items():
        # Check si algún chunk es de este archivo
        if any(chunk.metadata.file_path == file_path for chunk in chunks):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del self.cache[key]
```

### Compression con Token Budget

**Dónde se usa**: `/rag/compression.py`

**Ejemplo del código real**:

```python
# Decidir si comprimir
if not self.compressor.should_compress(query, raw_chunks, token_budget):
    return raw_chunks[:max_chunks]

# Comprimir inteligentemente
compressed_chunks, result = self.compressor.compress_chunks(
    chunks=raw_chunks,
    query=query,
    token_budget=token_budget
)

# Cache resultados comprimidos separadamente
cache_key = f"compressed:{query}:{max_chunks}:{token_budget}"
self.cache.set(cache_key, compressed_chunks, filters_dict)
```

## 🔄 Patrones de Serialización

### JSON con datetime ISO

**Dónde se usa**: Toda serialización a BD

**Ejemplo del código real**:

```python
# En metadata
metadata = json.dumps({
    "session_type": "conversation",
    "created_at": datetime.now(timezone.utc).isoformat(),
})

# Pydantic ConfigDict
model_config = ConfigDict(
    json_encoders={
        datetime: lambda v: v.isoformat(),
        uuid.UUID: lambda v: str(v),
    }
)
```

**Por qué se usa así**:

- ISO 8601 es estándar universal
- timezone.utc evita ambigüedades
- Compatible con JavaScript/frontend

### Arrays JSON en SQLite

**Dónde se usa**: Listas en campos de BD

**Ejemplo del código real**:

```python
# Guardar
related_sessions = ["session1", "session2"]
json.dumps(related_sessions)

# Leer
related_ids: List[str] = json.loads(row["related_sessions"])

# Query con JSON
"json_extract(metadata, '$.status') != 'completed'"
```

### Compresión zlib para BLOBs

**Dónde se usa**: Dream insights, datos grandes

**Ejemplo del código real**:

```python
# Comprimir antes de guardar
data_json = json.dumps(large_data)
compressed = zlib.compress(data_json.encode(), level=9)

# Descomprimir al leer
decompressed = zlib.decompress(blob_data)
data = json.loads(decompressed.decode())
```

## 📁 Patrones de Archivos y I/O

### Path Validation Segura

**Dónde se usa**: TODO manejo de paths

**Ejemplo del código real**:

```python
try:
    # Resolve y verificar dentro del proyecto
    safe_path = file_path.relative_to(project_root)
except ValueError:
    raise SecurityError("Path traversal attempt detected")

# Verificar symlinks
if file_path.is_symlink():
    real_path = file_path.resolve(strict=True)
    try:
        real_path.relative_to(project_root)
    except ValueError:
        return {"status": "skipped", "reason": "symlink_outside_project"}
```

**Por qué se usa así**:

- relative_to() falla si path está fuera
- Symlinks pueden apuntar fuera del proyecto
- Seguridad incluso en sistema local

### Archivos Soportados Pattern

**Dónde se usa**: Indexación, chunking

**Ejemplo del código real**:

```python
# Extensiones completas soportadas
extensions = (
    # Código
    "py|js|ts|jsx|tsx|java|go|rs|rb|php|swift|kt|scala|r|m|mm|"
    "c|cpp|h|hpp|cs|sh|bash|zsh|"
    # Documentación
    "md|rst|txt|adoc|"
    # Configuración
    "json|yaml|yml|toml|ini|cfg|env|properties|xml|"
    # Datos
    "csv|sql"
)

file_pattern = rf"\b[\w\-\.]+\.(?:{extensions})\b"
```

## 📊 Patrones de Métricas y Monitoring

### MetricsCollector sin Namespace

**Dónde se usa**: TODOS los servicios

**Ejemplo del código real**:

```python
# Inicialización simple
self.metrics = MetricsCollector()

# Uso con prefijos en la métrica
self.metrics.increment("services.conversation_service.sessions_created")
self.metrics.gauge("services.task.task_context_size", len(sessions))
self.metrics.record("services.conversation_service.save_turn_time_ms", elapsed_ms)
```

**Por qué se usa así**:

- Sin namespace = más simple
- Prefijos en strings = agrupación lógica
- Compatible con sistemas de métricas estándar

### Logging estructurado con kwargs (NO f-strings)

**Dónde se usa**: TODOS los servicios, módulos y utilidades

**Ejemplo del código real**:

```python
# ✅ CORRECTO - Logging estructurado
logger.info("Procesando archivo", file_path=path, chunk_count=len(chunks))
logger.error("Error al procesar", error=str(e), file=path)

# ❌ INCORRECTO - NO usar f-strings en el mensaje principal del logger
logger.info(f"Procesando archivo {path} con {len(chunks)} chunks")
logger.error(f"Error al procesar {path}: {e}")
```

**Por qué se usa así**:

- Permite logging estructurado: los datos se pueden indexar y filtrar fácilmente
- Evita el coste de interpolar cadenas si el nivel de log no está activo
- Consistencia con el resto del proyecto
- Compatible con sistemas de logging avanzados y análisis de logs

### Performance Logging Pattern

**Dónde se usa**: Operaciones costosas

**Ejemplo del código real**:

```python
start_time = time.time()
try:
    # Operación costosa
    result = await expensive_operation()

    elapsed_ms = (time.time() - start_time) * 1000
    self.metrics.record("operation_time_ms", elapsed_ms)
    return result

except Exception as e:
    # Registrar tiempo incluso en error
    elapsed_ms = (time.time() - start_time) * 1000
    self.metrics.record("operation_time_ms", elapsed_ms)
    raise
```

## 🔄 Patrones de Concurrencia

### asyncio.gather con return_exceptions

**Dónde se usa**: Dream analyzers, operaciones paralelas

**Ejemplo del código real**:

```python
# Ejecutar análisis en paralelo
results = await asyncio.gather(
    self.analyze_bugs(code),
    self.analyze_security(code),
    self.analyze_performance(code),
    self.analyze_architecture(code),
    self.analyze_patterns(code),
    return_exceptions=True  # No fallar si uno falla
)

# Procesar resultados
for i, result in enumerate(results):
    if isinstance(result, Exception):
        logger.error(f"Analysis {i} failed", error=str(result))
        # Continuar con otros resultados
    else:
        insights.extend(result)
```

### Queue Pattern para WebSocket

**Dónde se usa**: API WebSocket

**Ejemplo del código real**:

```python
# Cada conexión tiene su queue
event_queue: asyncio.Queue[ProgressEvent] = asyncio.Queue()

# Producer
await event_queue.put(ProgressEvent(...))

# Consumer con timeout
while True:
    try:
        event = await asyncio.wait_for(event_queue.get(), timeout=0.5)
        await websocket.send_json(format_event(event))
    except asyncio.TimeoutError:
        # Permite heartbeat
        pass
```

## 🔌 Patrones de Integración Git

### GitPython Lazy Loading

**Dónde se usa**: `/services/git_service.py`

**Ejemplo del código real**:

```python
@lru_cache(maxsize=1)
def _get_repo(self) -> Repo:
    """Cache repo con TTL de 5 minutos."""
    try:
        repo = Repo(self.repo_path, search_parent_directories=False)
        # Verificar que es válido
        _ = repo.head.commit
        return repo
    except Exception as e:
        logger.error("Failed to open repository", error=str(e))
        raise ExternalServiceError(f"Git repository error: {e}")
```

**Por qué se usa así**:

- Repo object es pesado
- LRU cache evita recrearlo
- TTL previene datos obsoletos

### Git Diff Parsing

**Dónde se usa**: Análisis de cambios

**Ejemplo del código real**:

```python
# Obtener diff entre commits
diff = repo.git.diff(
    commit1.hexsha,
    commit2.hexsha,
    "--unified=3",  # Contexto de 3 líneas
    "--no-color"    # Sin ANSI codes
)

# Parsear cambios
for line in diff.split('\n'):
    if line.startswith('+') and not line.startswith('+++'):
        # Línea añadida
    elif line.startswith('-') and not line.startswith('---'):
        # Línea eliminada
```

## 🌐 Patrones de Servicios Externos

### Ollama Client con Retry

**Dónde se usa**: `/services/chat_service.py`

**Ejemplo del código real**:

```python
async def _call_ollama_with_retry(self, messages, max_tokens):
    for attempt in range(self.max_retries):
        try:
            response = await self.ollama.chat(
                model=self.model_name,
                messages=messages,
                options={"num_predict": max_tokens}
            )
            return response

        except httpx.TimeoutException:
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise ExternalServiceError("Ollama timeout after retries")
```

### Weaviate Health Check

**Dónde se usa**: Startup, health endpoints

**Ejemplo del código real**
