# AkoweAI - Frontend Developer Implementation Guide

**Target Audience:** Frontend Developers  
**Date:** April 2026  
**Project:** AkoweAI - Multilingual AI Financial Bridge for Africa's Invisible MSMEs

---

## Table of Contents

1. [Overview](#overview)
2. [Project Setup](#project-setup)
3. [Landing Page Design](#landing-page-design)
4. [WhatsApp Integration](#whatsapp-integration)
5. [Mobile Responsiveness](#mobile-responsiveness)
6. [Performance Optimization](#performance-optimization)
7. [SEO & Analytics](#seo--analytics)
8. [Deployment](#deployment)

---

## Overview

### Project Scope

The frontend for AkoweAI consists of:

1. **Landing Page** - Informational site explaining the product
2. **WhatsApp CTA** - Primary call-to-action redirecting users to WhatsApp
3. **Responsive Design** - Mobile-first, works on all devices
4. **Fast Loading** - Optimized for low-bandwidth environments common in Nigeria

### Tech Stack

| Technology    | Purpose                             |
| ------------- | ----------------------------------- |
| **Framework** | React.js / Next.js (SSR for SEO)    |
| **Styling**   | Tailwind CSS + CSS Modules          |
| **Animation** | Framer Motion                       |
| **Forms**     | React Hook Form                     |
| **Analytics** | Google Analytics + Mixpanel         |
| **Hosting**   | Vercel / Netlify / Firebase Hosting |
| **CDN**       | Cloudflare (for Nigeria + Africa)   |

### Design Philosophy

-   **Simple & Clear**: Traders should understand the product in 10 seconds
-   **Mobile-First**: 80% of users access via mobile/WhatsApp
-   **Local Language**: Support for Nigerian context
-   **Fast**: Optimized for slow connections (2G/3G common in Nigeria)
-   **WhatsApp-Centric**: Primary interaction is WhatsApp

---

## Project Setup

### Initial Setup

```bash
# Create new Next.js project
npx create-next-app@latest akowe-landing --typescript --tailwind --eslint

# Navigate to project
cd akowe-landing

# Install additional dependencies
npm install framer-motion react-hook-form axios zustand

# Create folder structure
mkdir -p src/components src/pages src/styles src/utils src/hooks

# Start development
npm run dev
```

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_WHATSAPP_NUMBER=234XXXXXXXXXX
NEXT_PUBLIC_BUSINESS_NAME=AkoweAI
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_API_BASE_URL=https://api.akowe.ai
```

### Project Structure

```
akowe-landing/
├── public/
│   ├── images/
│   │   ├── hero-bg.jpg
│   │   ├── features/
│   │   └── testimonials/
│   └── videos/
│       └── demo.mp4
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── Hero.jsx
│   │   ├── Features.jsx
│   │   ├── HowItWorks.jsx
│   │   ├── Testimonials.jsx
│   │   ├── CTA.jsx
│   │   ├── Footer.jsx
│   │   └── WhatsAppButton.jsx
│   ├── pages/
│   │   ├── _app.jsx
│   │   ├── index.jsx
│   │   ├── about.jsx
│   │   ├── privacy.jsx
│   │   └── terms.jsx
│   ├── styles/
│   │   ├── globals.css
│   │   └── variables.css
│   ├── utils/
│   │   ├── analytics.js
│   │   ├── whatsapp.js
│   │   └── constants.js
│   └── hooks/
│       └── useWhatsApp.js
├── .env.local
├── .eslintrc.json
├── next.config.js
├── tailwind.config.js
└── package.json
```

---

## Landing Page Design

### 1. Page Layout Components

#### Header Component

```jsx
// src/components/Header.jsx
import Link from "next/link";
import { motion } from "framer-motion";
import { useState } from "react";

export default function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="fixed top-0 w-full bg-white/90 backdrop-blur-md shadow-sm z-50">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                {/* Logo */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2"
                >
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg" />
                    <span className="font-bold text-xl text-gray-800">
                        AkoweAI
                    </span>
                </motion.div>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex gap-8 items-center">
                    <Link
                        href="#features"
                        className="text-gray-700 hover:text-gray-900 transition"
                    >
                        Features
                    </Link>
                    <Link
                        href="#how-it-works"
                        className="text-gray-700 hover:text-gray-900 transition"
                    >
                        How It Works
                    </Link>
                    <Link
                        href="#faq"
                        className="text-gray-700 hover:text-gray-900 transition"
                    >
                        FAQ
                    </Link>
                    <Link
                        href="/about"
                        className="text-gray-700 hover:text-gray-900 transition"
                    >
                        About
                    </Link>
                </nav>

                {/* Mobile Menu Button */}
                <button
                    className="md:hidden"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                    <svg
                        className="w-6 h-6"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 6h16M4 12h16M4 18h16"
                        />
                    </svg>
                </button>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <motion.nav
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="md:hidden bg-white border-t flex flex-col gap-2 p-4"
                >
                    <Link href="#features" className="text-gray-700 py-2">
                        Features
                    </Link>
                    <Link href="#how-it-works" className="text-gray-700 py-2">
                        How It Works
                    </Link>
                    <Link href="/about" className="text-gray-700 py-2">
                        About
                    </Link>
                </motion.nav>
            )}
        </header>
    );
}
```

#### Hero Component

```jsx
// src/components/Hero.jsx
import { motion } from "framer-motion";
import WhatsAppButton from "./WhatsAppButton";

export default function Hero() {
    return (
        <section className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-500 to-green-600 text-white flex items-center pt-16">
            <div className="container mx-auto px-4 py-20">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                    {/* Left Content */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                            Your AI Business Co-Pilot
                        </h1>
                        <p className="text-lg md:text-xl text-blue-100 mb-8 leading-relaxed">
                            Speak your dialect. Take photos of receipts. We
                            handle the accounting.
                            <br />
                            <span className="font-semibold text-white">
                                Turn your informal business into formal growth.
                            </span>
                        </p>

                        {/* Key Metrics */}
                        <div className="grid grid-cols-2 gap-4 mb-8">
                            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4">
                                <div className="text-3xl font-bold">40M+</div>
                                <div className="text-blue-100">
                                    MSMEs in Nigeria
                                </div>
                            </div>
                            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4">
                                <div className="text-3xl font-bold">80%</div>
                                <div className="text-blue-100">
                                    Financially Invisible
                                </div>
                            </div>
                        </div>

                        <WhatsAppButton
                            label="🚀 Get Started Free"
                            message="Hi AkoweAI! I want to start managing my business smarter today!"
                            ctaType="primary"
                        />

                        <p className="text-blue-100 mt-4 text-sm">
                            ✓ Free for traders • Banks pay for reports • No
                            credit card needed
                        </p>
                    </motion.div>

                    {/* Right Visual */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="relative"
                    >
                        <div className="aspect-square bg-white/10 backdrop-blur-md rounded-2xl p-8 flex items-center justify-center">
                            <div className="text-center">
                                <div className="text-6xl mb-4">📱</div>
                                <p className="text-xl font-semibold">
                                    WhatsApp Interface
                                </p>
                                <p className="text-blue-100 mt-2 text-sm">
                                    Chat with your AI accountant
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Scroll Indicator */}
            <motion.div
                animate={{ y: [0, 5, 0] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
            >
                <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                </svg>
            </motion.div>
        </section>
    );
}
```

#### Features Component

```jsx
// src/components/Features.jsx
import { motion } from "framer-motion";

const features = [
    {
        id: 1,
        icon: "🎤",
        title: "Speak Your Language",
        description:
            "Voice notes in Pidgin, Yoruba, Igbo, or Hausa. AI understands your dialect.",
        longDescription:
            "No need to learn English business terminology. Speak naturally in your native dialect, and AkoweAI extracts transaction details automatically.",
    },
    {
        id: 2,
        icon: "📸",
        title: "Photo Receipts",
        description:
            "Snap photos of handwritten receipts or waybills. AI reads them instantly.",
        longDescription:
            "No more losing track of sales. Take a photo of any receipt, invoice, or handwritten note, and AkoweAI digitizes it automatically.",
    },
    {
        id: 3,
        icon: "📊",
        title: "Bank-Ready Reports",
        description:
            "Generate professional financial statements banks want to see.",
        longDescription:
            "6-month trading history, profit/loss analysis, and credit scores - all formatted for bank submissions. Get approved for loans faster.",
    },
    {
        id: 4,
        icon: "🎯",
        title: "Real-Time Analytics",
        description:
            "Know your numbers instantly: daily sales, expenses, and profit trends.",
        longDescription:
            "Stop guessing. Get real-time insights into your business performance with clear, actionable recommendations.",
    },
    {
        id: 5,
        icon: "🔒",
        title: "Your Data, Your Control",
        description:
            "All data encrypted and private. You decide who sees your reports.",
        longDescription:
            "Enterprise-level security for informal traders. Your business data belongs to you and only you.",
    },
    {
        id: 6,
        icon: "💰",
        title: "Free Forever (For You)",
        description:
            "Free for traders. Banks and lenders pay for credit reports.",
        longDescription:
            "Use AkoweAI completely free. We only make money when your bank wants to assess your credit.",
    },
];

export default function Features() {
    return (
        <section id="features" className="py-20 bg-gray-50">
            <div className="container mx-auto px-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                        Why Traders Love AkoweAI
                    </h2>
                    <p className="text-xl text-gray-600">
                        Designed for the Nigerian informal economy
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.id}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition cursor-pointer"
                        >
                            <div className="text-5xl mb-4">{feature.icon}</div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
```

#### How It Works Component

```jsx
// src/components/HowItWorks.jsx
import { motion } from "framer-motion";

const steps = [
    {
        number: 1,
        title: "Download WhatsApp",
        description: "AkoweAI lives in your WhatsApp chat",
        icon: "📲",
    },
    {
        number: 2,
        title: "Chat or Send Voice",
        description: "Send voice notes, receipts, or text messages",
        icon: "💬",
    },
    {
        number: 3,
        title: "AI Processes",
        description: "Claude AI extracts and organizes your transactions",
        icon: "🤖",
    },
    {
        number: 4,
        title: "Reports Ready",
        description: "Get instant financial reports and business insights",
        icon: "📊",
    },
];

export default function HowItWorks() {
    return (
        <section id="how-it-works" className="py-20 bg-white">
            <div className="container mx-auto px-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                        How It Works
                    </h2>
                    <p className="text-xl text-gray-600">
                        4 simple steps to smarter business management
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.number}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="relative"
                        >
                            {/* Arrow */}
                            {index < steps.length - 1 && (
                                <div className="hidden md:block absolute top-12 -right-2 text-3xl text-gray-300">
                                    →
                                </div>
                            )}

                            <div className="bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg p-8 text-center">
                                <div className="text-5xl mb-4">{step.icon}</div>
                                <div className="text-3xl font-bold mb-2">
                                    {step.number}
                                </div>
                                <h3 className="text-xl font-bold mb-2">
                                    {step.title}
                                </h3>
                                <p className="text-blue-100">
                                    {step.description}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
```

### 2. CTA (Call-to-Action) Section

```jsx
// src/components/CTA.jsx
import { motion } from "framer-motion";
import WhatsAppButton from "./WhatsAppButton";

export default function CTA() {
    return (
        <section className="py-20 bg-gradient-to-r from-blue-600 to-green-600 text-white">
            <div className="container mx-auto px-4 text-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6 }}
                >
                    <h2 className="text-4xl md:text-5xl font-bold mb-6">
                        Ready to Take Control of Your Business?
                    </h2>
                    <p className="text-lg md:text-xl text-blue-100 mb-10">
                        Join 100+ traders already using AkoweAI to get
                        bank-ready at scale.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <WhatsAppButton
                            label="Get Started Free"
                            message="Hi AkoweAI! I want to get started today!"
                            ctaType="primary"
                        />
                        <button className="px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-blue-50 transition">
                            Learn More
                        </button>
                    </div>

                    <p className="text-blue-100 mt-10 text-sm">
                        💰 100% free for traders • No credit card • Takes 30
                        seconds to start
                    </p>
                </motion.div>
            </div>
        </section>
    );
}
```

---

## WhatsApp Integration

### 1. WhatsApp Button Component

```jsx
// src/components/WhatsAppButton.jsx
import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useWhatsApp } from "../hooks/useWhatsApp";

export default function WhatsAppButton({
    label = "Chat on WhatsApp",
    message = "Hi! I'm interested in AkoweAI",
    ctaType = "secondary",
}) {
    const { openWhatsApp, isLoading } = useWhatsApp();

    const baseStyles =
        "px-6 py-3 rounded-lg font-semibold transition duration-300 flex items-center gap-2 justify-center";
    const styleMap = {
        primary: `${baseStyles} bg-green-500 text-white hover:bg-green-600 shadow-lg`,
        secondary: `${baseStyles} bg-white text-gray-900 hover:bg-gray-100`,
        outline: `${baseStyles} border-2 border-white text-white hover:bg-white hover:text-blue-600`,
    };

    return (
        <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => openWhatsApp(message)}
            disabled={isLoading}
            className={styleMap[ctaType]}
        >
            {!isLoading ? (
                <>
                    <svg
                        className="w-5 h-5"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.67-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421-7.403h-.004a9.87 9.87 0 00-5.031 1.378c-1.56.934-2.846 2.359-3.52 4.169-.64 1.67-.92 3.46-.52 5.12.39 1.66 1.36 3.14 2.64 4.29l.5.341.478.329c.21.144.477.326.751.548l.052.036c1.578 1.072 3.644 1.679 5.734 1.679 1.25 0 2.469-.194 3.637-.667l3.732 1.237-.98-3.868-.043-.123c.537-1.566.838-3.301.838-5.059 0-2.59-.52-5.07-1.53-7.514-.99-2.325-2.465-4.285-4.276-5.476-1.685-.98-3.63-1.45-5.694-1.45" />
                    </svg>
                    {label}
                </>
            ) : (
                "Loading..."
            )}
        </motion.button>
    );
}
```

### 2. WhatsApp Hook

```jsx
// src/hooks/useWhatsApp.js
import { useState } from "react";
import { useWhatsAppStore } from "../store/whatsapp";

export function useWhatsApp() {
    const [isLoading, setIsLoading] = useState(false);
    const { setLastAction } = useWhatsAppStore();

    const openWhatsApp = (message = "") => {
        setIsLoading(true);

        try {
            const phoneNumber = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER;
            const encodedMessage = encodeURIComponent(message);
            const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodedMessage}`;

            // Track analytics
            window.gtag?.("event", "whatsapp_click", {
                event_category: "engagement",
                event_label: message.substring(0, 30),
            });

            // Store last action
            setLastAction({
                type: "whatsapp_click",
                timestamp: new Date(),
                message: message,
            });

            // Open WhatsApp
            window.open(whatsappUrl, "_blank");
        } catch (error) {
            console.error("Error opening WhatsApp:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return { openWhatsApp, isLoading };
}
```

### 3. WhatsApp Helper Utilities

```jsx
// src/utils/whatsapp.js

/**
 * Format phone number for WhatsApp
 * Handles both +234 and 0 prefixes
 */
export function formatWhatsAppNumber(phone) {
    // Remove all non-digits
    let cleaned = phone.replace(/\D/g, "");

    // Handle Nigerian numbers
    if (cleaned.startsWith("234")) {
        return cleaned;
    }

    if (cleaned.startsWith("0")) {
        return "234" + cleaned.substring(1);
    }

    if (cleaned.length === 10) {
        return "234" + cleaned;
    }

    return cleaned;
}

/**
 * Generate WhatsApp URL
 */
export function generateWhatsAppUrl(phone, message = "") {
    const formattedPhone = formatWhatsAppNumber(phone);
    const encodedMessage = encodeURIComponent(message);
    return `https://wa.me/${formattedPhone}?text=${encodedMessage}`;
}

/**
 * Common message templates
 */
export const MESSAGE_TEMPLATES = {
    START: "Hi AkoweAI! I want to start managing my business smarter.",
    LEARN_MORE: "Tell me more about how AkoweAI works.",
    PRICING: "What's your pricing model?",
    SUPPORT: "I need help setting up AkoweAI.",
    DEMO: "Can you show me a demo?",
};

/**
 * Track WhatsApp engagement
 */
export function trackWhatsAppEngagement(eventType, data = {}) {
    if (typeof window !== "undefined" && window.gtag) {
        window.gtag("event", eventType, {
            event_category: "whatsapp_engagement",
            ...data,
        });
    }
}
```

---

## Mobile Responsiveness

### 1. Responsive Design Strategy

```css
/* src/styles/responsive.css */

/* Base styles: Mobile First */
@media (max-width: 640px) {
    :root {
        --spacing-unit: 0.25rem;
        --font-size-base: 14px;
        --font-size-h1: 28px;
        --font-size-h2: 22px;
        --font-size-h3: 18px;
    }

    body {
        font-size: var(--font-size-base);
    }

    h1 {
        font-size: var(--font-size-h1);
    }
    h2 {
        font-size: var(--font-size-h2);
    }
    h3 {
        font-size: var(--font-size-h3);
    }

    .container {
        padding: 0 1rem;
    }

    .grid-auto {
        grid-template-columns: 1fr;
    }

    .hero {
        min-height: 60vh;
        padding: 2rem 1rem;
    }

    .feature-card {
        padding: 1rem;
        text-align: center;
    }
}

/* Tablet: 641px - 1024px */
@media (min-width: 641px) and (max-width: 1024px) {
    :root {
        --spacing-unit: 0.5rem;
    }

    .grid-auto {
        grid-template-columns: repeat(2, 1fr);
    }

    .container {
        max-width: 640px;
    }
}

/* Desktop: 1025px+ */
@media (min-width: 1025px) {
    :root {
        --spacing-unit: 1rem;
    }

    .container {
        max-width: 1200px;
    }

    .grid-auto {
        grid-template-columns: repeat(3, 1fr);
    }

    .hero {
        min-height: 100vh;
    }
}

/* Very Small Devices: < 320px */
@media (max-width: 320px) {
    html {
        font-size: 12px;
    }

    h1 {
        font-size: 24px;
    }
    .btn {
        padding: 0.5rem 1rem;
    }
}

/* Large Screens: 1920px+ */
@media (min-width: 1920px) {
    .container {
        max-width: 1400px;
    }
}

/* Retina/High DPI Displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    img {
        image-rendering: -webkit-optimize-contrast;
    }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1a1a1a;
        --text-primary: #ffffff;
    }

    body {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### 2. Touch-Friendly Design

```jsx
// components/TouchFriendlyButton.jsx
import { motion } from "framer-motion";

export default function TouchFriendlyButton({ children, onClick, ...props }) {
    return (
        <motion.button
            whileTap={{ scale: 0.95 }}
            whileHover={{ scale: 1.05 }}
            onClick={onClick}
            className="min-h-12 min-w-12 px-4 py-3" // Min 44x44px for touch targets
            {...props}
        >
            {children}
        </motion.button>
    );
}
```

---

## Performance Optimization

### 1. Image Optimization

```jsx
// components/OptimizedImage.jsx
import Image from "next/image";

export default function OptimizedImage({ src, alt, ...props }) {
    return (
        <Image
            src={src}
            alt={alt}
            priority={props.priority || false}
            loading={props.loading || "lazy"}
            quality={75}
            placeholder="blur"
            blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRg..."
            {...props}
        />
    );
}
```

### 2. Code Splitting

```jsx
// pages/index.jsx
import dynamic from "next/dynamic";

const Hero = dynamic(() => import("../components/Hero"));
const Features = dynamic(() => import("../components/Features"));
const CTA = dynamic(() => import("../components/CTA"));
const Footer = dynamic(() => import("../components/Footer"));

export default function HomePage() {
    return (
        <main>
            <Hero />
            <Features />
            <CTA />
            <Footer />
        </main>
    );
}
```

### 3. Performance Monitoring

```jsx
// utils/performance.js
import { useEffect } from "react";

export function usePerformanceMonitoring() {
    useEffect(() => {
        if (typeof window !== "undefined" && "PerformanceObserver" in window) {
            // Monitor Core Web Vitals
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    console.log("Performance:", entry.name, entry.duration);

                    // Send to analytics
                    window.gtag?.("event", "page_speed", {
                        event_category: "performance",
                        event_label: entry.name,
                        value: Math.round(entry.duration),
                    });
                }
            });

            observer.observe({
                entryTypes: ["paint", "navigation", "largest-contentful-paint"],
            });
        }
    }, []);
}
```

---

## SEO & Analytics

### 1. SEO Setup

```jsx
// next-seo.config.js
export default {
    titleTemplate: "%s | AkoweAI",
    defaultTitle: "AkoweAI - AI Business Co-Pilot for Nigerian Traders",
    description:
        "Manage your informal business with voice notes and receipts. Generate bank-ready financial reports. Free for traders.",
    canonical: "https://akowe.ai",
    openGraph: {
        type: "website",
        locale: "en_NG",
        url: "https://akowe.ai",
        title: "AkoweAI - AI Business Co-Pilot",
        description: "Turn informal trade into formal growth",
        images: [
            {
                url: "https://akowe.ai/og-image.jpg",
                width: 1200,
                height: 630,
                alt: "AkoweAI - AI Business Co-Pilot for Nigerian Traders",
            },
        ],
    },
    twitter: {
        handle: "@AkoweAI",
        site: "@AkoweAI",
        cardType: "summary_large_image",
    },
};
```

### 2. Analytics Implementation

```jsx
// utils/analytics.js
import { useEffect } from "react";

export function useAnalytics() {
    useEffect(() => {
        // Google Analytics
        const script = document.createElement("script");
        script.src = `https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`;
        script.async = true;
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        function gtag() {
            window.dataLayer.push(arguments);
        }
        gtag("js", new Date());
        gtag("config", process.env.NEXT_PUBLIC_GA_ID);

        window.gtag = gtag;
    }, []);
}

// Custom event tracking
export function trackEvent(category, action, label, value) {
    if (typeof window !== "undefined" && window.gtag) {
        window.gtag("event", action, {
            event_category: category,
            event_label: label,
            value: value,
        });
    }
}

// Page view tracking
export function trackPageView(path) {
    trackEvent("page_view", "view", path);
}
```

---

## Deployment

### 1. Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# With custom domain
vercel --prod --domain akowe.ai
```

### 2. Environment Setup

```env
# .env.production
NEXT_PUBLIC_WHATSAPP_NUMBER=234XXXXXXXXXX
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_API_BASE_URL=https://api.akowe.ai
NODE_ENV=production
```

### 3. Next.js Config

```js
// next.config.js
module.exports = {
    reactStrictMode: true,
    swcMinify: true,
    compression: true,
    images: {
        formats: ["image/avif", "image/webp"],
        deviceSizes: [320, 500, 750, 1080, 1920],
        imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    },
    headers: async () => {
        return [
            {
                source: "/:path*",
                headers: [
                    { key: "X-DNS-Prefetch-Control", value: "on" },
                    { key: "X-Frame-Options", value: "SAMEORIGIN" },
                    { key: "X-Content-Type-Options", value: "nosniff" },
                ],
            },
        ];
    },
};
```

---

## Checklist Before Launch

-   [ ] Mobile responsiveness tested on multiple devices
-   [ ] WhatsApp links working correctly
-   [ ] All images optimized and loading fast
-   [ ] SEO tags properly configured
-   [ ] Analytics tracking working
-   [ ] Performance metrics < 3 seconds LCP
-   [ ] Accessibility (WCAG 2.1 AA) passed
-   [ ] Copy reviewed for clarity
-   [ ] All links working
-   [ ] Privacy policy and terms updated
-   [ ] SSL certificate installed
-   [ ] CDN configured for Nigeria region

---

## Troubleshooting

| Issue                            | Solution                                                    |
| -------------------------------- | ----------------------------------------------------------- |
| WhatsApp link not opening        | Check phone number format, ensure `wa.me` not blocked       |
| Slow loading on mobile           | Optimize images, reduce JS bundle size with code splitting  |
| Layout breaking on small screens | Test on actual devices, use Chrome DevTools responsive mode |
| Analytics not tracking           | Check GA ID, verify gtag loaded, check privacy settings     |
| Images not loading               | Verify image paths, check CDN configuration                 |

---

## Summary

The AkoweAI frontend is a sleek, mobile-first landing page focused on converting traders to WhatsApp. Key priorities:

1. **Speed** - Optimized for slow Nigerian connections
2. **Clarity** - Simple messaging for traders
3. **Conversion** - Clear WhatsApp CTA
4. **Mobile** - Touch-friendly, responsive design
5. **Analytics** - Track user engagement

This guide provides everything needed to build, optimize, and deploy the frontend successfully.
