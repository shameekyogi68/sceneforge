# SceneForge Style Guide: Cyber Tech-Noir Color Palette

This document provides a comprehensive overview of the design system, color palette, typography, and styling classes configured for the **SceneForge** project.

---

## 🎨 Theme Colors

The interface employs a premium **Cyber Tech-Noir / Obsidian Glassmorphism** color scheme with neon high-contrast accents:

| Color Name | Hex / RGBA Value | Role / Usage | Visual Sample |
| :--- | :--- | :--- | :--- |
| **Accent / Neon Cyan** | `#00F0FF` | Primary action buttons, active tab indicators, focus borders, primary highlights | `🔵` |
| **Background / Dark Blue** | `#05080F` | Main application background | `⚫` |
| **Surface / Glass Panel** | `rgba(10, 15, 25, 0.8)` | Sidebar navigation, dialog panels, project cards | `⬜` |
| **Text Color / Slate Silver**| `#E2E8F0` | Body copy, primary headers, readable text labels | `⚪` |
| **Muted Color / Zinc** | `rgba(161, 161, 170, 0.7)`| Subheadings, secondary metadata, inactive buttons | `🔘` |
| **Success / Neon Mint** | `#00FF88` | Success toasts, valid confirmations, completed file processing | `🟢` |
| **Error / Neon Magenta** | `#FF0055` | Error toasts, delete warnings, failed file processing limits | `🔴` |

---

## 🔤 Typography & Fonts

SceneForge uses three distinct font families tailored for different components:

1. **Primary Interface Font**:
   - **Family**: `'Plus Jakarta Sans', 'Inter', sans-serif`
   - **Usage**: General app interface, navigation, headers, button text, and dialog fields.
2. **HUD / Tech Font**:
   - **Family**: `'JetBrains Mono', monospace`
   - **Usage**: Used for technical identifiers, page numbers, tags, and uppercase status indicators (via the `.hud-text` helper class).
3. **Screenplay / Monospace Font**:
   - **Family**: `'Courier Prime', 'Courier New', monospace`
   - **Usage**: Dedicated display for script dialogs, screenplay text blocks, and original documents.

---

## ✨ CSS UI Utility Classes

Defined globally in `sceneforge/styles.py` to ensure premium visual design:

### 1. `.glass-panel`
- **Background**: `rgba(8, 12, 22, 0.85)`
- **Effects**: `backdrop-filter: blur(6px) saturate(1.2)`
- **Border**: `1px solid rgba(255, 255, 255, 0.05)`
- **Shadow**: `0 8px 32px 0 rgba(0, 0, 0, 0.5)`
- **Behavior**: Smooth transition on hover, border, and scale adjustments.

### 2. `.glass-panel-glow`
- **Border**: `1px solid rgba(0, 240, 255, 0.15)`
- **Effects**: `box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.05)`, nested inset glow.

### 3. `.premium-input`
- **Background**: `rgba(6, 9, 16, 0.85)`
- **Border**: `1px solid rgba(255, 255, 255, 0.07)`
- **Focus State**: Turns borders to Neon Cyan (`#00F0FF`), glows with `rgba(0, 240, 255, 0.18)` shadow, and darkens input background.

### 4. `.cyber-button-hover`
- **Hover Behavior**: Triggers dynamic Cyan outer glow (`box-shadow: 0 0 15px rgba(0, 240, 255, 0.45)`).
