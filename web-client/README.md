# ChatBet AI Web Client

## Simple Web Client for ChatBet AI

This is a simple and functional web client that connects with the ChatBet AI API to provide a clean and intuitive user interface.

## Main Features

### Three Main Sections:
1. **Input Area:** Text field to write questions with send and clear buttons
2. **Brief Response:** Shows a concise summary of the response (first 2-3 lines)
3. **Complete Response:** Shows the complete and detailed ChatBet AI response

### Implemented Functionalities:
- **Real-time connection** with ChatBet AI API (http://localhost:8000)
- **Connection status indicator** (Connected / Disconnected)
- **Loading indicators** while processing responses
- **Error handling** with informative messages
- **Responsive design** that works on desktop and mobile
- **Enter key** to send messages (Shift+Enter for new line)
- **Smart formatting** of responses with bold and italics
- **Session information** with Session ID and User ID
- **Clear button** to reset the interface

## How to Use the Web Client

### **Step 1: Start All Services**
Simply run the docker-compose command to start both the API and web client:
```powershell
# In the project directory
docker-compose up --build
```

### **Step 2: Open in Browser**
- Open web browser
- Go to: `http://localhost:3000`
- The web client will automatically connect to the backend API at `http://localhost:8000`

### **Step 3: Use ChatBet AI**
1. **Write question** in the text area
2. **Send** with button or pressing Enter
3. **View brief response** in the left panel
4. **View complete response** in the right panel

### **Alternative: Manual Setup (Development)**
If you prefer to run the web client manually:
```powershell
# Navigate to the web-client directory
cd C:\Users\samir\OneDrive\Escritorio\Chatbet\Chatbet\chatbet-ai\web-client

# Start local HTTP server
python -m http.server 3000
```

## Query Examples

```text
# Basic queries
When does Barcelona play?
Show me Real Madrid schedule
What matches are today?

# Betting analysis
What can I bet with $100?
Which is the most competitive match this weekend?
Who is favorite between Liverpool and Chelsea?

# Bet simulation
I want to bet $50 on a draw
How much would I win if I bet $100 on Barcelona?
What are the best betting opportunities today?

# Balance and history
Check my balance
Show my bet history
My simulated bets
```

## Design Features

### **Visual:**
- **Modern gradient** background (blue-purple)
- **Cards with shadows** for each section
- **Differentiated colors:**
  - Green for brief responses
  - Blue for complete responses
  - Red for errors
- **Smooth animations** on hover and loading

### **Responsive:**
- **Desktop:** 2-column grid layout
- **Mobile:** Vertical stacked layout
- **Adaptable** to different screen sizes

### **User Experience:**
- **Loading states** with animations
- **Visual error handling**
- **Success animations** on responses
- **Keyboard shortcuts** (Enter to send)

## Technical Configuration

### **Files:**
- `index.html` - Complete web client (HTML + CSS + JavaScript)

### **APIs Used:**
- `GET /health` - Check backend status
- `POST /chat` - Send messages to ChatBet AI

### **Ports:**
- **Backend:** http://localhost:8000 (ChatBet AI API)
- **Web Client:** http://localhost:3000 (Nginx server in Docker)

### **Docker Services:**
- **chatbet-ai:** Main API service
- **web-client:** Static file server using nginx:alpine

### **Compatibility:**
- **Browsers:** Chrome, Firefox, Safari, Edge (modern versions)
- **Devices:** Desktop, Tablet, Mobile
- **JavaScript:** ES6+ features used

## Testing and Validation

### **Tested States:**
- Connection successful with backend
- Message sending and responses
- Connection error handling
- Loading states working
- Brief and complete responses
- Responsive design on different screens
- Correct response formatting

### **Implemented Validations:**
- Empty input verification before sending
- API response validation
- Graceful network error handling
- Appropriate loading states
- Interface cleanup

## Web Client Screenshots

```
┌─────────────────────────────────────────┐
│  ChatBet AI                             │
│  Intelligent sports query system...     │
├─────────────────────────────────────────┤
│  Session: 1 | Con... │
│  ┌─────────────────────────────────────┐ │
│  │ Write your question here...         │ │
│  └─────────────────────────────────────┘ │
│  [Send] [Clear]                         │
├─────────────┬───────────────────────────┤
│Brief        │Complete                   │
│Response     │Response                   │
│             │                          │
│ Q: When does│ Q: When does Barcelona... │
│ Barcelona...│                          │
│             │ Barcelona has the         │
│ A: Barcelona│ following matches...      │
│ plays on... │                          │
│             │ • Sep 20 vs Espanyol     │
└─────────────┴───────────────────────────┘
```

## Possible Future Improvements

- **Persistent chat history**
- **Dark/light theme** toggle
- **Export conversations** to PDF
- **Notifications** for long responses
- **Auto-complete** for common questions
- **Multiple sessions** in tabs

---

**ChatBet AI Web Client ready to use!**