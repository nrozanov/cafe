# Cafe
A test task to implement a server emulating a coffee shop.

## Task Description

Your task is to implement an HTTP server that emulates a coffee shop using FastAPI. The server should not use any external services, databases, queues, or buses.

The server must support three essential routes:

- `/order/`: Clients order an americano here.
- `/start/`: Baristas start brewing coffee here.
- `/finish/`: Baristas declare the coffee ready here.

### Details

- The shop only serves one type of coffee: americano. Clients order it by sending a POST request to `/order/`. The server must respond with a `200 OK` status code when the coffee is ready.
- Clients are ready to wait indefinitely for their coffee at `/order/`.
- Client requests may come in groups of 100-200.
- Clients and workers should interact with different FastAPI servers on separate ports within the same Python application.
- The service should be protected from a DDoS attack from a single IP address.

### Example Workflow

- **Client**: Sends a POST request to `/order/` and waits for a `200 OK` response when their americano is ready.
- **Worker**: Checks the queue with GET `/start/`, picks up the oldest order, starts making it, and then calls POST `/finish/` once done.

## How to Run

Follow these steps to run the coffee shop server:

1. Run `docker-compose up -d`.
2. Verify that you can access [http://localhost:8080/api/v1/client/docs](http://localhost:8080/api/v1/client/docs).
3. To shut down the application, run `docker-compose down`.

## How to Test

1. Initialize the virtual environment: `python3.10 -m venv cafe-test-venv`.
2. Activate it: `source cafe-test-venv/bin/activate.sh`.
3. Install test dependencies: `pip install -r requirements.txt`.
4. Start test workers: `./test_worker.py 10`.
5. Send multiple order requests:

    ```bash
    for i in {1..200}
    do
        curl -v 'http://localhost:8080/api/v1/client/order/' &
    done
    ```

### Running Tests Locally

To run tests locally, execute the following commands:

```bash
cd client_service/; python -m pytest; cd -;
cd worker_service/; python -m pytest; cd -;
```