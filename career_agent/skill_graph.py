"""
Skill Dependency Graph.

Defines prerequisite relationships between skills.
Used by Skill Agent to identify blocking gaps.
"""

# Skill dependency graph: skill -> list of prerequisites
# If a user lacks a prerequisite, that skill is "blocked"
SKILL_DEPENDENCIES: dict[str, list[str]] = {
    # Programming fundamentals
    "algorithms": ["data_structures", "programming_basics"],
    "data_structures": ["programming_basics"],
    "system_design": ["algorithms", "databases", "networking"],
    
    # Web development
    "frontend_frameworks": ["html_css", "javascript"],
    "backend_frameworks": ["programming_basics", "databases"],
    "javascript": ["html_css", "programming_basics"],
    "typescript": ["javascript"],
    "react": ["javascript", "html_css"],
    "nodejs": ["javascript"],
    
    # Data & ML
    "machine_learning": ["python", "statistics", "linear_algebra"],
    "deep_learning": ["machine_learning", "python"],
    "data_analysis": ["python", "statistics"],
    "statistics": ["math_basics"],
    
    # Infrastructure
    "databases": ["programming_basics"],
    "sql": ["databases"],
    "nosql": ["databases"],
    "devops": ["linux", "git", "networking"],
    "docker": ["linux", "git"],
    "kubernetes": ["docker", "networking"],
    "cloud_services": ["networking", "linux"],
    
    # Core skills (no prerequisites)
    "programming_basics": [],
    "python": ["programming_basics"],
    "java": ["programming_basics"],
    "html_css": [],
    "git": [],
    "linux": [],
    "networking": [],
    "math_basics": [],
    "linear_algebra": ["math_basics"],
}

# Descriptions for why skills matter
SKILL_DESCRIPTIONS: dict[str, str] = {
    "programming_basics": "Write clean, maintainable code using core programming concepts like variables, loops, functions, and object-oriented principles.",
    "data_structures": "Understand arrays, linked lists, trees, hash maps, and when to use each for optimal performance.",
    "algorithms": "Master sorting, searching, recursion, and dynamic programming for efficient problem-solving.",
    "system_design": "Design scalable, distributed systems with considerations for load balancing, caching, and databases.",
    "git": "Version control essentials: branching, merging, rebasing, and collaboration workflows.",
    "databases": "Understand relational and NoSQL databases, data modeling, and query optimization.",
    "sql": "Write efficient queries, joins, aggregations, and understand indexing strategies.",
    "python": "Write clean Python for scripting, data processing, and backend development.",
    "javascript": "Build interactive web experiences with modern JavaScript (ES6+) features.",
    "machine_learning": "Understand supervised/unsupervised learning, model evaluation, and common algorithms.",
    "deep_learning": "Build neural networks using frameworks like TensorFlow or PyTorch.",
    "docker": "Containerize applications for consistent development and deployment environments.",
    "linux": "Navigate the command line, manage processes, and configure servers.",
    "statistics": "Apply probability, distributions, hypothesis testing for data-driven decisions.",
    "linear_algebra": "Master vectors, matrices, and linear transformations essential for ML.",
    "html_css": "Structure web pages and style them with modern CSS techniques.",
    "react": "Build component-based UIs with state management and hooks.",
    "nodejs": "Create server-side applications and APIs with JavaScript.",
    "networking": "Understand TCP/IP, HTTP, DNS, and how the internet works.",
    "cloud_services": "Deploy and manage applications on AWS, GCP, or Azure.",
    "devops": "Automate CI/CD pipelines, infrastructure as code, and monitoring.",
    "kubernetes": "Orchestrate containers at scale with deployments, services, and ingress.",
    "data_analysis": "Clean, explore, and visualize data to extract insights.",
}

# Curated learning resources for each skill
SKILL_RESOURCES: dict[str, list[dict]] = {
    "programming_basics": [
        {"type": "course", "title": "CS50: Introduction to Computer Science", "link": "https://cs50.harvard.edu", "level": "Beginner"},
        {"type": "course", "title": "freeCodeCamp - JavaScript Algorithms", "link": "https://freecodecamp.org", "level": "Beginner"},
    ],
    "python": [
        {"type": "course", "title": "Python for Everybody (Coursera)", "link": "https://coursera.org/specializations/python", "level": "Beginner"},
        {"type": "video", "title": "Corey Schafer Python Tutorials", "link": "https://youtube.com/@coreyms", "level": "Beginner"},
    ],
    "data_structures": [
        {"type": "course", "title": "NeetCode - Data Structures", "link": "https://neetcode.io", "level": "Intermediate"},
        {"type": "article", "title": "Visualgo - Visualize Algorithms", "link": "https://visualgo.net", "level": "Beginner"},
    ],
    "algorithms": [
        {"type": "course", "title": "Algorithms I & II (Princeton)", "link": "https://coursera.org/learn/algorithms-part1", "level": "Intermediate"},
        {"type": "tool", "title": "LeetCode", "link": "https://leetcode.com", "level": "Intermediate"},
    ],
    "git": [
        {"type": "course", "title": "Learn Git Branching (Interactive)", "link": "https://learngitbranching.js.org", "level": "Beginner"},
        {"type": "article", "title": "Pro Git Book", "link": "https://git-scm.com/book", "level": "Beginner"},
    ],
    "machine_learning": [
        {"type": "course", "title": "Andrew Ng's Machine Learning (Coursera)", "link": "https://coursera.org/learn/machine-learning", "level": "Intermediate"},
        {"type": "course", "title": "fast.ai - Practical Deep Learning", "link": "https://fast.ai", "level": "Intermediate"},
    ],
    "linear_algebra": [
        {"type": "course", "title": "3Blue1Brown - Essence of Linear Algebra", "link": "https://youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "level": "Beginner"},
        {"type": "course", "title": "Khan Academy - Linear Algebra", "link": "https://khanacademy.org/math/linear-algebra", "level": "Beginner"},
    ],
    "statistics": [
        {"type": "course", "title": "Khan Academy - Statistics", "link": "https://khanacademy.org/math/statistics-probability", "level": "Beginner"},
        {"type": "course", "title": "StatQuest with Josh Starmer", "link": "https://youtube.com/@statquest", "level": "Beginner"},
    ],
    "databases": [
        {"type": "course", "title": "SQLBolt - Interactive SQL Tutorial", "link": "https://sqlbolt.com", "level": "Beginner"},
        {"type": "course", "title": "Database Design (freeCodeCamp)", "link": "https://youtube.com/watch?v=ztHopE5Wnpc", "level": "Beginner"},
    ],
    "sql": [
        {"type": "course", "title": "SQLZoo Interactive Exercises", "link": "https://sqlzoo.net", "level": "Beginner"},
        {"type": "tool", "title": "Mode SQL Tutorial", "link": "https://mode.com/sql-tutorial", "level": "Intermediate"},
    ],
    "docker": [
        {"type": "course", "title": "Docker for Beginners (freeCodeCamp)", "link": "https://youtube.com/watch?v=fqMOX6JJhGo", "level": "Beginner"},
        {"type": "article", "title": "Docker Official Getting Started", "link": "https://docs.docker.com/get-started", "level": "Beginner"},
    ],
    "linux": [
        {"type": "course", "title": "Linux Journey", "link": "https://linuxjourney.com", "level": "Beginner"},
        {"type": "course", "title": "OverTheWire Bandit (CTF)", "link": "https://overthewire.org/wargames/bandit", "level": "Beginner"},
    ],
}

# Practice tasks for each skill
SKILL_PRACTICE: dict[str, list[str]] = {
    "programming_basics": [
        "Solve 10 easy problems on LeetCode",
        "Build a simple calculator CLI app",
        "Complete 5 coding challenges on Codewars",
    ],
    "python": [
        "Build a web scraper with BeautifulSoup",
        "Create a Flask REST API",
        "Automate a repetitive task with a Python script",
    ],
    "data_structures": [
        "Implement a linked list from scratch",
        "Solve 20 array/hashing problems on NeetCode",
        "Build a simple LRU cache",
    ],
    "algorithms": [
        "Solve 30 LeetCode mediums across categories",
        "Implement binary search variations",
        "Complete a graph traversal problem set",
    ],
    "git": [
        "Practice branching and merging on a sample repo",
        "Resolve a merge conflict intentionally",
        "Set up a GitHub Actions workflow",
    ],
    "machine_learning": [
        "Train a classifier on the Titanic dataset",
        "Build an end-to-end ML pipeline with scikit-learn",
        "Participate in a Kaggle competition",
    ],
    "linear_algebra": [
        "Implement matrix multiplication from scratch",
        "Visualize vector transformations in 2D",
        "Solve linear systems using NumPy",
    ],
    "statistics": [
        "Analyze a dataset and report findings",
        "Perform hypothesis testing on real data",
        "Calculate confidence intervals manually",
    ],
    "databases": [
        "Design a schema for an e-commerce app",
        "Normalize a denormalized dataset to 3NF",
        "Set up PostgreSQL locally and run queries",
    ],
    "sql": [
        "Solve 20 SQL problems on HackerRank",
        "Write complex JOINs across 3+ tables",
        "Optimize a slow query using EXPLAIN",
    ],
    "docker": [
        "Containerize an existing project",
        "Create a multi-container setup with docker-compose",
        "Deploy a container to a cloud service",
    ],
    "linux": [
        "Set up a Linux VM and configure SSH",
        "Write 5 bash scripts for automation",
        "Manage processes with systemd",
    ],
}


def get_prerequisites(skill: str) -> list[str]:
    """Get direct prerequisites for a skill."""
    return SKILL_DEPENDENCIES.get(skill, [])


def get_all_prerequisites(skill: str, visited: set[str] | None = None) -> set[str]:
    """Get all prerequisites recursively (transitive closure)."""
    if visited is None:
        visited = set()
    
    if skill in visited:
        return set()
    
    visited.add(skill)
    direct = set(get_prerequisites(skill))
    all_prereqs = direct.copy()
    
    for prereq in direct:
        all_prereqs |= get_all_prerequisites(prereq, visited)
    
    return all_prereqs


def get_skill_description(skill: str) -> str:
    """Get human-readable description of why a skill matters."""
    return SKILL_DESCRIPTIONS.get(skill, f"Important for career progression")


def get_skill_resources(skill: str) -> list[dict]:
    """Get curated learning resources for a skill."""
    return SKILL_RESOURCES.get(skill, [])


def get_skill_practice(skill: str) -> list[str]:
    """Get practice tasks for a skill."""
    return SKILL_PRACTICE.get(skill, [])

