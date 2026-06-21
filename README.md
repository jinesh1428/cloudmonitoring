# ☁️ Cloud Infrastructure Monitoring & Auto-Deployment System

A cloud-native monitoring and CI/CD deployment platform built on **Google Cloud Platform (GCP)**. The system continuously tracks VM resource utilization (CPU, RAM, Disk), visualizes it on a live web dashboard, raises threshold alerts through **Google Cloud Pub/Sub**, and auto-deploys application updates via **GitHub Actions** and **Docker**.

![Final Dashboard Working](images/09-final-system-working.png)
*Final dashboard rendering live metrics served from inside a Docker container on the GCP VM.*

---

## 📌 Project Info

| | |
|---|---|
| **Author** | jinesh (Roll No. 25104B2007) manasvi (Roll No. 25104B2002)|
| **Repository** | [github.com/Jinesh1421/CloudMonitoring](https://github.com/Jinesh1421/CloudMonitoring) |
| **Cloud Platform** | Google Cloud Platform (Compute Engine) |
| **OS** | Ubuntu 22.04 LTS |

---

## 🎯 Objective

To design and implement a cloud-native monitoring and deployment platform that:

- Continuously monitors VM resource utilization (CPU, RAM, Disk)
- Displays metrics through a live, auto-refreshing web dashboard
- Publishes threshold-based alerts via Google Cloud Pub/Sub
- Automatically deploys application updates using GitHub Actions and Docker

---

## 🛠️ Tech Stack

`Google Cloud Platform` · `Ubuntu VM` · `Linux Administration` · `Python` · `Flask` · `psutil` · `Docker` · `Git & GitHub` · `GitHub Actions` · `Google Cloud Pub/Sub` · `Cron Jobs` · `JSON` · `Bootstrap`

---

## 🏗️ System Architecture

```
                    ┌──────────────────┐
                    │   Cron Job (1m)  │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │   monitor.py     │  (psutil: CPU / RAM / Disk)
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │   data.json      │
                    └────────┬─────────┘
                ┌────────────┴────────────┐
                ▼                         ▼
      ┌──────────────────┐     ┌───────────────────────┐
      │  Flask Dashboard  │     │  Threshold Check       │
      │  (Bootstrap UI,   │     │  → Pub/Sub Topic       │
      │  auto-refresh 5s) │     │  → Subscriber → Alert  │
      └────────┬──────────┘     └───────────────────────┘
               ▼
      ┌──────────────────┐
      │  Docker Container │  (volume-mounted to host data.json)
      └──────────────────┘

CI/CD:  Git Push → GitHub Actions → SSH into VM → Git Pull → Docker Rebuild → Container Restart
```

**Layers:**
1. **Monitoring Layer** – `monitor.py` collects CPU/RAM/Disk via `psutil` and writes to `data.json`.
2. **Visualization Layer** – Flask reads `data.json` and renders a Bootstrap dashboard with progress bars, auto-refreshing every 5 seconds.
3. **Alerting Layer** – When thresholds are breached, an alert is published to a Pub/Sub topic and consumed by a subscriber.
4. **Deployment Layer** – GitHub Actions SSHes into the VM on every push to `main`, pulls the latest code, rebuilds the Docker image, and restarts the container.

---

## 🚧 Implementation Journey

### Phase 1 — Cloud Platform Selection

The project initially started on **AWS EC2 (Amazon Linux)**, but ran into package-management friction (`apt` vs `yum`/`dnf`, missing `pip3`, missing `psutil`, inconsistent versions). The project was migrated to **GCP** on an **Ubuntu 22.04 LTS, e2-micro** instance for smoother compatibility with course tooling.

### Phase 2 — VM Environment Setup

Provisioned the Compute Engine VM, configured SSH access, and installed Python3, pip, Git, and Docker.

| Challenge | Resolution |
|---|---|
| Docker permission errors | Added user to the `docker` group |
| Package/dependency issues | Verified installs manually, one by one |

### Phase 3 — Monitoring Script (`monitor.py`)

Built using `psutil.cpu_percent()`, `psutil.virtual_memory()`, and `psutil.disk_usage()`, writing output to `monitor/data.json`:

```json
{
  "cpu": 50.0,
  "ram": 26.1,
  "disk": 48.3
}
```

| Challenge | Resolution |
|---|---|
| `ModuleNotFoundError: psutil` | Installed via pip |
| File path / location mismatches | Standardized project structure, used absolute paths |

### Phase 4 — Flask Dashboard (first version)

A minimal Flask app reading `data.json` and rendering plain HTML:

![Flask app.py source](images/02-flask-app-code.png)
*Early version of `app.py` — note the relative path `../monitor/data.json`, which later caused a 500 error.*

![Basic dashboard output](images/01-dashboard-basic.png)
*First successful dashboard render, accessed via the VM's public IP on port 5000.*

#### 🐞 Debugging the 500 Internal Server Error

Running the Flask app from a different working directory broke the relative path to `data.json`, throwing a `FileNotFoundError` baked inside a 500 response:

![500 error traceback in SSH terminal](images/03-500-error-debug.png)
*Two SSH-in-browser panes used side-by-side: left shows `curl localhost:5000` returning a 500 page; right shows the full Flask traceback — `FileNotFoundError: [Errno 2] No such file or directory: '../monitor/data.json'`.*

**Root cause:** relative path resolution depends on the *current working directory* the process was launched from, not the script's location.
**Fix:** switched to dynamic, absolute path resolution using `os.path.join()` / `os.path.dirname(__file__)`.

#### Other Issues Hit Along the Way

| Issue | Cause | Fix |
|---|---|---|
| `Address already in use` on port 5000 | A Docker container was already bound to port 5000 | Found the culprit with `sudo ss -tulpn \| grep 5000`, stopped it |
| `python: command not found` | Ubuntu ships Python3 only | Used `python3` explicitly |
| `SyntaxError` on Flask import | Typo in import statement | Corrected `from flask import Flask` |

### Phase 5 — Automation with Cron

Configured a cron job to run `monitor.py` every minute so `data.json` stays fresh without manual intervention:

```
* * * * * cd /home/nirajpawar981/CloudMonitoring/monitor && /usr/bin/python3 monitor.py >> cron.log 2>&1
```

![Editing crontab in nano via SSH](images/04-cron-automation.png)
*Editing the crontab through `crontab -e` over SSH-in-browser. Logging output to `cron.log` was added after the dashboard appeared to stop updating, to confirm the job was actually firing.*

| Challenge | Resolution |
|---|---|
| `new crontab file is missing newline before EOF` | Added a trailing newline; later used direct command-based cron install |
| Dashboard values appeared frozen | Cron failures were silent — added `>> cron.log 2>&1` to surface errors and confirm successful runs |

### Phase 6 — Bootstrap Dashboard UI

Upgraded the plain-HTML dashboard to a Bootstrap-based UI with colored progress bars and 5-second auto-refresh:

![Bootstrap dashboard with progress bars](images/08-bootstrap-dashboard.png)
*Upgraded dashboard — CPU, RAM, and Disk shown as color-coded Bootstrap progress bars, refreshing automatically.*

### Phase 7 — Docker Containerization

Wrote a `Dockerfile`, built the image, and ran the Flask dashboard inside a container (`cloud-monitor-container`), verified with `docker ps`.

**A subtler bug surfaced here:** the `Dockerfile`'s `COPY` instruction only copies `data.json` at *build time*, so the container's copy diverged from the host's copy as cron kept updating the host file.

**Fix:** replaced the static copy with a **Docker volume mount**:

```bash
-v /home/nirajpawar981/CloudMonitoring/monitor:/app/monitor
```

This bind-mounts the host's `monitor/` directory straight into the container, so every cron-driven update is reflected in the dashboard instantly — no rebuild required.

### Phase 8 — Google Cloud Pub/Sub Alerting

Set up a Pub/Sub **topic** (`cloud-monitor-alerts`) and **subscription** (`cloud-monitor-sub`) so `monitor.py` can publish an alert whenever a threshold is breached, picked up by a subscriber process.

![Pub/Sub subscription details](images/05-pubsub-subscription.png)
*`cloud-monitor-sub` — a Pull-type subscription attached to the `cloud-monitor-alerts` topic, shown active in the GCP console.*

#### IAM & Service Account Configuration

A dedicated service account (`cloud-monitor-sa`) was created and granted the **Pub/Sub Publisher** and **Pub/Sub Subscriber** IAM roles so `monitor.py` could authenticate and publish/consume messages without using a personal account:

![Service account IAM roles](images/06-service-account-iam.png)
*IAM role assignment for `cloud-monitor-sa` — Publisher and Subscriber roles granted at the project level.*

| Challenge | Resolution |
|---|---|
| Permission Denied / insufficient OAuth scope | Granted explicit Publisher/Subscriber roles to the service account |
| Credential path issues | Set `GOOGLE_APPLICATION_CREDENTIALS` to point at the downloaded service account key |

### Phase 9 — Networking & Firewall

Port `5000` (used by Flask/Docker) wasn't reachable externally by default on GCP, so a custom **VPC firewall rule** was created to allow ingress traffic on `tcp:5000`:

![Firewall rule allow-5000 created](images/07-firewall-rule.png)
*Custom ingress firewall rule `allow-5000` permitting `tcp:5000` from all IP ranges, alongside GCP's default rules (SSH, RDP, HTTP/HTTPS, ICMP).*

### Phase 10 — GitHub Actions CI/CD

Automated the deployment pipeline so every push to `main` triggers:

```
Developer Push → GitHub Repository → GitHub Actions
   → SSH into GCP VM → Git Pull → Docker Rebuild → Container Restart
```

| Challenge | Resolution |
|---|---|
| `ssh.ParsePrivateKey: ssh: no key found` | Regenerated SSH key pair; added private key to GitHub Secrets, public key to `authorized_keys` |
| `sudo: a password is required` | Removed unneeded `sudo` calls — the deploy user was already in the `docker` group |
| YAML indentation errors in `deploy.yml` | Carefully corrected spacing per YAML syntax rules |

GitHub Secrets configured: `VM_HOST`, `VM_USER`, `VM_SSH_KEY`.

### Phase 11 — Final Verification

End-to-end test confirming the monitoring script runs cleanly, writes fresh metrics, and the dashboard reflects them live through the Docker volume mount:

![Final end-to-end test in SSH terminal and browser](images/09-final-system-working.png)
*Right pane: `python3 monitor/monitor.py` executes successfully (`CPU Usage: 1.0%`, `RAM Usage: 27.3%`, `Disk Usage: 51.0%`, `System Healthy — No Alert Generated`). Left pane: the same values rendered live on the Bootstrap dashboard.*

---

## 🐛 Major Errors Encountered & Resolved

| # | Error | Root Cause | Fix |
|---|---|---|---|
| 1 | `FileNotFoundError` reading `data.json` | Relative path broke when run from a different CWD | Absolute path resolution via `os.path` |
| 2 | Flask `500 Internal Server Error` | Same root cause as above, surfaced as an unhandled exception | Same fix + better error visibility |
| 3 | Docker container showing stale metrics | `COPY` only runs at image build time | Switched to a Docker volume mount |
| 4 | `Address already in use` on port 5000 | An existing Docker container already bound the port | Identified via `ss -tulpn`, stopped the conflicting container |
| 5 | GitHub Actions SSH failure | Malformed/missing private key in GitHub Secrets | Regenerated key pair, reconfigured secrets |
| 6 | GitHub Actions YAML errors | Indentation mistakes in `deploy.yml` | Corrected YAML spacing |
| 7 | Pub/Sub Permission Denied / scope errors | Service account lacked Publisher/Subscriber roles | Granted IAM roles explicitly |
| 8 | Cron job not updating `data.json` | Cron failures were silent | Added logging (`>> cron.log 2>&1`) to confirm execution |
| 9 | `new crontab file is missing newline before EOF` | Crontab file lacked trailing newline | Added newline, reinstalled crontab |
| 10 | `python: command not found` | Ubuntu ships only `python3` | Used `python3` explicitly |

---

## ✅ Outcome

The completed system:

- Continuously monitors CPU, RAM, and Disk usage on a GCP VM
- Displays live metrics on an auto-refreshing Bootstrap dashboard
- Publishes/consumes threshold alerts through Google Cloud Pub/Sub
- Runs inside a Docker container, kept in sync with the host via a volume mount
- Redeploys automatically on every push via a GitHub Actions CI/CD pipeline
- Is reachable externally through a custom GCP firewall rule on port 5000

This project demonstrates practical, hands-on experience across **Linux administration, GCP VM management, Python scripting, monitoring automation, Docker containerization, CI/CD pipelines, event-driven architecture (Pub/Sub), and general DevOps debugging**.

---

## 📚 Key Learning Outcomes

- Linux server administration and process debugging
- Cloud VM provisioning and networking (GCP Compute Engine, VPC firewalls)
- Building monitoring tools with Python and `psutil`
- Task scheduling and automation with cron
- Git/GitHub version control and CI/CD with GitHub Actions
- Flask web application development
- Docker containerization, including the host-vs-container data sync pitfall
- Event-driven design using Google Cloud Pub/Sub
- Systematic debugging using logs, tracebacks, and terminal tools

---

## 🔮 Planned Next Steps

- [ ] Docker Compose for multi-container orchestration
- [ ] Telegram/email alert notifications on threshold breach
- [ ] HTTPS termination (reverse proxy via Nginx)
- [ ] Persistent metrics history (time-series storage) instead of single-point `data.json`
- [ ] Unit tests for `monitor.py` and the Flask routes

---

## 📂 Repository Structure

```
CloudMonitoring/
├── monitor/
│   ├── monitor.py        # Collects CPU/RAM/Disk metrics
│   └── data.json         # Latest metrics snapshot
├── dashboard/
│   ├── app.py             # Flask app serving the dashboard
│   └── templates/         # Bootstrap UI templates
├── Dockerfile
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD pipeline definition
└── README.md
```

---

*Report compiled from project logs, terminal sessions, and console screenshots captured during development on GCP.*
