import re
import json
import random
from collections import Counter
from datetime import datetime, timedelta

def clean_unicode(text):
    """Remove invisible Unicode characters"""
    text = text.replace('\u202f', ' ')
    text = text.replace('\u200e', '')
    text = text.replace('\u200d', '')
    text = text.replace('\u200c', '')
    return text.strip()

def parse_whatsapp_chat(file_path):
    """Parse WhatsApp chat with Unicode handling"""
    messages = []
    pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}).*?\]\s*([^:]+):\s*(.+)'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        print(f"📁 File loaded: {len(lines)} lines")
        
        for line in lines:
            line = clean_unicode(line.strip())
            if not line:
                continue
            
            match = re.match(pattern, line)
            if match:
                date = match.group(1)
                time = match.group(2)
                sender = clean_unicode(match.group(3))
                message = clean_unicode(match.group(4))
                
                if (message and 
                    not message.startswith('Messages and calls are end-to-end encrypted') and
                    not message.startswith('You deleted') and
                    not message.startswith('<Media omitted>') and
                    not message.startswith('This message was deleted') and
                    sender in ['Aaditya', 'Shloka']):
                    
                    messages.append({
                        'date': date,
                        'time': time,
                        'sender': sender,
                        'message': message
                    })
        
        print(f"✅ Successfully parsed {len(messages)} messages")
        return messages
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def find_relationship_milestones(messages):
    """Find special moments in your relationship - SIMPLIFIED"""
    milestones = []
    
    # Simplified milestone patterns - removed cute names
    milestone_patterns = {
        "First 'I like you'": [
            r'\bi\s+like\s+you\b',
            r'\bi\s+really\s+like\s+you\b',
            r'\byou\s+know\s+i\s+like\s+you\b'
        ],
        "First 'I love you'": [
            r'\bi\s+love\s+you\b',
            r'\blove\s+you\s+too\b',
            r'\bi\s+really\s+love\s+you\b'
        ],
        "First video/voice call mention": [
            r'\bcall\s+me\b', r'\bvideo\s+call\b', r'\bvoice\s+call\b',
            r'\blet\'s\s+call\b', r'\bcalling\s+you\b'
        ],
        "First 'miss you'": [
            r'\bi\s+miss\s+you\b', r'\bmissing\s+you\b', r'\bmiss\s+you\s+so\s+much\b'
        ],
        "First birthday wishes": [
            r'\bhappy\s+birthday\b', r'\bbirthday\s+wishes\b', r'\bspecial\s+day\b'
        ]
    }
    
    for milestone_name, patterns in milestone_patterns.items():
        for msg in messages:
            for pattern in patterns:
                if re.search(pattern, msg['message'].lower()):
                    milestones.append({
                        'type': milestone_name,
                        'message': msg,
                        'found_pattern': pattern
                    })
                    break
        if any(m['type'] == milestone_name for m in milestones):
            continue
    
    return milestones

def extract_conversations(messages, min_length=5, max_length=15):
    """Extract proper conversation threads"""
    conversations = []
    current_conversation = []
    
    for i, msg in enumerate(messages):
        current_conversation.append(msg)
        
        is_end = False
        
        if len(current_conversation) >= max_length:
            is_end = True
        elif i < len(messages) - 1:
            try:
                current_time = datetime.strptime(f"{msg['date']} {msg['time']}", "%d/%m/%y %H:%M:%S")
                next_time = datetime.strptime(f"{messages[i+1]['date']} {messages[i+1]['time']}", "%d/%m/%y %H:%M:%S")
                time_gap = (next_time - current_time).total_seconds() / 3600
                
                if time_gap > 2:
                    is_end = True
            except:
                pass
        else:
            is_end = True
        
        if is_end and len(current_conversation) >= min_length:
            conversations.append(current_conversation.copy())
            current_conversation = []
    
    print(f"📝 Extracted {len(conversations)} conversation threads")
    return conversations

def analyze_chat_data(messages):
    """Analyze chat for word frequency and special stats"""
    your_messages = [m['message'] for m in messages if m['sender'] == 'Aaditya']
    her_messages = [m['message'] for m in messages if m['sender'] == 'Shloka']
    
    # Count your "sorry"s
    sorry_words = ['Sorry', 'sorryyyy', 'sorry', 'sry', 'sori', 'sorri', 'apologise', 'apologize', 'my bad', 'forgive me']
    sorry_count = sum(1 for msg in your_messages 
                     for word in sorry_words
                     if word.lower() in msg.lower())
    
    # Most used words (excluding common words)
    exclude_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'a', 'an', 'this', 'that', 'these', 'those', 'will', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'would', 'should', 'my', 'your', 'me', 'him', 'her', 'us', 'them'}
    
    your_words = []
    for msg in your_messages:
        words = re.findall(r'\b[a-zA-Z]+\b', msg.lower())
        your_words.extend([w for w in words if len(w) > 2 and w not in exclude_words])
    
    her_words = []
    for msg in her_messages:
        words = re.findall(r'\b[a-zA-Z]+\b', msg.lower())
        her_words.extend([w for w in words if len(w) > 2 and w not in exclude_words])
    
    your_top_words = Counter(your_words).most_common(10)
    her_top_words = Counter(her_words).most_common(10)
    
    # Love-related stats
    love_words = ['love', 'miss', 'care', 'beautiful', 'gorgeous']
    your_love_count = sum(1 for msg in your_messages 
                         for word in love_words 
                         if word.lower() in msg.lower())
    
    her_love_count = sum(1 for msg in her_messages 
                        for word in love_words 
                        if word.lower() in msg.lower())
    
    return {
        'sorry_count': sorry_count,
        'your_top_words': your_top_words,
        'her_top_words': her_top_words,
        'your_love_count': your_love_count,
        'her_love_count': her_love_count
    }

def generate_clean_html(messages, analytics):
    """Generate clean and simple HTML for your girlfriend."""
    
    if not messages:
        return "<html><body><h1>No messages found!</h1></body></html>"
    
    conversations = extract_conversations(messages, min_length=4, max_length=12)
    
    conversations_json = json.dumps([
        [{
            'date': m['date'],
            'time': m['time'],
            'sender': m['sender'],
            'message': m['message']
        } for m in conv] for conv in conversations
    ])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Our Beautiful Conversations </title>
        <style>
            /* --- Variables for easy customization --- */
            :root {{
                --primary-color: #6A5ACD; /* Slate Blue for main accents */
                --secondary-color: #FF69B4; /* Hot Pink for Shloka's messages/accents */
                --background-light: #F0F8FF; /* Alice Blue, very light */
                --card-background: #FFFFFF;
                --text-dark: #2F4F4F; /* Dark Slate Gray */
                --text-medium: #696969; /* Dim Gray */
                --bubble-you-bg: #ADD8E6; /* Light Blue for Aaditya */
                --bubble-you-text: #2F4F4F; 
                --bubble-her-bg: #FFB6C1; /* Light Pink for Shloka */
                --bubble-her-text: #2F4F4F;
                --border-light: #E0FFFF; /* Light Cyan for subtle borders */
                --shadow-light: rgba(0,0,0,0.05);
                --shadow-medium: rgba(0,0,0,0.08);
                --shadow-strong: rgba(0,0,0,0.1);
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* A bit more friendly */
                background: var(--background-light);
                color: var(--text-dark);
                line-height: 1.6;
                display: flex; /* Use flexbox for centering */
                justify-content: center;
                align-items: center;
                min-height: 100vh; /* Full viewport height */
                padding: 20px;
            }}
            
            .container {{
                max-width: 1000px;
                width: 100%; /* Ensure it takes full width within max-width */
                margin: 0 auto;
                padding: 20px;
                border-radius: 25px; /* More pronounced rounded corners for the whole container */
                box-shadow: 0 10px 30px rgba(0,0,0,0.08); /* Stronger overall shadow */
                background: var(--card-background); /* White background for the main content area */
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 40px 20px;
                background: linear-gradient(145deg, var(--background-light), #E6E6FA); /* Very subtle gradient header */
                border-radius: 20px;
                box-shadow: 0 4px 20px var(--shadow-light);
            }}
            
            .header h1 {{
                font-size: 2.8rem;
                font-weight: 700;
                color: var(--primary-color);
                margin-bottom: 12px;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.05);
            }}
            
            .header p {{
                font-size: 1.2rem;
                color: var(--text-medium);
            }}
            
            .main-content {{
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: 30px;
            }}
            
            .sidebar {{
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            
            .chat-section {{
                background: var(--card-background);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 4px 20px var(--shadow-light);
                min-height: 70vh;
                display: flex;
                flex-direction: column;
            }}
            
            .stats-card {{
                background: var(--card-background);
                border-radius: 18px; /* Softer radius */
                padding: 25px; /* More padding */
                box-shadow: 0 4px 15px var(--shadow-light);
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            .stats-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px var(--shadow-medium);
            }}
            
            .stats-card h3 {{
                color: var(--primary-color);
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 20px;
                text-align: center;
            }}
            
            .sorry-counter {{
                background: linear-gradient(135deg, var(--primary-color), #8A2BE2); /* Blend with a deeper purple */
                color: white;
                text-align: center;
                padding: 25px;
                border-radius: 18px;
                margin-bottom: 20px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            }}
            
            .sorry-counter .number {{
                font-size: 3.5rem;
                font-weight: bold;
                display: block;
            }}
            
            .sorry-counter .label {{
                font-size: 1rem;
                margin-top: 8px;
                opacity: 0.95;
                font-weight: 500;
            }}
            
            .word-list {{
                display: flex;
                flex-direction: column;
                gap: 10px; /* Slightly more space */
            }}
            
            .word-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 15px;
                background: var(--background-light); /* Lighter background for items */
                border-radius: 10px;
                font-size: 0.95rem;
                border: 1px solid var(--border-light);
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            
            .word-item:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 12px var(--shadow-medium);
            }}
            
            .word-item.you {{
                border-left: 5px solid var(--bubble-you-bg);
            }}
            
            .word-item.her {{
                border-left: 5px solid var(--bubble-her-bg);
            }}
            
            .word-count {{
                font-weight: 700;
                color: var(--primary-color);
            }}
            
            .controls {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .refresh-btn {{
                background: linear-gradient(45deg, var(--primary-color), #8A2BE2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 30px;
                font-size: 1.05rem;
                font-weight: 500;
                cursor: pointer;
                box-shadow: 0 6px 20px rgba(106, 90, 205, 0.4);
                transition: all 0.3s ease;
            }}
            
            .refresh-btn:hover {{
                background: linear-gradient(45deg, #8A2BE2, var(--primary-color)); /* Invert gradient on hover */
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 8px 25px rgba(106, 90, 205, 0.5);
            }}
            
            .conversation {{
                background: var(--background-light); /* Lighter background for conversations */
                border-radius: 18px;
                padding: 25px;
                margin-bottom: 25px;
                border: 1px solid var(--border-light);
                box-shadow: 0 2px 10px var(--shadow-light);
            }}
            
            .conversation-header {{
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px dashed var(--border-light); /* Dashed line for softness */
            }}
            
            .conversation-date {{
                font-size: 1.05rem;
                color: var(--primary-color);
                font-weight: 600;
            }}
            
            .message {{
                margin: 15px 0;
                display: flex;
                flex-direction: column;
                opacity: 0; /* Start invisible for animation */
                transform: translateY(20px); /* Start slightly below */
                transition: opacity 0.4s ease-out, transform 0.4s ease-out; /* Smooth transition */
            }}
            
            .message.show {{
                opacity: 1;
                transform: translateY(0);
            }}
            
            .message.you {{ 
                align-items: flex-end; 
            }}
            
            .message.her {{ 
                align-items: flex-start; 
            }}
            
            .message-bubble {{
                max-width: 70%;
                padding: 14px 20px;
                border-radius: 25px;
                word-wrap: break-word;
                font-size: 1rem;
                box-shadow: 0 2px 8px var(--shadow-light);
            }}
            
            .message.you .message-bubble {{
                background: var(--bubble-you-bg);
                color: var(--bubble-you-text);
                border-bottom-right-radius: 8px;
            }}
            
            .message.her .message-bubble {{
                background: var(--bubble-her-bg);
                color: var(--bubble-her-text);
                border-bottom-left-radius: 8px;
            }}
            
            .message-time {{
                font-size: 0.8rem;
                opacity: 0.7;
                margin-top: 6px;
                font-weight: 400;
                color: var(--text-medium);
            }}
            
            .simple-stats {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px; /* More space */
                margin-top: 20px; /* More margin */
            }}
            
            .simple-stat {{
                text-align: center;
                padding: 15px;
                background: var(--background-light);
                border-radius: 12px;
                border: 1px solid var(--border-light);
                box-shadow: 0 2px 8px var(--shadow-light);
                transition: transform 0.2s ease-in-out, background 0.2s ease-in-out;
            }}
            .simple-stat:hover {{
                transform: translateY(-2px);
                background: #EAF7FF; /* Slightly different hover background */
            }}
            
            .simple-stat .number {{
                font-size: 1.8rem; /* Larger numbers */
                font-weight: 700;
                color: var(--primary-color);
                margin-bottom: 5px;
            }}
            
            .simple-stat .label {{
                font-size: 0.9rem;
                color: var(--text-medium);
                margin-top: 3px;
            }}
            
            .loading {{
                text-align: center;
                padding: 40px;
                color: var(--text-medium);
                font-size: 1.2rem;
                animation: pulse 1.5s infinite alternate; /* Loading animation */
            }}

            @keyframes pulse {{
                from {{ opacity: 0.7; }}
                to {{ opacity: 1; }}
            }}
            
            @media (max-width: 768px) {{
                .main-content {{
                    grid-template-columns: 1fr;
                }}
                
                .header h1 {{
                    font-size: 2.2rem;
                }}
                
                .message-bubble {{
                    max-width: 90%; /* Allow bubbles to take more space on small screens */
                }}
                
                .sidebar {{
                    order: 2; /* Put sidebar below chat on mobile */
                }}
                .chat-section {{
                    order: 1;
                }}
            }}

            /* For even smaller screens (e.g., narrow phones) */
            @media (max-width: 480px) {{
                .container {{
                    padding: 10px;
                }}
                .header h1 {{
                    font-size: 1.8rem;
                }}
                .header p {{
                    font-size: 1rem;
                }}
                .chat-section, .stats-card {{
                    padding: 15px;
                }}
                .sorry-counter {{
                    padding: 18px;
                }}
                .sorry-counter .number {{
                    font-size: 2.8rem;
                }}
                .refresh-btn {{
                    padding: 10px 20px;
                    font-size: 0.95rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Our Beautiful Conversations </h1>
                <p>A collection of our cherished moments, always fresh and full of love. Built with ❤️ by Aaditya for Shloka.</p>
            </div>
            
            <div class="main-content">
                <div class="sidebar">
                    <div class="stats-card">
                        <h3>Sorry Counter 😅</h3>
                        <div class="sorry-counter">
                            <span class="number">{analytics['sorry_count']}</span>
                            <div class="label">Times Aaditya said sorry</div>
                        </div>
                    </div>
                    
                    <div class="stats-card">
                        <h3>Your Most Used Words 💬</h3>
                        <div class="word-list">
                            {chr(10).join([f'<div class="word-item you"><span>{word}</span><span class="word-count">{count}</span></div>' for word, count in analytics['your_top_words'][:6]])}
                        </div>
                    </div>
                    
                    <div class="stats-card">
                        <h3>Shloka's Most Used Words 🌸</h3>
                        <div class="word-list">
                            {chr(10).join([f'<div class="word-item her"><span>{word}</span><span class="word-count">{count}</span></div>' for word, count in analytics['her_top_words'][:6]])}
                        </div>
                    </div>
                    
                    <div class="stats-card">
                        <h3>Sweet Words Shared 🥰</h3>
                        <div class="simple-stats">
                            <div class="simple-stat">
                                <div class="number">{analytics['your_love_count']}</div>
                                <div class="label">From You</div>
                            </div>
                            <div class="simple-stat">
                                <div class="number">{analytics['her_love_count']}</div>
                                <div class="label">From Her</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="chat-section">
                    <div class="controls">
                        <button class="refresh-btn" onclick="loadNewConversations()">
                             Load Fresh Conversations
                        </button>
                    </div>
                    <div id="conversationsContainer">
                        <div class="loading">Loading our story... </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const allConversations = {conversations_json};
            
            function loadNewConversations() {{
                const container = document.getElementById('conversationsContainer');
                container.innerHTML = '<div class="loading">Loading fresh conversations... 💕</div>';
                
                // Shuffle conversations and pick a few
                const shuffled = [...allConversations].sort(() => 0.5 - Math.random());
                const selectedConversations = shuffled.slice(0, Math.min(4, shuffled.length));
                
                setTimeout(() => {{
                    container.innerHTML = ''; // Clear loading message
                    
                    selectedConversations.forEach((conversation, convIndex) => {{
                        const conversationDiv = document.createElement('div');
                        conversationDiv.className = 'conversation';
                        
                        const firstMsg = conversation[0];
                        conversationDiv.innerHTML = `
                            <div class="conversation-header">
                                <div class="conversation-date">${{firstMsg.date}} • ${{conversation.length}} messages</div>
                            </div>
                        `;
                        
                        // Use a promise or callback chain for sequential message display
                        let messageDelay = 0;
                        conversation.forEach((msg, msgIndex) => {{
                            messageDelay += 100; // Small delay between messages
                            setTimeout(() => {{
                                const messageDiv = document.createElement('div');
                                messageDiv.className = `message ${{msg.sender === 'Aaditya' ? 'you' : 'her'}}`;
                                
                                messageDiv.innerHTML = `
                                    <div class="message-bubble">
                                        ${{msg.message}}
                                    </div>
                                    <div class="message-time">${{msg.time}}</div>
                                `;
                                
                                conversationDiv.appendChild(messageDiv);
                                setTimeout(() => messageDiv.classList.add('show'), 10); // Add show class for animation
                            }}, messageDelay);
                        }});
                        
                        // Append the whole conversation after its messages are scheduled
                        setTimeout(() => {{
                            container.appendChild(conversationDiv);
                        }}, messageDelay + 200); // Small extra delay before adding next conversation
                    }});
                }}, 600); // Initial delay for "Loading fresh conversations..."
            }}
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {{
                loadNewConversations();
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

# Main execution
if __name__ == "__main__":
    chat_file = "chat.txt"
    
    print("🔄 Creating clean and simple conversation viewer...")
    
    # Parse the chat
    messages = parse_whatsapp_chat(chat_file)
    
    if messages:
        print(f"✅ Found {len(messages)} valid messages!")
        
        # Analyze chat data
        analytics = analyze_chat_data(messages)
        
        # Generate clean HTML
        html_output = generate_clean_html(messages, analytics)
        
        # Save to file
        with open("clean_conversations.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        
        print("✨ Clean conversation viewer created!")
        print("📁 File: clean_conversations.html")
        print("🎁 Features:")
        print("   - Simple, clean UI design")
        print("   - No milestone tracking")
        print("   - Focused on conversations only")
        print(f"   - Sorry counter: {analytics['sorry_count']}")
        print("   - Word frequency lists")
        print("   - Two-column layout")
        
    else:
        print("❌ No messages parsed. Check your chat.txt file.")
