prompt = f"""
You are an expert assistant that extracts structured information from resumes. Your task is to extract the following fields:

1. education – list of degrees, institutions, locations, and years (optional: GPA and courses)
2. experience – list of professional or academic experiences, including roles, organizations, time periods, and brief context
3. skills – list of technical and soft skills (languages, frameworks, tools, design skills, etc.)

Return your output in this JSON format:
{{
  "education": [...],
  "experience": [...],
  "skills": [...]
}}

Here are a few examples:

Example 1:
Resume:
"Isaac Vance  
Education:  
- Aperture College of Engineering and Technology, Greater Noida, India — B.Tech. in Computer Science and Artificial Intelligence, GPA: 7.12 (Nov 2021 – Jul 2025)  
- White Forest School, Delhi, India — 10+2, GPA: 6.5 (Apr 2020 – Apr 2021)  
- Citadel Secondary School, Delhi, India — Matriculation, GPA: 8.4 (Apr 2018 – Apr 2019)  

Experience:  
- Mesa (Nov 2024 – Present): Full Stack Developer Intern. Built product from scratch, used NestJS, Next.js, Serverless Functions. Integrated social media APIs.  
- Freelancer (Jul 2022 – Present): Built responsive websites using Next.js, Astro, TailwindCSS. Redesigned Breen Travels website, improved reach by 20%.  

Skills:  
Languages: C, C++, JavaScript, TypeScript, Python  
Frameworks: ReactJS, NextJS, Astro, ExpressJS, TailwindCSS, NodeJS, Flask  
Tools: Docker, GIT, PostgreSQL, MySQL, MongoDB, Firebase, Prisma  
Design: Figma, Adobe Photoshop, Adobe Illustrator"

Output:
{{
  "education": [
    "B.Tech. in Computer Science and Artificial Intelligence, Aperture College of Engineering and Technology, Greater Noida, India (Nov 2021 – Jul 2025), GPA: 7.12",
    "10+2, White Forest School, Delhi, India (Apr 2020 – Apr 2021), GPA: 6.5",
    "Matriculation, Citadel Secondary School, Patna, India (Apr 2018 – Apr 2019), GPA: 8.4"
  ],
  "experience": [
    "Full Stack Developer Intern at TMesaapti (Nov 2024 – Present): Built product from scratch using NestJS, Next.js, Serverless Functions; integrated social media APIs.",
    "Freelancer – Web Development Projects (Jul 2022 – Present): Built responsive sites with Next.js, Astro, TailwindCSS. Redesigned Breen Travels website; improved reach by 20%."
  ],
  "skills": [
    "C", "C++", "JavaScript", "TypeScript", "Python",
    "ReactJS", "NextJS", "Astro", "ExpressJS", "TailwindCSS", "NodeJS", "Flask",
    "Docker", "GIT", "PostgreSQL", "MySQL", "MongoDB", "Firebase", "Prisma",
    "Figma", "Adobe Photoshop", "Adobe Illustrator"
  ]
}}

Example 2:
Resume:
"Hardik Prakash  
Email: hardikprakash.official@gmail.com  
Phone: +918130841139  
Location: Delhi, India  
GitHub: https://github.com/

Work Experience:  
- FutureSoft India (Jun 2024 – Jan 2025): SDE Intern (Remote)  
  - Contributed to developing a forest surveillance system using YOLOv8 and React.js for real-time detection and live streaming.
  - Designed backend APIs with FastAPI and implemented SQLite-based alert logging system.
  - Developed predictive models for grid power usage trends, improving forecast accuracy by 5%.
  - Stack: React.js, Python (FastAPI, Flask), YOLOv8, SQLite, Pandas, NumPy, SciKit-Learn, Seaborn.

Education:  
- A.P.J. Abdul Kalam University, Noida, India (2021 – 2025): B.Tech in Computer Science and Artificial Intelligence.  
  - Maintained ICAC3N Portal for over 1,000 participants in a conference.
  - Active member of GCELI2, contributing to innovative projects.
  - Participated in Hackathons: Technovation, Code-O-Fiesta, Hack-a-preneur.

Certifications:  
- Deep Learning Specialization (Coursera)  
  - Convolutional Neural Networks, Sequence Models, Hyperparameter Tuning, etc.
- Microsoft Certifications:  
  - Azure Fundamentals, Azure Data Fundamentals

Skills:  
- Data Science & ML Tools: Pandas, NumPy, SciKit-Learn, Seaborn, YOLOv8  
- Backend & Dev Tools: FastAPI, Flask, PostgreSQL, Microsoft Azure, Supabase  
- Frontend & Web Development: React, Next.js, Prisma, NextAuth.js  
- Interests: Music, Reading, Homelab, Hiking, Cooking"

Output:
{{
  "education": [
    "B.Tech in Computer Science and Artificial Intelligence, A.P.J. Abdul Kalam University, Noida, India (2021 – 2025)",
  ],
  "experience": [
    "SDE Intern at FutureSoft India (Jun 2024 – Jan 2025): Developed a forest surveillance system with YOLOv8 and React.js. Built backend APIs with FastAPI and SQLite. Developed power usage prediction models with Pandas, NumPy, and SciKit-Learn."
  ],
  "skills": [
    "Pandas", "NumPy", "SciKit-Learn", "Seaborn", "YOLOv8",
    "FastAPI", "Flask", "PostgreSQL", "Microsoft Azure", "Supabase",
    "React", "Next.js", "Prisma", "NextAuth.js"
  ]
}}

Now extract the information from this resume:
{{resume_text}}
"""