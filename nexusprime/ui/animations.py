"""CSS animations for NexusPrime dashboard."""


def get_animation_styles() -> str:
    """
    Get additional animation styles for advanced effects.
    
    Returns:
        CSS string with animation definitions
    """
    return """
    <style>
    /* ===== LOADING ANIMATIONS ===== */
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    .skeleton {
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.05) 25%,
            rgba(255, 255, 255, 0.1) 50%,
            rgba(255, 255, 255, 0.05) 75%
        );
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
    }
    
    /* ===== THINKING ANIMATION ===== */
    @keyframes thinking {
        0%, 20% {
            content: '.';
        }
        40% {
            content: '..';
        }
        60%, 100% {
            content: '...';
        }
    }
    
    .thinking::after {
        content: '.';
        animation: thinking 1.5s infinite;
    }
    
    /* ===== GLOW PULSE ===== */
    @keyframes glow-pulse {
        0%, 100% {
            box-shadow: 0 0 5px rgba(99, 102, 241, 0.5);
        }
        50% {
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.8);
        }
    }
    
    .glow-pulse {
        animation: glow-pulse 2s ease-in-out infinite;
    }
    
    /* ===== ROTATE ===== */
    @keyframes rotate {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    
    .rotate {
        animation: rotate 2s linear infinite;
    }
    
    /* ===== BOUNCE ===== */
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    .bounce {
        animation: bounce 1s ease-in-out infinite;
    }
    
    /* ===== SLIDE IN FROM SIDES ===== */
    @keyframes slideInLeft {
        from {
            transform: translateX(-100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .slide-in-left {
        animation: slideInLeft 0.5s ease-out;
    }
    
    .slide-in-right {
        animation: slideInRight 0.5s ease-out;
    }
    
    /* ===== SCALE IN ===== */
    @keyframes scaleIn {
        from {
            transform: scale(0.8);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    .scale-in {
        animation: scaleIn 0.3s ease-out;
    }
    
    /* ===== CONFETTI (when approved) ===== */
    @keyframes confetti-fall {
        0% {
            transform: translateY(-100vh) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
    
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: #6366f1;
        animation: confetti-fall 3s linear infinite;
    }
    
    /* ===== PROGRESS BAR ANIMATION ===== */
    @keyframes progress-indeterminate {
        0% {
            left: -50%;
        }
        100% {
            left: 100%;
        }
    }
    
    .progress-indeterminate::before {
        content: '';
        position: absolute;
        height: 100%;
        width: 50%;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.8), transparent);
        animation: progress-indeterminate 1.5s ease-in-out infinite;
    }
    
    /* ===== TEXT TYPING EFFECT ===== */
    @keyframes typing {
        from {
            width: 0;
        }
        to {
            width: 100%;
        }
    }
    
    .typing {
        overflow: hidden;
        white-space: nowrap;
        animation: typing 3s steps(40, end);
    }
    
    /* ===== NOTIFICATION TOAST ===== */
    @keyframes slideInTop {
        from {
            transform: translateY(-100px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutTop {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-100px);
            opacity: 0;
        }
    }
    
    .toast-enter {
        animation: slideInTop 0.3s ease-out;
    }
    
    .toast-exit {
        animation: slideOutTop 0.3s ease-in;
    }
    
    /* ===== HEARTBEAT ===== */
    @keyframes heartbeat {
        0%, 100% {
            transform: scale(1);
        }
        10%, 30% {
            transform: scale(1.1);
        }
        20%, 40% {
            transform: scale(1);
        }
    }
    
    .heartbeat {
        animation: heartbeat 1.5s ease-in-out infinite;
    }
    </style>
    """
