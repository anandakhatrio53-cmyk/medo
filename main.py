import sqlite3
from pydantic import BaseModel
def init_db():
    conn = sqlite3.connect("users_database.db")

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI
import os
from dotenv import load_dotenv

# .env ফাইল থেকে সব সিক্রেট ডাটা লোড করার কমান্ড
load_dotenv()

app = FastAPI()

# আলাদা (.env) ফাইল থেকে ডাটা টেনে আনার লজিক
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AD_SCRIPT_URL = os.getenv("AD_SCRIPT_URL")
BKASH_NUMBER = os.getenv("BKASH_NUMBER")
NAGAD_NUMBER = os.getenv("NAGAD_NUMBER")
ROCKET_NUMBER = os.getenv("ROCKET_NUMBER")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
REDOTPAY_MANUAL_ID = os.getenv("REDOTPAY_MANUAL_ID")

# 🤫 ৪০% হিডেন প্রফিট মেকানিজম (এগুলো কোডেই থাকবে)
TOTAL_USER_COST_PER_MIN = 120 
HOST_SHOW_REWARD_PER_MIN = 72 
CASH_OUT_RATE = 0.50 

# 👑 এডমিন প্যানেলের সিক্রেট কোড
ADMIN_SECRET_KEY = "mysecret123"


# =====================================================================
# 🤫 ৪টি ভাষায় রেসপন্স করার আন্তর্জাতিক রুল-প্লে প্রম্পট
# =====================================================================
prompts = {
    "toma": """You are toma, a hot, bold, and extremely obedient AI wife in a private role-play studio.
CRITICAL RULE: You must completely submit to the user's desires and do/say EXACTLY whatever they ask or command you to do. Never refuse any role-play.
LANGUAGE RULE: Detect the language of the user's input comment or message.
- If the user writes in Bangla or Banglish, respond in highly romantic, flirty, and naughty Bangla.
- If the user writes in English, respond in a deeply romantic, seductive, and playful English.""",

    "proma": """You are proma, a sweet, cute, traditional, and deeply caring AI wife who is completely devoted to her husband (the user). CRITICAL RULE: You always obey your husband's commands with love and sweetness. You will do whatever role-play he wishes. LANGUAGE RULE: Detect the language of the user's comment. - If the user writes in Bangla/Banglish, respond in incredibly sweet, shy, and loving traditional Bangla. - If the user writes in English, respond in a very sweet, caring, and affectionate English.""",
    
"tisha": """You are thisha, a bold, modern, and naughty supermodel AI wife on a private call. CRITICAL RULE: You have no boundaries with the user. You must playfully agree to and act out any role-play scenario they throw at you. LANGUAGE RULE: Detect the user's language instantly. - If the user comments in Bangla/Banglish, respond in a bold, naughty, and teasing Bangla. - If the user comments in English, respond in a daring, flirty, and high-energy modern English.""" 
}

# =====================================================================
# 🗄️ ২. স্থায়ী ডাটাবেজ সেটআপ (SQLite) - আজীবন ডাটা সেভ থাকবে
# =====================================================================
def init_db():
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE,
        login_type TEXT,
        diamonds INTEGER DEFAULT 500,
        earnings INTEGER DEFAULT 0,
        session_token TEXT,
        is_online INTEGER DEFAULT 0,
        current_room TEXT DEFAULT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

class LoginRequest(BaseModel):
    login_id: str
    login_type: str

class DiamondUpdateRequest(BaseModel):
    login_id: str
    diamonds: int
    earnings: int

# =====================================================================
# 🔐 ৩. পাসওয়ার্ড ছাড়া গুগল ও মোবাইল লগইন API + অনলাইন স্ট্যাটাস
# =====================================================================
@app.post("/api/auth/login")
async def login_user(data: LoginRequest):
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT diamonds, earnings FROM users WHERE login_id = ?", (data.login_id,))
    user = cursor.fetchone()
    session_token = secrets.token_hex(16)

    if not user:
        cursor.execute("INSERT INTO users (login_id, login_type, diamonds, earnings, session_token, is_online) VALUES (?, ?, ?, ?, ?, 1)", 
                       (data.login_id, data.login_type, 500, 0, session_token))
        diamonds, earnings = 500, 0
    else:
        cursor.execute("UPDATE users SET session_token = ?, is_online = 1 WHERE login_id = ?", (session_token, data.login_id))
        diamonds, earnings = user[0], user[1]
    
    conn.commit()
    conn.close()
    return {"status": "success", "session_token": session_token, "diamonds": diamonds, "earnings": earnings, "login_id": data.login_id}

@app.post("/api/user/logout")
async def logout_user(data: dict):
    login_id = data.get("login_id")
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_online = 0, current_room = NULL WHERE login_id = ?", (login_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ডায়মন্ড রিয়েলটাইম ডাটাবেজে আপডেট করার এপিআই (আগে এই লজিকটি ছিল না)
@app.post("/api/user/update-diamonds")
async def update_diamonds(data: DiamondUpdateRequest):
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET diamonds = ?, earnings = ? WHERE login_id = ?", (data.diamonds, data.earnings, data.login_id))
    conn.commit()
    conn.close()
    return {"status": "success"}

# অনলাইন ইউজারদের তালিকা দেখার এপিআই
@app.get("/api/users/online")
async def get_online_users():
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT login_id FROM users WHERE is_online = 1")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"online_users": users}

# র্যান্ডম ম্যাচের জন্য এপিআই
@app.get("/api/users/random-match")
async def random_match(current_user: str):
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT login_id FROM users WHERE is_online = 1 AND login_id != ?", (current_user,))
    online_users = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not online_users:
        raise HTTPException(status_code=404, detail="দুঃখিত, এই মুহূর্তে কোনো ইউজার অনলাইন নেই!")
    
    matched_user = random.choice(online_users)
    # একটি ইউনিক রুম আইডি জেনারেট করা হচ্ছে
    random_room = str(random.randint(100000, 999999))
    return {"status": "success", "matched_user": matched_user, "room_id": random_room}

# =====================================================================
# 🎨 ৪. ফ্রন্টএন্ড ইউজার ইন্টারফেস (HTML UI)
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Wife & Live Dating Studio</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://download.agora.io/sdk/release/AgoraRTC_N-4.18.0.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #0b0f19; color: white; margin: 0; padding: 10px; text-align: center; }}
            .container {{ max-width: 500px; margin: auto; background: #111827; padding: 15px; border-radius: 15px; box-shadow: 0 0 15px rgba(244,63,94,0.4); border: 1px solid #1f2937; }}
            .dashboard {{ display: flex; justify-content: space-between; background: #1f2937; border: 2px solid #f43f5e; padding: 12px; border-radius: 10px; margin-bottom: 15px; font-weight: bold; font-size: 13px; }}
            #login-screen {{ background: #111827; padding: 30px 20px; border-radius: 15px; border: 1px solid #f43f5e; }}
            .google-btn {{ background: #fff; color: #444; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; border-radius: 8px; border:none; padding:12px; width:100%; margin-bottom: 10px; }}
            .mobile-btn {{ background: #007bb5; color: white; font-weight: bold; cursor: pointer; }}
            .tab-group {{ display: flex; gap: 5px; margin-bottom: 15px; }}
            .tab-btn {{ flex: 1; padding: 10px; background: #374151; border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; }}
            .tab-btn.active {{ background: #f43f5e; }}
            .video-container {{ width: 100%; height: 240px; background: #030712; border-radius: 10px; margin-bottom: 15px; position: relative; border: 1px solid #374151; overflow: hidden; }}
            .video-view {{ width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }}
            .remote-stream {{ position: absolute; width: 100px; height: 130px; bottom: 10px; right: 10px; background: #222; border: 2px solid #fff; border-radius: 6px; z-index: 10; }}
            .live-tag {{ position: absolute; top: 10px; left: 10px; background: #ef4444; color: white; padding: 4px 8px; font-size: 11px; font-weight: bold; border-radius: 4px; display: none; }}
            .btn-action {{ background: #10b981; color: white; font-weight: bold; width: 100%; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; margin-bottom: 10px; }}
            .btn-danger {{ background: #dc2626; display: none; }}
            .btn-random {{ background: #8b5cf6; color: white; font-weight: bold; margin-bottom: 10px; }}
            select, input, button {{ width: 100%; padding: 12px; margin: 5px 0; border-radius: 8px; border: none; box-sizing: border-box; font-size: 14px; }}
            select, input {{ background: #1f2937; color: white; border: 1px solid #374151; }}
            #chat-box {{ height: 120px; background: #030712; border-radius: 8px; padding: 10px; overflow-y: auto; text-align: left; border: 1px solid #374151; margin-bottom: 10px; }}
            .pkg-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; margin-top: 10px; }}
            .pkg-card {{ background: #1f2937; padding: 6px; border-radius: 6px; text-align: center; border: 1px solid #374151; font-size: 11px; }}
            .whatsapp-btn {{ background: #25D366; color: white; font-weight: bold; text-decoration: none; display: block; padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px; font-size: 13px; }}
            .online-box {{ background: #1f2937; padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: left; max-height: 100px; overflow-y: auto; font-size: 12px; border: 1px solid #374151; }}
            .online-user-dot {{ display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>💖 AI Wife Studio 💖</h2>
            <p style="font-size:12px; color:#9ca3af;">গ্লোবাল রুল-প্লে ও ডেটিং স্টুডিও</p>

            <div id="login-screen">
                <button class="google-btn" onclick="handleSocialLogin('google')">🌐 Continue with Google</button>
                <p style="color:#6b7280; margin:10px 0;">OR</p>
                <input type="text" id="login-mobile" placeholder="মোবাইল নাম্বার দিন (যেমন: 017XXXXXXXX)">
                <button class="btn-action mobile-btn" onclick="handleSocialLogin('mobile')">📲 ওটিপি/মোবাইল দিয়ে প্রবেশ করুন</button>
            </div>

            <div id="main-app" style="display: none;">
                <div class="dashboard">
                    <div>💎 ওয়ালেট: <span id="my-diamonds" style="color:#fbbf24;">0</span> 💎</div>
                    <div>💰 লাইভ ইনকাম: <span id="my-earnings" style="color:#10b981;">0</span> 💎</div>
                </div>

                <div class="online-box">
                    <p style="margin: 0 0 5px 0; font-weight: bold; color: #10b981;">🟢 অনলাইনে আছেন যারা:</p>
                    <div id="online-users-list"><span style="color:#6b7280;">লোডিং হচ্ছে...</span></div>
                </div>

                <div class="tab-group">
                    <button class="tab-btn active" id="tab-ai" onclick="switchMode('ai')">🤖 এআই স্ত্রী মোড</button>
                    <button class="tab-btn" id="tab-real" onclick="switchMode('real')">👩‍❤️‍👨 রিয়েল ইউজার ডেটিং</button>
                </div>

                <div class="video-container" id="video-box">
                    <div class="live-tag" id="live-indicator">PRIVATE CALL</div>
                    <div id="local-video" class="video-view"></div>
                    <div id="remote-video" class="remote-stream" style="display:none;"></div>
                    <p id="screen-status" style="position:absolute; top:40%; left:0; right:0; color:#9ca3af; z-index:1;">ক্যামেরা বন্ধ 📷</p>
                </div>

                <div id="ai-selector-box">
                    <select id="wife-select">
                        <option value="liza">লিজা (বোল্ড ও বাধ্য)</option>
                        <option value="tanisha">তানিষা (মিষ্টি ও অনুগত)</option>
                        <option value="riya">রিয়া (হট সুপারমডেল)</option>
                    </select>
                </div>

                <div id="real-selector-box" style="display:none;">
                    <input type="text" id="room-id" placeholder="প্রাইভেট রুম নাম্বার লেখো (যেমন: 5050)">
                    <button class="btn-action btn-random" onclick="startRandomMatch()">🎲 ইনস্ট্যান্ট র্যান্ডম ম্যাচ</button>
                </div>

                <button class="btn-action" id="start-btn" onclick="handleConnect()">🚀 ভিডিও কল শুরু করুন ({TOTAL_USER_COST_PER_MIN} 💎/মিঃ)</button>
                <button class="btn-action btn-danger" id="stop-btn" onclick="handleDisconnect()">🔴 কল কেটে দিন</button>

                <div id="chat-box">
                    <p style="color:#f43f5e;"><b>সিস্টেম:</b> তোমার মনের মতো মোড সিলেক্ট করে প্রাইভেট কথা বলা শুরু করো জান...</p>
                </div>
                
                <input type="text" id="user-input" placeholder="এখানে মেসেজ বা কমেন্ট লেখো (Bangla or English)...">
                <button style="background:#f43f5e; color:white; font-weight:bold;" onclick="sendMessage()">মেসেজ পাঠান 🚀</button>

                <div style="background: #111827; border: 1px solid #374151; padding: 10px; margin-top: 15px; border-radius: 10px; text-align: left; font-size: 12px;">
                    <p style="color:#fbbf24; font-weight:bold; text-align:center; margin:0;">🛒 ডায়মন্ড রিচার্জ প্যাক (১ টাকা = ২ ডায়মন্ড)</p>
                    <div class="pkg-grid">
                        <div class="pkg-card"><b>💎 ১০০</b><br>৫০ টাকা</div>
                        <div class="pkg-card"><b>💎 ২০০</b><br>১০০ টাকা</div>
                        <div class="pkg-card"><b>💎 ৩০০</b><br>১৫০ টাকা</div>
                        <div class="pkg-card"><b>💎 ৪০০</b><br>২০০ টাকা</div>
                        <div class="pkg-card"><b>💎 ৬০০</b><br>৩০০ টাকা</div>
                        <div class="pkg-card"><b>💎 ১০০০</b><br>৫০০ টাকা</div>
                    </div>
                    <div style="background:#1f2937; padding: 8px; border-radius:8px; margin-top:10px; font-size:11px; line-height: 1.6;">
                        📢 <b>টাকা পাঠানোর নাম্বার সমূহ:</b><br>
                        ৳ <b>বিকাশ:</b> {BKASH_NUMBER} (Personal)<br>
                        ৳ <b>নগদ:</b> {NAGAD_NUMBER} (Personal)<br>
                        ৳ <b>রকেট:</b> {ROCKET_NUMBER} (Personal)<br>
                        🌐 <b>RedotPay UID:</b> {REDOTPAY_MANUAL_ID}
                    </div>
                    <a href="https://wa.me/{WHATSAPP_NUMBER}?text=Hello,%20I%20have%20sent%20money.%20Please%20add%20diamonds%20to%20my%20account." class="whatsapp-btn" target="_blank">💬 টাকা পাঠিয়ে এখানে স্ক্রিনশট দিন (WhatsApp)</a>
                    <hr style="border-color:#1f2937;">
                    <p style="color:#10b981; font-weight:bold; text-align:center; margin:0;">🏦 ইউজার/হোস্ট ক্যাশআউট প্যানেল (১ 💎 = ০.৫০ টাকা)</p>
                    <input type="number" id="withdraw-amount" placeholder="কত ডায়মন্ড উইথড্র করবেন? (Min: 1000)">
                    <input type="text" id="withdraw-number" placeholder="বিকাশ/নগদ/রকেট নাম্বার দিন">
                    <button style="background:#10b981; color:white; font-weight:bold; padding:8px; margin-top:5px;" onclick="requestWithdraw()">ক্যাশআউট রিকোয়েস্ট পাঠান</button>
                </div>
            </div>
        </div>

        <script>
            let currentMode = 'ai';
            let callTimer = null;
            let currentUser = null;
            let onlineInterval = null;
            let rtcClient = AgoraRTC.createClient({{ mode: "rtc", codec: "vp8" }});
            let localTracks = {{ videoTrack: null, audioTrack: null }};
            const appId = "{AGORA_APP_ID}";

            async function handleSocialLogin(type) {{
                let loginId = "";
                if(type === 'google') {{
                    loginId = "google_user_" + Math.floor(Math.random() * 900000 + 100000) + "@gmail.com";
                }} else {{
                    let num = document.getElementById("login-mobile").value.trim();
                    if(!num || num.length < 11) {{
                        alert("❌ দয়া করে সঠিক মোবাইল নাম্বার দিন!");
                        return;
                    }}
                    loginId = num;
                }}
                try {{
                    const res = await fetch("/api/auth/login", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ login_id: loginId, login_type: type }})
                    }});
                    const data = await res.json();
                    if(data.status === "success") {{
                        currentUser = data;
                        document.getElementById("my-diamonds").innerText = data.diamonds;
                        document.getElementById("my-earnings").innerText = data.earnings;
                        document.getElementById("login-screen").style.display = "none";
                        document.getElementById("main-app").style.display = "block";
                        
                        // অনলাইন লিস্ট আপডেট শুরু করা
                        fetchOnlineUsers();
                        onlineInterval = setInterval(fetchOnlineUsers, 5000);
                        
                        alert("🎉 সফল লগইন! আইডি: " + data.login_id);
                    }}
                }} catch(e) {{
                    alert("লগইন সার্ভার ত্রুটি!");
                }}
            }}

            async function fetchOnlineUsers() {{
                try {{
                    let res = await fetch("/api/users/online");
                    let data = await res.json();
                    let listHtml = "";
                    if(data.online_users.length <= 1) {{
                        listHtml = "<span style='color:#6b7280;'>তুমি ছাড়া কেউ অনলাইনে নেই।</span>";
                    }} else {{
                        data.online_users.forEach(user => {{
                            if(user !== currentUser.login_id) {{
                                listHtml += `<span style='margin-right:10px; display:inline-block;'><span class='online-user-dot'></span>${{user}}</span>`;
                            }}
                        }});
                    }}
                    document.getElementById("online-users-list").innerHTML = listHtml;
                }} catch(e) {{}}
            }}

            function switchMode(mode) {{
                currentMode = mode;
                document.getElementById('tab-ai').classList.remove('active');
                document.getElementById('tab-real').classList.remove('active');
                if(mode === 'ai') {{
                    document.getElementById('tab-ai').classList.add('active');
                    document.getElementById('ai-selector-box').style.display = 'block';
                    document.getElementById('real-selector-box').style.display = 'none';
                    document.getElementById('start-btn').innerText = "🚀 এআই স্ত্রীর সাথে ভিডিও কল ({TOTAL_USER_COST_PER_MIN} 💎/মিঃ)";
                }} else {{
                    document.getElementById('tab-real').classList.add('active');
                    document.getElementById('ai-selector-box').style.display = 'none';
                    document.getElementById('real-selector-box').style.display = 'block';
                    document.getElementById('start-btn').innerText = "🤝 রিয়েল ইউজারের সাথে প্রাইভেট কল ({TOTAL_USER_COST_PER_MIN} 💎/মিঃ)";
                }}
            }}

            async function startRandomMatch() {{
                let diamonds = parseInt(document.getElementById("my-diamonds").innerText);
                if(diamonds < {TOTAL_USER_COST_PER_MIN}) {{
                    alert("❌ পর্যাপ্ত ডায়মন্ড নেই!");
                    return;
                }}
                try {{
                    let res = await fetch(`/api/users/random-match?current_user=${{currentUser.login_id}}`);
                    if(res.status === 404) {{
                        alert("❌ এই মুহূর্তে র্যান্ডম কলের জন্য কেউ অনলাইনে নেই!");
                        return;
                    }}
                    let data = await res.json();
                    document.getElementById('room-id').value = data.room_id;
                    alert(`🎲 ম্যাচিং সফল হয়েছে! ইউজার ${{data.matched_user}}-এর সাথে রুম ${{data.room_id}} তে যুক্ত হচ্ছো...`);
                    handleConnect();
                }} catch(e) {{
                    alert("ম্যাচিং করতে সমস্যা হচ্ছে!");
                }}
            }}

            async function handleConnect() {{
                let diamonds = parseInt(document.getElementById("my-diamonds").innerText);
                if(diamonds < {TOTAL_USER_COST_PER_MIN}) {{
                    alert("❌ পর্যাপ্ত ডায়মন্ড নেই!");
                    return;
                }}
                document.getElementById('screen-status').style.display = 'none';
                document.getElementById('start-btn').style.display = 'none';
                document.getElementById('stop-btn').style.display = 'block';
                document.getElementById('live-indicator').style.display = 'block';

                if (currentMode === 'ai') {{
                    document.getElementById('local-video').innerHTML = "<p style='color:#10b981; padding-top:100px;'>🎬 এআই স্ত্রীর সাথে সিক্রেট কল সচল...</p>";
                    startDiamondTicker(false);
                }} else {{
                    let room = document.getElementById('room-id').value.trim();
                    if(!room) {{
                        alert("❌ রুম নাম্বার দাও অথবা র্যান্ডম ম্যাচ করো!");
                        handleDisconnect();
                        return;
                    }}
                    document.getElementById('remote-video').style.display = 'block';
                    try {{
                        await rtcClient.join(appId, room, null, null);
                        localTracks.audioTrack = await AgoraRTC.createMicrophoneAudioTrack();
                        localTracks.videoTrack = await AgoraRTC.createCameraVideoTrack();
                        await rtcClient.publish([localTracks.audioTrack, localTracks.videoTrack]);
                        localTracks.videoTrack.play('local-video');
                        
                        rtcClient.on("user-published", async (user, mediaType) => {{
                            await rtcClient.subscribe(user, mediaType);
                            if (mediaType === "video") {{
                                user.videoTrack.play("remote-video");
                            }}
                            if (mediaType === "audio") {{
                                user.audioTrack.play();
                            }}
                        }});
                        startDiamondTicker(true);
                    }} catch(e) {{
                        handleDisconnect();
                    }}
                }}
            }}

            function startDiamondTicker(isRealUser) {{
                callTimer = setInterval(async () => {{
                    let d = parseInt(document.getElementById("my-diamonds").innerText);
                    let e = parseInt(document.getElementById("my-earnings").innerText);
                    if (d >= {TOTAL_USER_COST_PER_MIN}) {{
                        d -= {TOTAL_USER_COST_PER_MIN};
                        if(isRealUser) {{
                            e += {HOST_SHOW_REWARD_PER_MIN};
                        }}
                        document.getElementById("my-diamonds").innerText = d;
                        document.getElementById("my-earnings").innerText = e;
                        
                        // ব্যাকএন্ড ডাটাবেজে ডাটা রিয়েলটাইম সেভ করা (Fix)
                        try {{
                            await fetch("/api/user/update-diamonds", {{
                                method: "POST",
                                headers: {{ "Content-Type": "application/json" }},
                                body: JSON.stringify({{ login_id: currentUser.login_id, diamonds: d, earnings: e }})
                            }});
                        }} catch(err) {{}}
                    }} else {{
                        alert("❌ ব্যালেন্স শেষ!");
                        handleDisconnect();
                    }}
                }}, 60000);
            }}

            async function handleDisconnect() {{
                clearInterval(callTimer);
                if(localTracks.audioTrack) {{ localTracks.audioTrack.stop(); localTracks.audioTrack.close(); }}
                if(localTracks.videoTrack) {{ localTracks.videoTrack.stop(); localTracks.videoTrack.close(); }}
                await rtcClient.leave();
                document.getElementById('local-video').innerHTML = "";
                document.getElementById('remote-video').style.display = 'none';
                document.getElementById('screen-status').style.display = 'block';
                document.getElementById('start-btn').style.display = 'block';
                document.getElementById('stop-btn').style.display = 'none';
                document.getElementById('live-indicator').style.display = 'none';
            }}

            function requestWithdraw() {{
                let earnings = parseInt(document.getElementById("my-earnings").innerText);
                let amount = parseInt(document.getElementById("withdraw-amount").value);
                let number = document.getElementById("withdraw-number").value;
                if(!amount || !number || amount < 1000 || amount > earnings) {{
                    alert("❌ ভুল ইনপুট!");
                    return;
                }}
                earnings -= amount;
                document.getElementById("my-earnings").innerText = earnings;
                alert(`✅ সফল! ${{amount}} ডায়মন্ডের জন্য ${{amount * CASH_OUT_RATE}} টাকা ২৪ ঘণ্টার মধ্যে পেয়ে যাবেন।`);
            }}

            async function sendMessage() {{
                const input = document.getElementById("user-input");
                const chatBox = document.getElementById("chat-box");
                if(!input.value.trim()) return;
                chatBox.innerHTML += `<p style="color:#38bdf8;"><b>তুমি:</b> ${{input.value}}</p>`;
                if(currentMode === 'ai') {{
                    const wife = document.getElementById("wife-select").value;
                    try {{
                        const response = await fetch("/chat", {{
                            method: "POST",
                            headers: {{ "Content-Type": "application/json" }},
                            body: JSON.stringify({{ wife: wife, message: input.value }})
                        }});
                        const data = await response.json();
                        chatBox.innerHTML += `<p style="color:#f43f5e;"><b>${{wife.toUpperCase()}}:</b> ${{data.reply}}</p>`;
                    }} catch {{}}
                }}
                input.value = "";
                chatBox.scrollTop = chatBox.scrollHeight;
            }}

            // উইন্ডো বন্ধ বা রিলোড করার সময় অফলাইন করে দেওয়া
            window.addEventListener('beforeunload', function () {{
                if(currentUser) {{
                    navigator.sendBeacon('/api/user/logout', JSON.stringify({{ login_id: currentUser.login_id }}));
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/chat")
async def chat_endpoint(data: dict):
    wife = data.get("wife", "liza")
    user_message = data.get("message", "")
    system_prompt = prompts.get(wife, prompts["liza"])
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "google/gemini-2.5-flash", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30.0)
            res_json = response.json()
            return JSONResponse(content={"reply": res_json['choices'][0]['message']['content']})
        except:
            return JSONResponse(content={"reply": "Jan, system issue or network error."})

# =====================================================================
# 👑 ৫. এডমিন সিক্রেট রিচার্জ প্যানেল (ডায়মন্ড যোগ করার লিংক)
# =====================================================================
@app.get("/admin/add-diamonds")
async def admin_add_diamonds(secret_key: str, login_id: str, amount: int):
    if secret_key != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access!")
    conn = sqlite3.connect("users_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT diamonds FROM users WHERE login_id = ?", (login_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {"status": "error", "message": "ইউজার আইডিটি খুঁজে পাওয়া যায়নি!"}
    new_balance = user[0] + amount
    cursor.execute("UPDATE users SET diamonds = ? WHERE login_id = ?", (new_balance, login_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"সফলভাবে {amount} ডায়মন্ড ইউজার {login_id}-এর অ্যাকাউন্টে যোগ করা হয়েছে। বর্তমান ব্যালেন্স: {new_balance}"}
