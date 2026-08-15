const PROGRAMS = [
  {
    id: "data-analytics-ai",
    title: "Data Analytics with AI",
    duration: "5 Months",
    featured: true,
    tags: ["beginner", "career"],
    description: "Master Excel, SQL, and Power BI with AI-driven automation to transform raw data into business decisions.",
    topics: ["Excel and Power BI", "SQL for Data Analysis", "Data Cleaning and EDA", "AI-Powered Dashboards", "Business Intelligence", "Statistical Analysis"],
    section: "featured",
  },
  {
    id: "data-science-gen-ai",
    title: "Data Science Gen AI",
    duration: "6 Months",
    featured: true,
    tags: ["beginner", "career"],
    description: "Become a full-stack data scientist with Python, machine learning, deep learning, LLMs and RAG for real-world AI systems.",
    topics: ["Python for Data Science", "Core Machine Learning", "Deep Learning Foundations", "LLM Integration", "RAG Systems", "Model Deployment"],
    section: "featured",
  },
  {
    id: "gen-ai-developers",
    title: "Gen AI For Developers",
    duration: "3 Months",
    featured: true,
    tags: ["specialization"],
    description: "Build AI-powered applications — RAG chatbots, knowledge agents and automated workflows using modern LLM SDKs.",
    topics: ["Foundations for GenAI Applications", "API and SDK Integration", "RAG Pipelines", "Agent Workflows", "Prompt Engineering", "Production Deployment"],
    section: "featured",
  },
  {
    id: "gen-ai-specialization",
    title: "Gen AI Specialization",
    duration: "5 Months",
    featured: true,
    tags: ["career", "architect"],
    description: "Master Generative AI end-to-end — multimodal AI, RAG, LLM fine-tuning, quantization and agentic deployment.",
    topics: ["Advanced LLM Architectures", "Vision-Language and Multimodal Models", "RAG Design Patterns", "Fine-tuning and PEFT", "Quantization", "Agentic Deployment"],
    section: "featured",
  },
  {
    id: "mlops",
    title: "MLOP's",
    duration: "6 Months",
    featured: true,
    tags: ["specialization", "architect"],
    description: "Deploy and scale ML workflows with versioning, CI/CD, model serving, monitoring and evaluation pipelines.",
    topics: ["Docker and Containerization", "Kubernetes for ML Services", "Data and Model Versioning", "CI/CD for ML", "Model Monitoring", "Evaluation Pipelines"],
    section: "featured",
  },
  {
    id: "llmops",
    title: "LLMOP's",
    duration: "3 Months",
    featured: true,
    tags: ["specialization", "architect"],
    description: "Full GenAI lifecycle — prompt operations, RAGOps, agentOps, observability, governance and cost optimization.",
    topics: ["LLM Serving and Scaling", "Prompt Versioning and Governance", "RAG in Production", "AgentOps", "Observability", "Cost Optimization"],
    section: "featured",
  },
  {
    id: "aiops",
    title: "AIOP's",
    duration: "4 Months",
    featured: true,
    tags: ["architect"],
    description: "Unified machine learning, deep learning and Generative AI operations — deployment, scaling, governance and automation at enterprise level.",
    topics: ["Traditional ML Operations", "Deep Learning in Production", "LLMOps and AgentOps Foundations", "Enterprise Governance", "Automation Pipelines", "Scaling Strategies"],
    section: "featured",
  },
  {
    id: "ai-course-placement",
    title: "AI Course with Placement",
    duration: "4 Months",
    featured: true,
    tags: ["beginner", "career"],
    description: "Career starter AI course — build LLM apps, RAG and agents, then prepare for interviews with a structured Placement Prep Kit.",
    topics: ["Python for AI", "LLM App Development", "RAG Pipelines", "Agent Building", "Portfolio Projects", "Interview Preparation"],
    section: "featured",
  },
  {
    id: "agentic-ai",
    title: "Agentic AI",
    duration: "3 Months",
    featured: true,
    tags: ["specialization"],
    description: "Build autonomous AI agents that plan, reason and execute tasks using external tools and APIs.",
    topics: ["Agent and Tool Design", "Multi-agent Orchestration", "LangGraph and AutoGen Workflows", "Tool Use Patterns", "Memory Systems", "Evaluation Frameworks"],
    section: "featured",
  },
  {
    id: "llm-mastery",
    title: "LLM Mastery",
    duration: "2 Months",
    featured: true,
    tags: ["specialization"],
    description: "Strengthen core LLM engineering — embeddings, evaluation, scalable inference and knowledge workflows.",
    topics: ["LLM Fundamentals", "Tokenization and Embeddings", "Fine-tuning and PEFT", "Scalable Inference", "Knowledge Workflows", "Evaluation Metrics"],
    section: "featured",
  },
  {
    id: "ds-ml",
    title: "Data Science with Machine Learning",
    duration: "5 Months",
    featured: false,
    tags: ["beginner"],
    description: "Enter the machine learning world — Python, feature engineering, supervised and unsupervised modeling applied to real use cases.",
    topics: ["Python Essentials", "Supervised Learning", "Unsupervised Learning", "Feature Engineering", "Model Evaluation", "Real-world Projects"],
    section: "more",
  },
  {
    id: "ds-dl",
    title: "Data Science with Deep Learning",
    duration: "7 Months",
    featured: false,
    tags: ["specialization"],
    description: "Apply deep neural networks to language and vision applications with modern deep learning architectures.",
    topics: ["Neural Network Foundations", "Convolutional Networks", "Recurrent Networks", "Transformers", "Transfer Learning", "Deployment"],
    section: "more",
  },
  {
    id: "full-stack-ds",
    title: "Full Stack Data Science",
    duration: "10 Months",
    featured: false,
    tags: ["architect", "career"],
    description: "Complete career track — analytics, machine learning, cloud, deployment and monitoring to deliver end-to-end AI.",
    topics: ["Data Engineering Workflows", "Analytics and BI", "Machine Learning and Deep Learning", "Cloud Deployment", "MLOps", "End-to-End Projects"],
    section: "more",
  },
  {
    id: "ml-specialization",
    title: "Machine Learning Specialization",
    duration: "1 Month",
    featured: false,
    tags: ["specialization"],
    description: "Hands-on machine learning — evaluation, tuning, interpretability and performance optimization for real deployments.",
    topics: ["Core ML Algorithms", "Regression and Classification", "Clustering and Anomaly Detection", "Hyperparameter Tuning", "Model Interpretability", "Performance Optimization"],
    section: "more",
  },
  {
    id: "dl-specialization",
    title: "Deep Learning Specialization",
    duration: "3 Months",
    featured: false,
    tags: ["specialization"],
    description: "Convolutional, recurrent and transformer architectures, plus generative models, to master deep learning foundations.",
    topics: ["Neural Network Architectures", "Convolutional and Recurrent Models", "Generative Models", "Attention Mechanisms", "Transfer Learning", "Model Optimization"],
    section: "more",
  },
  {
    id: "computer-vision",
    title: "Computer Vision",
    duration: "2 Months",
    featured: false,
    tags: ["specialization"],
    description: "Detection, segmentation and visual analytics with deployment optimized for real-time environments.",
    topics: ["Image Processing", "Object Detection", "Segmentation", "Visual Analytics", "Real-time Inference", "Model Optimization"],
    section: "more",
  },
  {
    id: "nlp",
    title: "Natural Language Processing",
    duration: "2 Months",
    featured: false,
    tags: ["specialization"],
    description: "Build language AI — embeddings, transformers, information extraction and conversational systems.",
    topics: ["Text Preprocessing and Tokenization", "Word Embeddings and Transformers", "Named Entity Recognition", "Sentiment Analysis", "Conversational AI", "Information Extraction"],
    section: "more",
  },
];

const TAG_LABELS = {
  beginner: { label: "Beginner friendly", cls: "badge-green" },
  specialization: { label: "Specialization", cls: "" },
  architect: { label: "Architect level", cls: "" },
  career: { label: "Career track", cls: "" },
};

const MAX_TOPICS = 3;
const TOTAL = PROGRAMS.length;

function createCard(program) {
  const visibleTopics = program.topics.slice(0, MAX_TOPICS);
  const extraCount = program.topics.length - MAX_TOPICS;

  const badges = program.featured
    ? `<span class="badge badge-orange">Featured</span>`
    : "";

  const tagBadges = program.tags
    .map((t) => {
      const info = TAG_LABELS[t];
      return info ? `<span class="badge ${info.cls}">${info.label}</span>` : "";
    })
    .join("");

  const topicTags = visibleTopics
    .map((t) => `<span class="topic">${t}</span>`)
    .join("");

  const moreTag =
    extraCount > 0 ? `<span class="topic-more">+${extraCount} more</span>` : "";

  return `
    <article class="card" data-tags="${program.tags.join(",")}" data-id="${program.id}">
      <div class="card-top">
        <span class="card-duration">${program.duration}</span>
        <div class="card-badges">${badges}${tagBadges}</div>
      </div>
      <h3 class="card-title">${program.title}</h3>
      <p class="card-desc">${program.description}</p>
      <div class="card-topics">${topicTags}${moreTag}</div>
      <div class="card-footer">
        <a href="#" class="card-link" aria-label="View ${program.title} program">
          View program
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </a>
      </div>
    </article>
  `;
}

function renderPrograms() {
  const featured = PROGRAMS.filter((p) => p.section === "featured");
  const more = PROGRAMS.filter((p) => p.section === "more");

  document.getElementById("featuredGrid").innerHTML = featured.map(createCard).join("");
  document.getElementById("moreGrid").innerHTML = more.map(createCard).join("");
}

function applyFilter(filter) {
  const cards = document.querySelectorAll(".card");
  let visibleCount = 0;

  cards.forEach((card) => {
    const tags = card.dataset.tags.split(",");
    const show = filter === "all" || tags.includes(filter);
    card.classList.toggle("hidden", !show);
    if (show) visibleCount++;
  });

  ["featuredSection", "moreSection"].forEach((sectionId) => {
    const grid = document.getElementById(sectionId).querySelector(".grid");
    const visibleInSection = grid.querySelectorAll(".card:not(.hidden)").length;
    const existing = grid.querySelector(".empty-state");

    if (visibleInSection === 0) {
      if (!existing) {
        const tpl = document.getElementById("emptyTpl");
        grid.appendChild(tpl.content.cloneNode(true));
      }
    } else if (existing) {
      existing.remove();
    }
  });

  document.getElementById("showingCount").textContent =
    filter === "all"
      ? `Showing all ${TOTAL} programs`
      : `Showing ${visibleCount} of ${TOTAL} programs`;
}

function initFilters() {
  const pills = document.querySelectorAll(".filter-pill");
  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pills.forEach((p) => {
        p.classList.remove("active");
        p.setAttribute("aria-selected", "false");
      });
      pill.classList.add("active");
      pill.setAttribute("aria-selected", "true");
      applyFilter(pill.dataset.filter);
    });
  });
}

function initReveal() {
  if (!("IntersectionObserver" in window)) return;

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08 }
  );

  document.querySelectorAll(".grid").forEach((grid) => {
    grid.querySelectorAll(".card").forEach((card, i) => {
      card.classList.add("reveal");
      card.style.setProperty("--d", `${(i % 3) * 60}ms`);
      card.addEventListener(
        "animationend",
        () => {
          card.classList.remove("reveal", "in");
          card.style.removeProperty("--d");
        },
        { once: true }
      );
      io.observe(card);
    });
  });
}

function initNav() {
  const toggle = document.getElementById("navToggle");
  const nav = document.getElementById("nav");

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

function initHeader() {
  const header = document.getElementById("header");
  window.addEventListener(
    "scroll",
    () => header.classList.toggle("scrolled", window.scrollY > 8),
    { passive: true }
  );
}

document.getElementById("year").textContent = new Date().getFullYear();

renderPrograms();
initFilters();
initReveal();
initNav();
initHeader();
