<div align="center">
   <a href="https://github.com/Sang-Buster/Swarm-Squad">
      <img src="/src/assets/favicon.ico" width=20% alt="logo">
   </a>   
   <h1>Swarm Squad</h1>
   <h5>A simulation framework for multi-agent systems.</h5>
   <a href="https://swarm-squad.vercel.app/">
   <img src="https://img.shields.io/badge/Web-282c34?style=for-the-badge&logoColor=white" />
   </a> &nbsp;&nbsp;
   <a href="https://swarm-squad-doc.vercel.app/">
   <img src="https://img.shields.io/badge/Doc-282c34?style=for-the-badge&logoColor=white" />
   </a>
</div>

---

<div align="center">
  <h2>✨ Key Features</h2>
</div>

1. **Agent Simulation:** Swarm Squad allows you to simulate the behavior of multiple agents in a controlled environment. This is essential for testing how agents interact with each other and their environment.

2. **Scalability:** It should be able to handle a large number of agents simultaneously. This is important for testing the system's performance under various load conditions.

3. **Behavior Specification:** Swarm Squad may include a way to define and specify the expected behavior of agents. This can be used to evaluate whether the agents are acting as intended.

4. **Environment Modeling:** It provides tools for creating and managing the environment in which the agents operate. This could be a physical or virtual space with obstacles, goals, or other entities.

5. **Metrics and Analytics:** The framework likely offers mechanisms for collecting and analyzing data on agent behavior. This could include metrics like speed, coordination, efficiency, or any other relevant performance indicators.

6. **Customization and Extensibility:** It should allow users to customize and extend the framework to suit their specific needs. This might involve adding new types of agents, modifying the environment, or defining custom evaluation criteria.

7. **Visualization and Reporting:** Swarm Squad may include tools for visualizing the simulation in real-time or for generating reports after a simulation run. This helps in understanding and communicating the results.

8. **Integration with Other Tools:** It may have the capability to integrate with other software or libraries commonly used in multi-agent systems development, such as reinforcement learning libraries, communication protocols, or visualization tools.

9. **Support for Various Types of Agents:** Swarm Squad should be versatile enough to support different types of agents, such as robots, drones, and autonomous vehicles.

10. **Documentation and Support:** Proper documentation and support resources are essential for users to effectively utilize the framework.

---

<div align="center">
  <h2>🚀 Getting Started</h2>
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

3. **Create a virtual environment at `Swarm-Squad/.venv/`:**
   ```bash
   uv venv --python 3.12.1
   ```

4. **Activate the virtual environment:**
   ```bash
   # macOS/Linux
   source .venv/bin/activate
   ```

   ```powershell
   # Windows
   .venv\Scripts\activate
   ```

5. **Install the required packages:**
   ```bash
   uv pip install -r requirements.txt
   ```

<div align="center">
  <h2>👨‍💻 Development Setup</h2>
</div>

1. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp .env_example .env
   ```
   Then edit `.env` and add your configurations:
   ```
   MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
   OLLAMA_API_URL=http://localhost:11434
   ```
   - You can get a Mapbox access token by signing up at https://www.mapbox.com/
   - Update the `OLLAMA_API_URL` if your Ollama instance is running on a different address

2. **Install ruff and pre-commit:**
   ```bash
   uv pip install ruff pre-commit
   ```
   - `ruff` is a super fast Python linter and formatter.
   - `pre-commit` helps maintain code quality by running automated checks before commits are made.

3. **Install git hooks:**
   ```bash
   pre-commit install --hook-type commit-msg --hook-type pre-commit --hook-type pre-push
   ```

   These hooks perform different checks at various stages:
   - `commit-msg`: Ensures commit messages follow the conventional format
   - `pre-commit`: Runs Ruff linting and formatting checks before each commit
   - `pre-push`: Performs final validation before pushing to remote
  
4. **Code Linting:**
   ```bash
   ruff check
   ruff check --fix
   ruff check --select I
   ruff check --select I --fix
   ruff format
   ```

5. **Run the application:**
   ```bash
   python src/app.py
   ```

---

<div align="center">
  <h2>📝 File Structure</h2>
</div>

```text
📦Swarm Squad
 ┣ 📂src                         // Source Code
 ┃ ┣ 📂assets                       // Static assets (CSS, images, favicon, etc.)
 ┃ ┣ 📂components                   // Reusable UI components
 ┃ ┣ 📂data                         // Database files
 ┃ ┣ 📂pages                        // Page components and routing
 ┃ ┣ 📂scripts                      // Simulation and algorithm scripts
 ┃ ┣ 📂util                         // Utility functions and helpers
 ┃ ┗ 📄app.py                       // Main Dash application entry point
 ┣ 📄.env_example                // Template for environment variables
 ┣ 📄.gitignore                  // Git ignore patterns (env, cache, database)
 ┣ 📄.pre-commit-config.yaml     // Pre-commit hooks (ruff, commit message)
 ┣ 📄.pre-commit_msg_template.py // Commit message format validator
 ┣ 📄LICENSE                     // MIT License
 ┣ 📄README.md                   // Project documentation
 ┗ 📄requirements.txt            // Python dependencies
```