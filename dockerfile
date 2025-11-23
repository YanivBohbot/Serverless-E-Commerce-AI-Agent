FROM public.ecr.aws/lambda/python:3.11

# 1. Installation des outils de base (GCC) pour éviter les erreurs de compilation
RUN yum update -y && \
    yum install -y gcc make openssl-devel && \
    yum clean all

# 2. Mise à jour de pip
RUN pip install --upgrade pip

# 3. Copie des requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# 4. INSTALLATION PROPRE
# --target : Place les fichiers au bon endroit pour Lambda (Règle l'erreur "No module named langchain")
# On retire --only-binary pour laisser pip se débrouiller (évite le blocage)
RUN pip install \
    --target "${LAMBDA_TASK_ROOT}" \
    -r requirements.txt

# 5. Copie du code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# 6. Démarrage
CMD [ "src.lambda_handler.lambda_handler" ]