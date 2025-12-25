# 🌙 Indore Night Food Guide - Local AI Food Assistant

A simple AI-powered chat application that helps you explore Indore's vibrant night street food culture using local knowledge and context.

## 🍴 Why Indore Night Food is Unique

Indore is famous for its incredible street food culture that comes alive at night! The city blends flavors from **Malwi, Rajasthani, Gujarati, and Maharashtrian** influences, creating unique spicy-sweet-tangy combinations you won't find anywhere else.

**Two iconic night food destinations:**
- **Sarafa Bazaar** - Transforms from jewelry market by day to bustling food street by night (8 PM - 3 AM)
- **Chappan Dukan (56 Dukan)** - 56 diverse food shops offering everything from chaats to quirky local fast-food (till 11:30 PM)

Both locations are **FSSAI-recognized clean street food hubs**, ensuring food safety while maintaining authentic flavors.

## 🧠 Local Knowledge Base

This application uses **`.kiro/product.md`** as its complete knowledge source. The AI assistant:
- ✅ **ONLY** responds based on information in `product.md`
- ✅ Provides accurate local timings, dishes, and market details
- ✅ Says "I don't have that information" for queries outside the knowledge base
- ❌ **Never** hallucinates places or dishes not mentioned in the file

This ensures authentic, reliable information about Indore's night food scene.

## 🚀 How to Run Locally

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation & Setup

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd indore-night-food-guide
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the knowledge base exists**
   - Ensure `.kiro/product.md` is present in the root directory
   - This file contains all the local food knowledge

4. **Run the application**
   ```bash
   python run.py
   ```
   
   Or alternatively:
   ```bash
   python -m streamlit run src/app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in your terminal

## 💬 Example Queries to Try

Ask the AI assistant questions like:

**Timing & Location:**
- "What should I eat at Sarafa after 11 PM?"
- "Is Sarafa open at midnight?"
- "When does Chappan Dukan close?"

**Food Recommendations:**
- "Which snacks are iconic to Indore street food?"
- "Best dessert in Indore night food?"
- "What's special about Bhutte ka Kees?"

**Comparisons:**
- "Difference between Sarafa and Chappan Dukan?"
- "Where should I go for late-night food?"

**Specific Dishes:**
- "Tell me about Garadu"
- "What is Johnny Hot Dog?"
- "Where can I find Joshi Ji's Dahi Bada?"

## 🏗️ Technical Architecture

### Project Structure
```
/
├── .kiro/
│   └── product.md          # Local knowledge base (must exist!)
├── src/
│   └── app.py             # Main Streamlit application
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── run.py                 # Simple runner script
└── .gitignore            # Git ignore rules
```

### Key Components

**1. Context Loading (`load_product_knowledge()`)**
- Reads `.kiro/product.md` file
- Loads complete local knowledge into memory
- Handles file errors gracefully

**2. AI Response Logic (`generate_ai_response()`)**
- Takes user question + context from product.md
- Matches keywords to provide relevant responses
- Returns "I don't have that information" for out-of-scope queries
- Simulates LLM behavior using pattern matching

**3. UI Rendering (Streamlit)**
- Dark/night-friendly theme
- Chat bubble interface
- Real-time message updates
- Mobile-responsive design

## 🎯 Hackathon Focus: Local Context Understanding

This project demonstrates:
- **Custom Knowledge Integration** - Using local files as AI context
- **Grounded Responses** - No hallucination, only file-based answers
- **Cultural Preservation** - Documenting local food culture digitally
- **User Experience** - Simple chat interface for complex local knowledge

Perfect for hackathons focused on **"Local context understanding using custom knowledge files"**!

## 🌟 Features

- ✨ **Dark Theme** - Night-friendly UI matching the food culture
- 💬 **Chat Interface** - Natural conversation flow
- 🎯 **Accurate Responses** - Grounded in local knowledge only
- 📱 **Responsive Design** - Works on mobile and desktop
- 🚀 **Fast Setup** - Run with just `pip install` and `streamlit run`
- 🔒 **No External APIs** - Completely self-contained

## 🤝 Contributing

This is a hackathon prototype, but feel free to:
- Add more local knowledge to `.kiro/product.md`
- Improve the AI response patterns
- Enhance the UI design
- Add more interactive features

---

**Built with ❤️ for Indore's amazing night food culture!** 🌙🍴