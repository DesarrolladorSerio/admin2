import { useState, useEffect, useRef } from 'react';
import chatbotAPI from '../services/simpleChatbotAPI.js';

export default function ChatBotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null); // 👈 Nuevo: Guardar usuario actual
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Cargar sesión desde localStorage al montar
  useEffect(() => {
    // Verificar si hay token (usuario autenticado)
    const token = localStorage.getItem('authToken') || localStorage.getItem('token');

    if (!token) {
      // Si no hay token, limpiar sesión del chatbot
      localStorage.removeItem('chatbot_session_id');
      localStorage.removeItem('chatbot_messages');
      localStorage.removeItem('chatbot_user');
      setSessionId(null);
      setMessages([]);
      setCurrentUser(null);
      return;
    }

    // Obtener el usuario del token (decodificar el JWT para obtener user_id o email)
    const userData = getUserFromToken(token);
    const savedUser = localStorage.getItem('chatbot_user');

    // Si el usuario cambió, limpiar sesión anterior
    if (savedUser && savedUser !== userData) {
      console.log('🔄 Usuario diferente detectado, limpiando sesión anterior');
      localStorage.removeItem('chatbot_session_id');
      localStorage.removeItem('chatbot_messages');
      setSessionId(null);
      setMessages([]);
    }

    // Guardar usuario actual
    setCurrentUser(userData);
    localStorage.setItem('chatbot_user', userData);

    // Cargar sesión solo si es del mismo usuario
    const savedSessionId = localStorage.getItem('chatbot_session_id');
    const savedMessages = localStorage.getItem('chatbot_messages');

    if (savedSessionId) {
      setSessionId(savedSessionId);
    }

    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Error cargando mensajes guardados:', e);
      }
    }
  }, []); // Solo se ejecuta al montar el componente

  // 👇 Nuevo: Función para extraer datos del usuario del token JWT
  const getUserFromToken = (token) => {
    try {
      // Decodificar la parte del payload del JWT (segunda parte)
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      // Retornar un identificador único del usuario (puede ser user_id, email, etc.)
      return decoded.sub || decoded.user_id || decoded.email || 'unknown';
    } catch (e) {
      console.error('Error decodificando token:', e);
      return 'unknown';
    }
  };

  // Guardar mensajes en localStorage cuando cambien
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatbot_messages', JSON.stringify(messages));
    }
  }, [messages]);

  // Scroll automático al último mensaje
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus en input cuando se abre el chat
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]); const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setError(null);
  };

  const getCurrentContext = () => {
    // Detectar contexto actual del usuario
    const path = window.location.pathname;
    const context = {
      current_page: path,
      timestamp: new Date().toISOString()
    };
    d
    // Agregar contexto específico según la página
    if (path.includes('/reservas')) {
      context.section = 'reservations';
      context.action = 'viewing_reservations';
    } else if (path.includes('/documentos')) {
      context.section = 'documents';
      context.action = 'managing_documents';
    } else if (path.includes('/menu')) {
      context.section = 'main_menu';
    }

    return context;
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return; const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    // Agregar mensaje del usuario inmediatamente
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatbotAPI.sendMessage(inputMessage, sessionId);

      const { response: botResponse, session_id: newSessionId } = response;

      // Guardar session_id si es nueva
      if (newSessionId && newSessionId !== sessionId) {
        setSessionId(newSessionId);
        localStorage.setItem('chatbot_session_id', newSessionId);
      }

      // Agregar respuesta del bot
      const assistantMessage = {
        role: 'assistant',
        content: botResponse,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Error enviando mensaje:', err);
      let errorMessage = 'No se pudo enviar el mensaje. Por favor intenta nuevamente.';

      if (err.response?.status === 401) {
        errorMessage = 'Para funciones avanzadas necesitas iniciar sesión. Puedo ayudarte con preguntas generales.';
      } else if (err.response?.status === 500) {
        errorMessage = 'Error en el servidor. Por favor intenta más tarde.';
      }

      // Agregar mensaje de error visible en el chat
      const errorMsg = {
        role: 'assistant',
        content: `ℹ️ ${errorMessage}`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    if (window.confirm('¿Estás seguro de que quieres limpiar el chat?')) {
      setMessages([]);
      setSessionId(null);
      localStorage.removeItem('chatbot_session_id');
      localStorage.removeItem('chatbot_messages');

      // Mensaje de bienvenida
      setMessages([{
        role: 'assistant',
        content: '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?',
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
  };

  // Sugerencias rápidas
  const quickSuggestions = [
    '¿Qué documentos necesito para licencia clase B?',
    '¿Cómo hago una reserva?',
    '¿Cuánto cuesta la licencia?',
    '¿Cuáles son los horarios de atención?'
  ];

  const sendSuggestion = (suggestion) => {
    setInputMessage(suggestion);
    // Auto-enviar después de un breve delay para que el usuario vea el texto
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={toggleChat}
        className={`fixed bottom-6 right-6 z-50 w-16 h-16 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 ${isOpen ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        aria-label={isOpen ? 'Cerrar chat' : 'Abrir chat'}
      >
        {isOpen ? (
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse"></span>
        )}
      </button>

      {/* Ventana de chat */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col overflow-hidden border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-lg">Asistente Virtual</h3>
                <p className="text-xs text-blue-100">Soporte en línea</p>
              </div>
            </div>
            <button
              onClick={clearChat}
              className="p-2 hover:bg-blue-700 rounded-lg transition-colors"
              title="Limpiar conversación"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          {/* Mensajes */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <p className="text-gray-600 mb-4">¡Hola! Soy tu asistente virtual.</p>
                <p className="text-sm text-gray-500 mb-6">¿En qué puedo ayudarte hoy?</p>

                {/* Sugerencias rápidas */}
                <div className="space-y-2">
                  <p className="text-xs text-gray-400 font-semibold uppercase">Preguntas frecuentes:</p>
                  {quickSuggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendSuggestion(suggestion)}
                      className="block w-full text-left px-4 py-2 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                  <div
                    className={`rounded-lg p-3 ${msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : msg.isError
                        ? 'bg-red-100 text-red-800 border border-red-200'
                        : 'bg-white text-gray-800 border border-gray-200'
                      }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  <p className={`text-xs text-gray-400 mt-1 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                    {formatTime(msg.timestamp)}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Error message */}
          {error && (
            <div className="px-4 py-2 bg-red-50 border-t border-red-200">
              <p className="text-xs text-red-600">{error}</p>
            </div>
          )}

          {/* Input */}
          <div className="p-4 bg-white border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu pregunta..."
                disabled={isLoading}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              Presiona Enter para enviar
            </p>
          </div>
        </div>
      )}
    </>
  );
}
