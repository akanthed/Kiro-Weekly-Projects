# Meeting Time Zone Converter - Project Context

## Project Overview
This is a single-purpose web application for converting meeting times across 22 global timezones with calendar export and multiple date format options.

## Code Style Guidelines
- Use vanilla JavaScript (ES6+)
- Keep functions small and focused
- Use descriptive variable names
- Add comments for complex logic
- Follow consistent indentation (2 spaces)

## Key Libraries
- **Luxon**: For timezone conversions and date manipulation
- **Tailwind CSS**: For styling (via CDN)

## Important Notes
- No build process required - runs directly in browser
- All timezone conversions use IANA timezone identifiers
- URL parameters encode meeting data for sharing
- The .kiro directory should be tracked in git (not in .gitignore)

## Key Features
- 22 global timezones organized by region
- 4 date format options (Full, Short, ISO, European)
- Calendar export (.ics file generation)
- Copy individual or all times to clipboard
- Shareable URLs with encoded parameters

## Testing Checklist
- Test DST transitions
- Verify mobile responsiveness
- Check clipboard functionality
- Validate URL parameter encoding/decoding
- Test calendar export in multiple apps
- Test all date format options
- Verify regional grouping displays correctly
