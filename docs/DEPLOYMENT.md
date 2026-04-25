# EDR System Deployment Guide

This guide covers deploying the Automated EDR system in various environments.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Production Hardening](#production-hardening)

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/automated-edr.git
cd automated-edr

# Run setup script
./setup.sh        # Linux/macOS
.\setup.bat       # Windows

# Start the system
python main.py --frontend
```

### Manual Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies (optional)
cd frontend && npm install && cd ..

# Set environment variables
export EDR_SESSION_SECRET="$(openssl rand -hex 32)"

# Start backend
python main.py

# In another terminal, start frontend (optional)
cd frontend && npm run dev
```

---

## Docker Deployment

### Single Container (Backend Only)

```bash
# Build image
docker build -f backend/Dockerfile -t automated-edr:latest .

# Run container
docker run -d \
  --name edr-backend \
  -p 8000:8000 \
  -e EDR_SESSION_SECRET="your-secret-here" \
  -e EDR_AUTO_START_AGENT=true \
  -v edr-data:/app/backend/data \
  automated-edr:latest
```

### Docker Compose (Full Stack)

```bash
# Copy environment file
cp .env.example .env

# Update .env with your configuration
# nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Docker Compose with Production Settings

```yaml
version: '3.8'

services:
  backend:
    image: automated-edr:latest
    container_name: edr-backend
    ports:
      - "8000:8000"
    environment:
      - EDR_SESSION_SECRET=${EDR_SESSION_SECRET}
      - EDR_COOKIE_SECURE=true
      - EDR_AUTO_START_AGENT=true
    volumes:
      - edr-data:/app/backend/data
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - edr-network

  frontend:
    image: automated-edr-frontend:latest
    container_name: edr-frontend
    ports:
      - "80:5173"
    environment:
      - VITE_API_URL=https://your-domain.com
    depends_on:
      - backend
    restart: always
    networks:
      - edr-network

volumes:
  edr-data:
    driver: local

networks:
  edr-network:
    driver: bridge
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Docker registry for images

### Build and Push Images

```bash
# Build backend image
docker build -f backend/Dockerfile -t your-registry/edr-backend:0.3.0 .
docker push your-registry/edr-backend:0.3.0

# Build frontend image
docker build -f frontend/Dockerfile -t your-registry/edr-frontend:0.3.0 frontend/
docker push your-registry/edr-frontend:0.3.0
```

### Kubernetes Manifests

**Namespace**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: edr-system
```

**ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: edr-config
  namespace: edr-system
data:
  EDR_AUTO_START_AGENT: "true"
  EDR_COOKIE_SECURE: "true"
```

**Secret**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: edr-secret
  namespace: edr-system
type: Opaque
stringData:
  EDR_SESSION_SECRET: "your-generated-secret-here"
```

**Backend Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edr-backend
  namespace: edr-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: edr-backend
  template:
    metadata:
      labels:
        app: edr-backend
    spec:
      containers:
      - name: backend
        image: your-registry/edr-backend:0.3.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: edr-config
        - secretRef:
            name: edr-secret
        volumeMounts:
        - name: edr-data
          mountPath: /app/backend/data
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: edr-data
        persistentVolumeClaim:
          claimName: edr-data-pvc
```

**Backend Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: edr-backend-service
  namespace: edr-system
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: edr-backend
```

**Frontend Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edr-frontend
  namespace: edr-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: edr-frontend
  template:
    metadata:
      labels:
        app: edr-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/edr-frontend:0.3.0
        ports:
        - containerPort: 5173
        env:
        - name: VITE_API_URL
          value: "https://your-domain.com"
        livenessProbe:
          httpGet:
            path: /
            port: 5173
          initialDelaySeconds: 10
          periodSeconds: 30
```

**Frontend Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: edr-frontend-service
  namespace: edr-system
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 5173
  selector:
    app: edr-frontend
```

**Ingress**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: edr-ingress
  namespace: edr-system
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    secretName: edr-tls-cert
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: edr-backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: edr-frontend-service
            port:
              number: 80
```

**Persistent Volume**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: edr-data-pvc
  namespace: edr-system
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Deploy to Kubernetes

```bash
# Create namespace and secrets
kubectl create namespace edr-system
kubectl create secret generic edr-secret \
  --from-literal=EDR_SESSION_SECRET=$(openssl rand -hex 32) \
  -n edr-system

# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n edr-system
kubectl get svc -n edr-system
kubectl get ingress -n edr-system
```

---

## Cloud Platforms

### AWS

#### Using Elastic Container Service (ECS)

1. Push images to ECR
2. Create task definitions
3. Create ECS service
4. Configure load balancer (ALB/NLB)
5. Set up RDS for database (optional)

#### Using Elastic Beanstalk

```bash
# Deploy with EB CLI
eb init -p docker automated-edr
eb create edr-env
eb deploy
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/edr-backend

# Deploy to Cloud Run
gcloud run deploy edr-backend \
  --image gcr.io/PROJECT-ID/edr-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars EDR_SESSION_SECRET=your-secret
```

#### Using GKE (Google Kubernetes Engine)

```bash
# Create GKE cluster
gcloud container clusters create edr-cluster

# Deploy using kubectl (same as above Kubernetes deployment)
kubectl apply -f k8s/
```

### Microsoft Azure

#### Using Azure Container Instances (ACI)

```bash
# Push to Azure Container Registry
az acr build --registry myregistry --image edr-backend:latest .

# Deploy container
az container create \
  --resource-group mygroup \
  --name edr-backend \
  --image myregistry.azurecr.io/edr-backend:latest \
  --environment-variables \
    EDR_SESSION_SECRET=your-secret \
    EDR_AUTO_START_AGENT=true \
  --ports 8000
```

#### Using Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create --resource-group mygroup --name edr-cluster

# Get credentials
az aks get-credentials --resource-group mygroup --name edr-cluster

# Deploy
kubectl apply -f k8s/
```

---

## Production Hardening

### Security Best Practices

1. **Change Default Credentials**
   ```bash
   # Create admin user
   python -c "from backend.edr.auth import hash_password, new_user_id; ..."
   ```

2. **Enable HTTPS**
   ```bash
   # Set secure cookie flag
   EDR_COOKIE_SECURE=true
   
   # Use valid SSL certificate
   ```

3. **Set Strong Session Secret**
   ```bash
   EDR_SESSION_SECRET=$(openssl rand -hex 32)
   ```

4. **Configure CORS Properly**
   ```bash
   EDR_FRONTEND_ORIGINS=https://yourdomain.com
   ```

5. **Enable Database Backups**
   ```bash
   # Backup SQLite database
   cp backend/data/edr.db backup/edr-$(date +%Y%m%d).db
   ```

6. **Monitor Logs**
   ```bash
   # Check application logs
   docker logs edr-backend
   
   # Check system logs
   journalctl -u docker.service
   ```

7. **Set Resource Limits**
   ```yaml
   resources:
     limits:
       cpu: "1"
       memory: "512Mi"
     requests:
       cpu: "500m"
       memory: "256Mi"
   ```

8. **Enable Network Policies** (Kubernetes)
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: edr-network-policy
   spec:
     podSelector:
       matchLabels:
         app: edr-backend
     policyTypes:
     - Ingress
     - Egress
   ```

### Monitoring & Logging

1. **Application Monitoring**
   - Use Prometheus for metrics
   - Use Grafana for dashboards
   - Set up alerts for critical events

2. **Log Aggregation**
   - Use ELK Stack (Elasticsearch, Logstash, Kibana)
   - Or use cloud-native solutions (CloudWatch, Stackdriver, etc.)

3. **Health Checks**
   - Regular health checks via `/api/health`
   - Monitor database connectivity
   - Check file system access

### Backup & Disaster Recovery

1. **Database Backups**
   ```bash
   # Daily automated backup
   0 2 * * * cp /app/backend/data/edr.db /backups/edr-$(date +\%Y\%m\%d).db
   ```

2. **Configuration Backups**
   ```bash
   # Backup rules and settings
   tar -czf rules-backup.tar.gz backend/config/
   ```

3. **Disaster Recovery Plan**
   - Document backup procedures
   - Test restore processes regularly
   - Maintain offsite backups

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs edr-backend

# Verify image exists
docker images | grep edr

# Rebuild image
docker build -f backend/Dockerfile -t automated-edr:latest .
```

### Connection Refused
```bash
# Check if port is available
lsof -i :8000

# Kill process using port
kill -9 <PID>

# Check firewall rules
sudo iptables -L
```

### Database Issues
```bash
# Verify database exists
ls -lah backend/data/edr.db

# Reset database (WARNING: deletes data)
rm backend/data/edr.db
```

### Performance Issues
```bash
# Monitor resource usage
docker stats edr-backend

# Check database size
du -sh backend/data/

# Archive old data (implement retention)
```

---

## Support & Questions

For deployment issues, refer to:
- [README.md](../README.md) - General documentation
- [Main Repository](https://github.com/yourusername/automated-edr) - Issues tracker
- [Documentation Wiki](https://github.com/yourusername/automated-edr/wiki)
