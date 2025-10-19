import { useState, useEffect, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PlusCircle, Send, Trash2, MessageSquare } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await axios.get(`${API}/sessions`);
      setSessions(response.data);
      if (response.data.length > 0 && !currentSession) {
        selectSession(response.data[0].id);
      }
    } catch (error) {
      console.error("Oturumlar yüklenemedi:", error);
      toast.error("Oturumlar yüklenemedi");
    }
  };

  const selectSession = async (sessionId) => {
    setCurrentSession(sessionId);
    try {
      const response = await axios.get(`${API}/sessions/${sessionId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error("Mesajlar yüklenemedi:", error);
      toast.error("Mesajlar yüklenemedi");
    }
  };

  const createNewSession = async () => {
    try {
      const response = await axios.post(`${API}/sessions`, {
        title: `Sohbet ${sessions.length + 1}`,
      });
      const newSession = response.data;
      setSessions([newSession, ...sessions]);
      setCurrentSession(newSession.id);
      setMessages([]);
      toast.success("Yeni sohbet oluşturuldu");
    } catch (error) {
      console.error("Oturum oluşturulamadı:", error);
      toast.error("Oturum oluşturulamadı");
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/sessions/${sessionId}`);
      const newSessions = sessions.filter((s) => s.id !== sessionId);
      setSessions(newSessions);
      if (currentSession === sessionId) {
        if (newSessions.length > 0) {
          selectSession(newSessions[0].id);
        } else {
          setCurrentSession(null);
          setMessages([]);
        }
      }
      toast.success("Sohbet silindi");
    } catch (error) {
      console.error("Oturum silinemedi:", error);
      toast.error("Oturum silinemedi");
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentSession) return;

    const userMessage = inputMessage;
    setInputMessage("");
    
    // Kullanıcı mesajını hemen göster
    const tempUserMsg = {
      id: Date.now().toString(),
      session_id: currentSession,
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages([...messages, tempUserMsg]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: currentSession,
        content: userMessage,
      });
      
      // Sadece assistant mesajını ekle (user mesajı zaten gösterildi)
      setMessages(prev => [...prev, response.data.assistant_message]);
    } catch (error) {
      console.error("Mesaj gönderilemedi:", error);
      toast.error("Mesaj gönderilemedi");
      // Hata olursa user mesajını geri al
      setMessages(messages);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1 className="app-title" data-testid="app-title">TürkGPT</h1>
          <Button
            onClick={createNewSession}
            className="new-chat-btn"
            data-testid="new-chat-button"
          >
            <PlusCircle className="icon" />
            Yeni Sohbet
          </Button>
          <div className="developer-badge">
            <div className="developer-badge-title">Developed by</div>
            <div className="developer-badge-name">Kadir Tolga Erdoğan</div>
            <div className="developer-badge-company">MaviGlobalSoft</div>
          </div>
        </div>
        <ScrollArea className="sessions-list">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${
                currentSession === session.id ? "active" : ""
              }`}
              onClick={() => selectSession(session.id)}
              data-testid={`session-${session.id}`}
            >
              <MessageSquare className="session-icon" />
              <span className="session-title">{session.title}</span>
              <button
                className="delete-btn"
                onClick={(e) => deleteSession(session.id, e)}
                data-testid={`delete-session-${session.id}`}
              >
                <Trash2 className="icon-small" />
              </button>
            </div>
          ))}
          {sessions.length === 0 && (
            <div className="empty-state" data-testid="empty-sessions">
              <p>Henüz sohbet yok</p>
              <p className="empty-subtitle">Yeni sohbet başlatın</p>
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Main Chat Area */}
      <div className="chat-area">
        {currentSession ? (
          <>
            <ScrollArea className="messages-container">
              {messages.length === 0 ? (
                <div className="welcome-screen" data-testid="welcome-screen">
                  <div className="welcome-content">
                    <h2 className="welcome-title">TürkGPT'ye Hoş Geldiniz</h2>
                    <p className="welcome-subtitle">
                      Size nasıl yardımcı olabilirim?
                    </p>
                    <div className="feature-cards">
                      <div className="feature-card">
                        <h3>🤔 Sorularınız</h3>
                        <p>Her türlü sorunuzu sorabilirsiniz</p>
                      </div>
                      <div className="feature-card">
                        <h3>💡 Fikir Üretme</h3>
                        <p>Yaratıcı fikirler ve çözümler</p>
                      </div>
                      <div className="feature-card">
                        <h3>✍️ Yazı Yazma</h3>
                        <p>Metin oluşturma ve düzenleme</p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="messages-list">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`message ${msg.role}`}
                      data-testid={`message-${msg.role}`}
                    >
                      <div className="message-avatar">
                        {msg.role === "user" ? "👤" : "🤖"}
                      </div>
                      <div className="message-content">
                        <div className="message-text">{msg.content}</div>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="message assistant" data-testid="loading-message">
                      <div className="message-avatar">🤖</div>
                      <div className="message-content">
                        <div className="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </ScrollArea>

            <div className="input-area">
              <div className="input-container">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Mesajınızı yazın..."
                  disabled={loading}
                  className="message-input"
                  data-testid="message-input"
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || loading}
                  className="send-btn"
                  data-testid="send-button"
                >
                  <Send className="icon" />
                </Button>
              </div>
              <div className="footer-credit">
                MaviGlobalSoft tarafından geliştirilmiştir. ( Kadir Tolga Erdoğan )
              </div>
            </div>
          </>
        ) : (
          <div className="no-session-screen" data-testid="no-session-screen">
            <h2>Sohbet Başlatın</h2>
            <p>Sol menüden yeni bir sohbet oluşturun</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
