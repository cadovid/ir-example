# ir-example

Originalmente hay una carpeta de dataset/ que contiene el archivo zip

Requisitos previos:

- Tener python instalado en el sistema.
- Tener python-venv instalado en el sistema.
- Usar un sistema que admita make command.
- Se trabaja con el dataset tal cual se descarga de Kaggle: archive.zip guardado en una carpeta dataset/ por defecto (esta ruta se puede dar como argumento de entrada)
- Se explora el dataset directamente con duckdb porque: es pequeño <10 GB y estamos suponiendo una maquina grande de un solo core, no procesamiento en paralelo ni por batches.
- Utilizamos una conexión de forma persistente al fichero que contiene la database. Esto es debido a que así podemos utilizar la función de duckdb que permite Larger-than-memory workloads are supported by spilling to disk to a tmp file.
- Old database storage version, upgrade it is essential.
- Desechamos resultados sin average_rating ni scraped_at
- No tengo en cuenta el lenguaje de la database, supongo que todo esta en ingles.
- Ojo con la memoria RAM, aqui se requieren 4GB para GoogleNews y otros 2 GB para jugar con el dataset.
- Descargarse la version de vectores [GoogleNews-vectors-negative300.bin.gz](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing)
- El tiempo en procesamiento es un gran handdicap, pero son 160000 textos que pasar a un vector_dict
