# Student Marks — hands-on Docker and CI/CD lab

**Goal:** Use a tiny Python web app to learn Linux terminal commands, automated tests, Docker image/container/ports, Git, and GitHub Actions CI. Plan ~2 hours for basic lab, ~3–4 hours including GitHub and troubleshooting.

> This is a **learning project**. The workflow performs **CI plus a temporary container smoke test on GitHub's runner**; it **does not** deploy to a permanent production server. An **optional, manual** workflow can publish the built image to GitHub Container Registry (GHCR), but that does not start a live website. The app uses Python's built-in `http.server` to avoid external packages, not a hardened production web server.

## Prerequisites

- Laptop with Python 3.12+ (works with other modern Python 3 versions), Git, Docker Desktop (or Docker Engine).
- GitHub account for the CI portion.
- No AWS, paid cloud account, pip dependencies, or credit card needed.

In your terminal/PowerShell check:

```bash
python --version
git --version
docker --version
docker info
```

If `docker info` fails, start Docker Desktop/Engine.

## Files

```text
devops-student-marks/
  app.py                      # Python app: /, /health and /grade, port 5000
  Dockerfile                  # Docker image recipe
  tests/test_app.py           # 6 unit + HTTP tests
  .dockerignore               # Unneeded source excluded from Docker build
  .gitignore                  # Cache files ignored by Git
  .github/workflows/ci.yml    # GitHub Actions CI pipeline
  .github/workflows/publish-image.yml # optional manual image release
```

## Stage 1 — Local Python app and tests (20–35 min)

Unzip the project, open terminal **inside** `devops-student-marks` and run:

```bash
python -m unittest discover -s tests -v
python app.py
```

On Windows, substitute `py -3` for `python` if needed. On some macOS/Linux installations, use `python3`.

Open **http://localhost:5000**, then enter `85` (Pass) and `49` (Fail). Try `http://localhost:5000/health`, which returns `{"status":"ok"}`. Press Ctrl+C in terminal to stop the server.

**Concept:** `unittest` is an automated test framework. Tests are a quality gate before Docker packaging.

## Stage 2 — Build image and run container (35–50 min)

Make sure Docker is running. In project directory:

```bash
docker build -t student-marks:v1 .
docker images
docker run -d --name student-marks -p 127.0.0.1:8000:5000 student-marks:v1
docker ps
```

Open **http://localhost:8000**. The **host** port is **8000** and the **container** port is **5000**; app still listens on 5000 *inside* the container.

Explore in terminal:

```bash
docker logs student-marks
curl http://localhost:8000/health
curl 'http://localhost:8000/grade?marks=85'
docker stop student-marks
docker rm student-marks
```

For Windows PowerShell, `curl.exe http://localhost:8000/health` avoids the built-in `curl` alias on older PowerShell versions.

If host port 8000 is busy, use **9000** on left: `-p 127.0.0.1:9000:5000`, then browse `localhost:9000`. The `127.0.0.1` host binding keeps it accessible locally, not to everyone on your network.

## Stage 3 — GitHub Actions automated CI (40–60 min)

1. On GitHub create a **new empty repository** named `student-marks-devops`. Do **not** initialize it with a README because you already have files.
2. From the project directory run:

```bash
git init -b main
git add .
git commit -m "First Docker and CI pipeline"
git remote add origin https://github.com/YOUR_USERNAME/student-marks-devops.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. GitHub authentication may be required.

3. In GitHub open the repo → **Actions** → **Python tests and Docker smoke test**. The workflow should run automatically after your push. It performs:

```text
GitHub push
   ↓
Checkout source
   ↓
Set up Python 3.12
   ↓
Run six automated tests   ← QUALITY GATE
   ↓ (only if tests pass)
Build Docker image
   ↓
Start Docker container on temporary GitHub runner
   ↓
HTTP smoke tests for /health and /grade
   ↓
Clean up runner container
```

The green check indicates this CI pipeline succeeded. If tests fail, later steps are skipped. **The temporary runner deployment is a smoke test, not deployment to a permanent public website.**

## Stage 4 — See a failing CI pipeline yourself (20–35 min)

1. In `app.py`, change the pass cutoff from `>= 50` to `>= 60` but **don't change tests yet**.
2. Run `python -m unittest discover -s tests -v`. The `test_pass_boundary` check will fail.
3. Commit and push the changed code:

```bash
git add app.py
git commit -m "Practice failing CI quality gate"
git push
```

4. In GitHub → Actions, observe the red failed job and logs. Docker build/container steps will not execute.
5. Restore cutoff to `>= 50`, commit and push. It should return to a green run.

## Extra exercise — Two containers, one image (10 min)

After stopping/removing previous container:

```bash
docker run -d --name marks-a -p 127.0.0.1:8000:5000 student-marks:v1
docker run -d --name marks-b -p 127.0.0.1:8001:5000 student-marks:v1
docker ps
```

Open both `localhost:8000` and `localhost:8001`. Both containers listen on **5000 internally**, but each host port is different. Clean up:

```bash
docker rm -f marks-a marks-b
```


## Optional Stage 5 — Deliver a Docker image to GitHub (30–45 min)

If you want to practice the **delivery** side as well, open GitHub repository → **Actions** → **Optional manual release to GitHub Container Registry** → **Run workflow**. This step **publishes** the Docker image to GHCR **only when you manually start it**. It requires GitHub Actions and package publishing permission.

The workflow runs tests first, builds the image, authenticates using GitHub's built-in `GITHUB_TOKEN`, then publishes an image named like `ghcr.io/YOUR_USERNAME/student-marks-devops:latest`. GitHub container packages are private by default, so do not assume an unauthenticated `docker pull` will work. Publishing an image is **Continuous Delivery (manual release)**, not Continuous Deployment to a production server. Check your account's package limits before using registry storage.

**Important:** No AWS account or permanent server is required. Don't put API keys in code or Git commits.

Official guide: https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions

## Key concepts

- **Linux terminal:** run commands, navigate project and inspect processes. GitHub's `ubuntu-latest` runner is Linux.
- **Dockerfile:** instructions to create an image.
- **Docker image:** packaged Python runtime + app file.
- **Container:** isolated runtime instance of the image.
- **Port mapping:** host `8000` → container `5000`.
- **Git:** version control; **GitHub:** repository/automation platform.
- **CI:** continuously run tests/build checks on changes.
- **CD:** release/delivery automation. Optional GHCR workflow publishes an image with a manual trigger; **neither workflow deploys to a permanent production service**.

## Troubleshooting

- **`docker: command not found`:** install Docker and reopen terminal.
- **Cannot connect to Docker daemon:** start Docker Desktop/Engine.
- **`python` not found:** macOS/Linux often uses `python3`, Windows can use `py -3`.
- **Port already occupied:** change host port or stop app currently using it.
- **Container exited:** use `docker logs student-marks`.
- **Actions unavailable:** check repository Actions settings and organization restrictions.
- **Git `Author identity unknown`:** set `git config --global user.name "Your Name"` and `git config --global user.email "your-email@example.com"`.

## Official documentation

- https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/
- https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/
- https://docs.github.com/en/actions/tutorials/build-and-test-code/python
