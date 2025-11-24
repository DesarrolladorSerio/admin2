import { useState, useEffect, useRef } from 'react';
import chatbotAPI from '../services/chatbotAPI.js';

export default function ChatBotWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [showHistory, setShowHistory] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [error, setError] = useState(null);
    const [conversations, setConversations] = useState([]);
    const [isLoadingConversations, setIsLoadingConversations] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Cargar conversaciones al abrir el chat (si está autenticado)
    useEffect(() => {
        const token = localStorage.getItem('authToken') || localStorage.getItem('token');
        if (token && isOpen) {
            loadConversations();
        }
    }, [isOpen]);

    // Scroll automático al último mensaje
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Focus en input cuando se abre el chat
    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const toggleChat = () => {
        setIsOpen(!isOpen);
        setError(null);
    };

    const toggleHistory = () => {
        setShowHistory(!showHistory);
        if (!showHistory) {
            loadConversations();
        }
    };

    // Cargar lista de conversaciones
    const loadConversations = async () => {
        setIsLoadingConversations(true);
        try {
            const data = await chatbotAPI.getConversations();
            setConversations(data.conversations || []);
        } catch (err) {
            console.error('Error cargando conversaciones:', err);
        } finally {
            setIsLoadingConversations(false);
        }
    };

    // Cargar una conversación específica
    const loadConversation = async (convSessionId) => {
        try {
            const history = await chatbotAPI.getSessionHistory(convSessionId);

            // Convertir el historial al formato de mensajes del componente
            const formattedMessages = history.messages?.map(msg => ({
                role: msg.role,
                content: msg.content,
                timestamp: msg.timestamp
            })) || [];

            setMessages(formattedMessages);
            setSessionId(convSessionId);
            setShowHistory(false); // Cerrar sidebar al cargar conversación
        } catch (err) {
            console.error('Error cargando conversación:', err);
            setError('No se pudo cargar la conversación');
        }
    };

    // Crear nueva conversación
    const createNewConversation = async () => {
        try {
            // Limpiar mensajes actuales
            setMessages([]);
            setSessionId(null);

            // Mensaje de bienvenida
            const welcomeMsg = {
                role: 'assistant',
                content: '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?',
                timestamp: new Date().toISOString()
            };
            setMessages([welcomeMsg]);

            setShowHistory(false);

            // Recargar lista de conversaciones
            await loadConversations();
        } catch (err) {
            console.error('Error creando nueva conversación:', err);
        }
    };

    const sendMessage = async (forceNew = false) => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
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
            const response = await chatbotAPI.sendMessage(inputMessage, sessionId, forceNew);

            const { response: botResponse, session_id: newSessionId } = response;

            // Guardar session_id si es nueva
            if (newSessionId && newSessionId !== sessionId) {
                setSessionId(newSessionId);
            }

            // Agregar respuesta del bot
            const assistantMessage = {
                role: 'assistant',
                content: botResponse,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Si se creó una nueva sesión, recargar lista de conversaciones
            if (forceNew) {
                await loadConversations();
            }

        } catch (err) {
            console.error('Error enviando mensaje:', err);
            let errorMessage = 'No se pudo enviar el mensaje. Por favor intenta nuevamente.';

            if (err.response?.status === 401) {
                errorMessage = 'Necesitas iniciar sesión para usar el chatbot.';
            } else if (err.response?.status === 500) {
                errorMessage = 'Error en el servidor. Por favor intenta más tarde.';
            }

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

    const clearCurrentChat = () => {
        if (window.confirm('¿Crear una nueva conversación? La actual se guardará en el historial.')) {
            createNewConversation();
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Ahora';
        if (diffMins < 60) return `Hace ${diffMins} min`;
        if (diffHours < 24) return `Hace ${diffHours}h`;
        if (diffDays < 7) return `Hace ${diffDays}d`;
        return date.toLocaleDateString();
    };

    return (
        <>
            {/* Botón flotante del chatbot */}
            <button
                onClick={toggleChat}
                className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-2xl hover:shadow-purple-500/50 hover:scale-110 transition-all duration-300 z-50 flex items-center justify-center group"
                aria-label="Abrir chat de asistencia"
            >
                {isOpen ? (
                    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                ) : (
                    <svg className="w-7 h-7 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                )}
            </button>

            {/* Ventana del chat */}
            {isOpen && (
                <div className="fixed bottom-24 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden border border-gray-200">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="font-bold text-lg">Asistente Virtual</h3>
                                <p className="text-xs text-white/80">En línea • Respondiendo al instante</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            {/* Botón historial */}
                            <button
                                onClick={toggleHistory}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                                title="Ver conversaciones anteriores"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </button>
                            {/* Botón nueva conversación */}
                            <button
                                onClick={createNewConversation}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                                title="Nueva conversación"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                            </button>
                            {/* Botón cerrar */}
                            <button
                                onClick={toggleChat}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    {/* Contenido principal con sidebar opcional */}
                    <div className="flex flex-1 overflow-hidden">
                        {/* Sidebar de historial */}
                        {showHistory && (
                            <div className="w-2/5 border-r border-gray-200 bg-gray-50 flex flex-col">
                                <div className="p-3 border-b border-gray-200 bg-white">
                                    <h4 className="font-semibold text-sm text-gray-700">Conversaciones</h4>
                                </div>
                                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                                    {isLoadingConversations ? (
                                        <div className="text-center py-4 text-gray-500 text-sm">
                                            Cargando...
                                        </div>
                                    ) : conversations.length === 0 ? (
                                        <div className="text-center py-4 text-gray-500 text-xs">
                                            No hay conversaciones previas
                                        </div>
                                    ) : (
                                        conversations.map((conv) => (
                                            <button
                                                key={conv.session_id}
                                                onClick={() => loadConversation(conv.session_id)}
                                                className={`w-full text-left p-2 rounded-lg hover:bg-white transition-colors ${sessionId === conv.session_id ? 'bg-blue-50 border border-blue-200' : 'bg-white'
                                                    }`}
                                            >
                                                <div className="text-xs font-medium text-gray-700 truncate">
                                                    {conv.preview}
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1 flex items-center justify-between">
                                                    <span>{formatTime(conv.updated_at)}</span>
                                                    <span className="text-xs bg-gray-200 px-1.5 py-0.5 rounded">
                                                        {conv.message_count}
                                                    </span>
                                                </div>
                                            </button>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Área de mensajes */}
                        <div className="flex-1 flex flex-col">
                            {/* Mensajes */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white">
                                {messages.length === 0 ? (
                                    <div className="text-center text-gray-500 mt-8">
                                        <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full mx-auto flex items-center justify-center mb-4">
                                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                            </svg>
                                        </div>
                                        <p className="text-sm font-medium">¡Hola! 👋</p>
                                        <p className="text-xs mt-2">¿En qué puedo ayudarte hoy?</p>
                                    </div>
                                ) : (
                                    messages.map((msg, index) => (
                                        <div
                                            key={index}
                                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                        >
                                            <div
                                                className={`max-w-[80%] rounded-2xl px-4 py-2 ${msg.role === 'user'
                                                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                                                        : msg.isError
                                                            ? 'bg-red-50 text-red-700 border border-red-200'
                                                            : 'bg-white text-gray-800 shadow-sm border border-gray-100'
                                                    }`}
                                            >
                                                <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                                                {msg.timestamp && (
                                                    <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-white/70' : 'text-gray-500'}`}>
                                                        {formatTime(msg.timestamp)}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}

                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-100">
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

                            {/* Input de mensaje */}
                            <div className="border-t border-gray-200 p-3 bg-white">
                                {error && (
                                    <div className="mb-2 p-2 bg-red-50 text-red-600 text-xs rounded-lg">
                                        {error}
                                    </div>
                                )}
                                <div className="flex space-x-2">
                                    <input
                                        ref={inputRef}
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Escribe tu mensaje..."
                                        className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                        disabled={isLoading}
                                    />
                                    <button
                                        onClick={() => sendMessage(false)}
                                        disabled={isLoading || !inputMessage.trim()}
                                        className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-2 rounded-full hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
