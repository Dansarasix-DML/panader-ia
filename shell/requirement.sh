#!/bin/bash

rutaEntorno=~/env
aplicacion=app.py
REPO_URL="https://github.com/Dansarasix-DML/panader-ia.git"
BRANCH="main"

# Verificar si Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "⚠️ Python3 no está instalado. Instalándolo..."
    sudo apt update
    sudo apt install -y python3
else
    echo "✅ Python3 está instalado."
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "⚠️ Pip no está instalado. Instalándolo..."
    sudo apt install -y python3-pip
else
    echo "✅ Pip está instalado."
fi

# Verificar entorno virtual
if [ ! -d "$rutaEntorno" ]; then
    echo "⚠️ Entorno virtual no encontrado. Creando entorno virtual..."
    python3 -m venv "$rutaEntorno"
fi

# Activar entorno virtual y asegurar dependencias
echo "✅ Activando entorno virtual..."
source "$rutaEntorno/bin/activate"
pip install --upgrade pip
pip install python-dotenv requests Flask opencv-python Flask-SocketIO pipeline eventlet flask-cors python-telegram-bot pillow scikit-image torch torchvision transformers 

# Verificar si el repositorio ya existe
if [ ! -d "$rutaEntorno/panader-ia/.git" ]; then
    echo "⚠️ Repositorio no encontrado en la carpeta esperada. Clonando..."
    git clone "$REPO_URL" "$rutaEntorno/panader-ia"
    cd "$rutaEntorno/panader-ia"
    find .git/objects/ -type f -empty -delete
    git fetch --all
    git checkout "$BRANCH"
else
    echo "✅ Repositorio encontrado. Comprobando actualizaciones..."
    cd "$rutaEntorno/panader-ia"
    git fetch origin "$BRANCH"

    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/$BRANCH)

    if [ "$LOCAL_COMMIT" == "$REMOTE_COMMIT" ]; then
        echo "✅ Tu proyecto ya está actualizado."
    else
        echo "⚠️ Se encontraron cambios en el repositorio remoto. Actualizando..."
        git reset --hard origin/$BRANCH
        git pull origin "$BRANCH"
        echo "✅ Proyecto actualizado."
    fi
fi

# Ejecutar la aplicación en el entorno virtual
echo "🚀 Iniciando aplicación..."
python3 "$aplicacion"
