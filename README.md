# ir-example

Originalmente hay una carpeta de dataset/ que contiene el archivo zip

Requisitos previos:

- Tener python instalado en el sistema.
- Tener python-venv instalado en el sistema.
- Usar un sistema que admita make command.
- Se trabaja con el dataset tal cual se descarga de Kaggle: podcastreviews.zip guardado en una carpeta dataset/ por defecto (esta ruta se puede dar como argumento de entrada).
- Se explora el dataset directamente con duckdb porque: es pequeño <10 GB y estamos suponiendo una maquina grande de un solo core, no procesamiento en paralelo ni por batches.
- Utilizamos una conexión de forma persistente al fichero que contiene la database. Esto es debido a que así podemos utilizar la función de duckdb que permite Larger-than-memory workloads are supported by spilling to disk to a tmp file.
- Old database storage version, upgrade it is essential.
- Desechamos resultados sin average_rating ni scraped_at
- No tengo en cuenta el lenguaje de la database, supongo que todo esta en ingles.
- Ojo con la memoria RAM, aqui se requieren 4GB para GoogleNews y otros 2 GB para jugar con el dataset.
- Descargarse la version de vectores [GoogleNews-vectors-negative300.bin.gz](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing)
- El tiempo en procesamiento es un gran handdicap, pero son 160000 textos que pasar a un vector_dict
- El scrapeo se produjo durante los dias 2019-07-07, 2019-07-08 y 2019-07-09. Mejor seria utilizar fechas de creacion de reviews.
- Se filtra con --min_score 3 --max_date 2019-07-09
- Añadidos test unitarios donde se mockean integraciones.
- Añadido test end2end donde se testea la funcionalidad, integracion y respuesta. No se pueden comprobar resultados exactos puesto que la naturaleza del algoritmo Retrieval no es deterministica. Si se cambia para serlo, se podrían probar dichas respuestas.
- Si quieres probarlo localmente, utilizando el comando "make" directamente en la CLI se muestran todas las opciones de ejecucion. Son automaticas.
- Metodos async solo para endpoint.

## Consideraciones del código actual

- Tanto la librería como la api están metidas juntas. En un proyecto serio se separarían, pero aquí he querido meter todo en el mismo repo.
- Ejemplo de llamada local:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/search/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "I want to listen to a podcast about entertainment industry, focusing on videogames", 
  "top_n": 5,
  "min_score": 3.0,
  "max_score": 5.0,
  "min_date": "2019-07-07", 
  "max_date": "2019-07-09",
  "boost_mode": true,
  "verbose": false
}'
```
- ¿Cómo funciona el workflow? Requiere de conexión con kaggle para bajarse el dataset automáticamente. Para no compartir secretos, en caso de hacer un fork del repo, habría que añadir las variables KAGGLE_USERNAME y KAGGLE_KEY como secrets en tu repositorio forkeado para que funcione. Estas se sacan de generar una API KEY en Kaggle.
- El workflow ejecuta las fases de ci del proyecto, ejecutando el test end2end para comprobar que todo funcione correctamente antes de cualquier subida al repo.


## TODOs

- La logica de procesamiento es lenta. Lo mas lento es volver a cargar los ficheros (esto se puede tener precargado para inferencias y mejorar el tiempo de respuesta). Lo mismo con los diccionarios generados para el modelo. En este ejemplo básico no he entrado en esta parte de optimización.
- Metricas y logs de rendimiento del sistema. A futuro hay que añadir metricas de utilizacion y rendimiento del endpoint.
- tener gestión de excepciones y mappear las excepciones de tu servicio, repositorios en el controller a errores HTTP.
- añadir un prometheus + grafana + opentelemetry para ver los métricas y logs.
- autenticación, seguridad de usuarios.
- En los workflows de github actions se podría extender para montar también la imagen y subirla a un registry privado, desde donde desplegar el servidor. Fase de deployment.
