
SKILLS_DB = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
        "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
        "MATLAB", "Perl", "Objective-C", "Dart", "Shell Scripting", "Bash"
    ],
    "Web & Frontend": [
        "HTML", "CSS", "React", "Angular", "Vue.js", "Next.js", "Svelte",
        "Redux", "Tailwind CSS", "Bootstrap", "jQuery", "Webpack", "SASS"
    ],
    "Backend & Frameworks": [
        "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "Ruby on Rails", "ASP.NET", "GraphQL", "REST API", "Microservices",
        "gRPC"
    ],
    "Data Science & ML": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
        "OpenCV", "Data Visualization", "Statistics", "A/B Testing",
        "Feature Engineering", "MLOps", "LLM", "Generative AI", "Hugging Face"
    ],
    "Data & Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra",
        "Elasticsearch", "Data Warehousing", "ETL", "Apache Spark",
        "Apache Kafka", "Hadoop", "Snowflake", "BigQuery", "Airflow",
        "dbt", "Data Modeling"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "CI/CD", "Ansible", "Linux", "Nginx", "Prometheus",
        "Grafana", "CloudFormation", "Serverless"
    ],
    "Mobile": [
        "Android", "iOS", "React Native", "Flutter", "SwiftUI", "Xamarin"
    ],
    "Design & Product": [
        "Figma", "UI/UX Design", "Wireframing", "Adobe XD", "Sketch",
        "Product Management", "User Research", "Prototyping"
    ],
    "Business & Analytics": [
        "Excel", "Power BI", "Tableau", "Google Analytics", "SEO",
        "Financial Modeling", "Salesforce", "SAP", "Jira", "Confluence",
        "Business Analysis", "Project Management", "Agile", "Scrum",
        "Six Sigma", "Stakeholder Management"
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Adaptability",
        "Negotiation", "Mentoring", "Public Speaking", "Collaboration"
    ],
    "Security": [
        "Cybersecurity", "Penetration Testing", "OWASP", "Network Security",
        "Cryptography", "SOC 2", "ISO 27001", "Identity Management"
    ],
}

# Flat lookup list of every known skill (used for fast scanning)
ALL_SKILLS = sorted({skill for group in SKILLS_DB.values() for skill in group})

# Reverse map: skill -> category, useful for grouping results in the UI
SKILL_TO_CATEGORY = {
    skill: category
    for category, skills in SKILLS_DB.items()
    for skill in skills
}

DEGREE_KEYWORDS = [
    "PhD", "Ph.D", "Doctorate", "Master", "M.Tech", "M.S.", "MS ", "MBA",
    "Bachelor", "B.Tech", "B.E.", "B.Sc", "BCA", "MCA", "Associate Degree",
    "High School Diploma"
]

# A distinct color per category, used to color-code skill pills in the UI.
# Chosen to be visually distinct from each other (not a single-hue ramp).
CATEGORY_COLORS = {
    "Programming Languages": "#3B82F6",   # blue
    "Web & Frontend": "#EC4899",          # pink
    "Backend & Frameworks": "#8B5CF6",    # violet
    "Data Science & ML": "#14B8A6",       # teal
    "Data & Databases": "#0EA5E9",        # sky
    "Cloud & DevOps": "#F97316",          # orange
    "Mobile": "#22C55E",                  # green
    "Design & Product": "#D946EF",        # fuchsia
    "Business & Analytics": "#EAB308",    # yellow
    "Soft Skills": "#64748B",             # slate
    "Security": "#EF4444",                # red
}
DEFAULT_CATEGORY_COLOR = "#64748B"

