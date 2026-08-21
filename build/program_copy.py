"""Clean program-page copy for the six live programs. Replaces scraped SCAI sections."""

from __future__ import annotations

PROGRAM_COPY = {
    "prog-data-analytics": {
        "title": "Data Analytics with AI — AI Career Academy",
        "description": "Live 5-month analyst sequence: Excel, SQL, Python, and Power BI. Copilot for spreadsheets and dashboards. Published fee ₹40,000. Book a 15-minute career call.",
        "hero_title": "Data Analytics with AI",
        "hero_sub": "A 5-month live sequence for people who need to turn tables into decisions. Stack: Excel, SQL, Python for analysis, and Power BI as the dashboard tool. We do not teach Tableau on this program. Fee is published on this page. A career call tells you if this is the right next move.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Excel for cleaning, pivots, and stakeholder sheets. SQL to pull and join data. Python (Pandas) for EDA you cannot do in a spreadsheet. Power BI for interactive dashboards and DAX — this is the only BI visualizer on the catalog. Copilot and NLQ as accelerators on Excel and Power BI, not as a replacement for knowing the data.",
            },
            {
                "heading": "Who it is for",
                "content": "Career switchers and early analysts who need a job-shaped stack, not a data-science degree. If you already want models, RAG, or Kubernetes, this is the wrong slab — look at Data Science Gen AI, Gen AI for Developers, or MLOps.",
            },
            {
                "heading": "Career support",
                "content": "This program includes placement support, a course certificate, and internship opportunities. Portfolio work (SQL cases, Power BI dashboards, Python EDA) is what we review with you on a career call. Power BI is a skill — not an offer letter by itself.",
            },
        ],
        "faqs": [
            {"question": "Is Power BI the only dashboard tool?", "answer": "Yes. This is the catalog’s only BI visualizer track. We teach Power BI (and Excel charts). We do not teach Tableau here."},
            {"question": "What is the fee and duration?", "answer": "₹40,000, one-time, for a 5-month live cohort. EMI is discussed on the career call if you need it."},
            {"question": "Do you offer placement, a certificate, and internships?", "answer": "Yes. Placement support, a course certificate, and internship opportunities are part of the program. Resume and interview practice when you are actually applying."},
        ],
        "related": [
            {"slug": "data-science-course", "title": "Data Science Gen AI"},
            {"slug": "ai-developers-course", "title": "Gen AI for Developers"},
        ],
    },
    "prog-data-science": {
        "title": "Data Science Gen AI — AI Career Academy",
        "description": "Live 6-month data science sequence: Python, SQL, statistics, machine learning, deep learning, and LLM/RAG foundations. Charts in Matplotlib and Seaborn — not Power BI. Fee ₹55,000.",
        "hero_title": "Data Science Gen AI",
        "hero_sub": "A 6-month live sequence from Python and SQL into machine learning, then enough deep learning and LLM/RAG to talk to a hiring manager without pretending this is a GenAI specialization. Visualization is Matplotlib and Seaborn. Power BI and Tableau are not on this syllabus — those live on Data Analytics with AI.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Python, NumPy, Pandas, SQL, statistics and hypothesis tests, scikit-learn (regression through gradient boosting), neural-net foundations, NLP essentials, and a grounded intro to LLMs and RAG. You plot in Python. You ship a small FastAPI or notebook-to-script workflow. You do not sit in a Power BI classroom.",
            },
            {
                "heading": "Who it is for",
                "content": "People aiming at data scientist / ML-adjacent titles who can commit six months. If you only need dashboards, take Data Analytics. If you already ship software and want RAG apps, take Gen AI for Developers.",
            },
            {
                "heading": "Career support",
                "content": "Placement support, a course certificate, and internship opportunities are included. U.S. BLS demand on the homepage is not your Indian CTC. Discounted fee on this page is ₹55,000 (listed ₹65,000 minus ₹10,000) — that is the number we stand behind today.",
            },
        ],
        "faqs": [
            {"question": "Do you teach Power BI or Tableau?", "answer": "No. Charts here are Matplotlib and Seaborn. Power BI lives only on Data Analytics with AI."},
            {"question": "What is the fee and duration?", "answer": "₹55,000 after the published ₹10,000 off from ₹65,000. Duration is 6 months, live."},
            {"question": "Is this the same as Gen AI Specialization?", "answer": "No. This is data science (stats + ML) with an LLM/RAG intro. Gen AI Specialization goes deeper on transformers, fine-tuning, and serving."},
        ],
        "related": [
            {"slug": "data-analytics-course-with-placement", "title": "Data Analytics with AI"},
            {"slug": "generative-ai-course", "title": "Gen AI Specialization"},
        ],
    },
    "prog-ai-developers": {
        "title": "Gen AI for Developers — AI Career Academy",
        "description": "Live 3-month path for software engineers: LLM APIs, RAG, tool-using agents, FastAPI, and a deployed capstone. Fee ₹40,000. Not a Power BI or data-science course.",
        "hero_title": "Gen AI for Developers",
        "hero_sub": "Three months, live, for people who already write software. You build RAG search, tool-using agents, FastAPI services, a thin UI, and a capstone you can explain. This is not analyst training and not MLOps.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "LLM APIs and structured outputs. Chunking, embeddings, retrieval, and evaluation of answers. Agents with tool calls and memory. Packaging with FastAPI plus Streamlit or Gradio. Tracing and a deploy you can demo. No Excel, no Power BI, no model-training track.",
            },
            {
                "heading": "Who it is for",
                "content": "Backend, frontend, and full-stack engineers adding AI features to products. If you need to train and fine-tune models, use Gen AI Specialization. If you need production ML pipelines, use MLOps.",
            },
            {
                "heading": "Career support",
                "content": "A three-month cohort does not make you an ML researcher. You do get placement support, a course certificate, and internship opportunities. The fee is ₹40,000, one-time, as published.",
            },
        ],
        "faqs": [
            {"question": "Do I need a data-science background?", "answer": "You need to already write software. This is APIs, RAG, and agents — not Excel or Power BI."},
            {"question": "What is the fee and duration?", "answer": "₹40,000, one-time, for 3 months live."},
            {"question": "How is this different from Gen AI Specialization?", "answer": "This slab ships apps. Specialization goes into model internals, fine-tuning, and multimodal systems."},
        ],
        "related": [
            {"slug": "generative-ai-course", "title": "Gen AI Specialization"},
            {"slug": "llmops-course", "title": "LLMOps"},
        ],
    },
    "prog-generative-ai": {
        "title": "Generative AI Specialization | AI Career Academy",
        "description": "Live 5-month Generative AI course covering transformers, RAG, LoRA/QLoRA, multimodal models, agents, quantization, and serving. Fee ₹64,999.",
        "hero_title": "Generative AI Specialization",
        "hero_sub": "Five months live from model foundations to shipping GenAI systems: transformers and LLMs, RAG design, fine-tuning (LoRA/QLoRA), multimodal workflows, agents, quantization, and serving. Deeper than Gen AI for Developers. Not a Power BI class.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Attention, tokenization, and how modern LLMs behave. RAG patterns with evaluation. Fine-tuning and when prompting is enough. Vision-language and multimodal pipelines. Tool-using agents. Quantization and API serving. PyTorch / Hugging Face style work — not Excel dashboards.",
            },
            {
                "heading": "Who it is for",
                "content": "Developers and ML learners who want system depth, not only app glue. Freshers can start if they will do the Python/ML foundation modules. If you only want to call APIs and ship a RAG UI, Gen AI for Developers is the shorter slab.",
            },
            {
                "heading": "Career support",
                "content": "Fee is ₹64,999 one-time. Duration on this catalog is 5 months. Placement support, a course certificate, and internship opportunities are included — we will not promise a research-scientist title.",
            },
        ],
        "faqs": [
            {"question": "Is this a dashboard or Power BI course?", "answer": "No. Power BI is only on Data Analytics with AI."},
            {"question": "What is the fee and duration?", "answer": "₹64,999, one-time, 5 months live."},
            {"question": "Should I take Gen AI for Developers instead?", "answer": "If you mainly want to call APIs and ship a RAG UI, take the 3-month developer slab. Take this if you want model and system depth."},
        ],
        "related": [
            {"slug": "ai-developers-course", "title": "Gen AI for Developers"},
            {"slug": "llmops-course", "title": "LLMOps"},
        ],
    },
    "prog-mlops": {
        "title": "MLOps — AI Career Academy",
        "description": "Live 6-month MLOps sequence: Docker, versioning, CI/CD for ML, Kubernetes serving, monitoring and drift. Fee ₹60,000. Grafana for ops — not Power BI.",
        "hero_title": "MLOps",
        "hero_sub": "Six months live for people who can already train a model and now need to ship it: data and model versioning, containers, CI/CD gates, Kubernetes serving, monitoring, and drift response. Observability is Prometheus/Grafana-style — not Power BI.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Git/DVC, MLflow tracking and registry, Docker, training pipelines with eval gates, Kubernetes for services, FastAPI/TorchServe-style serving, drift and incident habits. Optional mapping onto SageMaker / Azure ML / Vertex after the core patterns. No analyst visualizer stack.",
            },
            {
                "heading": "Who it is for",
                "content": "DevOps/platform, ML engineers, and software engineers moving into AI infra. Prerequisites: Python, Git, and basic train/validate. If you want LLM-specific serving, eval gates, and token cost, that is LLMOps.",
            },
            {
                "heading": "Career support",
                "content": "Fee is ₹60,000 one-time. This is not a beginner Python or Power BI course. Placement support, a course certificate, and internship opportunities are included.",
            },
        ],
        "faqs": [
            {"question": "Is the fee ₹80,000?", "answer": "No. The published fee is ₹60,000 one-time. Duration on this catalog is 6 months."},
            {"question": "Do you teach Power BI?", "answer": "No. Ops dashboards here are Prometheus/Grafana-style. Power BI is only on Data Analytics with AI."},
            {"question": "How is this different from LLMOps?", "answer": "MLOps is training pipelines, registries, and serving classical/ML models. LLMOps is inference, eval gates, traces, and token cost."},
        ],
        "related": [
            {"slug": "llmops-course", "title": "LLMOps"},
            {"slug": "data-science-course", "title": "Data Science Gen AI"},
        ],
    },
    "prog-llmops": {
        "title": "LLMOps — AI Career Academy",
        "description": "Live 3-month LLM operations path: inference serving, RAG eval gates, prompt/adapter versioning, traces, guardrails, and cost control. Fee ₹35,000.",
        "hero_title": "LLMOps",
        "hero_sub": "Three months live for engineers who already ship services and now need LLM production habits: serving (vLLM-class), golden-set eval gates, prompt and adapter versioning, traces (LangSmith/Langfuse), guardrails, and token budgets. Not MLOps-for-tabular and not Power BI.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Inference latency (p95/p99), batching, RAG evaluation harnesses, CI gates that block bad prompts or retrievers, observability and cost dashboards, tool allowlists, and rollback. Grafana/Langfuse for ops visibility — we do not teach Power BI here.",
            },
            {
                "heading": "Who it is for",
                "content": "ML, platform, and backend engineers operating LLM APIs. If you need classic ML pipelines (DVC, training CI, tabular drift), take MLOps. If you need to build the app, take Gen AI for Developers.",
            },
            {
                "heading": "Career support",
                "content": "Fee is ₹35,000 one-time. A 12-week-style cohort will not replace years of platform engineering. Placement support, a course certificate, and internship opportunities are included.",
            },
        ],
        "faqs": [
            {"question": "What is the fee and duration?", "answer": "₹35,000, one-time, 3 months live."},
            {"question": "Do you teach Power BI?", "answer": "No. Observability is Langfuse/Grafana. Power BI is only on Data Analytics with AI."},
            {"question": "Do I need MLOps first?", "answer": "Helpful if you already ship services. Take MLOps if your job is tabular/training pipelines; take this if your job is LLM APIs."},
        ],
        "related": [
            {"slug": "mlops-course", "title": "MLOps"},
            {"slug": "generative-ai-course", "title": "Gen AI Specialization"},
        ],
    },
    "prog-java": {
        "title": "Java — AI Career Academy",
        "description": "Live 3-month Java sequence: core Java, collections, JDBC, Spring Boot REST, JPA, tests. Fee ₹40,000. Placement support, certificate, internships.",
        "hero_title": "Java",
        "hero_sub": "Three months live, online. Core Java through a Spring Boot API you can explain. Not a year-long dump and not a frontend course.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "OOP, collections, exceptions, JDBC, Maven/Gradle, Spring Boot REST, JPA/Hibernate, validation, and tests. You ship a small service, not a slide deck of syntax.",
            },
            {
                "heading": "Who it is for",
                "content": "Career switchers and early engineers who need a Java job-shaped stack. If you want UI, take Frontend (Deepak Rohilla). If you want pipelines and clusters, take DevOps.",
            },
            {
                "heading": "Career support",
                "content": "Fee is ₹40,000 one-time. Placement support, a course certificate, and internship opportunities are included — no invented placement percentage.",
            },
        ],
        "faqs": [
            {"question": "What is the fee and duration?", "answer": "₹40,000, one-time, 3 months live online."},
            {"question": "Is this Spring only?", "answer": "Core Java first, then Spring Boot REST and JPA. You will not skip collections to paste controllers."},
            {"question": "Do you offer placement, a certificate, and internships?", "answer": "Yes. Placement support, a course certificate, and internship opportunities are part of the program."},
        ],
        "related": [
            {"slug": "frontend-course", "title": "Frontend"},
            {"slug": "devops-course", "title": "DevOps"},
        ],
    },
    "prog-devops": {
        "title": "DevOps — AI Career Academy",
        "description": "Live 6-month DevOps sequence: Linux, Git, CI/CD, Docker, Kubernetes, IaC, cloud, observability. Fee ₹60,000. Not the MLOps model-pipeline track.",
        "hero_title": "DevOps",
        "hero_sub": "Six months live, online. Software delivery: build, ship, watch. This is not MLOps (model registries and drift) and not LLMOps.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Linux and networking enough to debug a box, Git and PR habits, CI/CD (GitHub Actions-class), Docker, Kubernetes, Terraform/IaC, a cloud account workflow, and Grafana/Prometheus-style ops. Grafana here is ops — not Power BI.",
            },
            {
                "heading": "Who it is for",
                "content": "Developers and sysadmins moving into platform work. If your job is training and serving ML models, that is MLOps. If it is LLM APIs, that is LLMOps.",
            },
            {
                "heading": "Career support",
                "content": "Fee is ₹60,000 one-time. Placement support, a course certificate, and internship opportunities are included. We will not invent a placement percentage.",
            },
        ],
        "faqs": [
            {"question": "What is the fee and duration?", "answer": "₹60,000, one-time, 6 months live online."},
            {"question": "How is this different from MLOps?", "answer": "DevOps is software delivery (CI/CD, k8s, IaC). MLOps is data/model versioning, training gates, and model serving."},
            {"question": "Do you teach Power BI?", "answer": "No. Observability is Prometheus/Grafana-style."},
        ],
        "related": [
            {"slug": "mlops-course", "title": "MLOps"},
            {"slug": "java-course", "title": "Java"},
        ],
    },
    "prog-frontend": {
        "title": "Frontend — AI Career Academy",
        "description": "Live 3-month frontend sequence: HTML, CSS, JavaScript, React. Mentored by Deepak Rohilla, senior frontend engineer. Fee ₹40,000.",
        "hero_title": "Frontend",
        "hero_sub": "Three months live, online. HTML, CSS, JavaScript, and React you can defend in a review. Faculty: Deepak Rohilla, senior frontend engineer.",
        "sections": [
            {
                "heading": "What you learn",
                "content": "Semantic HTML, CSS layout (flex/grid), accessible components, JavaScript without framework cargo-cult, then React: state, effects, routing, forms, and a capstone UI. Performance and a11y are in the syllabus, not a bonus slide.",
            },
            {
                "heading": "Who it is for",
                "content": "People aiming at frontend / UI engineer titles. Mentored by Deepak Rohilla. If you want Spring APIs, take Java. If you want clusters, take DevOps.",
            },
            {
                "heading": "Career support",
                "content": "Fee is ₹40,000 one-time. Placement support, a course certificate, and internship opportunities are included — no invented placement percentage.",
            },
        ],
        "faqs": [
            {"question": "Who mentors this program?", "answer": "Deepak Rohilla, senior frontend engineer, mentors the Frontend cohort."},
            {"question": "What is the fee and duration?", "answer": "₹40,000, one-time, 3 months live online."},
            {"question": "Is this a design-only course?", "answer": "No. You write HTML, CSS, JavaScript, and React. Visual polish without a working UI is not the bar."},
        ],
        "related": [
            {"slug": "java-course", "title": "Java"},
            {"slug": "ai-developers-course", "title": "Gen AI for Developers"},
        ],
    },
}
