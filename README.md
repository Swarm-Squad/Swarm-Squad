<div align="center">
   <a href="https://github.com/Sang-Buster/Swarm-Squad">
      <img src="https://raw.githubusercontent.com/Swarm-Squad/Swarm-Squad/refs/heads/main/src/swarm_squad/assets/favicon.png" width=20% alt="logo">
   </a>   
   <h1>Swarm Squad</h1>
   <h5>A simulation framework for multi-agent systems.</h5>
   <a href="https://swarm-squad.com/">
   <img src="https://img.shields.io/badge/Web-282c34?style=for-the-badge&logoColor=white" />
   </a> &nbsp;&nbsp;
   <a href="https://docs.swarm-squad.com/">
   <img src="https://img.shields.io/badge/Doc-282c34?style=for-the-badge&logoColor=white" />
   </a>
   <a href="https://docs.swarm-squad.com/gallery/">
   <img src="https://img.shields.io/badge/Demo-282c34?style=for-the-badge&logoColor=white" />
   </a>
</div>

---

<div align="center">
  <h2>✨ Key Features</h2>
</div>

<table align="center">
  <tr>
    <td><img src="https://raw.githubusercontent.com/Swarm-Squad/Swarm-Squad/refs/heads/main/src/swarm_squad/assets/screenshots/home.png" /></td>
    <td><img src="https://raw.githubusercontent.com/Swarm-Squad/Swarm-Squad/refs/heads/main/src/swarm_squad/assets/screenshots/nav.png" /></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Swarm-Squad/Swarm-Squad/refs/heads/main/src/swarm_squad/assets/screenshots/map.png" /></td>
    <td><img src="https://raw.githubusercontent.com/Swarm-Squad/Swarm-Squad/refs/heads/main/src/swarm_squad/assets/screenshots/data.png" /></td>
  </tr>
</table>

- **Agent Simulation:** Simulates multiple agents in a shared environment.
- **Scalability:** Handles large-scale agent simulations efficiently.
- **Behavior Specs:** Define and test agent behavior against expected outcomes.
- **Environment Modeling:** Build and manage physical or virtual environments.
- **Analytics:** Collect metrics on speed, coordination, and performance.
- **Customizable:** Easily extend agents, environments, and evaluation logic.
- **Visualization:** Real-time views and post-run reports of simulations.
- **Tool Integration:** Connect with RL libraries, protocols, or visual tools.
- **Versatile Agents:** Supports robots, drones, and autonomous vehicles.
- **Docs & Support:** Includes clear documentation and helpful resources.

---

<div align="center">
  <h2>🚀 Getting Started</h2>
</div>

It is recommended to use [uv](https://docs.astral.sh/uv/getting-started/installation/) to create a virtual environment and install the following package.

```bash
uv pip install swarm-squad
```

To run the application, simply type:

```bash
swarm-squad
# or
swarm-squad --help
```

---

<div align="center">
  <h2>👨‍💻 Development Setup</h2>
</div>

1. **Clone the repository and navigate to project folder:**

   ```bash
   git clone https://github.com/Sang-Buster/Swarm-Squad
   cd Swarm-Squad
   ```

2. **Install uv first:**

   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```powershell
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install the required packages:**
   **Option 1 (recommended):** Synchronizes environment with dependencies in pyproject.toml and uv.lock

   ```bash
   uv sync
   source .venv/bin/activate # .venv\Scripts\activate for Windows
   ```

   **Option 2 (manual):** Manual editable installation without referencing lockfile

   ```bash
   uv venv --python 3.10 # Create virtual environment
   source .venv/bin/activate # .venv\Scripts\activate for Windows
   uv pip install -e .
   ```

4. **Set up environment variables:**

   ```bash
   # Copy the example environment file
   cp .env.example .env
   ```

   - You can get a `MAPBOX_ACCESS_TOKEN` by signing up at https://www.mapbox.com/
   - Update the `OLLAMA_API_URL` if your Ollama instance is running on a different address
   - Update the `DATABASE_PATH` if you want to use a custom database file

5. **Install ruff and pre-commit:**

   ```bash
   uv pip install ruff pre-commit
   ```

   - `ruff` is a super fast Python linter and formatter.
   - `pre-commit` helps maintain code quality by running automated checks before commits are made.

6. **Install git hooks:**

   ```bash
   pre-commit install --install-hooks
   ```

   These hooks perform different checks at various stages:

   - `commit-msg`: Ensures commit messages follow the conventional format
   - `pre-commit`: Runs Ruff linting and formatting checks before each commit
   - `pre-push`: Performs final validation before pushing to remote

7. **Code Linting & Formatting:**

   ```bash
   ruff check --fix
   ruff check --select I --fix
   ruff format
   ```

8. **Run the application:**
   ```bash
   uv run src/swarm_squad/app.py
   ```

---

<div align="center">
  <h2>📝 File Structure</h2>
</div>

```text
📂Swarm Squad
 ┣ 📂src                         // Source Code
 ┃ ┗ 📦swarm_squad                  //
 ┃ ┃ ┣ 📂assets                     // Static assets (CSS, images, favicon, etc.)
 ┃ ┃ ┃ ┣ 📂css                      // CSS files
 ┃ ┃ ┃ ┣ 📂js                       // JavaScript files
 ┃ ┃ ┃ ┣ 📂models                   // Model files
 ┃ ┃ ┃ ┣ 📄favicon.ico              // Favicon
 ┃ ┃ ┃ ┗ 📄favicon.png              // Favicon
 ┃ ┃ ┣ 📂cli                        // CLI commands
 ┃ ┃ ┣ 📂components                 // Reusable UI components
 ┃ ┃ ┣ 📂data                       // Database files
 ┃ ┃ ┣ 📂pages                      // Page components and routing
 ┃ ┃ ┣ 📂scripts                    // Simulation and algorithm scripts
 ┃ ┃ ┣ 📂utils                      // Utility functions and helpers
 ┃ ┃ ┣ 📂cli                        // CLI commands
 ┃ ┃ ┣ 📄app.py                     // Entry point
 ┃ ┃ ┗ 📄core.py                    // Dash app core
 ┣ 📄.env.example                // Template for environment variables
 ┣ 📄.gitignore                  // Git ignore patterns (env, cache, database)
 ┣ 📄.pre-commit-config.yaml     // Pre-commit hooks (ruff, commit message)
 ┣ 📄.python-version             // Python version
 ┣ 📄LICENSE                     // MIT License
 ┣ 📄README.md                   // Project documentation
 ┣ 📄pyproject.toml              // Project configuration
 ┗ 📄uv.lock                     // Lock file
```
