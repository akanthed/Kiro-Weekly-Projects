# Meeting Time Zone Converter

A clean, single-purpose web application that converts meeting times across global timezones with shareable links.

## Problem It Solves

Coordinating meetings across different timezones is challenging. This tool:
- Instantly converts your meeting time to 10 major global timezones
- Generates shareable links so everyone sees the meeting time in their timezone
- Eliminates timezone confusion and scheduling errors
- Provides a simple, distraction-free interface

## Features

- **22 Global Timezones** - Americas, Europe, Middle East, Asia, Pacific
- **Calendar Export** - Download .ics file for Outlook, Google Calendar, Apple Calendar
- **Copy to Clipboard** - Copy individual or all times instantly
- **Date Format Options** - Full, Short, ISO, European formats
- **Shareable URLs** - Encoded meeting data in URL parameters
- **Fully Responsive** - Mobile-friendly design
- **Zero Build Process** - Pure HTML/CSS/JS, runs immediately
- **DST Handling** - Automatic daylight saving time adjustments
- **Organized by Region** - Times grouped by geographic region
- **Professional UI** - Modern design with glassmorphism and smooth interactions

## Tech Stack

- **Frontend**: Pure HTML, CSS, JavaScript
- **Styling**: Custom CSS with modern design system
- **Typography**: Inter font (Google Fonts)
- **Date/Time Library**: Luxon.js
- **Design**: Professional UI with glassmorphism and smooth interactions
- **Deployment**: Vercel / AWS Amplify ready

## Setup Instructions

### Quick Start (No Installation Required)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd meeting-timezone-converter
```

2. Open `index.html` in your browser:
```bash
# On Windows
start index.html

# On Mac
open index.html

# On Linux
xdg-open index.html
```

That's it! No build process, no dependencies to install.

### Deploy to Vercel

1. Install Vercel CLI (optional):
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

Or simply connect your GitHub repo to Vercel for automatic deployments.

### Deploy to AWS Amplify

1. Push your code to GitHub
2. Go to AWS Amplify Console
3. Connect your repository
4. Deploy (no build settings needed)

## Usage

1. **Select Date & Time**: Choose your meeting date and time
2. **Select Timezone**: Pick your current timezone (auto-detected by default)
3. **Generate Link**: Click to see conversions across 22 timezones
4. **Choose Date Format**: Switch between Full, Short, ISO, or European formats
5. **Export to Calendar**: Download .ics file to add to your calendar app
6. **Copy Times**: Copy individual times or all at once
7. **Share**: Copy the URL and share with meeting participants

## Supported Timezones (22 Total)

### Americas
- US Pacific, Mountain, Central, Eastern
- Toronto, Mexico City, São Paulo

### Europe
- London, Paris, Berlin, Amsterdam, Stockholm, Moscow

### Middle East & Asia
- Dubai, India, Singapore, Hong Kong, Tokyo, Seoul

### Pacific
- Sydney, Melbourne, Auckland

## URL Parameters

The app uses URL parameters to encode meeting data:
```
?time=2024-11-30T15:00:00.000-05:00&tz=America/New_York
```

- `time`: ISO 8601 formatted datetime
- `tz`: IANA timezone identifier

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT

## Contributing

Pull requests welcome! Please ensure your code follows the existing style.

---

Built with ❤️ using Kiro IDE
