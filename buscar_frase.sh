#!/bin/bash

# Comprobamos que el usuario haya ingresado la frase
if [ $# -lt 1 ]; then
    echo "Por favor, ingresa la frase que deseas buscar."
    echo "Uso: ./buscar_frase.sh 'tu frase'"
    exit 1
fi

# La frase que se va a buscar
frase=$1

# Mostramos que estamos comenzando la búsqueda
echo "Buscando '$frase' en archivos HTML..."

# Usamos find para recorrer solo los archivos con extensión .html en el directorio actual y subdirectorios
# y luego usamos grep para buscar la frase dentro de esos archivos.
# -n: Muestra el número de línea.
# -H: Muestra el nombre del archivo.
# -r: Recurre en subdirectorios.
# -name "*.html": Filtra para buscar solo archivos .html

find ./ -type f -name "*.html" | while read archivo; do
    echo "Buscando en archivo: $archivo"
    # Ejecutamos grep en el archivo actual
    grep -nH "$frase" "$archivo"
done

# Si grep no encuentra la frase, informamos al usuario
if [ $? -ne 0 ]; then
    echo "No se encontró la frase '$frase' en ningún archivo HTML."
fi
