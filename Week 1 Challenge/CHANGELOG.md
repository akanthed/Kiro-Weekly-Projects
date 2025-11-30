# Changelog

## Version 2.1 - Modern UI Redesign (Current)

### 🎨 UI/UX Improvements

#### Visual Design
- **Glassmorphism effects** on cards for depth and modern aesthetic
- **Gradient backgrounds** - Purple to indigo theme throughout
- **Gradient text** for headings with brand colors
- **Smooth animations** - Float, fade-in, slide-in effects
- **Inter font** from Google Fonts for modern typography

#### Enhanced Components
- **Floating hero icon** with animation
- **Modern time cards** with gradient backgrounds and hover effects
- **Gradient buttons** with lift effects on hover
- **Improved input fields** with focus states and larger padding
- **Region headers** with accent borders and gradient backgrounds
- **Fixed notification** at top of screen with gradient

#### Color System
- Primary: Purple-Indigo gradient (#667eea → #764ba2)
- Secondary: Pink-Red gradient (#f093fb → #f5576c)
- Success: Blue-Cyan gradient (#4facfe → #00f2fe)
- Notification: Green-Emerald gradient

#### Interactions
- Hover lift effects on all cards and buttons
- Smooth transitions (0.3s cubic-bezier)
- Enhanced shadows on hover
- Better visual feedback

### 📚 Documentation
- Added DESIGN.md - Complete design system guide

---

## Version 2.0 - Enhanced Features

### 🎉 New Features

#### 1. Expanded Timezone Coverage
- **Before**: 10 timezones
- **After**: 22 timezones
- **Added**: Toronto, Mexico City, São Paulo, Berlin, Amsterdam, Stockholm, Moscow, Dubai, Hong Kong, Seoul, Melbourne, Auckland

#### 2. Calendar Export
- Export meetings to .ics format
- Compatible with Outlook, Google Calendar, Apple Calendar
- Includes all timezone conversions in event description
- One-click download

#### 3. Date Format Options
- **Full**: Tuesday, Nov 30, 2024
- **Short**: 11/30/2024 (US format)
- **ISO**: 2024-11-30 (International standard)
- **European**: 30/11/2024 (Day-first format)
- Live switching without regenerating

#### 4. Regional Organization
- Timezones grouped by geographic region
- **Americas**: 7 timezones
- **Europe**: 6 timezones
- **Middle East & Asia**: 6 timezones
- **Pacific**: 3 timezones

#### 5. Enhanced UI
- Emoji icons for better visual recognition
- 3-button action bar (Copy All, Export, New)
- Date format selector in results view
- Improved mobile responsiveness

### 🔧 Technical Improvements
- Better state management (currentDateTime, currentSourceTimezone)
- Cleaner code organization
- Improved error handling
- More efficient DOM manipulation

### 📚 Documentation
- Added FEATURES.md - Detailed feature explanations
- Added TESTING.md - Comprehensive testing guide
- Updated README.md - Reflects all new features
- Added CHANGELOG.md - Version history

---

## Version 1.0 - Initial Release

### Features
- Basic timezone conversion (10 timezones)
- Shareable URLs
- Copy to clipboard
- Responsive design
- Auto-detect user timezone
- DST handling
- Pure HTML/CSS/JS (no build process)

### Timezones
- US: Pacific, Mountain, Central, Eastern
- Europe: London, Paris
- Asia: India, Singapore, Tokyo
- Pacific: Sydney

---

## Roadmap (Future Versions)

### Version 2.1 (Planned)
- [ ] Meeting duration selector
- [ ] Dark mode toggle
- [ ] Custom timezone picker
- [ ] Print-friendly view

### Version 3.0 (Ideas)
- [ ] Multiple meeting comparison
- [ ] Email template generator
- [ ] Recurring meeting support
- [ ] Calendar API integration
- [ ] QR code sharing
- [ ] Time zone abbreviation toggle
