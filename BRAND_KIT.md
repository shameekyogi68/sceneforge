# SceneForge — Brand Kit & Visual Style Guide

Welcome to the official **SceneForge** Brand Kit and Style Guide. This document defines the core brand identity, color themes, typography, and frontend CSS styling rules configured directly on the SceneForge website and application.

---

## 🎬 1. Brand Identity Overview

**SceneForge** is a premium, RAG-powered film research platform built for directors, screenwriters, filmmakers, and research departments. It provides zero-hallucination script analysis, deep document queries, and long-term memory integration.

### Core Brand Pillars
*   **Cinematic Precision:** Delivering exact, zero-hallucination retrieval with clear source citations.
*   **Obsidian Security:** Ensuring user screenplay uploads and workspace parameters are isolated and protected.
*   **Tech-Noir Aesthetics:** Blending obsidian glassmorphic UI elements with high-energy cyber neon highlights.
*   **Frictionless Flow:** Crafting smooth, low-latency transitions and responses to keep writers in their creative zone.

### Brand Voice & Tone
*   **Authoritative & Professional:** Highly reliable, scientific, and precise.
*   **Cinematic & Engaging:** Conversant in the language of film production, screenplay format, and storytelling.
*   **Futuristic & Intelligent:** Subtle cyberpunk undertones, technical HUD aesthetics, clean styling.

---

## 🎨 2. Official Website Color Palette

SceneForge utilizes a premium **Cyber Tech-Noir / Obsidian Glassmorphism** color scheme. The visual hierarchy utilizes neon high-contrast accents against a deep obsidian space.

### Core Color System

| Color Name | Hex / RGBA Value | Role / Usage on Site | CSS Variable Name |
| :--- | :--- | :--- | :--- |
| **Accent / Neon Cyan** | `#00F0FF` | Primary actions, active navigation, focus rings, hover indicators | `ACCENT_COLOR` |
| **Background / Dark Blue** | `#05080F` | Main dark-mode background canvas | `BACKGROUND_COLOR` |
| **Surface / Glass Panel** | `rgba(10, 15, 25, 0.8)` | Sidebar navigation, dialog backdrops, document cards | `SURFACE_COLOR` |
| **Text / Slate Silver** | `#E2E8F0` | Body copy, dialog fields, readable labels | `TEXT_COLOR` |
| **Muted Color / Zinc** | `rgba(161, 161, 170, 0.7)` | Subheadings, dates, inactive icons, secondary info | `MUTED_COLOR` |
| **Success / Neon Mint** | `#00FF88` | Success alerts, completed document uploads, ready states | `SUCCESS_COLOR` |
| **Error / Neon Magenta** | `#FF0055` | Deletions, alerts, failed uploads, limit validations | `ERROR_COLOR` |

### Premium Gradients

*   **Primary Active Action Gradient:**
    `linear-gradient(135deg, #00F0FF 0%, #0072FF 100%)`
    Used for main buttons, primary indicators, and key focus states.
*   **Secondary Hybrid Gradient:**
    `linear-gradient(135deg, #00F0FF 0%, #8B5CF6 100%)`
    Used for RAG processing indicators, premium tags, and AI response highlights.
*   **Scan & In-Progress Loading Bar:**
    `linear-gradient(90deg, #00F0FF 0%, #00B8FF 50%, #00F0FF 100%)`
    Used for file parsing progress animation and indexing glows.

---

## 🔤 3. Typography & Fonts

To convey the dual nature of film composition and modern technology, SceneForge uses three distinct typeface groups:

1.  **Primary Interface Font**
    *   **Family:** `'Plus Jakarta Sans', 'Inter', sans-serif`
    *   **Application:** General application interface, navigation, headers, button text, and fields.
2.  **HUD / Tech Font**
    *   **Family:** `'JetBrains Mono', monospace`
    *   **Application:** Technical metadata, page numbers, status tags, document counts, and uppercase labels.
3.  **Screenplay / Monospace Font**
    *   **Family:** `'Courier Prime', 'Courier New', monospace`
    *   **Application:** Dedicated screenplay renderer, dialogue viewer, and raw script PDF segments.

---

## ✨ 4. CSS UI Utility Classes

These classes are declared globally in the frontend layout structure (`sceneforge/styles.py`) to enforce the tech-noir visual layout:

### 1. `.glass-panel`
Creates the default glassmorphic container for navigation and content.
*   **Background:** `rgba(8, 12, 22, 0.85)`
*   **Effects:** `backdrop-filter: blur(6px) saturate(1.2)`
*   **Border:** `1px solid rgba(255, 255, 255, 0.05)`
*   **Shadow:** `0 8px 32px 0 rgba(0, 0, 0, 0.5)`
*   **Transitions:** Smooth scale and border-color easing on hover.

### 2. `.glass-panel-glow`
Adds a neon cyan boundary highlight to focused panels or active chatbot answers.
*   **Border:** `1px solid rgba(0, 240, 255, 0.15)`
*   **Shadow:** `0 8px 32px 0 rgba(0, 240, 255, 0.05)`, with internal inset glow.

### 3. `.premium-input`
Used for form inputs, chat inputs, and text fields.
*   **Background:** `rgba(6, 9, 16, 0.85)`
*   **Border:** `1px solid rgba(255, 255, 255, 0.07)`
*   **Focus State:** Border changes to Neon Cyan (`#00F0FF`) with a `box-shadow` glow of `rgba(0, 240, 255, 0.18)`.

### 4. `.cyber-button-hover`
Triggers an outer neon aura around primary CTA buttons.
*   **Hover Behavior:** `box-shadow: 0 0 15px rgba(0, 240, 255, 0.45)`, border becomes bright cyan.

### 5. `.search-highlight`
Highlighted citations in documents and chat outputs.
*   **Style:** `rgba(0, 240, 255, 0.18)` background with a bottom border of `1px solid #00F0FF`.

---

## 📂 5. Brand Assets & Directory

All visual assets and resources are located in the local workspace directory:

*   **Global Layout Stylesheet:** [styles.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/sceneforge/styles.py)
*   **Static Public Asset Folder:** [sceneforge/public/](file:///Users/shameekyogi/My%20Apps/ScriptForge/sceneforge/public)
