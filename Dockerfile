# Utiliser une image de base avec Python 3.10
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . .

# Installer les dépendances système nécessaires (comme Git)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python directement dans l'environnement global du conteneur
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Exposer le port sur lequel le dashboard sera accessible
EXPOSE 8050

# Commande par défaut pour lancer le dashboard
CMD ["python", "main.py"]