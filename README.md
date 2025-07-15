https://github.com/a1harfoush/MedLang-AI/blob/b5ef2098481cb7441a8f1d4b52e8403df78fe7b3/theme=dark.png
# MedLang: An LLM-based Medical Chatbot

MedLang is a sophisticated medical chatbot powered by a fine-tuned LLaMA-3 8B large language model. It's designed to improve healthcare accessibility and efficiency by providing accurate medical information, assisting with symptom diagnosis, and offering pre-consultation guidance to patients.

## Abstract

This project details the development of MedLang, a large language model (LLM)-based medical chatbot aimed at enhancing the accessibility and efficiency of healthcare information delivery. MedLang is designed to provide accurate medical information, assist in symptom diagnosis, and offer pre-consultation instructions to patients, aiding in preparation and potentially reducing the need for follow-up visits. The chatbot utilizes the fine-tuned LLaMA-3 8B model, leveraging the QLoRA (Quantized Low-Rank Adaptation) technique to optimize performance for medical question answering (QA), ensuring efficient use of computational resources. Key features include multilingual support through integrated translation services and the ability to search medical databases for the most up-to-date information, ensuring the accuracy and relevance of responses.

The implementation of MedLang leverages advanced AI models, translation services, and cloud deployment tools to ensure high accuracy and accessibility, supporting interactions in both English and Arabic. Google Cloud Run and Docker are used for deployment, ensuring scalability and reliability. The chatbot's functionality is further enhanced through the use of the Google Translation API for multilingual support and DuckDuckGo Search to fetch relevant medical information from reputable sources such as WebMD.

## Key Features

*   **Accurate Medical Information**: Delivers reliable and up-to-date medical information from reputable sources.
*   **Symptom Diagnosis Assistance**: Analyzes user-reported symptoms to provide preliminary assessments.
*   **Multilingual Support**: Supports interactions in both English and Arabic through real-time translation.
*   **Advanced AI**: Built on a fine-tuned LLaMA-3 8B model, optimized with QLoRA for efficiency and accuracy.
*   **Live Search**: Integrates with DuckDuckGo Search to fetch the latest information from trusted sources like WebMD.
*   **Patient Empowerment**: Empowers patients with information to make informed decisions about their health.

## Technologies and Tools

*   **Model**: Fine-tuned LLaMA-3 8B with QLoRA
*   **Frameworks**: LangChain, Chainlit
*   **Deployment**: Docker, Google Cloud Run
*   **APIs**: Groq API, Google Translation API, DuckDuckGo Search
*   **Authentication**: Google OAuth

## Future Work

*   **Image Recognition**: Integrate image analysis for visual diagnoses (e.g., skin conditions).
*   **Appointment Scheduling**: Implement a system for users to book medical appointments directly.
*   **Comprehensive Patient Histories**: Gather detailed patient histories to generate initial predicted diagnoses.
*   **Expanded Language Support**: Add support for more languages to increase global accessibility.
