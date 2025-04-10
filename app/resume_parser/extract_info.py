import re
import spacy

nlp = spacy.load('en_core_web_sm')

def extract_name(text: str) -> str:
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent
            break
    return name

if __name__ == "__main__":
    # print(extract_name("Who the hell is Steve Jobs?"))
    print(extract_name("Hardik Prakash hardikprakash.official@gmail.com   +918130841139   Delhi, India   GitHub WORK EXPERIENCE FutureSoft June 2024   January 2025 SDE Intern Remote -FutureSoft India is a software consulting and technology services company specializing in industry-specific solutions, strategic outsourcing and integration services. -Anti-Poaching Surveillance System: o Contributed to developing a forest surveillance system by integrating YOLOv8 for real-time detection of humans and vehicles and building a React.js dashboard for live streams and automated alerts. Designed efficient backend APIs with FastAPI and implemented a lightweight logging system with SQLite to store alert history and system events. o Stack: JavaScript (React); Python (FastAPI + Flask); YOLOv8 (Object Recognition)."))