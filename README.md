# QueryJet: A Lightning-Fast Blog API

QueryJet is a high-performance, scalable blog API designed for efficient submission and search of blog posts. It showcases a modern microservices architecture, leveraging asynchronous processing and robust search capabilities to deliver a responsive user experience.

---

## ✨ Features

* **FastAPI Backend:** Built with FastAPI for high-performance and easy-to-define API endpoints.
* **Asynchronous Task Processing:** Uses Celery to offload heavy operations (like indexing) to background workers, ensuring the API remains responsive.
* **Reliable Message Broker:** Integrates RabbitMQ as a robust message queue for Celery, guaranteeing task delivery and processing.
* **Powerful Full-Text Search:** Employs Elasticsearch for rapid and efficient indexing and retrieval of blog posts with advanced search functionalities.
* **Containerized Development:** Utilizes Docker Compose for a consistent and easily reproducible local development environment.
* **Kubernetes Ready:** Designed with Kubernetes deployment in mind, including YAML configurations for production-grade orchestration (optional demo).

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* [Docker](https://www.docker.com/get-started) (Docker Desktop or Docker Engine)
* `curl` (for API testing, or you can use Postman/Insomnia)

### Local Development with Docker Compose

This is the quickest way to get QueryJet running locally.

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/chickenleaf/queryjet.git](https://github.com/chickenleaf/queryjet.git) 
    cd queryjet
    ```

2.  **Build and start services:**
    This command will build the Docker images and start all the services defined in `docker-compose.yml`. This might take a few minutes on the first run.

    ```bash
    sudo docker compose up --build -d
    ```

3.  **Verify services are running:**

    ```bash
    sudo docker compose ps
    ```
    You should see `rabbitmq`, `elasticsearch`, `celery_worker`, and `api` listed as `Up`.

4.  **Optional: Check service health (after a short wait for services to initialize):**

    * **RabbitMQ Management UI:**
        ```bash
        echo "RabbitMQ Management UI: http://localhost:15672 (guest/guest)"
        ```
    * **Elasticsearch Health:**
        ```bash
        curl http://localhost:9200/_cluster/health?pretty
        ```
        (Expect status `green` or `yellow`)

---

## 💡 Usage

Once the services are up, you can interact with the QueryJet API. The FastAPI application will be accessible at `http://localhost:8000`.

### Submitting a Blog Post

Blog posts are submitted asynchronously. The API will return a `task_id` immediately, and the actual indexing into Elasticsearch will happen in the background via Celery.

```bash
# Submit your first blog post
curl -X POST "http://localhost:8000/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "My First FastAPI Blog", "blog_text": "This is a test blog post for demonstration purposes.", "user_id": "user123"}' | tee submit_response_1.json

# Submit a second blog post
curl -X POST "http://localhost:8000/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "Understanding Celery & RabbitMQ", "blog_text": "Celery is a powerful distributed task queue. RabbitMQ is a robust message broker.", "user_id": "user456"}' | tee submit_response_2.json
```

### Checking Task Status

You can check the status of a background indexing task using the `task_id` returned from the submission endpoint.

First, extract a `task_id` from one of your submission responses (e.g., `submit_response_1.json`):

```bash
TASK_ID=$(cat submit_response_1.json | grep -o '"task_id": "[^"]*"' | cut -d '"' -f 4)
echo "Checking status for task_id: $TASK_ID"
```

Then, query the status endpoint:

```bash
curl "http://localhost:8000/task_status/$TASK_ID"
# Keep running this command until the status changes to "completed"
```

### Searching for Blog Posts

Once blog posts are indexed, you can perform full-text searches.

```bash
curl "http://localhost:8000/search?query=FastAPI"
echo ""
curl "http://localhost:8000/search?query=Elasticsearch"
echo ""
curl "http://localhost:8000/search?query=test blog"
echo ""
curl "http://localhost:8000/search?query=RabbitMQ"
echo ""
```

### API Health Checks

You can verify the connectivity of the API to its dependencies:

```bash
curl http://localhost:8000/health/elasticsearch
curl http://localhost:8000/health/rabbitmq
```

---

## 🛠️ Project Structure

```
.
├── celery_tasks/             # Celery application setup and background tasks
│   ├── celery_app.py         # Celery instance configuration
│   └── tasks.py              # Celery tasks (e.g., indexing blog posts)
├── kubernetes/               # Kubernetes deployment configurations (optional)
│   ├── ...                   # YAML files for deployments, services, configmaps
├── search_blog/              # Search API module
│   └── search.py             # FastAPI endpoint for searching blogs
├── submit_blog/              # Submit API module
│   └── submit.py             # FastAPI endpoint for submitting blogs
├── docker-compose.yml        # Orchestrates all services for local development
├── main.py                   # Main FastAPI application entry point
├── requirements.txt          # Python dependencies
└── ...                       # Other project files (tests, Dockerfiles per service)
```

---

## 🧹 Cleanup

To stop and remove all Docker Compose services and their associated networks:

```bash
sudo docker compose down
# Optional: To also remove Elasticsearch data volumes
# sudo docker volume rm queryjet_esdata
```

---

## ☁️ Kubernetes Deployment (Optional)

QueryJet is also designed for deployment on Kubernetes for production-grade orchestration, showcasing robust communication between microservices. The `kubernetes/` directory contains all necessary YAML configurations.

### Deploying to Kubernetes

**(Requires a running Kubernetes cluster, e.g., MiniKube or Docker Desktop's Kubernetes enabled)**

1.  **Verify Kubernetes cluster info:**

    ```bash
    kubectl cluster-info
    ```

2.  **Apply Kubernetes manifests:**

    ```bash
    kubectl apply -f kubernetes/configmap.yaml
    kubectl apply -f kubernetes/services.yaml
    kubectl apply -f kubernetes/rabbitmq-deployment.yaml
    kubectl apply -f kubernetes/elasticsearch-deployment.yaml
    kubectl apply -f kubernetes/celery-tasks-deployment.yaml
    kubectl apply -f kubernetes/submit-blog-deployment.yaml
    kubectl apply -f kubernetes/search-blog-deployment.yaml
    ```

3.  **Check deployment status:**

    ```bash
    kubectl get pods
    kubectl get svc
    ```

4.  **Accessing the API in Kubernetes:**
    * If using **Ingress**: Get the Ingress IP (`kubectl get ingress`) and use the configured paths.
    * If **port-forwarding**:
        ```bash
        kubectl port-forward service/submit-blog-service 8001:80 &
        kubectl port-forward service/search-blog-service 8002:80 &
        ```
        Then use `http://localhost:8001/submit_blog` and `http://localhost:8002/search?query=...`

### Cleaning Up Kubernetes Resources

```bash
kubectl delete -f kubernetes/submit-blog-deployment.yaml
kubectl delete -f kubernetes/search-blog-deployment.yaml
kubectl delete -f kubernetes/celery-tasks-deployment.yaml
kubectl delete -f kubernetes/elasticsearch-deployment.yaml
kubectl delete -f kubernetes/rabbitmq-deployment.yaml
kubectl delete -f kubernetes/services.yaml
kubectl delete -f kubernetes/configmap.yaml
# Optional: If you created persistent volumes, you might need to delete them explicitly
# kubectl delete pvc <your-pvc-name>
```

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions or find issues, please open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details (you might want to add a LICENSE file to your repo).

---
